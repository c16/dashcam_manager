import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/app_state.dart';
import '../../models/download_task.dart';

/// Right sidebar displaying download queue
class DownloadPanel extends StatelessWidget {
  const DownloadPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Theme.of(context).colorScheme.surface,
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              border: Border(
                bottom: BorderSide(
                  color: Theme.of(context).dividerColor,
                ),
              ),
            ),
            child: Row(
              children: [
                Text(
                  'Download Queue',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () {
                    context.read<AppState>().clearDownloadQueue();
                  },
                  child: const Text('Clear'),
                ),
              ],
            ),
          ),
          // Queue list
          Expanded(
            child: Consumer<AppState>(
              builder: (context, appState, child) {
                if (appState.downloadQueue.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.download_outlined,
                          size: 48,
                          color: Colors.grey[400],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'No downloads',
                          style:
                              Theme.of(context).textTheme.bodyMedium?.copyWith(
                                    color: Colors.grey[600],
                                  ),
                        ),
                      ],
                    ),
                  );
                }

                return ListView.separated(
                  padding: const EdgeInsets.all(8),
                  itemCount: appState.downloadQueue.length,
                  separatorBuilder: (context, index) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final task = appState.downloadQueue[index];
                    return _DownloadTaskCard(task: task);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

/// Individual download task card
class _DownloadTaskCard extends StatelessWidget {
  final DownloadTask task;

  const _DownloadTaskCard({required this.task});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Filename
            Text(
              task.file.filename,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),
            // Status
            Row(
              children: [
                _buildStatusIcon(),
                const SizedBox(width: 8),
                Text(
                  _getStatusText(),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: _getStatusColor(),
                      ),
                ),
                const Spacer(),
                if (task.status == 'downloading')
                  Text(
                    '${(task.progress * 100).toStringAsFixed(0)}%',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
              ],
            ),
            // Progress bar (only show if downloading)
            if (task.status == 'downloading') ...[
              const SizedBox(height: 8),
              LinearProgressIndicator(
                value: task.progress,
                backgroundColor: Colors.grey[300],
              ),
              const SizedBox(height: 4),
              if (task.speedMbps > 0)
                Text(
                  '${task.speedMbps.toStringAsFixed(1)} Mbps',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey[600],
                      ),
                ),
            ],
            // Error message (if failed)
            if (task.hasFailed && task.error != null) ...[
              const SizedBox(height: 8),
              Text(
                task.error!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.red,
                    ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatusIcon() {
    switch (task.status) {
      case 'queued':
        return const Icon(Icons.schedule, size: 16, color: Colors.grey);
      case 'downloading':
        return const SizedBox(
          width: 16,
          height: 16,
          child: CircularProgressIndicator(strokeWidth: 2),
        );
      case 'completed':
        return const Icon(Icons.check_circle, size: 16, color: Colors.green);
      case 'failed':
        return const Icon(Icons.error, size: 16, color: Colors.red);
      default:
        return const Icon(Icons.help_outline, size: 16, color: Colors.grey);
    }
  }

  String _getStatusText() {
    switch (task.status) {
      case 'queued':
        return 'Queued';
      case 'downloading':
        return 'Downloading';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  }

  Color _getStatusColor() {
    switch (task.status) {
      case 'queued':
        return Colors.grey;
      case 'downloading':
        return Colors.blue;
      case 'completed':
        return Colors.green;
      case 'failed':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}
