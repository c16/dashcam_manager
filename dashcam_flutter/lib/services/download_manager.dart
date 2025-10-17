import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as path;
import '../api/dashcam_api.dart';
import '../models/video_file.dart';
import '../models/download_task.dart';

/// Manages video download queue with parallel download support.
class DownloadManager extends ChangeNotifier {
  final DashcamAPI api;
  final String downloadDir;
  final int maxParallel;

  final List<DownloadTask> _queue = [];
  bool _isRunning = false;
  final Set<DownloadTask> _activeDownloads = {};

  DownloadManager({
    required this.api,
    required this.downloadDir,
    this.maxParallel = 3,
  }) {
    _ensureDownloadDirectory();
  }

  List<DownloadTask> get queue => List.unmodifiable(_queue);
  bool get isRunning => _isRunning;

  /// Ensure download directory exists
  Future<void> _ensureDownloadDirectory() async {
    final dir = Directory(downloadDir);
    if (!await dir.exists()) {
      await dir.create(recursive: true);
    }
  }

  /// Start the download manager
  void start() {
    if (_isRunning) {
      debugPrint('Download manager already running');
      return;
    }

    debugPrint('Starting download manager');
    _isRunning = true;
    _processQueue();
  }

  /// Stop the download manager
  void stop() {
    if (!_isRunning) return;

    debugPrint('Stopping download manager');
    _isRunning = false;
    notifyListeners();
  }

  /// Add a video to the download queue
  DownloadTask addToQueue(VideoFile video) {
    // Create download directory structure (by date)
    final dateDir = path.join(
      downloadDir,
      '${video.timestamp.year}-${video.timestamp.month.toString().padLeft(2, '0')}-${video.timestamp.day.toString().padLeft(2, '0')}',
    );

    final localPath = path.join(dateDir, video.filename);

    // Create task
    final task = DownloadTask(
      file: video,
      status: 'queued',
      progress: 0.0,
      speedMbps: 0.0,
      localPath: localPath,
    );

    // Check if file already exists
    if (File(localPath).existsSync()) {
      debugPrint('File already exists: ${video.filename}');
      task.status = 'completed';
      task.progress = 1.0;
      return task;
    }

    // Add to queue
    _queue.add(task);
    debugPrint('Added to queue: ${video.filename} (${_queue.length} in queue)');
    notifyListeners();

    // Start processing if not already running
    if (_isRunning) {
      _processQueue();
    }

    return task;
  }

  /// Add multiple videos to the download queue
  List<DownloadTask> addMultiple(List<VideoFile> videos) {
    final tasks = <DownloadTask>[];
    for (final video in videos) {
      tasks.add(addToQueue(video));
    }
    return tasks;
  }

  /// Remove a task from the queue (only if not currently downloading)
  bool removeFromQueue(DownloadTask task) {
    if (task.status == 'downloading') {
      debugPrint('Cannot remove active download: ${task.file.filename}');
      return false;
    }

    if (_queue.remove(task)) {
      debugPrint('Removed from queue: ${task.file.filename}');
      notifyListeners();
      return true;
    }

    return false;
  }

  /// Clear all completed tasks from the queue
  int clearCompleted() {
    final before = _queue.length;
    _queue.removeWhere((t) => t.isComplete);
    final removed = before - _queue.length;
    if (removed > 0) {
      debugPrint('Cleared $removed completed tasks');
      notifyListeners();
    }
    return removed;
  }

  /// Clear all tasks from the queue
  void clearAll() {
    final before = _queue.length;
    _queue.clear();
    _activeDownloads.clear();
    debugPrint('Cleared all $before tasks from queue');
    notifyListeners();
  }

  /// Get queue statistics
  Map<String, int> getQueueStatus() {
    final queued = _queue.where((t) => t.status == 'queued').length;
    final downloading = _queue.where((t) => t.status == 'downloading').length;
    final completed = _queue.where((t) => t.status == 'completed').length;
    final failed = _queue.where((t) => t.status == 'failed').length;

    return {
      'total': _queue.length,
      'queued': queued,
      'downloading': downloading,
      'completed': completed,
      'failed': failed,
    };
  }

