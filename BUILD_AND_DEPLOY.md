# Dashcam Manager - Build and Deployment Guide

This guide covers building and running release versions of the Dashcam Manager application across all supported platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Python GTK Application](#python-gtk-application)
- [Flutter Linux Application](#flutter-linux-application)
- [Flutter Android Application](#flutter-android-application)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Python Application
- Python 3.8 or higher
- pip (Python package manager)
- GTK 3.0 or higher (usually pre-installed on Linux)

### Flutter Applications
- Flutter SDK 3.0 or higher
- For Linux: GTK development libraries
- For Android: Android SDK, JDK 11 or higher
- Git (for version control)

## Python GTK Application

### Installation

1. **Navigate to the Python application directory:**
   ```bash
   cd dashcam_python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or install individually:
   ```bash
   pip install requests pygobject pillow
   ```

### Running the Application

**Development mode:**
```bash
python dashcam.py
```

**Production mode:**
```bash
python3 dashcam.py
```

### Creating a Desktop Launcher (Linux)

1. **Create a desktop entry file:**
   ```bash
   cat > ~/.local/share/applications/dashcam-manager.desktop <<EOF
   [Desktop Entry]
   Name=Dashcam Manager
   Comment=Manage and download dashcam videos
   Exec=python3 /path/to/dashcam_python/dashcam.py
   Icon=/path/to/dashcam_python/icon.png
   Terminal=false
   Type=Application
   Categories=Utility;Video;
   EOF
   ```

2. **Make the launcher executable:**
   ```bash
   chmod +x ~/.local/share/applications/dashcam-manager.desktop
   ```

### Packaging as Standalone Executable

**Using PyInstaller:**

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Create executable:**
   ```bash
   pyinstaller --onefile --windowed --name="Dashcam Manager" dashcam.py
   ```

3. **The executable will be in `dist/Dashcam Manager`**

## Flutter Linux Application

### Prerequisites for Linux Build

1. **Install Flutter dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y clang cmake ninja-build pkg-config libgtk-3-dev
   ```

2. **Enable Linux desktop support:**
   ```bash
   flutter config --enable-linux-desktop
   ```

### Building Release Version

1. **Navigate to Flutter project:**
   ```bash
   cd dashcam_flutter
   ```

2. **Get dependencies:**
   ```bash
   flutter pub get
   ```

3. **Build release version:**
   ```bash
   flutter build linux --release
   ```

4. **The release build will be in:**
   ```
   build/linux/x64/release/bundle/
   ```

### Running the Linux Application

**Development mode:**
```bash
flutter run -d linux
```

**Release build:**
```bash
./build/linux/x64/release/bundle/dashcam_flutter
```

### Creating an AppImage (Portable Linux Application)

1. **Install appimage-builder:**
   ```bash
   sudo apt-get install appimage-builder
   ```

2. **Create AppImage configuration (appimage.yml):**
   ```yaml
   version: 1
   AppDir:
     path: ./AppDir
     app_info:
       id: com.example.dashcam_flutter
       name: Dashcam Manager
       icon: dashcam_flutter
       version: 1.0.0
       exec: usr/bin/dashcam_flutter
     files:
       include:
         - build/linux/x64/release/bundle/*
   ```

3. **Build AppImage:**
   ```bash
   appimage-builder --recipe appimage.yml
   ```

### Creating a .deb Package

1. **Install packaging tools:**
   ```bash
   sudo apt-get install dpkg-dev
   ```

2. **Create package structure:**
   ```bash
   mkdir -p debian-package/DEBIAN
   mkdir -p debian-package/usr/bin
   mkdir -p debian-package/usr/share/applications
   mkdir -p debian-package/usr/share/icons/hicolor/256x256/apps
   ```

3. **Copy files:**
   ```bash
   cp -r build/linux/x64/release/bundle/* debian-package/usr/bin/
   ```

4. **Create control file (debian-package/DEBIAN/control):**
   ```
   Package: dashcam-manager
   Version: 1.0.0
   Section: utils
   Priority: optional
   Architecture: amd64
   Maintainer: Your Name <your.email@example.com>
   Description: Dashcam video management application
    Manage and download videos from your dashcam device.
   ```

5. **Build package:**
   ```bash
   dpkg-deb --build debian-package dashcam-manager_1.0.0_amd64.deb
   ```

6. **Install package:**
   ```bash
   sudo dpkg -i dashcam-manager_1.0.0_amd64.deb
   ```

## Flutter Android Application

### Prerequisites for Android Build

1. **Install Android Studio** or **Android SDK command-line tools**

2. **Set up environment variables:**
   ```bash
   export ANDROID_HOME=$HOME/Android/Sdk
   export PATH=$PATH:$ANDROID_HOME/tools
   export PATH=$PATH:$ANDROID_HOME/platform-tools
   ```

3. **Accept Android licenses:**
   ```bash
   flutter doctor --android-licenses
   ```

### Building Release APK

1. **Navigate to Flutter project:**
   ```bash
   cd dashcam_flutter
   ```

2. **Get dependencies:**
   ```bash
   flutter pub get
   ```

3. **Build release APK:**
   ```bash
   flutter build apk --release
   ```

4. **The APK will be at:**
   ```
   build/app/outputs/flutter-apk/app-release.apk
   ```

### Building Release App Bundle (For Google Play)

1. **Build app bundle:**
   ```bash
   flutter build appbundle --release
   ```

2. **The bundle will be at:**
   ```
   build/app/outputs/bundle/release/app-release.aab
   ```

### Building Split APKs (Optimized for Different Architectures)

```bash
flutter build apk --release --split-per-abi
```

This creates separate APKs for:
- `app-armeabi-v7a-release.apk` (32-bit ARM)
- `app-arm64-v8a-release.apk` (64-bit ARM)
- `app-x86_64-release.apk` (64-bit Intel/AMD)

### Installing Release APK on Device

**Via USB (ADB):**
```bash
# Connect device via USB and enable USB debugging
adb install build/app/outputs/flutter-apk/app-release.apk
```

**Via file transfer:**
1. Copy `app-release.apk` to device storage
2. Open file on device with file manager
3. Allow installation from unknown sources if prompted
4. Tap "Install"

### Signing the Android App (Required for Distribution)

1. **Generate signing key:**
   ```bash
   keytool -genkey -v -keystore ~/dashcam-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias dashcam
   ```

2. **Create key.properties file in `android/` directory:**
   ```properties
   storePassword=<password from previous step>
   keyPassword=<password from previous step>
   keyAlias=dashcam
   storeFile=/home/username/dashcam-release-key.jks
   ```

3. **Update `android/app/build.gradle`:**
   ```gradle
   def keystoreProperties = new Properties()
   def keystorePropertiesFile = rootProject.file('key.properties')
   if (keystorePropertiesFile.exists()) {
       keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
   }

   android {
       ...
       signingConfigs {
           release {
               keyAlias keystoreProperties['keyAlias']
               keyPassword keystoreProperties['keyPassword']
               storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
               storePassword keystoreProperties['storePassword']
           }
       }
       buildTypes {
           release {
               signingConfig signingConfigs.release
           }
       }
   }
   ```

4. **Build signed APK:**
   ```bash
   flutter build apk --release
   ```

### Running on Android Device

**Development mode (debug):**
```bash
# Connect device via USB
flutter run
```

**Release mode testing:**
```bash
flutter run --release
```

## Troubleshooting

### Python Application

**Issue: GTK not found**
```bash
# Ubuntu/Debian
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Fedora
sudo dnf install python3-gobject gtk3
```

**Issue: Import errors**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Flutter Linux

**Issue: Missing libraries**
```bash
sudo apt-get install libgtk-3-dev libblkid-dev liblzma-dev
```

**Issue: Build fails**
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter build linux --release
```

### Flutter Android

**Issue: License not accepted**
```bash
flutter doctor --android-licenses
```

**Issue: Build fails with Gradle error**
```bash
# Clean build
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
flutter build apk --release
```

**Issue: App requires permissions**

The app requires the following permissions on Android:
- Location (for WiFi scanning on Android 8+)
- Nearby WiFi devices (Android 13+)
- Internet and Network access

These are automatically requested when needed.

**Issue: Cannot connect to dashcam**

1. Manually connect to dashcam WiFi network first (SSID: `Dashcam_A79500`)
2. Verify dashcam IP is `192.168.0.1`
3. Check that auto WiFi switch is disabled in settings (default)
4. Try enabling auto WiFi switch in settings if manual connection doesn't work

### General Issues

**Issue: Videos not downloading**
- Check storage permissions
- Verify download directory has write access
- Check WiFi connection to dashcam
- Reduce max parallel downloads in settings

**Issue: Thumbnails not displaying**
- Ensure connected to dashcam
- Check network connectivity
- Try reloading the directory

## Distribution Checklist

### Before Release Build

- [ ] Update version number in `pubspec.yaml` (Flutter) or version constant (Python)
- [ ] Test all core functionality
- [ ] Update README.md with latest changes
- [ ] Review and update permissions in AndroidManifest.xml
- [ ] Test on target devices/platforms
- [ ] Create signed builds (Android)
- [ ] Document known issues

### Release Build Steps

1. **Python**: Create executable or package as needed
2. **Flutter Linux**: Build release bundle and create AppImage/deb
3. **Flutter Android**: Build signed APK and/or App Bundle
4. **Test**: Install and test release builds on clean devices
5. **Document**: Update changelog and version notes
6. **Distribute**: Upload to distribution channels

## Version Information

- **Python GTK**: Desktop application for Linux
- **Flutter Linux**: Native Linux application (desktop)
- **Flutter Android**: Mobile application for Android 8.0+

All versions support:
- Browsing dashcam videos by directory
- Filtering by camera (front/back) and type (normal/emergency)
- Parallel downloads with progress tracking
- Configurable download settings
- WiFi management (Android only)

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

Settings can be configured through the Settings dialog in the application:
- Download directory location
- Maximum parallel downloads (1-5)
- Auto WiFi switching (Android only)
- Camera settings (when connected to dashcam)

## Support

For issues, bugs, or feature requests, please refer to the project repository or contact the maintainer.
