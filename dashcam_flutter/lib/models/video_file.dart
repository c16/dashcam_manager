/// Data model for dashcam video files.
class VideoFile {
  final String path;
  final String filename;
  final DateTime timestamp;
  final double? sizeMb;
  final int? duration;
  final String camera; // front, back
  final String type; // normal, emergency, parking

  VideoFile({
    required this.path,
    required this.filename,
    required this.timestamp,
    this.sizeMb,
    this.duration,
    this.camera = "front",
    this.type = "normal",
  });

  /// Parse video file information from filename.
  ///
  /// Expected format: sd//norm/2025_10_12_220337_00.TS
  /// Pattern: YYYY_MM_DD_HHMMSS_XX.TS
  factory VideoFile.fromFilename(String path) {
    final filename = path.split('/').last;

    // Parse timestamp from filename
    // Handle both normal (YYYY_MM_DD_HHMMSS_XX.TS) and back camera (_b.TS) formats
    final pattern = RegExp(
        r'(\d{4})_(\d{2})_(\d{2})_(\d{6})_\d{2}(_b)?\.(TS|THM|TXT)');
    final match = pattern.firstMatch(filename);

    if (match == null) {
      throw FormatException('Invalid filename format: $filename');
    }

    final year = int.parse(match.group(1)!);
    final month = int.parse(match.group(2)!);
    final day = int.parse(match.group(3)!);
    final timeStr = match.group(4)!;
    final hour = int.parse(timeStr.substring(0, 2));
    final minute = int.parse(timeStr.substring(2, 4));
    final second = int.parse(timeStr.substring(4, 6));

    final timestamp = DateTime(year, month, day, hour, minute, second);

    // Determine camera type from path
    final camera = path.contains('/back_') ? 'back' : 'front';

    // Determine video type from directory
    String videoType;
    if (path.contains('/emr/') || path.contains('/back_emr/')) {
      videoType = 'emergency';
    } else if (path.contains('/photo/') || path.contains('/back_photo/')) {
      videoType = 'photo';
    } else {
      videoType = 'normal';
    }

    return VideoFile(
      path: path,
      filename: filename,
      timestamp: timestamp,
      camera: camera,
      type: videoType,
    );
  }

  /// Get thumbnail path for this video file
  String get thumbnailPath => path.replaceAll('.TS', '.THM');

  /// Get GPS data path for this video file
  String get gpsPath => path.replaceAll('.TS', '.TXT');

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is VideoFile &&
          runtimeType == other.runtimeType &&
          path == other.path &&
          filename == other.filename;

  @override
  int get hashCode => path.hashCode ^ filename.hashCode;

  @override
  String toString() {
    return 'VideoFile(filename: $filename, timestamp: $timestamp, camera: $camera, type: $type)';
  }
}
