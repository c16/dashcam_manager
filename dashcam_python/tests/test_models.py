"""Tests for data models."""
import pytest
from datetime import datetime
from src.api.models import VideoFile, DownloadTask


def test_video_file_from_filename():
    """Test VideoFile parsing from filename."""
    path = "sd//norm/2025_10_12_220337_00.TS"
    video = VideoFile.from_filename(path)

    assert video.filename == "2025_10_12_220337_00.TS"
    assert video.timestamp == datetime(2025, 10, 12, 22, 3, 37)
    assert video.camera == "front"
    assert video.type == "normal"


def test_video_file_back_camera():
    """Test VideoFile parsing for back camera."""
    path = "sd//back_norm/2025_10_12_220337_00.TS"
    video = VideoFile.from_filename(path)

    assert video.camera == "back"
    assert video.type == "normal"


def test_video_file_emergency():
    """Test VideoFile parsing for emergency recording."""
    path = "sd//emr/2025_10_12_220337_00.TS"
    video = VideoFile.from_filename(path)

    assert video.type == "emergency"


def test_video_file_invalid_filename():
    """Test VideoFile parsing with invalid filename."""
    with pytest.raises(ValueError):
        VideoFile.from_filename("invalid_filename.TS")


def test_download_task_states():
    """Test DownloadTask state methods."""
    video = VideoFile.from_filename("sd//norm/2025_10_12_220337_00.TS")

    task = DownloadTask(file=video, status="queued")
    assert task.is_active()
    assert not task.is_complete()
    assert not task.has_failed()

    task.status = "downloading"
    assert task.is_active()

    task.status = "completed"
    assert not task.is_active()
    assert task.is_complete()

    task.status = "failed"
    assert not task.is_active()
    assert task.has_failed()