  /// Main worker that processes the download queue
  Future<void> _processQueue() async {
    if (!_isRunning) return;

    // Get next batch of tasks to download
    final tasksToDownload = _getNextTasks();

    if (tasksToDownload.isEmpty) {
      // No tasks available, check again later
      await Future.delayed(const Duration(milliseconds: 500));
      if (_isRunning && _queue.any((t) => t.status == 'queued')) {
        _processQueue();
      }
      return;
    }

    // Start downloads in parallel
    final futures = <Future>[];
    for (final task in tasksToDownload) {
      futures.add(_downloadVideo(task));
    }

    // Wait for this batch to complete
    await Future.wait(futures);

    // Continue processing if there are more queued tasks
    if (_isRunning && _queue.any((t) => t.status == 'queued')) {
      _processQueue();
    }
  }

  /// Get next batch of tasks to download
  List<DownloadTask> _getNextTasks() {
    // Find queued tasks
    final available = _queue.where((t) => t.status == 'queued').toList();

    // Check how many are currently downloading
    final downloading = _activeDownloads.length;

    // Calculate how many more we can start
    final slotsAvailable = maxParallel - downloading;

    if (slotsAvailable <= 0) {
      return [];
    }

    // Mark tasks as downloading
    final tasksToStart = available.take(slotsAvailable).toList();
    for (final task in tasksToStart) {
      task.status = 'downloading';
      _activeDownloads.add(task);
    }

    notifyListeners();
    return tasksToStart;
  }

  /// Download a single video with progress tracking
  Future<void> _downloadVideo(DownloadTask task) async {
    debugPrint('Starting download: ${task.file.filename}');
    final startTime = DateTime.now();

    const maxRetries = 3;
    const retryDelay = Duration(seconds: 2);

    for (int attempt = 0; attempt < maxRetries; attempt++) {
      try {
        await _downloadVideoAttempt(task, startTime);
        _activeDownloads.remove(task);
        notifyListeners();
        return; // Success
      } catch (e) {
        if (attempt < maxRetries - 1) {
          debugPrint('Download attempt ${attempt + 1} failed: ${task.file.filename}, $e');
          debugPrint('Retrying in ${retryDelay.inSeconds} seconds...');
          await Future.delayed(retryDelay);
        } else {
          // Final attempt failed
          debugPrint('Download failed after $maxRetries attempts: ${task.file.filename}, $e');
          task.status = 'failed';
          task.error = 'Failed after $maxRetries attempts: $e';
          task.progress = 0.0;
          _activeDownloads.remove(task);
          notifyListeners();
          rethrow;
        }
      }
    }
  }

  /// Single download attempt with progress tracking
  Future<void> _downloadVideoAttempt(DownloadTask task, DateTime startTime) async {
    try {
      // Ensure directory exists
      final dir = Directory(path.dirname(task.localPath!));
      if (!await dir.exists()) {
        await dir.create(recursive: true);
      }

      // Stream download with progress tracking
      final response = await api.getVideoFile(task.file.path);

      // Get content length if available
      final contentLength = response.contentLength;
      int downloaded = 0;

      // Open file for writing
      final file = File(task.localPath!);
      final sink = file.openWrite();

      // Stream chunks and track progress
      await for (final chunk in response.stream) {
        sink.add(chunk);
        downloaded += chunk.length;

        // Update progress
        final elapsed = DateTime.now().difference(startTime);
        final sizeMb = downloaded / (1024 * 1024);
        task.speedMbps = (sizeMb * 8) / elapsed.inSeconds;

        if (contentLength != null && contentLength > 0) {
          // We know the total size
          task.progress = downloaded / contentLength;
        } else {
          // Estimate progress (typical video is ~50MB)
          const estimatedTotal = 50 * 1024 * 1024;
          task.progress = (downloaded / estimatedTotal).clamp(0.0, 0.95);
        }

        notifyListeners();
      }

      await sink.close();

      // Final stats
      final elapsed = DateTime.now().difference(startTime);
      final sizeMb = downloaded / (1024 * 1024);
      task.speedMbps = (sizeMb * 8) / elapsed.inSeconds;
      task.progress = 1.0;
      task.status = 'completed';

      debugPrint(
          'Download completed: ${task.file.filename} (${sizeMb.toStringAsFixed(1)}MB @ ${task.speedMbps.toStringAsFixed(1)} Mbps)');
    } catch (e) {
      debugPrint('Download attempt failed: ${task.file.filename}, $e');
      rethrow;
    }
  }

  @override
  void dispose() {
    stop();
    super.dispose();
  }
}
