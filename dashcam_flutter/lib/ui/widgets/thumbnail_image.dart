import 'package:flutter/material.dart';
import 'dart:typed_data';
import '../../api/dashcam_api.dart';

/// Widget that loads and displays a thumbnail from the dashcam
class ThumbnailImage extends StatefulWidget {
  final DashcamAPI api;
  final String thumbnailPath;

  const ThumbnailImage({
    super.key,
    required this.api,
    required this.thumbnailPath,
  });

  @override
  State<ThumbnailImage> createState() => _ThumbnailImageState();
}

class _ThumbnailImageState extends State<ThumbnailImage> {
  Uint8List? _imageData;
  bool _isLoading = true;
  bool _hasError = false;

  @override
  void initState() {
    super.initState();
    _loadThumbnail();
  }

  Future<void> _loadThumbnail() async {
    try {
      setState(() {
        _isLoading = true;
        _hasError = false;
      });

      // Load thumbnail using the API
      final data = await widget.api.getThumbnail(widget.thumbnailPath);

      if (mounted) {
        setState(() {
          _imageData = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Failed to load thumbnail ${widget.thumbnailPath}: $e');
      if (mounted) {
        setState(() {
          _hasError = true;
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Container(
        color: Colors.grey[300],
        child: const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (_hasError || _imageData == null) {
      return Container(
        color: Colors.grey[300],
        child: const Icon(
          Icons.videocam,
          size: 48,
          color: Colors.grey,
        ),
      );
    }

    return Image.memory(
      _imageData!,
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        return Container(
          color: Colors.grey[300],
          child: const Icon(
            Icons.videocam,
            size: 48,
            color: Colors.grey,
          ),
        );
      },
    );
  }
}
