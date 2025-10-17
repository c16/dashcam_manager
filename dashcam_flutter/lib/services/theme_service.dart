import 'package:flutter/material.dart';

/// Service for managing app themes and color schemes
class ThemeService {
  /// Available theme options
  static const List<String> availableThemes = [
    'blue',
    'purple',
    'green',
    'orange',
    'red',
    'teal',
    'pink',
    'amber',
  ];

  /// Display names for themes
  static const Map<String, String> themeDisplayNames = {
    'blue': 'Blue',
    'purple': 'Purple',
    'green': 'Green',
    'orange': 'Orange',
    'red': 'Red',
    'teal': 'Teal',
    'pink': 'Pink',
    'amber': 'Amber',
  };

  /// Get seed color for a theme
  static Color getSeedColor(String theme) {
    switch (theme.toLowerCase()) {
      case 'blue':
        return Colors.blue;
      case 'purple':
        return Colors.deepPurple;
      case 'green':
        return Colors.green;
      case 'orange':
        return Colors.orange;
      case 'red':
        return Colors.red;
      case 'teal':
        return Colors.teal;
      case 'pink':
        return Colors.pink;
      case 'amber':
        return Colors.amber;
      default:
        return Colors.blue;
    }
  }

  /// Get light theme for a specific color scheme
  static ThemeData getLightTheme(String theme) {
    return ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: getSeedColor(theme),
        brightness: Brightness.light,
      ),
      useMaterial3: true,
    );
  }

  /// Get dark theme for a specific color scheme
  static ThemeData getDarkTheme(String theme) {
    return ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: getSeedColor(theme),
        brightness: Brightness.dark,
      ),
      useMaterial3: true,
    );
  }

  /// Convert ThemeMode enum to string
  static String themeModeToString(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.light:
        return 'light';
      case ThemeMode.dark:
        return 'dark';
      case ThemeMode.system:
        return 'system';
    }
  }

  /// Convert string to ThemeMode enum
  static ThemeMode stringToThemeMode(String mode) {
    switch (mode.toLowerCase()) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      case 'system':
      default:
        return ThemeMode.system;
    }
  }

  /// Get display name for theme mode
  static String getThemeModeDisplayName(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.light:
        return 'Light';
      case ThemeMode.dark:
        return 'Dark';
      case ThemeMode.system:
        return 'System';
    }
  }

  /// Validate theme name
  static bool isValidTheme(String theme) {
    return availableThemes.contains(theme.toLowerCase());
  }
}
