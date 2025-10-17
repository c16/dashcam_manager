import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/app_state.dart';
import '../../models/video_file.dart';
import 'package:intl/intl.dart';
import 'thumbnail_image.dart';

/// Center panel displaying video thumbnails in a grid
class VideoGrid extends StatelessWidget {
  const VideoGrid({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Theme.of(context).colorScheme.surface,
      child: Consumer<AppState>(
        builder: (context, appState, child) {
          if (!appState.isConnected) {
            return _buildPlaceholder(
              context,
              Icons.link_off,
              'Connect to dashcam to view videos',
            );
          }

          if (appState.filteredVideos.isEmpty) {
            if (appState.currentDirectory == null) {
              return _buildPlaceholder(
                context,
                Icons.folder_open,
                'Select a directory to view videos',
              );
            } else {
              return _buildPlaceholder(
                context,
                Icons.filter_alt_off,
                'No videos match current filters',
              );
            }
          }

          return GridView.builder(
            padding: const EdgeInsets.all(16),
            gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
              maxCrossAxisExtent: 200,
              childAspectRatio: 0.75, // Adjusted for thumbnail aspect ratio (3:4)
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            itemCount: appState.filteredVideos.length,
            itemBuilder: (context, index) {
              final video = appState.filteredVideos[index];
              return _VideoThumbnail(video: video);
            },
          );
        },
      ),
    );
  }

  Widget _buildPlaceholder(BuildContext context, IconData icon, String message) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            icon,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          Text(
            message,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.grey,
                ),
          ),
        ],
      ),
    );
  }
}

/// Individual video thumbnail widget
class _VideoThumbnail extends StatelessWidget {
  final VideoFile video;

  const _VideoThumbnail({required this.video});

  @override
  Widget build(BuildContext context) {
    final appState = context.read<AppState>();

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () {
          context.read<AppState>().addToDownloadQueue(video);
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Thumbnail image
            Expanded(
              child: appState.isConnected && appState.api != null
                  ? ThumbnailImage(
                      api: appState.api!,
                      thumbnailPath: video.thumbnailPath,
                    )
                  : Container(
                      color: Colors.grey[300],
                      child: const Icon(
                        Icons.videocam,
                        size: 48,
                        color: Colors.grey,
                      ),
                    ),
            ),
            // Video info
            Container(
              padding: const EdgeInsets.all(8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    DateFormat('MMM d, y').format(video.timestamp),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    DateFormat('h:mm a').format(video.timestamp),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey[600],
                        ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      _buildBadge(
                        context,
                        video.camera == 'front' ? 'Front' : 'Back',
                        Colors.blue,
                      ),
                      const SizedBox(width: 4),
                      if (video.type == 'emergency')
                        _buildBadge(
                          context,
                          'Emergency',
                          Colors.red,
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBadge(BuildContext context, String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color, width: 1),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
      ),
    );
  }
}
