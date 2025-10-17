import 'video_file.dart';

/// Represents a video download task with progress tracking.
class DownloadTask {
  final VideoFile file;
  String status; // queued, downloading, completed, failed
  double progress;
  double speedMbps;
  String? error;
  String? localPath;

  DownloadTask({
    required this.file,
    this.status = 'queued',
    this.progress = 0.0,
    this.speedMbps = 0.0,
    this.error,
    this.localPath,
  });

  /// Check if download is currently active
  bool get isActive => status == 'queued' || status == 'downloading';

  /// Check if download completed successfully
  bool get isComplete => status == 'completed';

  /// Check if download failed
  bool get hasFailed => status == 'failed';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DownloadTask &&
          runtimeType == other.runtimeType &&
          file == other.file;

  @override
  int get hashCode => file.hashCode;

  @override
  String toString() {
    return 'DownloadTask(filename: ${file.filename}, status: $status, progress: ${(progress * 100).toStringAsFixed(1)}%)';
  }
}
