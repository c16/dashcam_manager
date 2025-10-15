import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/app_state.dart';
import '../widgets/settings_dialog.dart';
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
                const Text('Dashcam'),
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
              return IconButton(
                icon: Icon(appState.isConnected ? Icons.link_off : Icons.link),
                tooltip: appState.isConnected ? 'Disconnect' : 'Connect',
                onPressed: () async {
                  if (appState.isConnected) {
                    appState.disconnect();
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
