# Android Implementation Plan

## Overview
Port the Flutter dashcam manager app to Android mobile devices. The core Flutter code is already cross-platform compatible, but the UI layout and user experience need to be adapted for mobile screens.

## Current Status
- ✅ All core functionality implemented and working on Linux
- ✅ Flutter app structure is cross-platform ready
- ⚠️ UI layout is optimized for desktop (three-panel horizontal layout)
- ⚠️ No mobile-specific adaptations yet

## What Works Out of the Box
Since Flutter is cross-platform, these should work immediately on Android:
1. **Data Models** - VideoFile and DownloadTask (pure Dart)
2. **API Client** - DashcamAPI with HTTP communication
3. **State Management** - Provider-based AppState
4. **Download Manager** - Parallel downloads with progress tracking
5. **Preferences Service** - SharedPreferences works on Android
6. **Settings Dialog** - Already implemented

## Required Changes for Android

### 1. UI Layout Adaptation (CRITICAL)
**Current Issue:** Three-panel horizontal layout (200px + flexible + 300px) doesn't work on mobile screens

**Solution:** Implement responsive layout that adapts to screen size

#### Option A: Bottom Navigation
```
┌─────────────────────┐
│   App Bar           │
├─────────────────────┤
│                     │
│   Main Content      │
│   (varies by tab)   │
│                     │
├─────────────────────┤
│ [Videos|Queue|More] │ ← Bottom nav
└─────────────────────┘
```

#### Option B: Drawer + Tabs
```
┌─────────────────────┐
│ ☰ App Bar      ⚙️   │
├─────────────────────┤
│                     │
│   Video Grid        │
│   (full width)      │
│                     │
└─────────────────────┘
Drawer: Directories + Filters
Floating Action Button: Queue
```

#### Recommended Approach: **Bottom Navigation**
- Tab 1: **Browse** - Video grid + directory selector (dropdown)
- Tab 2: **Queue** - Download queue (full screen)
- Tab 3: **Settings** - Settings + filters

### 2. Network Permissions
**File:** `android/app/src/main/AndroidManifest.xml`

Add permissions:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="32" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />
```

For Android 13+, use:
```xml
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
```

### 3. Storage/Download Location
**Current:** `~/Videos/Dashcam` (Linux path)

**Android Options:**
1. **App-specific directory** (no permission needed):
   ```dart
   final appDir = await getApplicationDocumentsDirectory();
   // /data/data/com.example.dashcam_flutter/files/
   ```

2. **External storage** (requires permission):
   ```dart
   final downloadsDir = await getExternalStorageDirectory();
   // /storage/emulated/0/Android/data/com.example.dashcam_flutter/files/
   ```

3. **Public Downloads** (best for user access):
   ```dart
   Directory('/storage/emulated/0/Download/Dashcam')
   ```

**Recommendation:** Use public Downloads folder with proper permissions

### 4. WiFi Network Handling
**Challenge:** Android may disconnect from dashcam WiFi if it detects no internet

**Solutions:**
1. Add `android:networkSecurityConfig` in manifest
2. Request to keep WiFi connection even without internet
3. Use `ConnectivityManager` to monitor network state
4. Show user instructions for disabling mobile data during connection

### 5. File Picker Adaptation
**Current:** Uses `file_picker` package which should work on Android

**Test:** Verify directory picker works on Android (may need SAF - Storage Access Framework)

### 6. Thumbnail Image Loading
**Current:** Custom `ThumbnailImage` widget using API's `getThumbnail()`

**Should work on Android** - Pure Flutter implementation

### 7. Background Downloads
**Optional Enhancement:** Allow downloads to continue in background

**Implementation:**
- Use `flutter_background` or `workmanager` package
- Show persistent notification during downloads
- Handle Android 12+ foreground service restrictions

## Implementation Steps

### Phase 1: Basic Android Port (Priority: HIGH)
1. ✅ Verify Android build configuration
2. Create responsive layout wrapper
   - Detect screen size/orientation
   - Switch between desktop and mobile layouts
3. Implement mobile layout with bottom navigation
   - Browse tab: Video grid
   - Queue tab: Download queue
   - Settings tab: Filters + settings
4. Test on Android emulator
5. Fix any Android-specific issues

### Phase 2: Mobile UX Improvements (Priority: MEDIUM)
1. Add pull-to-refresh for video list
2. Implement swipe gestures (swipe to add to queue, swipe to delete from queue)
3. Add floating action button for quick actions
4. Optimize thumbnail size for mobile
5. Add loading indicators and error handling
6. Implement long-press for multi-select

### Phase 3: Android-Specific Features (Priority: LOW)
1. Background download support
2. Download notifications with progress
3. Share downloaded videos
4. Android Auto support (future)

## File Structure Changes

### New Files to Create
```
lib/
  ui/
    screens/
      mobile_main_screen.dart      # Mobile-specific layout
    widgets/
      responsive_layout.dart        # Screen size detection
      mobile_video_grid.dart        # Mobile-optimized grid
      mobile_download_queue.dart    # Mobile queue view
