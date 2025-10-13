"""Main application window for dashcam manager."""
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib
import logging
from threading import Thread
from src.services.connection_manager import ConnectionManager

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

        # Initialize connection manager
        self.connection_manager = ConnectionManager(on_status_change=self.on_connection_status_changed)

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

        return frame

    def create_center_panel(self):
        """Create center panel for thumbnail grid."""
        frame = Gtk.Frame()

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        frame.set_child(scrolled)

        # Placeholder for thumbnail grid
        placeholder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        placeholder.set_valign(Gtk.Align.CENTER)
        placeholder.set_halign(Gtk.Align.CENTER)
        scrolled.set_child(placeholder)

        icon = Gtk.Image.new_from_icon_name("folder-videos-symbolic")
        icon.set_pixel_size(64)
        icon.add_css_class("dim-label")
        placeholder.append(icon)

        label = Gtk.Label(label="Connect to dashcam to view videos")
        label.add_css_class("title-2")
        label.add_css_class("dim-label")
        placeholder.append(label)

        return frame

    def create_right_sidebar(self):
        """Create right sidebar with download queue."""
        frame = Gtk.Frame()
        frame.set_size_request(250, -1)

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
        title = Gtk.Label(label="Download Queue")
        title.add_css_class("heading")
        title.set_xalign(0)
        box.append(title)

        # Placeholder message
        placeholder = Gtk.Label(label="No downloads")
        placeholder.add_css_class("dim-label")
        placeholder.set_margin_top(24)
        box.append(placeholder)

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

    def on_settings_clicked(self, button):
        """Handle settings button click."""
        logger.info("Settings button clicked")
        # TODO: Implement settings dialog in Sprint 4

    def on_directory_selected(self, button, dir_name):
        """Handle directory selection."""
        logger.info(f"Directory selected: {dir_name}")
        self.status_label.set_label(f"Selected: {dir_name}")
        # TODO: Implement directory browsing in Sprint 2

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
        else:
            button.set_label("Connect")


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
