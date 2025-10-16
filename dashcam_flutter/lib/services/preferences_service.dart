import 'package:shared_preferences/shared_preferences.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

/// Service for managing app preferences
class PreferencesService {
  static const String _downloadDirKey = 'download_directory';
  static const String _maxParallelDownloadsKey = 'max_parallel_downloads';

  final SharedPreferences _prefs;

  PreferencesService(this._prefs);

  /// Initialize preferences service
  static Future<PreferencesService> init() async {
    final prefs = await SharedPreferences.getInstance();
    return PreferencesService(prefs);
  }

  /// Get download directory
  Future<String> getDownloadDirectory() async {
    final saved = _prefs.getString(_downloadDirKey);
    if (saved != null) {
      final dir = Directory(saved);
      if (await dir.exists()) {
        return saved;
      }
      // Try to create it if it doesn't exist
      try {
        await dir.create(recursive: true);
        return saved;
      } catch (e) {
        // If can't create, fall through to default
      }
    }
    // Return default and save it
    final defaultDir = await _getDefaultDownloadDirectory();
    await _prefs.setString(_downloadDirKey, defaultDir);
    return defaultDir;
  }

  /// Set download directory
  Future<void> setDownloadDirectory(String path) async {
    await _prefs.setString(_downloadDirKey, path);
  }

  /// Get max parallel downloads
  int getMaxParallelDownloads() {
    return _prefs.getInt(_maxParallelDownloadsKey) ?? 3;
  }

  /// Set max parallel downloads
  Future<void> setMaxParallelDownloads(int count) async {
    await _prefs.setInt(_maxParallelDownloadsKey, count);
  }

  /// Get default download directory
  Future<String> _getDefaultDownloadDirectory() async {
    // Try user-specific directories first
    if (Platform.isLinux || Platform.isMacOS || Platform.isWindows) {
      final home = Platform.environment['HOME'] ?? Platform.environment['USERPROFILE'];
      if (home != null) {
        final videosDir = Directory('$home/Videos/Dashcam');
        try {
          // Try to create the directory to verify write access
          if (!await videosDir.exists()) {
            await videosDir.create(recursive: true);
          }
          return videosDir.path;
        } catch (e) {
          // Fall through to app documents directory if can't create
        }
      }
    }

    // Fallback to app-specific directory (always writable)
    try {
      if (Platform.isAndroid) {
        // On Android, use external storage (Downloads/Dashcam)
        final externalDir = await getExternalStorageDirectory();
        if (externalDir != null) {
          // This maps to /storage/emulated/0/Android/data/com.example.dashcam_flutter/files/
          final dashcamDir = Directory('${externalDir.path}/Dashcam');
          if (!await dashcamDir.exists()) {
            await dashcamDir.create(recursive: true);
          }
          return dashcamDir.path;
        }
      }

      // Final fallback: app documents directory (works on all platforms)
      final documentsDir = await getApplicationDocumentsDirectory();
      final dashcamDir = Directory('${documentsDir.path}/Dashcam');
      if (!await dashcamDir.exists()) {
        await dashcamDir.create(recursive: true);
      }
      return dashcamDir.path;
    } catch (e) {
      // Absolute last resort
      final tempDir = Directory.systemTemp;
      return '${tempDir.path}/Dashcam';
    }
  }
}
