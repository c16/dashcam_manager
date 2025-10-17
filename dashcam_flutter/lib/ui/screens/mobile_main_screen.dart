import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../constants.dart';
import '../../services/app_state.dart';
import '../widgets/mobile_video_grid.dart';
import '../widgets/mobile_download_queue.dart';
import '../widgets/mobile_settings_tab.dart';

/// Mobile-optimized main screen with bottom navigation
class MobileMainScreen extends StatefulWidget {
  const MobileMainScreen({super.key});

  @override
  State<MobileMainScreen> createState() => _MobileMainScreenState();
}

class _MobileMainScreenState extends State<MobileMainScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Consumer<AppState>(
          builder: (context, appState, child) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(AppConstants.appTitle),
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
          // WiFi Settings button (Android only)
          Consumer<AppState>(
            builder: (context, appState, child) {
              if (appState.isConnected) return const SizedBox();

              return IconButton(
                icon: const Icon(Icons.wifi_find),
                tooltip: 'Open WiFi Settings',
                onPressed: () {
                  appState.connectWithSettingsIntent(
                    onConnected: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Connected to dashcam!'),
                          backgroundColor: Colors.green,
                        ),
                      );
                    },
                    onTimeout: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Connection timeout. Try again?'),
                          backgroundColor: Colors.orange,
                        ),
                      );
                    },
                  );
                },
              );
            },
          ),
          // Connect/Disconnect button
          Consumer<AppState>(
            builder: (context, appState, child) {
              return IconButton(
                icon: Icon(appState.isConnected ? Icons.link_off : Icons.link),
                tooltip: appState.isConnected ? 'Disconnect' : 'Connect',
                onPressed: () async {
                  if (appState.isConnected) {
                    // Show disconnect confirmation
                    final shouldOpen = await showDialog<bool>(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Disconnect'),
                        content: const Text('Open WiFi settings to reconnect to your original network?'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(context, false),
                            child: const Text('No'),
                          ),
                          TextButton(
                            onPressed: () => Navigator.pop(context, true),
                            child: const Text('Yes'),
                          ),
                        ],
                      ),
                    );

                    if (shouldOpen == true) {
                      await appState.disconnectAndOpenSettings();
                    } else {
                      await appState.disconnect();
                    }
                  } else {
                    await appState.connect();
                  }
                },
              );
            },
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: const [
          MobileVideoGrid(),
          MobileDownloadQueue(),
          MobileSettingsTab(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.video_library),
            label: 'Videos',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.download),
            label: 'Queue',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
      ),
    );
  }
}
