import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/app_state.dart';

/// Left sidebar with directory list and filters
class LeftSidebar extends StatelessWidget {
  const LeftSidebar({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Theme.of(context).colorScheme.surface,
      child: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Directories section
                  Text(
                    'Directories',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  _buildDirectoryList(context),

                  const SizedBox(height: 24),
                  const Divider(),
                  const SizedBox(height: 12),

                  // Filters section
                  Text(
                    'Filters',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  _buildFilters(context),

                  const SizedBox(height: 12),

                  // Reset filters button
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton(
                      onPressed: () {
                        context.read<AppState>().resetFilters();
                      },
                      child: const Text('Reset Filters'),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDirectoryList(BuildContext context) {
    final directories = [
      ('Normal Videos', 'norm'),
      ('Emergency Videos', 'emr'),
      ('Back Camera', 'back_norm'),
      ('Back Emergency', 'back_emr'),
      ('Photos', 'photo'),
    ];

    return Column(
      children: directories.map((dirInfo) {
        final displayName = dirInfo.$1;
        final apiName = dirInfo.$2;

        return Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                alignment: Alignment.centerLeft,
              ),
              onPressed: () {
                context.read<AppState>().loadDirectory(apiName);
              },
              child: Text(displayName),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildFilters(BuildContext context) {
    return Consumer<AppState>(
      builder: (context, appState, child) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Camera filter
            Text(
              'Camera',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey,
                  ),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                Expanded(
                  child: CheckboxListTile(
                    title: const Text('Front'),
                    value: appState.showFront,
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    controlAffinity: ListTileControlAffinity.leading,
                    onChanged: (value) {
                      appState.updateFilters(showFront: value);
                    },
                  ),
                ),
              ],
            ),
            Row(
              children: [
                Expanded(
                  child: CheckboxListTile(
                    title: const Text('Back'),
                    value: appState.showBack,
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    controlAffinity: ListTileControlAffinity.leading,
                    onChanged: (value) {
                      appState.updateFilters(showBack: value);
                    },
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Type filter
            Text(
              'Type',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey,
                  ),
            ),
            const SizedBox(height: 4),
            CheckboxListTile(
              title: const Text('Normal'),
              value: appState.showNormal,
              dense: true,
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
              onChanged: (value) {
                appState.updateFilters(showNormal: value);
              },
            ),
            CheckboxListTile(
              title: const Text('Emergency'),
              value: appState.showEmergency,
              dense: true,
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
              onChanged: (value) {
                appState.updateFilters(showEmergency: value);
              },
            ),
          ],
        );
      },
    );
  }
}
