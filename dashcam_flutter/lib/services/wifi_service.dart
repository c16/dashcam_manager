import 'dart:io';
import 'package:flutter/material.dart';
import 'package:wifi_iot/wifi_iot.dart';
import 'package:network_info_plus/network_info_plus.dart';
import 'package:permission_handler/permission_handler.dart';

/// Service for managing WiFi connections to dashcam
class WiFiService {
  String? _previousSSID;
  bool _isConnectedToDashcam = false;

  /// Default dashcam WiFi SSID (can be configured)
  static const String defaultDashcamSSID = 'Dashcam_A79500';
  String dashcamSSID = defaultDashcamSSID;
  String? dashcamPassword;

  /// Get current WiFi SSID
  Future<String?> getCurrentSSID() async {
    try {
      final info = NetworkInfo();
      return await info.getWifiName();
    } catch (e) {
      debugPrint('Error getting current SSID: $e');
      return null;
    }
  }

  /// Request necessary permissions for WiFi management
  Future<bool> requestPermissions() async {
    if (!Platform.isAndroid) {
      return true; // Only needed on Android
    }

    // Request location permission (required for WiFi scanning on Android 8+)
    final locationStatus = await Permission.location.request();
    if (!locationStatus.isGranted) {
      debugPrint('Location permission denied');
      return false;
    }

    // Request nearby WiFi devices permission (Android 13+)
    if (Platform.isAndroid) {
      try {
        final nearbyStatus = await Permission.nearbyWifiDevices.request();
        if (!nearbyStatus.isGranted) {
          debugPrint('Nearby WiFi devices permission denied');
          // Continue anyway, might work on older Android versions
        }
      } catch (e) {
        debugPrint('Nearby WiFi permission not available: $e');
      }
    }

    return true;
  }

  /// Connect to dashcam WiFi network
  Future<bool> connectToDashcam({
    required String ssid,
    String? password,
  }) async {
    try {
      // Request permissions first
      final hasPermissions = await requestPermissions();
      if (!hasPermissions) {
        debugPrint('Required permissions not granted');
        return false;
      }

      // Save current network to restore later
      _previousSSID = await getCurrentSSID();
      debugPrint('Current WiFi: $_previousSSID');

      // Save dashcam credentials
      dashcamSSID = ssid;
      dashcamPassword = password;

      // Check if already connected to dashcam
      final currentSSID = await getCurrentSSID();
      if (currentSSID != null && currentSSID.contains(ssid)) {
        debugPrint('Already connected to dashcam WiFi: $currentSSID');
        _isConnectedToDashcam = true;
        return true;
      }

      if (!Platform.isAndroid) {
        // On non-Android platforms, just track the intention
        debugPrint('WiFi switching not implemented for this platform');
        return false;
      }

      // Connect to dashcam WiFi on Android
      debugPrint('Connecting to dashcam WiFi: $ssid');

      bool connected = false;
      if (password != null && password.isNotEmpty) {
        connected = await WiFiForIoTPlugin.connect(
          ssid,
          password: password,
          security: NetworkSecurity.WPA,
          withInternet: false,
        );
      } else {
        connected = await WiFiForIoTPlugin.connect(
          ssid,
          withInternet: false,
        );
      }

      if (connected) {
        debugPrint('Successfully connected to dashcam WiFi');
        _isConnectedToDashcam = true;

        // Wait a bit for connection to stabilize
        await Future.delayed(const Duration(seconds: 2));

        return true;
      } else {
        debugPrint('Failed to connect to dashcam WiFi');
        return false;
      }
    } catch (e) {
      debugPrint('Error connecting to dashcam WiFi: $e');
      return false;
    }
  }

  /// Disconnect from dashcam and restore previous WiFi
  Future<bool> disconnectFromDashcam() async {
    if (!_isConnectedToDashcam) {
      debugPrint('Not connected to dashcam WiFi');
      return true;
    }

    try {
      if (!Platform.isAndroid) {
        _isConnectedToDashcam = false;
        return true;
      }

      // Disconnect from current network
      await WiFiForIoTPlugin.disconnect();
      debugPrint('Disconnected from dashcam WiFi');

      // Try to reconnect to previous network
      if (_previousSSID != null && _previousSSID!.isNotEmpty) {
        debugPrint('Attempting to reconnect to previous WiFi: $_previousSSID');

        // Remove quotes if present (Android returns SSID with quotes)
        final ssid = _previousSSID!.replaceAll('"', '');

        // Try to connect to previous network
        // Note: This might not work if we don't have the password
        try {
          await WiFiForIoTPlugin.connect(ssid, withInternet: true);
          debugPrint('Reconnected to previous WiFi');
        } catch (e) {
          debugPrint('Could not automatically reconnect to previous WiFi: $e');
          debugPrint('User may need to manually reconnect');
        }
      }

      _isConnectedToDashcam = false;
      _previousSSID = null;

      return true;
    } catch (e) {
      debugPrint('Error disconnecting from dashcam WiFi: $e');
      return false;
    }
  }

  /// Check if currently connected to dashcam WiFi
  Future<bool> isConnectedToDashcam() async {
    final currentSSID = await getCurrentSSID();
    if (currentSSID == null) return false;

    final ssid = currentSSID.replaceAll('"', '');
    return ssid.contains(dashcamSSID);
  }

  /// Get list of available WiFi networks
  Future<List<WifiNetwork>> scanNetworks() async {
    try {
      if (!Platform.isAndroid) {
        return [];
      }

      final hasPermissions = await requestPermissions();
      if (!hasPermissions) {
        return [];
      }

      final networks = await WiFiForIoTPlugin.loadWifiList();
      return networks;
    } catch (e) {
      debugPrint('Error scanning WiFi networks: $e');
      return [];
    }
  }

  /// Find dashcam networks in available networks
  Future<List<WifiNetwork>> findDashcamNetworks({String ssidPattern = 'Dashcam_'}) async {
    final networks = await scanNetworks();
    return networks.where((network) =>
      network.ssid?.startsWith(ssidPattern) ?? false
    ).toList();
  }
}
