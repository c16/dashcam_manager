import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/app_state.dart';
import '../widgets/left_sidebar.dart';
import '../widgets/video_grid.dart';
import '../widgets/download_panel.dart';
import '../widgets/settings_dialog.dart';

/// Main screen with three-panel layout matching Python GTK app
class MainScreen extends StatelessWidget {
  const MainScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Consumer<AppState>(
          builder: (context, appState, child) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Dashcam Manager'),
                Text(
                  appState.connectionStatus,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: appState.isConnected ? Colors.green : Colors.grey,
                      ),
                ),
              ],
            );
          },
        ),
        actions: [
          // Connect/Disconnect button
          Consumer<AppState>(
            builder: (context, appState, child) {
              return ElevatedButton(
                onPressed: () async {
                  if (appState.isConnected) {
                    appState.disconnect();
                  } else {
                    await appState.connect();
                  }
                },
                child: Text(appState.isConnected ? 'Disconnect' : 'Connect'),
              );
            },
          ),
          const SizedBox(width: 8),
          // Download All button
          Consumer<AppState>(
            builder: (context, appState, child) {
              return ElevatedButton(
                onPressed: appState.filteredVideos.isEmpty
                    ? null
                    : () {
                        appState
                            .addMultipleToDownloadQueue(appState.filteredVideos);
                      },
                child: const Text('Download All'),
              );
            },
          ),
          const SizedBox(width: 8),
          // Settings button
          Consumer<AppState>(
            builder: (context, appState, child) {
              return IconButton(
                icon: const Icon(Icons.settings),
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (context) => SettingsDialog(api: appState.api),
                  );
                },
              );
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          // Main content area with three panels
          Expanded(
            child: Row(
              children: [
                // Left sidebar (200px width)
                const SizedBox(
                  width: 200,
                  child: LeftSidebar(),
                ),
                // Divider
                const VerticalDivider(width: 1),
                // Center panel (expandable)
                const Expanded(
                  child: VideoGrid(),
                ),
                // Divider
                const VerticalDivider(width: 1),
                // Right sidebar (300px width)
                const SizedBox(
                  width: 300,
                  child: DownloadPanel(),
                ),
              ],
            ),
          ),
          // Status bar
          Container(
            height: 32,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              border: Border(
                top: BorderSide(
                  color: Theme.of(context).dividerColor,
                ),
              ),
            ),
            child: Row(
              children: [
                Consumer<AppState>(
                  builder: (context, appState, child) {
                    return Text(
                      appState.statusMessage,
                      style: Theme.of(context).textTheme.bodySmall,
                    );
                  },
                ),
                const Spacer(),
                Text(
                  'Storage: -- / --',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
