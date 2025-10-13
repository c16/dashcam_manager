"""Video thumbnail grid view component."""
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gio
import logging
import time
from typing import List, Optional, Callable
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from src.api.models import VideoFile
from src.services.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class VideoThumbnail(Gtk.Box):
    """Individual video thumbnail widget."""

    def __init__(self, video_file: VideoFile, on_click: Optional[Callable] = None):
        """Initialize video thumbnail.

        Args:
            video_file: VideoFile instance
            on_click: Callback when thumbnail is clicked
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.video_file = video_file
        self.on_click_callback = on_click

        # Main button container
        self.button = Gtk.Button()
        self.button.set_has_frame(True)
        self.button.connect("clicked", self._on_clicked)
        self.append(self.button)

        # Content box
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        content.set_margin_start(6)
        content.set_margin_end(6)
        content.set_margin_top(6)
        content.set_margin_bottom(6)
        self.button.set_child(content)

        # Thumbnail image
        self.image = Gtk.Image()
        self.image.set_size_request(160, 120)
        self.image.set_pixel_size(160)
        content.append(self.image)

        # Loading placeholder
        self._show_placeholder()

        # Info label
        info_text = video_file.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        info_label = Gtk.Label(label=info_text)
        info_label.add_css_class("caption")
        info_label.set_max_width_chars(20)
        info_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        content.append(info_label)

        # Camera/type badge
        badge_text = f"{video_file.camera} • {video_file.type}"
        badge_label = Gtk.Label(label=badge_text)
        badge_label.add_css_class("dim-label")
        badge_label.add_css_class("caption")
        content.append(badge_label)

    def _show_placeholder(self) -> None:
        """Show placeholder icon while loading."""
        self.image.set_from_icon_name("video-x-generic-symbolic")

    def set_thumbnail_data(self, image_data: bytes) -> None:
        """Set thumbnail image from data.

        Args:
            image_data: JPEG image data
        """
        try:
            # Load image data into pixbuf
            loader = GdkPixbuf.PixbufLoader.new_with_type('jpeg')
            loader.write(image_data)
            loader.close()
            pixbuf = loader.get_pixbuf()

            # Scale to fit
            width = 160
            height = int(pixbuf.get_height() * (width / pixbuf.get_width()))
            scaled = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)

            # Set image
            self.image.set_from_pixbuf(scaled)
            logger.debug(f"Set thumbnail for {self.video_file.filename}")
        except Exception as e:
            logger.error(f"Failed to load thumbnail image: {e}")
            self._show_error()

    def _show_error(self) -> None:
        """Show error icon."""
        self.image.set_from_icon_name("dialog-error-symbolic")

    def _on_clicked(self, button) -> None:
        """Handle thumbnail click."""
        logger.info(f"Thumbnail clicked: {self.video_file.filename}")
        if self.on_click_callback:
            self.on_click_callback(self.video_file)


class VideoGrid(Gtk.ScrolledWindow):
    """Grid view for video thumbnails."""

    def __init__(self, cache_manager: CacheManager, on_video_click: Optional[Callable] = None):
        """Initialize video grid.

        Args:
            cache_manager: CacheManager instance
            on_video_click: Callback when video is clicked
        """
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_vexpand(True)
        self.set_hexpand(True)

        self.cache_manager = cache_manager
        self.on_video_click = on_video_click
        self.api = None  # Set by caller
        self.thumbnails: List[VideoThumbnail] = []

        # Thread pool for controlled thumbnail loading (max 3 concurrent downloads)
        # Using 3 instead of 5 to be more conservative with API rate limiting
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="thumbnail-loader")
        self.loading_batch_id = 0  # Track which batch of thumbnails we're loading

        # Flow box for grid layout
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(10)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_homogeneous(True)
        self.flowbox.set_row_spacing(12)
        self.flowbox.set_column_spacing(12)
        self.flowbox.set_margin_start(12)
        self.flowbox.set_margin_end(12)
        self.flowbox.set_margin_top(12)
        self.flowbox.set_margin_bottom(12)
        self.set_child(self.flowbox)

        logger.info("VideoGrid initialized")

    def set_api(self, api) -> None:
        """Set API client for loading thumbnails.

        Args:
            api: DashcamAPI instance
        """
        self.api = api
        logger.debug("API client set for VideoGrid")

    def clear(self) -> None:
        """Clear all thumbnails from grid."""
        # Increment batch ID to invalidate any in-flight thumbnail loads
        self.loading_batch_id += 1
        logger.debug(f"Grid cleared, batch_id now {self.loading_batch_id}")

        # Remove all children
        child = self.flowbox.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.flowbox.remove(child)
            child = next_child

        self.thumbnails.clear()

    def load_videos(self, video_files: List[VideoFile]) -> None:
        """Load video thumbnails into grid.

        Args:
            video_files: List of VideoFile instances
        """
        logger.info(f"Loading {len(video_files)} videos into grid")
        self.clear()

        # Capture current batch ID for this load
        current_batch_id = self.loading_batch_id

        for video_file in video_files:
            # Create thumbnail widget
            thumbnail = VideoThumbnail(video_file, on_click=self.on_video_click)
            self.flowbox.append(thumbnail)
            self.thumbnails.append(thumbnail)

            # Load thumbnail data using thread pool (limits concurrent downloads)
            self.executor.submit(self._load_thumbnail_async, thumbnail, video_file, current_batch_id)

    def _load_thumbnail_async(self, thumbnail: VideoThumbnail, video_file: VideoFile, batch_id: int) -> None:
        """Load thumbnail data asynchronously.

        Args:
            thumbnail: VideoThumbnail widget
            video_file: VideoFile instance
            batch_id: Batch ID when this load was initiated
        """
        try:
            # Check if this batch is still active (not cancelled by a new load)
            if batch_id != self.loading_batch_id:
                logger.debug(f"Skipping outdated thumbnail load for {video_file.filename} (batch {batch_id} != {self.loading_batch_id})")
                return

            # Check cache first
            cached_data = self.cache_manager.get_thumbnail(video_file.path)
            if cached_data:
                # Validate cached data is actually a JPEG
                if len(cached_data) >= 2 and cached_data[:2] == b'\xff\xd8':
                    logger.debug(f"Using cached thumbnail: {video_file.filename}")
                    # Check again before updating UI
                    if batch_id == self.loading_batch_id:
                        GLib.idle_add(thumbnail.set_thumbnail_data, cached_data)
                    return
                else:
                    # Invalid cached data - invalidate it
                    logger.warning(f"Invalid cached thumbnail for {video_file.filename}, will re-fetch")
                    self.cache_manager.invalidate(video_file.path)

            # Load from API if not cached
            if not self.api:
                logger.warning("No API client set, cannot load thumbnails")
                return

            # Check again before making API call
            if batch_id != self.loading_batch_id:
                logger.debug(f"Batch cancelled before API call for {video_file.filename}")
                return

            logger.debug(f"Fetching thumbnail from API: {video_file.filename}")
            # Convert .TS video path to .THM thumbnail path
            thumbnail_path = video_file.path.replace('.TS', '.THM')

            # Small delay to avoid overwhelming API with too many simultaneous requests
            time.sleep(0.05)

            thumbnail_data = self.api.get_thumbnail(thumbnail_path)

            # Check one final time before updating UI
            if batch_id != self.loading_batch_id:
                logger.debug(f"Batch cancelled after API call for {video_file.filename}")
                return

            if thumbnail_data:
                # Validate it's actually a JPEG (starts with FF D8)
                if len(thumbnail_data) < 2 or thumbnail_data[:2] != b'\xff\xd8':
                    logger.error(f"Invalid thumbnail data for {video_file.filename} (path: {thumbnail_path})")
                    logger.error(f"  Data starts with: {thumbnail_data[:20].hex() if len(thumbnail_data) >= 20 else 'empty'}")
                    logger.error(f"  Data size: {len(thumbnail_data)} bytes")
                    # If it starts with <! it's likely an HTML error page
                    if thumbnail_data[:2] == b'<!':
                        logger.error(f"  API returned HTML error: {thumbnail_data[:200].decode('latin1', errors='ignore')}")
                    # If it starts with G@ (0x47 0x40) it's a .TS video file
                    elif thumbnail_data[:2] == b'G@':
                        logger.error(f"  API returned video file instead of thumbnail!")
                    # Don't cache invalid data
                    GLib.idle_add(thumbnail._show_error)
                    return

                # Cache the thumbnail
                self.cache_manager.save_thumbnail(video_file.path, thumbnail_data)

                # Update UI on main thread
                GLib.idle_add(thumbnail.set_thumbnail_data, thumbnail_data)
            else:
                logger.warning(f"No thumbnail data received: {video_file.filename}")
                GLib.idle_add(thumbnail._show_error)

        except Exception as e:
            logger.error(f"Failed to load thumbnail for {video_file.filename}: {e}")
            if batch_id == self.loading_batch_id:
                GLib.idle_add(thumbnail._show_error)

    def show_placeholder(self, message: str = "No videos to display") -> None:
        """Show placeholder message when grid is empty.

        Args:
            message: Message to display
        """
        self.clear()

        placeholder_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        placeholder_box.set_valign(Gtk.Align.CENTER)
        placeholder_box.set_halign(Gtk.Align.CENTER)

        icon = Gtk.Image.new_from_icon_name("folder-videos-symbolic")
        icon.set_pixel_size(64)
        icon.add_css_class("dim-label")
        placeholder_box.append(icon)

        label = Gtk.Label(label=message)
        label.add_css_class("title-2")
        label.add_css_class("dim-label")
        placeholder_box.append(label)

        self.flowbox.append(placeholder_box)
