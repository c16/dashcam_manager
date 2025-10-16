import 'package:flutter/material.dart';
import 'dart:io';
import '../api/dashcam_api.dart';
import '../models/video_file.dart';
import '../models/download_task.dart';
import 'download_manager.dart';
import 'preferences_service.dart';
import 'wifi_service.dart';

/// Application state management
class AppState extends ChangeNotifier {
  // Services
  final PreferencesService preferencesService;
  final WiFiService _wifiService = WiFiService();

  // Connection state
  bool _isConnected = false;
  String _connectionStatus = 'Not connected';
  DashcamAPI? _api;
  DownloadManager? _downloadManager;

  // Video browsing state
  String? _currentDirectory;
  List<VideoFile> _allVideos = [];
  List<VideoFile> _filteredVideos = [];

  // Filter state
  bool _showFront = true;
  bool _showBack = true;
  bool _showNormal = true;
  bool _showEmergency = true;

  // Status message
  String _statusMessage = 'Ready';

  // Getters
  bool get isConnected => _isConnected;
  String get connectionStatus => _connectionStatus;
  DashcamAPI? get api => _api;
  DownloadManager? get downloadManager => _downloadManager;
  String? get currentDirectory => _currentDirectory;
  List<VideoFile> get filteredVideos => _filteredVideos;
  bool get showFront => _showFront;
  bool get showBack => _showBack;
  bool get showNormal => _showNormal;
  bool get showEmergency => _showEmergency;
  List<DownloadTask> get downloadQueue => _downloadManager?.queue ?? [];
  String get statusMessage => _statusMessage;

  AppState({required this.preferencesService});

  /// Connect to dashcam
  Future<bool> connect({String? dashcamSSID, String? dashcamPassword}) async {
    try {
      _connectionStatus = 'Connecting...';
      notifyListeners();

      // Switch to dashcam WiFi if enabled and on Android
      final autoWifiSwitch = preferencesService.getAutoWifiSwitch();
      if (Platform.isAndroid && autoWifiSwitch) {
        _connectionStatus = 'Switching to dashcam WiFi...';
        notifyListeners();

        final ssid = dashcamSSID ?? 'DIRECT-'; // Default or user-provided SSID
        final wifiConnected = await _wifiService.connectToDashcam(
          ssid: ssid,
          password: dashcamPassword,
        );

        if (!wifiConnected) {
          _connectionStatus = 'Failed to connect to dashcam WiFi';
          _statusMessage = 'Could not switch to dashcam WiFi. Please connect manually.';
          notifyListeners();
          return false;
        }

        _connectionStatus = 'Connected to dashcam WiFi, initializing...';
        notifyListeners();
      }

      _api = DashcamAPI();

      // Register client
      await _api!.registerClient();

      // Stop recording and enter playback mode
      await _api!.workModeCmd('stop');
      await _api!.setWorkMode('ENTER_PLAYBACK');

      // Initialize download manager
      final downloadsDir = await preferencesService.getDownloadDirectory();
      final maxParallel = preferencesService.getMaxParallelDownloads();

      // Ensure directory exists
      final dir = Directory(downloadsDir);
      if (!await dir.exists()) {
        await dir.create(recursive: true);
      }

      _downloadManager = DownloadManager(
        api: _api!,
        downloadDir: downloadsDir,
        maxParallel: maxParallel,
      );
      _downloadManager!.addListener(_onDownloadManagerUpdate);
      _downloadManager!.start();

      _isConnected = true;
      _connectionStatus = 'Connected';
      _statusMessage = 'Connected to dashcam';
      notifyListeners();
      return true;
    } catch (e) {
      _isConnected = false;
      _connectionStatus = 'Connection failed';
      _statusMessage = 'Failed to connect: $e';
      _api?.dispose();
      _api = null;
      _downloadManager?.dispose();
      _downloadManager = null;
      notifyListeners();
      return false;
    }
  }

  /// Disconnect from dashcam
  Future<void> disconnect() async {
    _downloadManager?.stop();
    _downloadManager?.removeListener(_onDownloadManagerUpdate);
    _downloadManager?.dispose();
    _downloadManager = null;
    _api?.dispose();
    _api = null;
    _isConnected = false;
    _connectionStatus = 'Disconnecting...';
    _currentDirectory = null;
    _allVideos = [];
    _filteredVideos = [];
    notifyListeners();

    // Restore previous WiFi on Android (only if auto switch was enabled)
    final autoWifiSwitch = preferencesService.getAutoWifiSwitch();
    if (Platform.isAndroid && autoWifiSwitch) {
      _statusMessage = 'Restoring previous WiFi connection...';
      notifyListeners();

      await _wifiService.disconnectFromDashcam();
    }

    _connectionStatus = 'Not connected';
    _statusMessage = 'Disconnected';
    notifyListeners();
  }

