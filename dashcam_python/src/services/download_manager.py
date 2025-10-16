"""Download manager for orchestrating parallel video downloads."""
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from queue import Queue, Empty
from threading import Thread, Event, Lock
from typing import List, Optional, Callable
from src.api.client import DashcamAPI
from src.api.models import VideoFile, DownloadTask

logger = logging.getLogger(__name__)


class DownloadManager:
    """Manages video download queue with parallel download support."""

    def __init__(
        self,
        api: DashcamAPI,
        download_dir: str,
        max_parallel: int = 3,
        on_progress_update: Optional[Callable[[DownloadTask], None]] = None,
        on_complete: Optional[Callable[[DownloadTask], None]] = None
    ):
        """Initialize download manager.

        Args:
            api: DashcamAPI instance for downloading files
            download_dir: Base directory for downloaded videos
            max_parallel: Maximum number of parallel downloads (2-3 recommended)
            on_progress_update: Callback for progress updates
            on_complete: Callback when a download completes
        """
        self.api = api
        self.download_dir = Path(download_dir)
        self.max_parallel = max_parallel
        self.on_progress_update = on_progress_update
        self.on_complete = on_complete

        # Create download directory
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Download queue and active downloads
        self.queue: List[DownloadTask] = []
        self.queue_lock = Lock()

        # Worker thread control
        self._stop_workers = Event()
        self._worker_thread: Optional[Thread] = None
        self._executor: Optional[ThreadPoolExecutor] = None

        logger.info(f"DownloadManager initialized with download_dir={download_dir}, max_parallel={max_parallel}")

    def start(self) -> None:
        """Start the download manager worker thread."""
        if self._worker_thread and self._worker_thread.is_alive():
            logger.warning("Download manager already running")
            return

        logger.info("Starting download manager")
        self._stop_workers.clear()
        self._executor = ThreadPoolExecutor(max_workers=self.max_parallel)
        self._worker_thread = Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

    def stop(self) -> None:
        """Stop the download manager and wait for active downloads to complete."""
        if not self._worker_thread:
            return

        logger.info("Stopping download manager")
        self._stop_workers.set()

        # Shutdown executor gracefully
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None

        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)
        self._worker_thread = None

        logger.info("Download manager stopped")

    def add_to_queue(self, video: VideoFile) -> DownloadTask:
        """Add a video to the download queue.

        Args:
            video: VideoFile to download

        Returns:
            DownloadTask instance for tracking
        """
        # Create download directory structure (by date)
        date_dir = self.download_dir / video.timestamp.strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)

        # Create task
        task = DownloadTask(
            file=video,
            status="queued",
            progress=0.0,
            speed_mbps=0.0,
            local_path=str(date_dir / video.filename)
        )

        # Check if file already exists
        if Path(task.local_path).exists():
            logger.info(f"File already exists: {video.filename}")
            task.status = "completed"
            task.progress = 100.0
            if self.on_complete:
                self.on_complete(task)
            return task

        # Add to queue
        with self.queue_lock:
            self.queue.append(task)
            logger.info(f"Added to queue: {video.filename} ({len(self.queue)} in queue)")

        return task

    def add_multiple(self, videos: List[VideoFile]) -> List[DownloadTask]:
        """Add multiple videos to the download queue.

        Args:
            videos: List of VideoFile objects to download

        Returns:
            List of DownloadTask instances
        """
        tasks = []
        for video in videos:
            task = self.add_to_queue(video)
            tasks.append(task)
        return tasks

    def remove_from_queue(self, task: DownloadTask) -> bool:
        """Remove a task from the queue (only if not currently downloading).

        Args:
            task: Task to remove

        Returns:
            True if removed, False if task is active or not found
        """
        if task.status == "downloading":
            logger.warning(f"Cannot remove active download: {task.file.filename}")
            return False

        with self.queue_lock:
            if task in self.queue:
                self.queue.remove(task)
                logger.info(f"Removed from queue: {task.file.filename}")
                return True

        return False

    def pause_task(self, task: DownloadTask) -> bool:
        """Pause a download task.

        Args:
            task: Task to pause

        Returns:
            True if paused successfully
        """
        # For now, we remove from queue and mark as paused
        # True pause/resume would require partial download support
        if task.status == "queued":
            task.status = "paused"
            logger.info(f"Paused task: {task.file.filename}")
            return True
        return False

    def resume_task(self, task: DownloadTask) -> bool:
        """Resume a paused download task.

        Args:
            task: Task to resume

        Returns:
            True if resumed successfully
        """
        if task.status == "paused":
            task.status = "queued"
            logger.info(f"Resumed task: {task.file.filename}")
            return True
        return False

    def clear_completed(self) -> int:
        """Remove all completed tasks from the queue.

        Returns:
            Number of tasks removed
        """
        with self.queue_lock:
            before = len(self.queue)
            self.queue = [t for t in self.queue if not t.is_complete()]
            removed = before - len(self.queue)
            if removed > 0:
                logger.info(f"Cleared {removed} completed tasks")
            return removed

    def get_queue_status(self) -> dict:
        """Get current queue status.

        Returns:
            Dictionary with queue statistics
        """
        with self.queue_lock:
            queued = sum(1 for t in self.queue if t.status == "queued")
            downloading = sum(1 for t in self.queue if t.status == "downloading")
            completed = sum(1 for t in self.queue if t.status == "completed")
            failed = sum(1 for t in self.queue if t.status == "failed")
            paused = sum(1 for t in self.queue if t.status == "paused")

            return {
                "total": len(self.queue),
                "queued": queued,
                "downloading": downloading,
                "completed": completed,
                "failed": failed,
                "paused": paused
            }

    def _process_queue(self) -> None:
        """Main worker loop that processes the download queue."""
        logger.info("Download queue processor started")

        while not self._stop_workers.is_set():
            # Get next batch of tasks to download
            tasks_to_download = self._get_next_tasks()

            if not tasks_to_download:
                # No tasks available, sleep briefly
                time.sleep(0.5)
                continue

            # Submit tasks to executor
            futures = {}
            for task in tasks_to_download:
                future = self._executor.submit(self._download_video, task)
                futures[future] = task

            # Wait for downloads to complete
            for future in as_completed(futures):
                task = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Download failed: {task.file.filename}, {e}", exc_info=True)
                    task.status = "failed"
                    task.error = str(e)

                # Notify completion
                if self.on_complete:
                    try:
                        self.on_complete(task)
                    except Exception as e:
                        logger.error(f"Error in completion callback: {e}")

        logger.info("Download queue processor stopped")

    def _get_next_tasks(self) -> List[DownloadTask]:
        """Get next batch of tasks to download.

        Returns:
            List of tasks to download (up to max_parallel)
        """
        with self.queue_lock:
            # Find queued tasks
            available = [t for t in self.queue if t.status == "queued"]

            # Check how many are currently downloading
            downloading = sum(1 for t in self.queue if t.status == "downloading")

            # Calculate how many more we can start
            slots_available = self.max_parallel - downloading

            if slots_available <= 0:
                return []

            # Mark tasks as downloading
            tasks_to_start = available[:slots_available]
            for task in tasks_to_start:
                task.status = "downloading"

            return tasks_to_start

    def _download_video(self, task: DownloadTask) -> None:
        """Download a single video with progress tracking.

        Args:
            task: DownloadTask to process
        """
        logger.info(f"Starting download: {task.file.filename}")
        start_time = time.time()

        # Retry logic
        max_retries = 3
        retry_delay = 2.0

        for attempt in range(max_retries):
            try:
                self._download_video_attempt(task, start_time)
                return  # Success
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Download attempt {attempt + 1} failed: {task.file.filename}, {e}")
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    # Final attempt failed
                    logger.error(f"Download failed after {max_retries} attempts: {task.file.filename}, {e}", exc_info=True)
                    task.status = "failed"
                    task.error = f"Failed after {max_retries} attempts: {str(e)}"
                    task.progress = 0.0
                    raise

    def _download_video_attempt(self, task: DownloadTask, start_time: float) -> None:
        """Single download attempt with progress tracking.

        Args:
            task: DownloadTask to process
            start_time: Download start time
        """
        try:
            # Stream download with progress tracking
            response = self.api.get_video_file(task.file.path, stream=True)

            if not hasattr(response, 'iter_content'):
                # Response is bytes, not streaming
                content = response
                total_size = len(content)

                # Write to file
                with open(task.local_path, 'wb') as f:
                    f.write(content)

                # Calculate stats
                elapsed = time.time() - start_time
                size_mb = total_size / (1024 * 1024)
                task.speed_mbps = (size_mb * 8) / elapsed if elapsed > 0 else 0
                task.progress = 100.0

            else:
                # Streaming response
                chunk_size = 8192 * 16  # 128KB chunks
                downloaded = 0

                with open(task.local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            # Update progress
                            elapsed = time.time() - start_time
                            size_mb = downloaded / (1024 * 1024)
                            task.speed_mbps = (size_mb * 8) / elapsed if elapsed > 0 else 0

                            # Estimate progress (we don't know total size upfront)
                            # Use heuristic: typical video is ~50MB for 1 min
                            estimated_total = 50 * 1024 * 1024  # 50MB estimate
                            task.progress = min(95.0, (downloaded / estimated_total) * 100)

                            # Notify progress
                            if self.on_progress_update:
                                try:
                                    self.on_progress_update(task)
                                except Exception as e:
                                    logger.error(f"Error in progress callback: {e}")

                # Final stats
                elapsed = time.time() - start_time
                size_mb = downloaded / (1024 * 1024)
                task.speed_mbps = (size_mb * 8) / elapsed if elapsed > 0 else 0
                task.progress = 100.0

            # Mark as completed
            task.status = "completed"
            logger.info(f"Download completed: {task.file.filename} ({size_mb:.1f}MB @ {task.speed_mbps:.1f} Mbps)")

        except Exception as e:
            logger.error(f"Download attempt failed: {task.file.filename}, {e}", exc_info=True)
            raise

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop()
