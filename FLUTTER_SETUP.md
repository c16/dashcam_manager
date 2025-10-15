# Flutter Setup Instructions

## Installation Steps

### 1. Visit Official Flutter Documentation
Go to: https://docs.flutter.dev/get-started/install/linux

### 2. What You'll Need to Install
- Flutter SDK
- Android Studio (for Android development)
- Android SDK and emulator
- Chrome (for web/desktop testing)

### 3. Installation Process (High-Level)

#### Download and Install Flutter SDK
```bash
# Download Flutter SDK (follow website instructions for latest version)
# Extract to a location like ~/development/flutter

# Add Flutter to your PATH
# Add this to your ~/.bashrc or ~/.zshrc:
export PATH="$PATH:$HOME/development/flutter/bin"

# Reload your shell configuration
source ~/.bashrc
```

#### Run Flutter Doctor
```bash
flutter doctor
```
This command checks your environment and displays a report of Flutter installation status.

#### Install Android Studio
- Download from: https://developer.android.com/studio
- Install Android Studio
- Open Android Studio and go through the setup wizard
- Install Android SDK, Android SDK Platform-Tools, and Android SDK Build-Tools

#### Accept Android Licenses
```bash
flutter doctor --android-licenses
```
Press 'y' to accept all licenses.

#### Enable Linux Desktop Support
```bash
flutter config --enable-linux-desktop
```

#### Install Linux Desktop Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install clang cmake ninja-build pkg-config libgtk-3-dev

# Fedora
sudo dnf install clang cmake ninja-build gtk3-devel
```

### 4. Verify Installation

Run the full diagnostic:
```bash
flutter doctor -v
```

Expected output should show:
- ✓ Flutter (Channel stable, version X.X.X)
- ✓ Android toolchain - develop for Android devices
- ✓ Chrome - develop for the web
- ✓ Linux toolchain - develop for Linux desktop
- ✓ Android Studio (version X.X.X)

**Note**: Warnings about optional IDEs (VS Code, IntelliJ) are fine if you don't use them.

### 5. Test Flutter Installation

Create a test app to verify everything works:
```bash
cd ~
flutter create test_app
cd test_app
flutter run -d linux
```

If a window opens with the Flutter demo app, you're ready!

---

## Next Steps: Flutter Port

Once Flutter is installed successfully, come back and we'll start porting the dashcam manager!

### What We'll Do

1. **Project Setup**
   - Create new Flutter project
   - Set up directory structure
   - Add required dependencies (http, path_provider, etc.)

2. **Port API Client**
   - Convert Python DashcamAPI to Dart
   - Port data models (VideoFile, DownloadTask)
   - Implement HTTP client with keep-alive

3. **Port Services**
   - Connection manager
   - Download manager with parallel downloads
   - Cache manager for thumbnails

4. **Build Flutter UI**
   - Main screen with navigation
   - Video grid with thumbnails
   - Download queue panel
   - Settings dialog
   - Responsive layout for desktop and mobile

5. **Test on Linux Desktop**
   - Run and debug on Linux
   - Verify all features work
   - Performance testing

6. **Adapt for Android**
   - Adjust UI for mobile screens
   - Handle Android permissions (storage, network)
   - Test on Android emulator
   - Build APK for real device testing

### Architecture Benefits

The good news is that much of the logic can be ported directly:
- API client logic is straightforward HTTP requests
- Data models translate easily to Dart classes
- Download manager uses similar async patterns
- File caching works the same way

The main work will be:
- Rebuilding UI with Flutter widgets instead of GTK
- Handling mobile-specific concerns (permissions, screen sizes)
- Adapting navigation patterns for mobile

---

## Troubleshooting Common Issues

### Flutter Doctor Shows Missing Dependencies
Run each failed check's suggested fix command. Most issues can be resolved by installing missing packages.

### Android Licenses Not Accepting
Make sure Android Studio is fully installed first, then try:
```bash
flutter doctor --android-licenses
```

### Linux Desktop Build Fails
Install the required dependencies:
```bash
sudo apt-get install clang cmake ninja-build pkg-config libgtk-3-dev
```

### Flutter Command Not Found
Make sure Flutter is in your PATH and you've reloaded your shell:
```bash
export PATH="$PATH:$HOME/development/flutter/bin"
source ~/.bashrc
```

---

## When You're Ready

Come back with the output of:
```bash
flutter doctor -v
```

And we'll start building the Flutter version of the dashcam manager!
