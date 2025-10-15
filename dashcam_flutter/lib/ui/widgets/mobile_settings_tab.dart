import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/app_state.dart';
import 'settings_dialog.dart';

/// Mobile settings tab with filters and app settings
class MobileSettingsTab extends StatelessWidget {
  const MobileSettingsTab({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Filters section
        _buildSection(context, 'Filters'),
        const SizedBox(height: 8),
        Consumer<AppState>(
          builder: (context, appState, child) {
            return Card(
              child: Column(
                children: [
                  _buildSwitchTile(
                    context,
                    'Show Front Camera',
                    appState.showFront,
                    (value) => appState.updateFilters(showFront: value),
                  ),
                  const Divider(height: 1),
                  _buildSwitchTile(
                    context,
                    'Show Back Camera',
                    appState.showBack,
                    (value) => appState.updateFilters(showBack: value),
                  ),
                  const Divider(height: 1),
                  _buildSwitchTile(
                    context,
                    'Show Normal Videos',
                    appState.showNormal,
                    (value) => appState.updateFilters(showNormal: value),
                  ),
                  const Divider(height: 1),
                  _buildSwitchTile(
                    context,
                    'Show Emergency Videos',
                    appState.showEmergency,
                    (value) => appState.updateFilters(showEmergency: value),
                  ),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 16),
        Consumer<AppState>(
          builder: (context, appState, child) {
            return ElevatedButton(
              onPressed: appState.resetFilters,
              child: const Text('Reset Filters'),
            );
          },
        ),

        const SizedBox(height: 32),

        // App Settings section
        _buildSection(context, 'App Settings'),
        const SizedBox(height: 8),
        Card(
          child: ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('Dashcam Settings'),
            subtitle: const Text('Configure app and camera settings'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              final appState = context.read<AppState>();
              showDialog(
                context: context,
                builder: (context) => SettingsDialog(
                  api: appState.api,
                  preferencesService: appState.preferencesService,
                ),
              );
            },
          ),
        ),

        const SizedBox(height: 16),

        // About section
        _buildSection(context, 'About'),
        const SizedBox(height: 8),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Dashcam Manager',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Version 1.0.0',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey[600],
                      ),
                ),
                const SizedBox(height: 16),
                Text(
                  'A Flutter app for managing and downloading dashcam videos.',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSection(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 8),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
              color: Theme.of(context).colorScheme.primary,
              fontWeight: FontWeight.bold,
            ),
      ),
    );
  }

  Widget _buildSwitchTile(
    BuildContext context,
    String title,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    return SwitchListTile(
      title: Text(title),
      value: value,
      onChanged: onChanged,
    );
  }
}
