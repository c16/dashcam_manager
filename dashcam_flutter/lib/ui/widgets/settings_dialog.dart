import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../../api/dashcam_api.dart';
import '../../services/preferences_service.dart';

/// Settings dialog for dashcam configuration
class SettingsDialog extends StatefulWidget {
  final DashcamAPI? api;
  final PreferencesService preferencesService;

  const SettingsDialog({
    super.key,
    this.api,
    required this.preferencesService,
  });

  @override
  State<SettingsDialog> createState() => _SettingsDialogState();
}

class _SettingsDialogState extends State<SettingsDialog> {
  String _deviceInfo = '';
  String _statusMessage = '';
  bool _isLoading = false;

  // App settings
  String _downloadDirectory = '';

  @override
  void initState() {
    super.initState();
    _loadAppSettings();
    if (widget.api != null) {
      _loadDeviceSettings();
    }
  }

  Future<void> _loadAppSettings() async {
    final downloadDir = await widget.preferencesService.getDownloadDirectory();

    setState(() {
      _downloadDirectory = downloadDir;
    });
  }

  Future<void> _loadDeviceSettings() async {
    if (widget.api == null) {
      setState(() {
        _statusMessage = 'Not connected to dashcam';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _statusMessage = 'Loading settings...';
    });

    try {
      // Get device info
      final deviceInfo = await widget.api!.getDeviceAttr();

      setState(() {
        _deviceInfo = deviceInfo;
        _statusMessage = 'Settings loaded';
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _statusMessage = 'Failed to load settings: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _saveSettings() async {
    setState(() {
      _isLoading = true;
      _statusMessage = 'Saving settings...';
    });

    try {
      // Save app settings
      await widget.preferencesService.setDownloadDirectory(_downloadDirectory);

      setState(() {
        _statusMessage = 'Settings saved successfully';
        _isLoading = false;
      });

      // Close dialog after brief delay
      Future.delayed(const Duration(seconds: 1), () {
        if (mounted) {
          Navigator.of(context).pop();
        }
      });
    } catch (e) {
      setState(() {
        _statusMessage = 'Failed to save settings: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _browseDownloadDirectory() async {
    String? selectedDirectory = await FilePicker.platform.getDirectoryPath();
    if (selectedDirectory != null) {
      setState(() {
        _downloadDirectory = selectedDirectory;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Container(
        width: 600,
        constraints: const BoxConstraints(maxHeight: 700),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primaryContainer,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(4),
                  topRight: Radius.circular(4),
                ),
              ),
              child: Row(
                children: [
                  Text(
                    'Settings',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
            ),

            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Download Directory
                    _buildDirectorySetting(
                      'Download Directory',
                      _downloadDirectory,
                      _browseDownloadDirectory,
                    ),

                    const SizedBox(height: 24),

                    // Device Information
                    if (_deviceInfo.isNotEmpty) ...[
                      _buildSection('Device Information'),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: SelectableText(
                          _deviceInfo,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                fontFamily: 'monospace',
                              ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),

            // Status and actions
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                border: Border(
                  top: BorderSide(
                    color: Theme.of(context).dividerColor,
                  ),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (_statusMessage.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Text(
                        _statusMessage,
                        style: Theme.of(context).textTheme.bodySmall,
                        textAlign: TextAlign.center,
                      ),
                    ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text('Close'),
                      ),
                      const SizedBox(width: 8),
                      FilledButton(
                        onPressed: _isLoading ? null : _saveSettings,
                        child: _isLoading
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text('Save'),
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

  Widget _buildSection(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const Divider(),
        ],
      ),
    );
  }

  Widget _buildDirectorySetting(
      String label, String path, VoidCallback onBrowse) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(
                      color: Theme.of(context).dividerColor,
                    ),
                  ),
                  child: Text(
                    path.isEmpty ? 'Not set' : path,
                    style: Theme.of(context).textTheme.bodySmall,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: onBrowse,
                child: const Text('Browse...'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
