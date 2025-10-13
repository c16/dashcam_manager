"""Connection manager for WiFi handling and dashcam discovery."""
import logging
import socket
import time
from typing import Optional, Callable
from threading import Thread, Event
from src.api.client import DashcamAPI
from src.api.exceptions import ConnectionError as DashcamConnectionError
from src.utils.config import Config

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages connection to dashcam device with auto-discovery and reconnection."""

    def __init__(self, on_status_change: Optional[Callable[[str, bool], None]] = None):
        """Initialize connection manager.

        Args:
            on_status_change: Callback function(status_message, is_connected)
        """
        self.api: Optional[DashcamAPI] = None
        self.is_connected = False
        self.on_status_change = on_status_change
        self._stop_monitoring = Event()
        self._monitor_thread: Optional[Thread] = None
        self._auto_reconnect = False

    def discover_dashcam(self, timeout: float = 5.0) -> bool:
        """Attempt to discover dashcam on the network.

        Args:
            timeout: Timeout in seconds for discovery attempt

        Returns:
            True if dashcam was found, False otherwise
        """
        logger.info(f"Attempting to discover dashcam at {Config.DASHCAM_IP}")

        try:
            # Try to connect to the dashcam IP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((Config.DASHCAM_IP, Config.DASHCAM_PORT))
            sock.close()

            if result == 0:
                logger.info(f"Dashcam discovered at {Config.DASHCAM_IP}")
                return True
            else:
                logger.warning(f"Could not connect to {Config.DASHCAM_IP}:{Config.DASHCAM_PORT}")
                return False

        except socket.error as e:
            logger.error(f"Socket error during discovery: {e}")
            return False

    def connect(self) -> bool:
        """Connect to the dashcam device.

        Returns:
            True if connection successful, False otherwise
        """
        self._notify_status("Discovering dashcam...", False)

        # Discover dashcam first
        if not self.discover_dashcam():
            error_msg = f"Dashcam not found at {Config.DASHCAM_IP}"
            logger.error(error_msg)
            self._notify_status(error_msg, False)
            return False

        self._notify_status("Connecting to dashcam...", False)

        try:
            # Create API client
            base_url = f"http://{Config.DASHCAM_IP}"
            self.api = DashcamAPI(base_url=base_url, keep_alive=True)

            # Test connection by getting device info
            logger.info("Testing connection with getdeviceattr")
            device_info = self.api.get_device_attr()

            if not device_info:
                raise DashcamConnectionError("Empty response from dashcam")

            # Register client
            logger.info("Registering client")
            register_result = self.api.register_client()

            if "error" in register_result.lower():
                logger.warning(f"Client registration returned: {register_result}")
                # Continue anyway - registration might not be critical

            # Try to get WiFi info as another connectivity test
            logger.info("Getting WiFi info")
            wifi_info = self.api.get_wifi()
            logger.debug(f"WiFi info: {wifi_info}")

            # Stop recording to enable file browsing
            logger.info("Stopping recording to enable file access")
            try:
                stop_result = self.api.work_mode_cmd('stop')
                logger.debug(f"Stop recording result: {stop_result}")
            except Exception as e:
                logger.warning(f"Failed to stop recording: {e}")
                # Continue anyway - not critical

            self.is_connected = True
            success_msg = f"Connected to dashcam at {Config.DASHCAM_IP}"
            logger.info(success_msg)
            self._notify_status(success_msg, True)

            return True

        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.api = None
            self.is_connected = False
            self._notify_status(error_msg, False)
            return False

    def disconnect(self) -> None:
        """Disconnect from the dashcam."""
        logger.info("Disconnecting from dashcam")
        self.stop_monitoring()
        self.api = None
        self.is_connected = False
        self._notify_status("Disconnected", False)

    def test_connectivity(self) -> bool:
        """Test if connection is still alive.

        Returns:
            True if connection is active, False otherwise
        """
        if not self.api or not self.is_connected:
            return False

        try:
            # Quick connectivity test
            self.api.get_work_state()
            return True
        except Exception as e:
            logger.warning(f"Connectivity test failed: {e}")
            return False

    def start_monitoring(self, interval: float = 10.0, auto_reconnect: bool = True) -> None:
        """Start monitoring connection status in background thread.

        Args:
            interval: Check interval in seconds
            auto_reconnect: Attempt to reconnect if connection is lost
        """
        if self._monitor_thread and self._monitor_thread.is_alive():
            logger.warning("Monitoring already running")
            return

        logger.info(f"Starting connection monitoring (interval: {interval}s, auto_reconnect: {auto_reconnect})")
        self._stop_monitoring.clear()
        self._auto_reconnect = auto_reconnect
        self._monitor_thread = Thread(
            target=self._monitor_connection,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop connection monitoring."""
        if not self._monitor_thread:
            return

        logger.info("Stopping connection monitoring")
        self._stop_monitoring.set()
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)
        self._monitor_thread = None

    def _monitor_connection(self, interval: float) -> None:
        """Background thread that monitors connection status.

        Args:
            interval: Check interval in seconds
        """
        logger.info("Connection monitoring thread started")

        while not self._stop_monitoring.is_set():
            if self.is_connected:
                # Test connectivity
                if not self.test_connectivity():
                    logger.warning("Connection lost")
                    self.is_connected = False
                    self._notify_status("Connection lost", False)

                    if self._auto_reconnect:
                        logger.info("Attempting auto-reconnect...")
                        self._notify_status("Reconnecting...", False)
                        if self.connect():
                            logger.info("Auto-reconnect successful")
                        else:
                            logger.error("Auto-reconnect failed")
                else:
                    # Keep recording stopped so files can be browsed
                    # The dashcam auto-restarts recording periodically
                    try:
                        logger.debug("Ensuring recording stays stopped")
                        self.api.work_mode_cmd('stop')
                    except Exception as e:
                        logger.warning(f"Failed to keep recording stopped: {e}")

            # Wait for next check or stop signal
            self._stop_monitoring.wait(interval)

        logger.info("Connection monitoring thread stopped")

    def _notify_status(self, message: str, connected: bool) -> None:
        """Notify status change via callback.

        Args:
            message: Status message
            connected: Connection state
        """
        logger.debug(f"Status: {message} (connected={connected})")
        if self.on_status_change:
            try:
                self.on_status_change(message, connected)
            except Exception as e:
                logger.error(f"Error in status change callback: {e}")

    def get_device_info(self) -> Optional[str]:
        """Get device information if connected.

        Returns:
            Device info string or None if not connected
        """
        if not self.api or not self.is_connected:
            return None

        try:
            return self.api.get_device_attr()
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return None

    def get_storage_info(self) -> Optional[str]:
        """Get storage information if connected.

        Returns:
            Storage info string or None if not connected
        """
        if not self.api or not self.is_connected:
            return None

        try:
            return self.api.get_sd_status()
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            return None
