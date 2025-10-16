# Dashcam Manager v1.0.0

A cross-platform application for managing and downloading videos from WiFi-enabled dashcams. Available for Linux desktop (Python GTK4), Linux desktop (Flutter), and Android (Flutter).

<img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version 1.0.0"/> <img src="https://img.shields.io/badge/python-3.11+-green.svg" alt="Python 3.11+"/> <img src="https://img.shields.io/badge/flutter-3.0+-blue.svg" alt="Flutter 3.0+"/> <img src="https://img.shields.io/badge/platform-Linux%20%7C%20Android-lightgrey.svg" alt="Platforms"/>

## Features

- **Browse Videos**: View videos organized by directory (Normal, Emergency, Back Camera, etc.)
- **Thumbnail Preview**: Quick visual preview of video files
- **Filtering**: Filter by camera position (front/back) and type (normal/emergency)
- **Parallel Downloads**: Download multiple videos simultaneously with progress tracking
- **WiFi Management** (Android): Automatic or manual WiFi switching to connect to dashcam
- **Configurable Settings**: Customizable download directory and parallel download limits
- **Cross-Platform**: Choose between Python GTK (Linux), Flutter Linux, or Flutter Android

## Screenshots

### Python GTK Desktop Application
Full-featured desktop application with three-panel layout.

### Flutter Linux Application
Native Flutter desktop application with the same functionality.

### Flutter Android Application
Mobile-optimized interface with bottom navigation and touch-friendly controls.

## Quick Start

### Python GTK (Linux Desktop)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python3 src/ui/main_window.py
```

### Flutter Linux

```bash
cd dashcam_flutter
flutter pub get
flutter run -d linux
```

### Flutter Android

```bash
cd dashcam_flutter
flutter pub get
flutter run  # Or build APK with: flutter build apk --release
```

## Installation

See [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md) for complete build instructions, packaging guides, and distribution preparation.

## Requirements

### Python Application
- Python 3.11+
- GTK 4.0+
- Dependencies: `requests`, `PyGObject`, `Pillow`

### Flutter Applications
- Flutter SDK 3.0+
- For Linux: GTK development libraries
- For Android: Android SDK, JDK 11+

## Usage

1. **Connect to Dashcam**
   - **Manual mode** (default): Connect your device to the dashcam WiFi network (SSID: `Dashcam_A79500`)
   - **Auto mode** (Android): Enable "Auto WiFi Switch" in settings for automatic connection

2. **Click "Connect"** button in the app

3. **Browse Videos**
   - Select a directory from the left sidebar
   - View thumbnails in the center panel
   - Filter videos using the filter controls

4. **Download Videos**
   - Click a thumbnail to add to download queue
   - Or click "Download All" to queue all visible videos
   - Monitor progress in the right panel

5. **Configure Settings**
   - Click settings icon to configure download directory, parallel downloads, and WiFi behavior

## Configuration

### Default Settings

- **Dashcam WiFi SSID**: `Dashcam_A79500`
- **Dashcam IP Address**: `192.168.0.1`
- **Download Directory**:
  - Linux: `~/Videos/Dashcam`
  - Android: `/storage/emulated/0/Android/data/com.example.dashcam_flutter/files/Dashcam`
- **Max Parallel Downloads**: 3
- **Auto WiFi Switch**: Disabled (manual mode)

### Customization

All settings can be customized through the Settings dialog:
- Download directory location
- Maximum parallel downloads (1-5)
- Auto WiFi switching (Android only)

## Architecture

The application consists of three main components:

### 1. Python GTK Application (`src/`)
- **API Client** (`src/api/`): HTTP client for dashcam communication
- **Services** (`src/services/`): Connection management, caching, downloads
- **UI** (`src/ui/`): GTK4-based desktop interface

### 2. Flutter Linux Application (`dashcam_flutter/`)
- **API Client** (`lib/api/`): Dart HTTP client
- **Services** (`lib/services/`): State management, downloads, preferences
- **UI** (`lib/ui/`): Flutter desktop widgets

### 3. Flutter Android Application (`dashcam_flutter/`)
- Shares codebase with Flutter Linux
- **Additional Services**: WiFi management for automatic network switching
- **Mobile UI**: Touch-optimized interface with bottom navigation

## API Protocol

The dashcam uses a simple HTTP-based API:

- **Base URL**: `http://192.168.0.1`
- **File Structure**: Videos organized by directory (norm, emr, back_norm, back_emr, etc.)
- **File Format**: `.TS` video files with `.THM` thumbnails
- **Authentication**: Session-based (Cookie: SessionID)

See `src/api/dashcam_api.py` or `dashcam_flutter/lib/api/dashcam_api.dart` for complete API implementation.

## Project Structure

```
dashcam/
├── src/                    # Python GTK application
│   ├── api/               # API client and models
│   ├── services/          # Business logic
│   ├── ui/                # GTK4 interface
│   └── utils/             # Utilities
├── dashcam_flutter/       # Flutter application (Linux & Android)
│   ├── lib/
│   │   ├── api/          # API client
│   │   ├── models/       # Data models
│   │   ├── services/     # State management
│   │   └── ui/           # Flutter widgets
│   ├── android/          # Android-specific configuration
│   └── linux/            # Linux-specific configuration
├── BUILD_AND_DEPLOY.md   # Build and deployment guide
├── requirements.txt       # Python dependencies
└── setup.py              # Python package configuration
```

## Development

### Running Tests

```bash
# Python tests
pytest tests/

# Flutter tests
cd dashcam_flutter
flutter test
```

### Building for Production

See [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md) for:
- Creating Python executable with PyInstaller
- Building Flutter release packages (AppImage, .deb, APK, AAB)
- App signing for Android
- Distribution preparation

## Known Issues

- WiFi auto-switching on Android can be unreliable due to platform restrictions (use manual mode)
- Thumbnail loading may be slow on first directory load (images are cached after first load)
- Some dashcam models may use different directory structures or API endpoints

## Troubleshooting

### Cannot connect to dashcam
- Verify you're connected to the dashcam WiFi network (SSID: `Dashcam_A79500`)
- Check that dashcam IP is `192.168.0.1`
- Try disabling auto WiFi switch and connecting manually

### Videos not downloading
- Check storage permissions (Android)
- Verify download directory has write access
- Reduce max parallel downloads in settings

### Thumbnails not displaying
- Ensure you're connected to the dashcam
- Check network connectivity
- Try reloading the directory

See [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md) for more troubleshooting tips.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

MIT License - see LICENSE file for details.

## Roadmap

- [ ] Support for additional dashcam models/APIs
- [ ] Video playback within the application
- [ ] GPS track visualization
- [ ] Cloud backup integration
- [ ] iOS support

## Credits

Built with:
- **Python**: GTK4, Requests, Pillow
- **Flutter**: Provider, HTTP, CachedNetworkImage
- **Android WiFi**: wifi_iot, network_info_plus, permission_handler

## Version History

### 1.0.0 (2025-10-16)
- Initial release
- Python GTK desktop application
- Flutter Linux desktop application
- Flutter Android mobile application
- Cross-platform video browsing and download
- Configurable settings and WiFi management
- Parallel download support
