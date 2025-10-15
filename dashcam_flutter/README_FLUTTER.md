# Dashcam Manager - Flutter Implementation

Linux desktop and Android app for managing dashcam videos over WiFi.

This is a Flutter port of the Python GTK application, providing:
- Cross-platform support (Linux desktop + Android)
- Modern Material Design UI
- Same functionality as Python app
- Better mobile support

## Screenshots

The Flutter app matches the Python GTK layout:
- Left sidebar: Directory navigation and filters
- Center panel: Video thumbnail grid
- Right panel: Download queue

## Quick Start

### Prerequisites

- Flutter SDK 3.35.6 or later
- For Linux: `sudo apt install clang cmake ninja-build pkg-config libgtk-3-dev`
- For Android: Android Studio with SDK

### Running on Linux Desktop

```bash
cd dashcam_flutter
flutter run -d linux
```

### Running on Android

```bash
cd dashcam_flutter
flutter run -d <device-id>
```

### Building for Release

**Linux:**
```bash
flutter build linux --release
# Executable will be in build/linux/x64/release/bundle/
```

**Android:**
```bash
flutter build apk --release
# APK will be in build/app/outputs/flutter-apk/
```

## Project Structure

```
dashcam_flutter/
├── lib/
│   ├── api/
│   │   └── dashcam_api.dart          # HTTP API client
│   ├── models/
│   │   ├── video_file.dart           # Video file model
│   │   └── download_task.dart        # Download task model
│   ├── services/
│   │   └── app_state.dart            # App state management (Provider)
│   ├── ui/
│   │   ├── screens/
│   │   │   └── main_screen.dart      # Main application screen
│   │   └── widgets/
│   │       ├── left_sidebar.dart     # Directory/filter sidebar
│   │       ├── video_grid.dart       # Video thumbnail grid
│   │       └── download_panel.dart   # Download queue panel
│   └── main.dart                      # App entry point
├── android/                           # Android-specific config
├── linux/                             # Linux-specific config
└── pubspec.yaml                       # Dependencies
```

## Features

### Implemented
- ✅ Connect/disconnect to dashcam WiFi
- ✅ Browse video directories (normal, emergency, back camera, etc.)
- ✅ Filter videos by camera type (front/back)
- ✅ Filter videos by type (normal/emergency)
- ✅ Video thumbnail grid with cached images
- ✅ Download queue management
- ✅ Real-time connection status
- ✅ Responsive three-panel layout

### In Progress
- 🚧 Download manager with progress tracking
- 🚧 Parallel downloads (2-3 connections)
- 🚧 Cache manager for thumbnails
- 🚧 Connection manager with auto-reconnect

### Planned
- 📋 Video playback
- 📋 Settings panel
- 📋 Storage info display
- 📋 GPS data viewing
- 📋 Android mobile optimizations

## Architecture

### State Management
Uses `Provider` package for reactive state management:
- `AppState`: Global application state
- Connection status
- Video list and filters
- Download queue

### API Client
`DashcamAPI` class provides:
- HTTP keep-alive for performance (10-30 Mbps)
- All dashcam API endpoints
- Streaming for large file downloads
- Thumbnail caching

### Data Models
- `VideoFile`: Represents a dashcam video with metadata
- `DownloadTask`: Tracks download progress and status

## Dependencies

Key packages:
- `http`: HTTP client for API calls
- `provider`: State management
- `cached_network_image`: Image caching
- `path_provider`: File system paths
- `intl`: Date formatting

See `pubspec.yaml` for full list.

## Differences from Python App

| Feature | Python GTK | Flutter |
|---------|-----------|---------|
| UI Framework | GTK4 | Material Design |
| Language | Python | Dart |
| Platforms | Linux | Linux + Android |
| State Mgmt | Direct | Provider |
| Image Cache | Manual | cached_network_image |
| Threading | threading.Thread | async/await |

## Development

### Hot Reload

Flutter supports hot reload for fast development:
```bash
# Make code changes, then:
r  # Hot reload
R  # Hot restart
q  # Quit
```

### Adding Features

1. Update models in `lib/models/`
2. Add API methods in `lib/api/`
3. Update state in `lib/services/app_state.dart`
4. Build UI widgets in `lib/ui/widgets/`

### Testing

```bash
flutter test
```

## Performance

Expected WiFi download speeds:
- Sequential with keep-alive: 5-15 Mbps
- Parallel (3 connections): 10-30 Mbps

## Troubleshooting

### Linux Build Issues

Install required dependencies:
```bash
sudo apt install clang cmake ninja-build pkg-config libgtk-3-dev
```

### Android Build Issues

Ensure Android SDK is properly configured:
```bash
flutter doctor --android-licenses
```

### Connection Issues

- Ensure you're connected to dashcam WiFi (typically `Dashcam_XXXXXX`)
- Default IP: `192.168.0.1`
- Check firewall settings

## Next Steps

To complete the Flutter implementation:

1. **Download Manager**: Port `DownloadManager` from Python
2. **Cache Manager**: Port `CacheManager` for persistent thumbnail cache
3. **Connection Manager**: Port `ConnectionManager` with monitoring
4. **Video Player**: Add video playback capability
5. **Settings**: Implement settings dialog
6. **Testing**: Write unit and widget tests
7. **Android Optimizations**: Adapt UI for mobile screens

## Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [Dart Language](https://dart.dev/)
- [Material Design](https://m3.material.io/)
- [Provider Package](https://pub.dev/packages/provider)

## License

Same as parent project.