```

### Files to Modify
```
lib/
  main.dart                         # Add responsive wrapper
  services/
    preferences_service.dart        # Android-specific paths
  ui/
    screens/
      main_screen.dart              # Keep for desktop, wrap with responsive
```

## Testing Checklist

### Android Emulator Testing
- [ ] App launches successfully
- [ ] Can connect to dashcam WiFi (test with actual device)
- [ ] Video list loads and displays correctly
- [ ] Thumbnails load and display properly
- [ ] Downloads work and save to correct location
- [ ] Settings persist across app restarts
- [ ] File picker works for directory selection
- [ ] Navigation between tabs works smoothly
- [ ] Rotation works correctly

### Physical Device Testing (Required!)
- [ ] Connect to actual dashcam WiFi
- [ ] Verify download speeds
- [ ] Test with poor WiFi signal
- [ ] Test with low battery
- [ ] Test with interruptions (phone calls, etc.)
- [ ] Verify files are accessible from Files app

## Known Challenges

### 1. WiFi Connection Stability
**Problem:** Android may disconnect from dashcam WiFi if it detects no internet

**Workaround:**
- Show user dialog: "Disable mobile data during connection"
- Or use `NetworkRequest` to keep WiFi connected

### 2. Storage Permissions
**Problem:** Android 11+ restricts app access to external storage

**Solution:** Use scoped storage or app-specific directory

### 3. Large Downloads on Mobile
**Problem:** Downloads may fail if phone sleeps or app backgrounds

**Solution:**
- Show notification asking user to keep app open
- Or implement background download service (complex)

## Performance Considerations

### Mobile Optimizations
1. **Thumbnail Size:** Reduce thumbnail resolution for mobile
2. **Grid Layout:** Adjust grid column count based on screen size
3. **Lazy Loading:** Only load visible thumbnails
4. **Download Limits:** Default to 2 parallel downloads on mobile (vs 3 on desktop)
5. **Memory Management:** Clear thumbnail cache more aggressively

## Package Compatibility

### Already Android-Compatible
- ✅ `provider` - State management
- ✅ `http` - HTTP client
- ✅ `path_provider` - Cross-platform paths
- ✅ `shared_preferences` - Persistent storage
- ✅ `intl` - Internationalization
- ✅ `file_picker` - File/directory picker

### May Need Android-Specific Setup
- ⚠️ `cached_network_image` - We replaced this with custom widget
- ⚠️ Network permissions in manifest

## Success Criteria

### Minimum Viable Product (MVP)
1. ✅ App launches on Android
2. ✅ Can connect to dashcam WiFi
3. ✅ Can browse and view video thumbnails
4. ✅ Can download videos to phone storage
5. ✅ Mobile-optimized UI layout
6. ✅ Settings work correctly

### Nice to Have
- Background downloads
- Share downloaded videos
- Multi-select for bulk operations
- Search/filter by date
- Video playback preview

## Estimated Effort
- **Phase 1 (Basic Port):** 4-6 hours
- **Phase 2 (UX Polish):** 3-4 hours
- **Phase 3 (Advanced Features):** 6-8 hours

**Total:** ~13-18 hours for full Android implementation

## Next Steps
1. Create `flutter-android` branch
2. Implement responsive layout wrapper
3. Create mobile-specific main screen with bottom navigation
4. Test on Android emulator
5. Fix issues and optimize
6. Test on physical device with actual dashcam
