"""Main application window for dashcam manager."""
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib
import logging
from threading import Thread
from typing import List
from src.services.connection_manager import ConnectionManager
from src.services.cache_manager import CacheManager
from src.services.download_manager import DownloadManager
from src.ui.video_grid import VideoGrid
from src.ui.download_panel import DownloadPanel
from src.ui.settings_panel import SettingsDialog
from src.api.models import VideoFile
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class DashcamApp(Gtk.Application):
    """Main GTK application for dashcam manager."""

    def __init__(self):
        super().__init__(
            application_id='com.example.dashcam',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.api = None
        self.window = None
        logger.info("DashcamApp initialized")

    def do_activate(self):
        """Called when the application is activated."""
        if not self.window:
            self.window = MainWindow(application=self)
        self.window.present()


class MainWindow(Gtk.ApplicationWindow):
    """Main application window with video browser interface."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Dashcam Manager")
        self.set_default_size(1200, 800)

        # Initialize managers
        self.connection_manager = ConnectionManager(on_status_change=self.on_connection_status_changed)
        self.cache_manager = CacheManager()
        self.download_manager = None  # Created after connection

        # Download directory
        self.download_dir = str(Path.home() / "Videos" / "Dashcam")

        # Current state
        self.current_directory = None
        self.current_videos: List[VideoFile] = []

        logger.info("Initializing main window")
        self.setup_ui()

    def setup_ui(self):
        """Build the main UI layout."""
        # Main vertical box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)

        # Header bar
        header_bar = self.create_header_bar()
        main_box.append(header_bar)

        # Content area with horizontal panes
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_vexpand(True)
        main_box.append(paned)

        # Left sidebar (directory tree)
        left_sidebar = self.create_left_sidebar()
        paned.set_start_child(left_sidebar)
        paned.set_resize_start_child(False)
        paned.set_shrink_start_child(False)

        # Right side with center content and right panel
        right_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_end_child(right_paned)

        # Center: thumbnail grid placeholder
        center_panel = self.create_center_panel()
        right_paned.set_start_child(center_panel)
        right_paned.set_resize_start_child(True)
        right_paned.set_shrink_start_child(False)

        # Right sidebar (download queue)
        right_sidebar = self.create_right_sidebar()
        right_paned.set_end_child(right_sidebar)
        right_paned.set_resize_end_child(False)
        right_paned.set_shrink_end_child(False)

        # Bottom status bar
        status_bar = self.create_status_bar()
        main_box.append(status_bar)

        logger.info("UI setup complete")

    def create_header_bar(self):
        """Create the header bar with connection status."""
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)

        # Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        title_label = Gtk.Label(label="Dashcam Manager")
        title_label.add_css_class("title")
        title_box.append(title_label)

        # Connection status
        self.connection_status = Gtk.Label(label="Not connected")
        self.connection_status.add_css_class("subtitle")
        title_box.append(self.connection_status)

        header.set_title_widget(title_box)

        # Connect button
        connect_button = Gtk.Button(label="Connect")
        connect_button.connect("clicked", self.on_connect_clicked)
        header.pack_start(connect_button)

        # Download All button
        self.download_all_button = Gtk.Button(label="Download All")
        self.download_all_button.set_sensitive(False)
        self.download_all_button.connect("clicked", self.on_download_all_clicked)
        header.pack_start(self.download_all_button)

        # Settings button
        settings_button = Gtk.Button(icon_name="preferences-system-symbolic")
        settings_button.connect("clicked", self.on_settings_clicked)
        header.pack_end(settings_button)

        return header

    def create_left_sidebar(self):
        """Create left sidebar with directory tree."""
        frame = Gtk.Frame()
        frame.set_size_request(200, -1)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        frame.set_child(scrolled)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        scrolled.set_child(box)

        # Title
        title = Gtk.Label(label="Directories")
        title.add_css_class("heading")
        title.set_xalign(0)
        box.append(title)

        # Placeholder directory list
        directories = [
            "Normal Videos",
            "Emergency Videos",
            "Parking Mode",
            "Back Camera",
            "Back Emergency",
            "Photos"
        ]

        for dir_name in directories:
            button = Gtk.Button(label=dir_name)
            button.set_hexpand(True)
            button.connect("clicked", self.on_directory_selected, dir_name)
            box.append(button)

        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(12)
        separator.set_margin_bottom(12)
        box.append(separator)

        # Filter section
        filter_title = Gtk.Label(label="Filters")
        filter_title.add_css_class("heading")
        filter_title.set_xalign(0)
        box.append(filter_title)

        # Camera filter
        camera_label = Gtk.Label(label="Camera")
        camera_label.set_xalign(0)
        camera_label.add_css_class("caption")
        box.append(camera_label)

        camera_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.filter_front = Gtk.CheckButton(label="Front")
        self.filter_front.set_active(True)
        self.filter_front.connect("toggled", self._on_filter_changed)
        camera_box.append(self.filter_front)

        self.filter_back = Gtk.CheckButton(label="Back")
        self.filter_back.set_active(True)
        self.filter_back.connect("toggled", self._on_filter_changed)
        camera_box.append(self.filter_back)
        box.append(camera_box)

        # Video type filter
        type_label = Gtk.Label(label="Type")
        type_label.set_xalign(0)
        type_label.add_css_class("caption")
        type_label.set_margin_top(6)
        box.append(type_label)

        self.filter_normal = Gtk.CheckButton(label="Normal")
        self.filter_normal.set_active(True)
        self.filter_normal.connect("toggled", self._on_filter_changed)
        box.append(self.filter_normal)

        self.filter_emergency = Gtk.CheckButton(label="Emergency")
        self.filter_emergency.set_active(True)
        self.filter_emergency.connect("toggled", self._on_filter_changed)
        box.append(self.filter_emergency)

        # Clear filters button
        clear_btn = Gtk.Button(label="Reset Filters")
        clear_btn.set_margin_top(12)
        clear_btn.connect("clicked", self._on_clear_filters)
        box.append(clear_btn)

        return frame

    def create_center_panel(self):
        """Create center panel for thumbnail grid."""
        frame = Gtk.Frame()

        # Create video grid
        self.video_grid = VideoGrid(
            cache_manager=self.cache_manager,
            on_video_click=self.on_video_clicked
        )
        frame.set_child(self.video_grid)

        # Show initial placeholder
        self.video_grid.show_placeholder("Connect to dashcam to view videos")

        return frame

    def create_right_sidebar(self):
        """Create right sidebar with download queue."""
        frame = Gtk.Frame()
        frame.set_size_request(300, -1)

        # Create download panel
        self.download_panel = DownloadPanel(self.download_manager)
        frame.set_child(self.download_panel)

        return frame

    def create_status_bar(self):
        """Create bottom status bar."""
        status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        status_bar.set_margin_start(12)
        status_bar.set_margin_end(12)
        status_bar.set_margin_top(6)
        status_bar.set_margin_bottom(6)

        # Status label
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_xalign(0)
        status_bar.append(self.status_label)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        status_bar.append(spacer)

        # Storage info placeholder
        storage_label = Gtk.Label(label="Storage: -- / --")
        storage_label.add_css_class("dim-label")
        status_bar.append(storage_label)

        return status_bar

    def on_connect_clicked(self, button):
        """Handle connect button click."""
        logger.info("Connect button clicked")

        if self.connection_manager.is_connected:
            # Disconnect
            self.connection_manager.disconnect()
            button.set_label("Connect")
        else:
            # Connect in background thread to avoid blocking UI
            button.set_sensitive(False)
            button.set_label("Connecting...")

            def connect_thread():
                success = self.connection_manager.connect()
                if success:
                    # Start monitoring connection
                    self.connection_manager.start_monitoring(interval=10.0, auto_reconnect=True)

                # Re-enable button on main thread
                GLib.idle_add(self._update_connect_button_state, button)

            Thread(target=connect_thread, daemon=True).start()

    def on_download_all_clicked(self, button):
        """Handle download all button click."""
        logger.info("Download All button clicked")

        if not self.download_manager or not self.current_videos:
            logger.warning("No videos to download or download manager not initialized")
            return

        # Add all current videos to download queue
        tasks = self.download_manager.add_multiple(self.current_videos)
        self.download_panel.refresh_queue()

        count = len(tasks)
        self.status_label.set_label(f"Added {count} videos to download queue")
        logger.info(f"Added {count} videos to download queue")

    def on_settings_clicked(self, button):
        """Handle settings button click."""
        logger.info("Settings button clicked")

        # Create and show settings dialog
        settings_dialog = SettingsDialog(
            parent_window=self,
            api=self.connection_manager.api if self.connection_manager.is_connected else None
        )
        settings_dialog.show()

    def on_directory_selected(self, button, dir_name):
        """Handle directory selection."""
        logger.info(f"Directory selected: {dir_name}")

        if not self.connection_manager.is_connected:
            self.status_label.set_label("Not connected to dashcam")
            return

        # Map UI names to API directory names
        dir_mapping = {
            "Normal Videos": "norm",
            "Emergency Videos": "emr",
            "Parking Mode": "norm",  # Same as normal
            "Back Camera": "back_norm",
            "Back Emergency": "back_emr",
            "Photos": "photo"
        }

        api_dir = dir_mapping.get(dir_name)
        if not api_dir:
            logger.warning(f"Unknown directory: {dir_name}")
            return

        self.current_directory = api_dir
        self.status_label.set_label(f"Loading {dir_name}...")

        # Load videos in background
        Thread(target=self._load_directory_async, args=(api_dir,), daemon=True).start()

    def on_connection_status_changed(self, message: str, connected: bool):
        """Handle connection status changes from ConnectionManager.

        Args:
            message: Status message
            connected: Connection state
        """
        # Update UI on main thread
        GLib.idle_add(self._update_connection_ui, message, connected)

    def _update_connection_ui(self, message: str, connected: bool):
        """Update connection UI elements (must be called on main thread).

        Args:
            message: Status message
            connected: Connection state
        """
        self.connection_status.set_label(message)
        self.status_label.set_label(message)

        if connected:
            self.connection_status.remove_css_class("error")
            self.connection_status.add_css_class("success")
        else:
            self.connection_status.remove_css_class("success")
            if "error" in message.lower() or "failed" in message.lower() or "lost" in message.lower():
                self.connection_status.add_css_class("error")

    def _update_connect_button_state(self, button):
        """Update connect button based on connection state.

        Args:
            button: Connect button widget
        """
        button.set_sensitive(True)
        if self.connection_manager.is_connected:
            button.set_label("Disconnect")
            # Set API for video grid when connected
            if self.connection_manager.api:
                self.video_grid.set_api(self.connection_manager.api)

                # Initialize download manager if not already created
                if not self.download_manager:
                    self.download_manager = DownloadManager(
                        api=self.connection_manager.api,
                        download_dir=self.download_dir,
                        max_parallel=3,
                        on_progress_update=self.download_panel.on_task_progress,
                        on_complete=self.download_panel.on_task_complete
                    )
                    self.download_manager.start()
                    self.download_panel.set_download_manager(self.download_manager)
                    logger.info(f"Download manager initialized with dir: {self.download_dir}")
        else:
            button.set_label("Connect")
            # Stop download manager on disconnect
            if self.download_manager:
                self.download_manager.stop()
                self.download_manager = None
                logger.info("Download manager stopped")

    def _load_directory_async(self, directory: str) -> None:
        """Load videos from directory in background thread.

        Args:
            directory: Directory name (e.g., "norm", "emr")
        """
        try:
            api = self.connection_manager.api
            if not api:
                logger.error("No API client available")
                GLib.idle_add(self.status_label.set_label, "Connection lost")
                return

            logger.info(f"Loading directory: {directory}")

            # Stop recording before each directory load to ensure API is in correct state
            try:
                api.work_mode_cmd('stop')
            except Exception as e:
                logger.warning(f"Failed to stop recording before directory load: {e}")

            # Get file list from API
            file_paths = api.get_dir_file_list_parsed(directory, 0, 100)
            logger.info(f"Found {len(file_paths)} files in {directory}")

            # Parse into VideoFile objects
            videos = []
            for file_path in file_paths:
                try:
                    # Only process video files (.TS)
                    if file_path.endswith('.TS'):
                        video = VideoFile.from_filename(file_path)
                        videos.append(video)
                except Exception as e:
                    logger.warning(f"Failed to parse file: {file_path}, {e}")

            logger.info(f"Parsed {len(videos)} video files")
            self.current_videos = videos

            # Update UI on main thread
            GLib.idle_add(self._update_video_grid, videos, directory)

        except Exception as e:
            logger.error(f"Failed to load directory: {e}", exc_info=True)
            GLib.idle_add(self.status_label.set_label, f"Error loading directory: {str(e)}")
            GLib.idle_add(self.video_grid.show_placeholder, "Failed to load videos")

    def _update_video_grid(self, videos: List[VideoFile], directory: str) -> None:
        """Update video grid with loaded videos (must be called on main thread).

        Args:
            videos: List of VideoFile instances
            directory: Directory name
        """
        if videos:
            self.video_grid.load_videos(videos)
            self.status_label.set_label(f"Loaded {len(videos)} videos from {directory}")
            self.download_all_button.set_sensitive(True)
        else:
            self.video_grid.show_placeholder(f"No videos found in {directory}")
            self.status_label.set_label(f"No videos in {directory}")
            self.download_all_button.set_sensitive(False)

    def on_video_clicked(self, video_file: VideoFile) -> None:
        """Handle video thumbnail click.

        Args:
            video_file: VideoFile that was clicked
        """
        logger.info(f"Video clicked: {video_file.filename}")

        # Add to download queue
        if self.download_manager:
            task = self.download_manager.add_to_queue(video_file)
            self.download_panel.refresh_queue()
            self.status_label.set_label(f"Added to download queue: {video_file.filename}")
        else:
            self.status_label.set_label(f"Not connected - cannot download {video_file.filename}")

    def _on_filter_changed(self, checkbox) -> None:
        """Handle filter checkbox change."""
        logger.debug("Filter changed, reapplying filters")
        self._apply_filters()

    def _on_clear_filters(self, button) -> None:
        """Reset all filters to default."""
        logger.info("Clearing filters")
        self.filter_front.set_active(True)
        self.filter_back.set_active(True)
        self.filter_normal.set_active(True)
        self.filter_emergency.set_active(True)
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Apply current filters to video list."""
        if not self.current_videos:
            return

        # Get filter states
        show_front = self.filter_front.get_active()
        show_back = self.filter_back.get_active()
        show_normal = self.filter_normal.get_active()
        show_emergency = self.filter_emergency.get_active()

        # Filter videos
        filtered_videos = []
        for video in self.current_videos:
            # Camera filter
            if video.camera == "front" and not show_front:
                continue
            if video.camera == "back" and not show_back:
                continue

            # Type filter
            if video.type == "normal" and not show_normal:
                continue
            if video.type == "emergency" and not show_emergency:
                continue

            filtered_videos.append(video)

        logger.info(f"Filtered {len(self.current_videos)} videos to {len(filtered_videos)}")

        # Update grid
        if filtered_videos:
            self.video_grid.load_videos(filtered_videos)
            self.status_label.set_label(f"Showing {len(filtered_videos)} of {len(self.current_videos)} videos")
        else:
            self.video_grid.show_placeholder("No videos match current filters")
            self.status_label.set_label("No videos match filters")


def main():
    """Main entry point for the application."""
    from src.utils.logging_setup import setup_logging

    # Setup logging
    setup_logging(log_level="INFO")

    # Create and run application
    app = DashcamApp()
    return app.run(None)


if __name__ == '__main__':
    main()
