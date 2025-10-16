"""Cache manager for thumbnail and metadata storage."""
import logging
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from src.utils.config import Config

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages local caching of thumbnails and metadata."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache manager.

        Args:
            cache_dir: Custom cache directory (defaults to Config.CACHE_DIR)
        """
        self.cache_dir = cache_dir or Config.CACHE_DIR
        self.thumbnail_dir = self.cache_dir / "thumbnails"
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata: Dict[str, Dict[str, Any]] = {}

        # Ensure cache directories exist
        self._ensure_cache_dirs()
        self._load_metadata()

        logger.info(f"CacheManager initialized with cache_dir: {self.cache_dir}")

    def _ensure_cache_dirs(self) -> None:
        """Create cache directories if they don't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Cache directories ensured: {self.cache_dir}")

    def _load_metadata(self) -> None:
        """Load metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded metadata for {len(self.metadata)} items")
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
                self.metadata = {}
        else:
            self.metadata = {}

    def _save_metadata(self) -> None:
        """Save metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.debug("Metadata saved to disk")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def _get_cache_key(self, file_path: str) -> str:
        """Generate cache key from file path.

        Args:
            file_path: File path from dashcam

        Returns:
            Cache key (hash of file path)
        """
        return hashlib.md5(file_path.encode()).hexdigest()

    def _get_thumbnail_path(self, cache_key: str) -> Path:
        """Get filesystem path for cached thumbnail.

        Args:
            cache_key: Cache key for the thumbnail

        Returns:
            Path to thumbnail file
        """
        return self.thumbnail_dir / f"{cache_key}.jpg"

    def has_thumbnail(self, file_path: str) -> bool:
        """Check if thumbnail is cached.

        Args:
            file_path: File path from dashcam

        Returns:
            True if thumbnail is cached, False otherwise
        """
        cache_key = self._get_cache_key(file_path)
        thumbnail_path = self._get_thumbnail_path(cache_key)
        return thumbnail_path.exists()

    def get_thumbnail(self, file_path: str) -> Optional[bytes]:
        """Get cached thumbnail.

        Args:
            file_path: File path from dashcam

        Returns:
            Thumbnail data or None if not cached
        """
        cache_key = self._get_cache_key(file_path)
        thumbnail_path = self._get_thumbnail_path(cache_key)

        if not thumbnail_path.exists():
            logger.debug(f"Thumbnail not cached: {file_path}")
            return None

        try:
            with open(thumbnail_path, 'rb') as f:
                data = f.read()
            logger.debug(f"Retrieved cached thumbnail: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to read cached thumbnail: {e}")
            return None

    def save_thumbnail(self, file_path: str, thumbnail_data: bytes) -> bool:
        """Save thumbnail to cache.

        Args:
            file_path: File path from dashcam
            thumbnail_data: Thumbnail image data

        Returns:
            True if saved successfully, False otherwise
        """
        cache_key = self._get_cache_key(file_path)
        thumbnail_path = self._get_thumbnail_path(cache_key)

        try:
            with open(thumbnail_path, 'wb') as f:
                f.write(thumbnail_data)

            # Update metadata
            self.metadata[cache_key] = {
                'file_path': file_path,
                'cached_at': datetime.now().isoformat(),
                'size': len(thumbnail_data)
            }
            self._save_metadata()

            logger.debug(f"Saved thumbnail to cache: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save thumbnail: {e}")
            return False

    def get_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for cached file.

        Args:
            file_path: File path from dashcam

        Returns:
            Metadata dict or None if not cached
        """
        cache_key = self._get_cache_key(file_path)
        return self.metadata.get(cache_key)

    def invalidate(self, file_path: str) -> bool:
        """Remove file from cache.

        Args:
            file_path: File path from dashcam

        Returns:
            True if removed, False if not cached
        """
        cache_key = self._get_cache_key(file_path)
        thumbnail_path = self._get_thumbnail_path(cache_key)

        removed = False
        if thumbnail_path.exists():
            try:
                thumbnail_path.unlink()
                removed = True
                logger.debug(f"Removed cached thumbnail: {file_path}")
            except Exception as e:
                logger.error(f"Failed to remove thumbnail: {e}")

        if cache_key in self.metadata:
            del self.metadata[cache_key]
            self._save_metadata()
            removed = True

        return removed

    def clear_cache(self) -> int:
        """Clear all cached thumbnails and metadata.

        Returns:
            Number of files removed
        """
        count = 0
        try:
            for thumbnail_path in self.thumbnail_dir.glob("*.jpg"):
                thumbnail_path.unlink()
                count += 1

            self.metadata = {}
            self._save_metadata()

            logger.info(f"Cleared cache: {count} thumbnails removed")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

        return count

    def cleanup_old_entries(self, max_age_days: int = 30) -> int:
        """Remove cache entries older than specified age.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of entries removed
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        count = 0

        keys_to_remove = []
        for cache_key, meta in self.metadata.items():
            try:
                cached_at = datetime.fromisoformat(meta['cached_at'])
                if cached_at < cutoff_date:
                    keys_to_remove.append(cache_key)
            except Exception as e:
                logger.warning(f"Invalid metadata entry: {cache_key}, {e}")
                keys_to_remove.append(cache_key)

        for cache_key in keys_to_remove:
            thumbnail_path = self._get_thumbnail_path(cache_key)
            if thumbnail_path.exists():
                try:
                    thumbnail_path.unlink()
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to remove old thumbnail: {e}")

            if cache_key in self.metadata:
                del self.metadata[cache_key]

        if keys_to_remove:
            self._save_metadata()
            logger.info(f"Cleaned up {count} old cache entries")

        return count

    def get_cache_size(self) -> int:
        """Get total size of cache in bytes.

        Returns:
            Total cache size in bytes
        """
        total_size = 0
        try:
            for thumbnail_path in self.thumbnail_dir.glob("*.jpg"):
                total_size += thumbnail_path.stat().st_size
        except Exception as e:
            logger.error(f"Failed to calculate cache size: {e}")

        return total_size

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        thumbnail_count = len(list(self.thumbnail_dir.glob("*.jpg")))
        cache_size = self.get_cache_size()

        return {
            'thumbnail_count': thumbnail_count,
            'cache_size_bytes': cache_size,
            'cache_size_mb': cache_size / (1024 * 1024),
            'metadata_entries': len(self.metadata)
        }
