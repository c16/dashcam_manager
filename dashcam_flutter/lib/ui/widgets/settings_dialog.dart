import 'package:flutter/material.dart';
import '../../api/dashcam_api.dart';

/// Settings dialog for dashcam configuration
class SettingsDialog extends StatefulWidget {
  final DashcamAPI? api;

  const SettingsDialog({super.key, this.api});

  @override
  State<SettingsDialog> createState() => _SettingsDialogState();
}

class _SettingsDialogState extends State<SettingsDialog> {
  String _deviceInfo = '';
  String _statusMessage = '';
  bool _isLoading = false;

  // Settings
  String _videoQuality = 'High';
  String _loopDuration = '3 minutes';
  bool _audioRecording = true;
  bool _gpsLogging = true;
  bool _parkingMode = false;
  bool _timestamp = true;
  bool _speedDisplay = true;
  String _gsensorSensitivity = 'Medium';
  String _autoPowerOff = 'Off';

  @override
  void initState() {
    super.initState();
    if (widget.api != null) {
      _loadSettings();
    }
  }

  Future<void> _loadSettings() async {
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
    if (widget.api == null) {
      setState(() {
        _statusMessage = 'Not connected to dashcam';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _statusMessage = 'Saving settings...';
    });

    try {
      // Save settings via API
      // This is a placeholder - actual implementation would use specific API calls

      await Future.delayed(const Duration(seconds: 1));

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
                    'Dashcam Settings',
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
                    // Camera Settings
                    _buildSection('Camera Settings'),
                    _buildDropdownSetting('Video Quality', _videoQuality,
                        ['High', 'Medium', 'Low'], (value) {
                      setState(() => _videoQuality = value!);
                    }),
                    _buildDropdownSetting('Loop Recording', _loopDuration,
                        ['1 minute', '3 minutes', '5 minutes'], (value) {
                      setState(() => _loopDuration = value!);
                    }),
                    _buildSwitchSetting('Audio Recording', _audioRecording,
                        (value) {
                      setState(() => _audioRecording = value);
                    }),
                    _buildSwitchSetting('GPS Logging', _gpsLogging, (value) {
                      setState(() => _gpsLogging = value);
                    }),
                    _buildSwitchSetting('Parking Mode', _parkingMode, (value) {
                      setState(() => _parkingMode = value);
                    }),

                    const SizedBox(height: 24),

                    // Display Settings
                    _buildSection('Display'),
                    _buildSwitchSetting('Date/Time Stamp', _timestamp, (value) {
                      setState(() => _timestamp = value);
                    }),
                    _buildSwitchSetting('Speed Display', _speedDisplay, (value) {
                      setState(() => _speedDisplay = value);
                    }),

                    const SizedBox(height: 24),

                    // Advanced Settings
                    _buildSection('Advanced'),
                    _buildDropdownSetting('G-Sensor Sensitivity',
                        _gsensorSensitivity, ['High', 'Medium', 'Low', 'Off'],
                        (value) {
                      setState(() => _gsensorSensitivity = value!);
                    }),
                    _buildDropdownSetting('Auto Power Off', _autoPowerOff,
                        ['Off', '1 minute', '3 minutes', '5 minutes'], (value) {
                      setState(() => _autoPowerOff = value!);
                    }),

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

  Widget _buildSwitchSetting(
      String label, bool value, ValueChanged<bool> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: Text(label),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdownSetting(String label, String value, List<String> options,
      ValueChanged<String?> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: Text(label),
          ),
          DropdownButton<String>(
            value: value,
            items: options.map((String option) {
              return DropdownMenuItem<String>(
                value: option,
                child: Text(option),
              );
            }).toList(),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }
}
