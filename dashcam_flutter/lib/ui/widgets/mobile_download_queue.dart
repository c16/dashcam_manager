import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../services/app_state.dart';
import '../../models/download_task.dart';

/// Mobile-optimized download queue view
class MobileDownloadQueue extends StatelessWidget {
  const MobileDownloadQueue({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Header with clear button
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
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
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const Spacer(),
              Consumer<AppState>(
                builder: (context, appState, child) {
                  if (appState.downloadQueue.isEmpty) {
                    return const SizedBox.shrink();
                  }
                  return TextButton.icon(
                    onPressed: () {
                      appState.clearDownloadQueue();
                    },
                    icon: const Icon(Icons.clear_all),
                    label: const Text('Clear'),
                  );
                },
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
                        Icons.download_done,
                        size: 64,
                        color: Colors.grey[400],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'No downloads',
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                              color: Colors.grey,
                            ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Tap videos to add them to the queue',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey,
                            ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                );
              }

              return ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: appState.downloadQueue.length,
                separatorBuilder: (context, index) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final task = appState.downloadQueue[index];
                  return _DownloadTaskCard(task: task);
                },
              );
            },
          ),
        ),
      ],
    );
  }
}

/// Download task card showing progress
class _DownloadTaskCard extends StatelessWidget {
  final DownloadTask task;

  const _DownloadTaskCard({required this.task});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // File info
            Row(
              children: [
                Icon(
                  _getStatusIcon(),
                  color: _getStatusColor(),
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        task.file.filename,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        DateFormat('MMM d, y h:mm a').format(task.file.timestamp),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                            ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Status
            if (task.status == 'downloading') ...[
              LinearProgressIndicator(
                value: task.progress,
                backgroundColor: Colors.grey[200],
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${(task.progress * 100).toStringAsFixed(1)}%',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  if (task.speedMbps > 0)
                    Text(
                      '${task.speedMbps.toStringAsFixed(1)} Mbps',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.blue,
                          ),
                    ),
                ],
              ),
            ] else if (task.status == 'queued') ...[
              Text(
                'Waiting...',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.orange,
                    ),
              ),
            ] else if (task.status == 'completed') ...[
              Row(
                children: [
                  const Icon(Icons.check_circle, size: 16, color: Colors.green),
                  const SizedBox(width: 4),
                  Text(
                    'Completed',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.green,
                        ),
                  ),
                ],
              ),
            ] else if (task.status == 'failed') ...[
              Row(
                children: [
                  const Icon(Icons.error, size: 16, color: Colors.red),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      'Failed: ${task.error}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.red,
                          ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  IconData _getStatusIcon() {
    switch (task.status) {
      case 'queued':
        return Icons.schedule;
      case 'downloading':
        return Icons.downloading;
      case 'completed':
        return Icons.check_circle;
      case 'failed':
        return Icons.error;
      default:
        return Icons.help;
    }
  }

  Color _getStatusColor() {
    switch (task.status) {
      case 'queued':
        return Colors.orange;
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
