"""Data models for dashcam video files and download tasks."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


@dataclass
class VideoFile:
    """Represents a video file from the dashcam."""
    path: str
    filename: str
    timestamp: datetime
    size_mb: Optional[float] = None
    duration: Optional[int] = None
    camera: str = "front"  # front, back
    type: str = "normal"   # normal, emergency, parking

    @classmethod
    def from_filename(cls, path: str) -> 'VideoFile':
        """Parse video file information from filename.

        Expected format: sd//norm/2025_10_12_220337_00.TS
        Pattern: YYYY_MM_DD_HHMMSS_XX.TS

        Args:
            path: Full path to the video file

        Returns:
            VideoFile instance with parsed metadata

        Raises:
            ValueError: If filename doesn't match expected pattern
        """
        filename = path.split('/')[-1]

        # Parse timestamp from filename
        pattern = r'(\d{4})_(\d{2})_(\d{2})_(\d{6})_\d{2}\.(TS|THM|TXT)'
        match = re.match(pattern, filename)

        if not match:
            raise ValueError(f"Invalid filename format: {filename}")

        year, month, day, time_str = match.groups()[:4]
        hour = time_str[:2]
        minute = time_str[2:4]
        second = time_str[4:6]

        timestamp = datetime(
            int(year), int(month), int(day),
            int(hour), int(minute), int(second)
        )

        # Determine camera type from path
        camera = "back" if "/back_" in path else "front"

        # Determine video type from directory
        if "/emr/" in path or "/back_emr/" in path:
            video_type = "emergency"
        elif "/photo/" in path or "/back_photo/" in path:
            video_type = "photo"
        else:
            video_type = "normal"

        return cls(
            path=path,
            filename=filename,
            timestamp=timestamp,
            camera=camera,
            type=video_type
        )


@dataclass
class DownloadTask:
    """Represents a video download task with progress tracking."""
    file: VideoFile
    status: str  # queued, downloading, completed, failed
    progress: float = 0.0
    speed_mbps: float = 0.0
    error: Optional[str] = None
    local_path: Optional[str] = None

    def is_active(self) -> bool:
        """Check if download is currently active."""
        return self.status in ("queued", "downloading")

    def is_complete(self) -> bool:
        """Check if download completed successfully."""
        return self.status == "completed"

    def has_failed(self) -> bool:
        """Check if download failed."""
        return self.status == "failed"
