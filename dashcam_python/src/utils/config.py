"""Application configuration management."""
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration settings."""

    # Dashcam connection
    DASHCAM_IP: str = "192.168.0.1"
    DASHCAM_PORT: int = 80
    CONNECTION_TIMEOUT: int = 10

    # Download settings
    PARALLEL_DOWNLOADS: int = 3
    CHUNK_SIZE: int = 8192
    MAX_RETRIES: int = 3

    # Cache settings
    CACHE_DIR: Path = Path.home() / ".cache" / "dashcam-manager"
    THUMBNAIL_CACHE_DIR: Path = CACHE_DIR / "thumbnails"
    MAX_CACHE_SIZE_MB: int = 500

    # Video directories on dashcam
    VIDEO_DIRECTORIES = [
        "norm",
        "back_norm",
        "emr",
        "back_emr",
        "photo",
        "back_photo"
    ]

    @classmethod
    def ensure_cache_dirs(cls) -> None:
        """Create cache directories if they don't exist."""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.THUMBNAIL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
