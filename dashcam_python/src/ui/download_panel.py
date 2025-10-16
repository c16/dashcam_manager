"""Download manager panel with progress tracking."""
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import logging
from typing import Optional, Dict
from src.api.models import DownloadTask
from src.services.download_manager import DownloadManager
from src.ui.video_player import VideoPlayer

logger = logging.getLogger(__name__)


class DownloadPanel(Gtk.Box):
    """UI panel for displaying and managing download queue."""

    def __init__(self, download_manager: Optional[DownloadManager] = None):
        """Initialize download panel.

        Args:
            download_manager: DownloadManager instance to display
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        self.download_manager = download_manager
        self.task_widgets: Dict[DownloadTask, Gtk.Box] = {}

        logger.info("Initializing download panel")
        self.setup_ui()

    def setup_ui(self):
        """Build the download panel UI."""
        # Header with title and controls
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        title = Gtk.Label(label="Download Queue")
        title.add_css_class("heading")
        title.set_xalign(0)
        title.set_hexpand(True)
        header.append(title)

        # Clear completed button
        self.clear_btn = Gtk.Button(label="Clear")
        self.clear_btn.set_tooltip_text("Clear completed downloads")
        self.clear_btn.connect("clicked", self.on_clear_completed)
        header.append(self.clear_btn)

        self.append(header)

        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(6)
        separator.set_margin_bottom(6)
        self.append(separator)

        # Scrolled window for download list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        self.append(scrolled)

        # Container for download items
        self.downloads_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scrolled.set_child(self.downloads_box)

        # Placeholder message
        self.placeholder = Gtk.Label(label="No downloads")
        self.placeholder.add_css_class("dim-label")
        self.placeholder.set_margin_top(24)
        self.downloads_box.append(self.placeholder)

        # Status summary at bottom
        self.status_label = Gtk.Label(label="")
        self.status_label.add_css_class("caption")
        self.status_label.set_xalign(0)
        self.status_label.set_margin_top(6)
        self.append(self.status_label)

        logger.info("Download panel UI setup complete")

    def set_download_manager(self, download_manager: DownloadManager):
        """Set the download manager and start updating UI.

        Args:
            download_manager: DownloadManager instance
        """
        self.download_manager = download_manager
        self.refresh_queue()

    def refresh_queue(self):
        """Refresh the entire download queue display."""
        if not self.download_manager:
            return

        # Clear existing widgets
        for widget in self.task_widgets.values():
            self.downloads_box.remove(widget)
        self.task_widgets.clear()

        # Get queue
        queue = self.download_manager.queue.copy()

        # Show/hide placeholder
        if queue:
            if self.placeholder.get_parent():
                self.downloads_box.remove(self.placeholder)
        else:
            if not self.placeholder.get_parent():
                self.downloads_box.append(self.placeholder)

        # Add task widgets
        for task in queue:
            widget = self.create_task_widget(task)
            self.downloads_box.append(widget)
            self.task_widgets[task] = widget

        # Update status
        self.update_status()

    def create_task_widget(self, task: DownloadTask) -> Gtk.Box:
        """Create a widget for displaying a download task.

        Args:
            task: DownloadTask to display

        Returns:
            Gtk.Box containing task UI
        """
        # Main container
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        container.add_css_class("card")
        container.set_margin_top(2)
        container.set_margin_bottom(2)

        # Top row: filename and status
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        filename_label = Gtk.Label(label=task.file.filename)
        filename_label.set_xalign(0)
        filename_label.set_hexpand(True)
        filename_label.set_ellipsize(3)  # ELLIPSIZE_END
        top_row.append(filename_label)

        status_label = Gtk.Label(label=self.get_status_text(task))
        status_label.add_css_class("caption")
        status_label.set_name(f"status_{id(task)}")
        top_row.append(status_label)

        container.append(top_row)

        # Progress bar
        progress_bar = Gtk.ProgressBar()
        progress_bar.set_fraction(task.progress / 100.0)
        progress_bar.set_show_text(True)
        progress_bar.set_text(self.get_progress_text(task))
        progress_bar.set_name(f"progress_{id(task)}")
        container.append(progress_bar)

        # Bottom row: info and controls
        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        info_label = Gtk.Label(label=self.get_info_text(task))
        info_label.add_css_class("caption")
        info_label.set_xalign(0)
        info_label.set_hexpand(True)
        info_label.set_name(f"info_{id(task)}")
        bottom_row.append(info_label)

        # Control buttons
        if task.status == "queued":
            pause_btn = Gtk.Button(label="Pause")
            pause_btn.connect("clicked", lambda w: self.on_pause_task(task))
            bottom_row.append(pause_btn)

        elif task.status == "paused":
            resume_btn = Gtk.Button(label="Resume")
            resume_btn.connect("clicked", lambda w: self.on_resume_task(task))
            bottom_row.append(resume_btn)

        if task.status in ("queued", "paused", "failed"):
            remove_btn = Gtk.Button(label="Remove")
            remove_btn.connect("clicked", lambda w: self.on_remove_task(task))
            bottom_row.append(remove_btn)

        # Play button for completed downloads
        if task.status == "completed" and task.local_path:
            play_btn = Gtk.Button(label="Play")
            play_btn.connect("clicked", lambda w: self.on_play_task(task))
            bottom_row.append(play_btn)

            folder_btn = Gtk.Button(label="Show")
            folder_btn.connect("clicked", lambda w: self.on_show_task(task))
            bottom_row.append(folder_btn)

        container.append(bottom_row)

        return container

    def update_task_widget(self, task: DownloadTask):
        """Update an existing task widget with new progress.

        Args:
            task: DownloadTask with updated progress
        """
        if task not in self.task_widgets:
            return

        widget = self.task_widgets[task]

        # Find and update progress bar
        progress_bar = self.find_child_by_name(widget, f"progress_{id(task)}")
        if progress_bar and isinstance(progress_bar, Gtk.ProgressBar):
            progress_bar.set_fraction(task.progress / 100.0)
            progress_bar.set_text(self.get_progress_text(task))

        # Update status label
        status_label = self.find_child_by_name(widget, f"status_{id(task)}")
        if status_label and isinstance(status_label, Gtk.Label):
            status_label.set_text(self.get_status_text(task))

        # Update info label
        info_label = self.find_child_by_name(widget, f"info_{id(task)}")
        if info_label and isinstance(info_label, Gtk.Label):
            info_label.set_text(self.get_info_text(task))

    def find_child_by_name(self, container, name: str):
        """Recursively find a child widget by name.

        Args:
            container: Parent widget to search
            name: Widget name to find

        Returns:
            Widget if found, None otherwise
        """
        if hasattr(container, 'get_name') and container.get_name() == name:
            return container

        if hasattr(container, 'get_first_child'):
            child = container.get_first_child()
            while child:
                result = self.find_child_by_name(child, name)
                if result:
                    return result
                child = child.get_next_sibling()

        return None

    def get_status_text(self, task: DownloadTask) -> str:
        """Get status text for a task.

        Args:
            task: DownloadTask

        Returns:
            Status string
        """
        status_map = {
            "queued": "Queued",
            "downloading": "Downloading",
            "completed": "Completed",
            "failed": "Failed",
            "paused": "Paused"
        }
        return status_map.get(task.status, task.status.title())

    def get_progress_text(self, task: DownloadTask) -> str:
        """Get progress text for a task.

        Args:
            task: DownloadTask

        Returns:
            Progress string (e.g., "45%")
        """
        return f"{task.progress:.0f}%"

    def get_info_text(self, task: DownloadTask) -> str:
        """Get info text for a task.

        Args:
            task: DownloadTask

        Returns:
            Info string (e.g., "12.5 Mbps" or timestamp)
        """
        if task.status == "downloading" and task.speed_mbps > 0:
            return f"{task.speed_mbps:.1f} Mbps"
        elif task.status == "failed" and task.error:
            return f"Error: {task.error[:50]}"
        else:
            return task.file.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def on_task_progress(self, task: DownloadTask):
        """Callback for task progress updates.

        Args:
            task: DownloadTask with updated progress
        """
        # Schedule UI update on main thread
        GLib.idle_add(self.update_task_widget, task)
        GLib.idle_add(self.update_status)

    def on_task_complete(self, task: DownloadTask):
        """Callback when a task completes.

        Args:
            task: Completed DownloadTask
        """
        # Schedule UI update on main thread
        GLib.idle_add(self.update_task_widget, task)
        GLib.idle_add(self.update_status)

    def on_pause_task(self, task: DownloadTask):
        """Handle pause button click.

        Args:
            task: Task to pause
        """
        if self.download_manager:
            self.download_manager.pause_task(task)
            self.refresh_queue()

    def on_resume_task(self, task: DownloadTask):
        """Handle resume button click.

        Args:
            task: Task to resume
        """
        if self.download_manager:
            self.download_manager.resume_task(task)
            self.refresh_queue()

    def on_remove_task(self, task: DownloadTask):
        """Handle remove button click.

        Args:
            task: Task to remove
        """
        if self.download_manager:
            self.download_manager.remove_from_queue(task)
            self.refresh_queue()

    def on_play_task(self, task: DownloadTask):
        """Handle play button click.

        Args:
            task: Task to play
        """
        if task.local_path:
            success = VideoPlayer.play_video(task.local_path)
            if not success:
                logger.warning(f"Failed to play video: {task.file.filename}")

    def on_show_task(self, task: DownloadTask):
        """Handle show in folder button click.

        Args:
            task: Task to show
        """
        if task.local_path:
            VideoPlayer.open_in_file_manager(task.local_path)

    def on_clear_completed(self, button):
        """Handle clear completed button click.

        Args:
            button: Button widget
        """
        if self.download_manager:
            self.download_manager.clear_completed()
            self.refresh_queue()

    def update_status(self):
        """Update the status summary label."""
        if not self.download_manager:
            self.status_label.set_text("")
            return

        status = self.download_manager.get_queue_status()

        if status["total"] == 0:
            self.status_label.set_text("")
            return

        parts = []
        if status["downloading"] > 0:
            parts.append(f"{status['downloading']} downloading")
        if status["queued"] > 0:
            parts.append(f"{status['queued']} queued")
        if status["completed"] > 0:
            parts.append(f"{status['completed']} completed")
        if status["failed"] > 0:
            parts.append(f"{status['failed']} failed")

        self.status_label.set_text(" • ".join(parts))
