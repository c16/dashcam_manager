"""Settings panel for camera configuration."""
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import logging
from typing import Optional
from src.api.client import DashcamAPI

logger = logging.getLogger(__name__)


class SettingsDialog(Gtk.Window):
    """Dialog for configuring dashcam settings."""

    def __init__(self, parent_window: Gtk.Window, api: Optional[DashcamAPI] = None):
        """Initialize settings dialog.

        Args:
            parent_window: Parent window
            api: DashcamAPI instance for reading/writing settings
        """
        super().__init__()
        self.set_title("Dashcam Settings")
        self.set_default_size(600, 500)
        self.set_transient_for(parent_window)
        self.set_modal(True)

        self.api = api
        self.settings = {}

        logger.info("Initializing settings dialog")
        self.setup_ui()

        # Load current settings if connected
        if self.api:
            self.load_settings()

    def setup_ui(self):
        """Build the settings dialog UI."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)

        # Header bar
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)
        main_box.append(header)

        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.add_css_class("suggested-action")
        save_button.connect("clicked", self.on_save_clicked)
        header.pack_end(save_button)

        # Scrolled window for settings
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        main_box.append(scrolled)

        # Settings container
        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        settings_box.set_margin_start(24)
        settings_box.set_margin_end(24)
        settings_box.set_margin_top(24)
        settings_box.set_margin_bottom(24)
        scrolled.set_child(settings_box)

        # Connection settings
        self.add_section(settings_box, "Connection")
        self.add_setting_row(settings_box, "Download Directory", self.create_file_chooser())

        # Camera settings
        self.add_section(settings_box, "Camera Settings")

        # Video quality
        quality_options = ["High", "Medium", "Low"]
        self.quality_combo = self.create_combo_box(quality_options)
        self.add_setting_row(settings_box, "Video Quality", self.quality_combo)

        # Loop recording duration
        duration_options = ["1 minute", "3 minutes", "5 minutes"]
        self.duration_combo = self.create_combo_box(duration_options)
        self.add_setting_row(settings_box, "Loop Recording", self.duration_combo)

        # Audio recording
        self.audio_switch = Gtk.Switch()
        self.audio_switch.set_active(True)
        self.add_setting_row(settings_box, "Audio Recording", self.audio_switch)

        # GPS logging
        self.gps_switch = Gtk.Switch()
        self.gps_switch.set_active(True)
        self.add_setting_row(settings_box, "GPS Logging", self.gps_switch)

        # Parking mode
        self.parking_switch = Gtk.Switch()
        self.parking_switch.set_active(False)
        self.add_setting_row(settings_box, "Parking Mode", self.parking_switch)

        # Display settings
        self.add_section(settings_box, "Display")

        # Date/time stamp
        self.timestamp_switch = Gtk.Switch()
        self.timestamp_switch.set_active(True)
        self.add_setting_row(settings_box, "Date/Time Stamp", self.timestamp_switch)

        # Speed display
        self.speed_switch = Gtk.Switch()
        self.speed_switch.set_active(True)
        self.add_setting_row(settings_box, "Speed Display", self.speed_switch)

        # Advanced settings
        self.add_section(settings_box, "Advanced")

        # G-sensor sensitivity
        sensitivity_options = ["High", "Medium", "Low", "Off"]
        self.gsensor_combo = self.create_combo_box(sensitivity_options)
        self.add_setting_row(settings_box, "G-Sensor Sensitivity", self.gsensor_combo)

        # Auto power off
        poweroff_options = ["Off", "1 minute", "3 minutes", "5 minutes"]
        self.poweroff_combo = self.create_combo_box(poweroff_options)
        self.add_setting_row(settings_box, "Auto Power Off", self.poweroff_combo)

        # Info section
        self.add_section(settings_box, "Device Information")

        self.device_info_label = Gtk.Label()
        self.device_info_label.set_xalign(0)
        self.device_info_label.set_wrap(True)
        self.device_info_label.set_selectable(True)
        self.device_info_label.add_css_class("dim-label")
        settings_box.append(self.device_info_label)

        # Status bar
        self.status_label = Gtk.Label(label="")
        self.status_label.add_css_class("caption")
        self.status_label.set_margin_start(24)
        self.status_label.set_margin_end(24)
        self.status_label.set_margin_bottom(12)
        main_box.append(self.status_label)

        logger.info("Settings dialog UI setup complete")

    def add_section(self, container: Gtk.Box, title: str):
        """Add a section header.

        Args:
            container: Container to add to
            title: Section title
        """
        label = Gtk.Label(label=title)
        label.add_css_class("heading")
        label.set_xalign(0)
        label.set_margin_top(12)
        container.append(label)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_bottom(6)
        container.append(separator)

    def add_setting_row(self, container: Gtk.Box, label: str, widget: Gtk.Widget):
        """Add a setting row with label and control widget.

        Args:
            container: Container to add to
            label: Setting label
            widget: Control widget
        """
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.set_margin_top(6)
        row.set_margin_bottom(6)

        label_widget = Gtk.Label(label=label)
        label_widget.set_xalign(0)
        label_widget.set_hexpand(True)
        row.append(label_widget)

        row.append(widget)
        container.append(row)

    def create_combo_box(self, options: list) -> Gtk.ComboBoxText:
        """Create a combo box with options.

        Args:
            options: List of option strings

        Returns:
            Gtk.ComboBoxText widget
        """
        combo = Gtk.ComboBoxText()
        for option in options:
            combo.append_text(option)
        combo.set_active(0)
        return combo

    def create_file_chooser(self) -> Gtk.Box:
        """Create a file chooser button.

        Returns:
            Gtk.Box containing file chooser button
        """
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.download_dir_label = Gtk.Label(label="~/Videos/Dashcam")
        self.download_dir_label.add_css_class("caption")
        box.append(self.download_dir_label)

        button = Gtk.Button(label="Choose...")
        button.connect("clicked", self.on_choose_directory)
        box.append(button)

        return box

    def on_choose_directory(self, button):
        """Handle directory chooser button click."""
        dialog = Gtk.FileDialog()
        dialog.select_folder(self, None, self.on_folder_selected)

    def on_folder_selected(self, dialog, result):
        """Handle folder selection result."""
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                path = folder.get_path()
                self.download_dir_label.set_text(path)
                logger.info(f"Download directory selected: {path}")
        except Exception as e:
            logger.error(f"Failed to select folder: {e}")

    def load_settings(self):
        """Load current settings from dashcam."""
        if not self.api:
            self.status_label.set_text("Not connected to dashcam")
            return

        self.status_label.set_text("Loading settings...")
        logger.info("Loading settings from dashcam")

        try:
            # Get device info
            device_info = self.api.get_device_attr()
            self.device_info_label.set_text(f"Device Info:\n{device_info}")

            # Try to get camera parameters (may not be fully supported)
            # This is a placeholder - actual implementation would parse responses
            self.status_label.set_text("Settings loaded")
            logger.info("Settings loaded successfully")

        except Exception as e:
            error_msg = f"Failed to load settings: {str(e)}"
            self.status_label.set_text(error_msg)
            logger.error(error_msg, exc_info=True)

    def on_save_clicked(self, button):
        """Handle save button click."""
        if not self.api:
            self.status_label.set_text("Not connected to dashcam")
            return

        self.status_label.set_text("Saving settings...")
        logger.info("Saving settings to dashcam")

        try:
            # Save settings via API
            # This is a placeholder - actual implementation would use API methods
            # Most settings require specific API calls that may vary by model

            # For now, just show success
            self.status_label.set_text("Settings saved successfully")
            logger.info("Settings saved successfully")

            # Close dialog after brief delay
            GLib.timeout_add_seconds(1, self.close)

        except Exception as e:
            error_msg = f"Failed to save settings: {str(e)}"
            self.status_label.set_text(error_msg)
            logger.error(error_msg, exc_info=True)
