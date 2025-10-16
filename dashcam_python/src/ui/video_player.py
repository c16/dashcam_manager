"""Video playback component."""
import logging
import subprocess
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoPlayer:
    """Simple video player that launches external player."""

    @staticmethod
    def play_video(video_path: str) -> bool:
        """Play a video file using the system's default video player.

        Args:
            video_path: Path to the video file

        Returns:
            True if player was launched successfully
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return False

        logger.info(f"Opening video: {video_path}")

        try:
            # Try different video players in order of preference
            players = [
                ['xdg-open', video_path],  # Linux default
                ['vlc', video_path],        # VLC
                ['mpv', video_path],        # MPV
                ['ffplay', video_path],     # FFmpeg player
            ]

            for player_cmd in players:
                try:
                    subprocess.Popen(
                        player_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    logger.info(f"Launched video player: {player_cmd[0]}")
                    return True
                except FileNotFoundError:
                    continue

            logger.error("No suitable video player found")
            return False

        except Exception as e:
            logger.error(f"Failed to open video: {e}", exc_info=True)
            return False

    @staticmethod
    def open_in_file_manager(video_path: str) -> bool:
        """Open the video's directory in the file manager.

        Args:
            video_path: Path to the video file

        Returns:
            True if file manager was opened successfully
        """
        directory = str(Path(video_path).parent)

        if not os.path.exists(directory):
            logger.error(f"Directory not found: {directory}")
            return False

        logger.info(f"Opening directory: {directory}")

        try:
            subprocess.Popen(
                ['xdg-open', directory],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except Exception as e:
            logger.error(f"Failed to open directory: {e}", exc_info=True)
            return False