  /// Called when download manager updates
  void _onDownloadManagerUpdate() {
    notifyListeners();
  }

  /// Load videos from a directory
  Future<void> loadDirectory(String directory) async {
    if (!_isConnected || _api == null) {
      _statusMessage = 'Not connected to dashcam';
      notifyListeners();
      return;
    }

    try {
      _currentDirectory = directory;
      _statusMessage = 'Loading $directory...';
      notifyListeners();

      // Stop recording before loading directory
      try {
        await _api!.workModeCmd('stop');
      } catch (e) {
        debugPrint('Failed to stop recording: $e');
      }

      // Get file list
      final filePaths = await _api!.getDirFileListParsed(directory, 0, 100);
      debugPrint('API returned ${filePaths.length} files from $directory');

      // Parse into VideoFile objects
      final videos = <VideoFile>[];
      for (final filePath in filePaths) {
        try {
          // Only process video files (.TS)
          if (filePath.endsWith('.TS')) {
            final video = VideoFile.fromFilename(filePath);
            videos.add(video);
            debugPrint('Parsed video: ${video.filename} - camera: ${video.camera}, type: ${video.type}');
          }
        } catch (e) {
          debugPrint('Failed to parse file: $filePath, $e');
        }
      }

      debugPrint('Parsed ${videos.length} videos from ${filePaths.length} files');
      _allVideos = videos;
      _applyFilters();
      _statusMessage = 'Loaded ${videos.length} videos from $directory';
      notifyListeners();
    } catch (e) {
      _statusMessage = 'Error loading directory: $e';
      _allVideos = [];
      _filteredVideos = [];
      notifyListeners();
    }
  }

  /// Update filter settings
  void updateFilters({
    bool? showFront,
    bool? showBack,
    bool? showNormal,
    bool? showEmergency,
  }) {
    if (showFront != null) _showFront = showFront;
    if (showBack != null) _showBack = showBack;
    if (showNormal != null) _showNormal = showNormal;
    if (showEmergency != null) _showEmergency = showEmergency;
    _applyFilters();
    notifyListeners();
  }

  /// Reset all filters to default
  void resetFilters() {
    _showFront = true;
    _showBack = true;
    _showNormal = true;
    _showEmergency = true;
    _applyFilters();
    notifyListeners();
  }

  /// Apply current filters to video list
  void _applyFilters() {
    _filteredVideos = _allVideos.where((video) {
      // Camera filter
      if (video.camera == 'front' && !_showFront) return false;
      if (video.camera == 'back' && !_showBack) return false;

      // Type filter
      if (video.type == 'normal' && !_showNormal) return false;
      if (video.type == 'emergency' && !_showEmergency) return false;

      return true;
    }).toList();

    if (_filteredVideos.isNotEmpty) {
      _statusMessage =
          'Showing ${_filteredVideos.length} of ${_allVideos.length} videos';
    } else {
      _statusMessage = 'No videos match current filters';
    }
  }

  /// Add video to download queue
  void addToDownloadQueue(VideoFile video) {
    if (_downloadManager == null) {
      _statusMessage = 'Download manager not initialized';
      notifyListeners();
      return;
    }

    _downloadManager!.addToQueue(video);
    _statusMessage = 'Added to download queue: ${video.filename}';
    notifyListeners();
  }

  /// Add multiple videos to download queue
  void addMultipleToDownloadQueue(List<VideoFile> videos) {
    if (_downloadManager == null) {
      _statusMessage = 'Download manager not initialized';
      notifyListeners();
      return;
    }

    _downloadManager!.addMultiple(videos);
    _statusMessage = 'Added ${videos.length} videos to download queue';
    notifyListeners();
  }

  /// Clear download queue
  void clearDownloadQueue() {
    if (_downloadManager == null) {
      return;
    }

    _downloadManager!.clearAll();
    _statusMessage = 'Download queue cleared';
    notifyListeners();
  }

  /// Update status message
  void setStatus(String message) {
    _statusMessage = message;
    notifyListeners();
  }
}
