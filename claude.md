# Dashcam Manager Project Setup

## Quick Start for Claude CLI

This project builds a dashcam video management application. Start with Linux desktop, then a flutter app, then port to Flutter mobile.

---

## Development Workflow (IMPORTANT)

### Branch Management
**CRITICAL: ALWAYS create a new branch BEFORE starting ANY work.**

```bash
# FIRST: Create and switch to a new feature branch
git checkout -b feature/your-feature-name

# Work on your changes...

# When ready to merge
git checkout master
git merge feature/your-feature-name
git branch -d feature/your-feature-name  # Clean up
git push origin master
```

**NEVER commit directly to master. EVER.**

This includes:
- ❌ New features
- ❌ Dependency updates
- ❌ Bug fixes
- ❌ Refactoring
- ❌ Code cleanup
- ❌ ANY code changes

**Only exception:** Documentation-only changes (README, comments, markdown files with no code impact)

**Why this is critical:**
- Allows testing in isolation
- Easy to revert if something breaks
- Clean git history
- Follows professional workflow
- Makes code review possible

**If you forget and commit to master:**
1. Stop immediately
2. Create a branch from current commit
3. Reset master to previous state
4. Merge the branch properly

### Pre-Push Build Verification
**Before pushing to GitHub, verify all applications build successfully.**

Use git worktrees to test builds in isolation without affecting your working directory:

```bash
# Create a worktree from current branch for testing
git worktree add ../dashcam-test-build

# Navigate to the worktree
cd ../dashcam-test-build

# Test Python application
cd dashcam_python
pip install -r requirements.txt
python3 src/ui/main_window.py --help  # Quick validation

# Test Flutter builds
cd ../dashcam_flutter
./buildall.sh  # Builds both Linux and Android

# If all builds pass, return to main directory
cd ../../dashcam

# Clean up the worktree
git worktree remove ../dashcam-test-build

# Now safe to push
git push origin your-branch-name
```

**Why use worktrees?**
- Isolated testing environment
- Doesn't affect your working directory
- Can test multiple branches simultaneously
- Catches missing files before they reach GitHub
- Ensures fresh clones will build successfully

**Build verification checklist:**
- [ ] Python app runs without import errors
- [ ] Flutter Linux builds successfully
- [ ] Flutter Android APK builds successfully
- [ ] All source files are tracked in git
- [ ] No build artifacts committed

---

## Project Context

**What we have**:
- ✅ Working Python API client (`dashcam_api.py`) - reverse-engineered from PCAP
- ✅ Complete design document (`claude.md`)
- ✅ Dashcam device specs and API endpoints documented

**What we're building**:
- Phase 1: Linux desktop app (GTK4 or Qt) for video browsing and downloading
- Phase 2: Linux Flutter app
- Phase 3: Flutter mobile app for Android/iOS

**Current priority**: Build Linux desktop prototype

---

## File Structure

```
dashcam-manager/
├── claude.md                    # Main design document (READ THIS FIRST)
├── README.md                    # Project overview
├── docs/
│   ├── api-reference.md        # Dashcam API endpoints
│   ├── pcap-analysis.md        # Original PCAP findings
│   └── device-info.md          # Hardware specs
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py           # DashcamAPI class (DONE)
│   │   ├── models.py           # Data models (TODO)
│   │   └── exceptions.py       # Custom exceptions (TODO)
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main app window (TODO)
│   │   ├── video_grid.py       # Thumbnail browser (TODO)
│   │   ├── download_panel.py   # Download manager (TODO)
│   │   ├── settings_panel.py   # Settings UI (TODO)
│   │   └── video_player.py     # Video playback (TODO)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── download_manager.py # Download orchestration (TODO)
│   │   ├── cache_manager.py    # Thumbnail caching (TODO)
│   │   └── connection_manager.py # WiFi handling (TODO)
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # App config (TODO)
│       └── logging_setup.py    # Logging (TODO)
├── tests/
│   ├── test_api.py
│   ├── test_download_manager.py
│   └── test_models.py
├── resources/
│   └── icons/
├── requirements.txt
└── setup.py
```

---

## Technology Decisions

### Phase 1: Linux Desktop
**UI Framework**: GTK4 (decided - native Linux look, good performance)
**Language**: Python 3.11+
**Key Libraries**:
- `requests` - HTTP client with session pooling
- `PyGObject` - GTK4 bindings
- `Pillow` - Image processing
- `python-vlc` - Video playback

### Why GTK4?
- Native look on Linux (target platform)
- Excellent grid/list performance
- Built-in video support via GStreamer
- Good Python bindings (PyGObject)

### Alternative Considered: Qt
- Rejected for now (overkill for Linux-only prototype)
- May reconsider if we need Windows/Mac later

---

## Development Priorities

### Sprint 1: Foundation (Week 1)
1. ✅ API client (done)
2. Set up project structure
3. Data models (VideoFile, DownloadTask)
4. Basic GTK4 window with placeholder UI
5. Connection manager (find dashcam, test connectivity)

### Sprint 2: Video Browser (Week 2)
1. Thumbnail grid view
2. Cache manager for thumbnails
3. Load and display videos from dashcam
4. Basic navigation (front/back camera, date filters)

### Sprint 3: Downloads (Week 3)
1. Download manager service
2. Download queue UI with progress bars
3. Parallel download support
4. Pause/resume functionality

### Sprint 4: Polish (Week 4)
1. Settings panel (camera config)
2. Video playback
3. Error handling and reconnection
4. Performance optimization
5. Testing and bug fixes

---

## Key Implementation Details

### API Client (Already Done ✅)
Located in `dashcam_api.py` - this is production-ready.

**Key features**:
- HTTP keep-alive for speed (10-30 Mbps vs 1.2 Mbps without it)
- Parallel downloads (2-5x speedup)
- Streaming for large files
- All API endpoints mapped

**Usage**:
```python
from dashcam_api import DashcamAPI

api = DashcamAPI("http://192.168.0.1", keep_alive=True)
api.register_client()

# Get video list
files = api.get_dir_file_list_parsed("norm", 0, 100)

# Download with progress
api.download_directory("norm", "./videos", parallel=3)
```

### Data Models (TODO - High Priority)
```python
@dataclass
class VideoFile:
    path: str
    filename: str
    timestamp: datetime
    size_mb: Optional[float] = None
    duration: Optional[int] = None
    camera: str = "front"  # front, back
    type: str = "normal"   # normal, emergency, parking
    
    @classmethod
    def from_filename(cls, path: str):
        """Parse: sd//norm/2025_10_12_220337_00.TS"""
        # Parse year, month, day, time from filename
        pass

@dataclass
class DownloadTask:
    file: VideoFile
    status: str  # queued, downloading, completed, failed
    progress: float = 0.0
    speed_mbps: float = 0.0
```

### GTK4 Main Window (TODO - Next Priority)
```python
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio

class DashcamApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id='com.example.dashcam',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.api = None
        
    def do_activate(self):
        window = MainWindow(application=self)
        window.present()

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Dashcam Manager")
        self.set_default_size(1200, 800)
        
        # Build UI
        self.setup_ui()
        
    def setup_ui(self):
        # Header bar with connection status
        # Left sidebar: directory tree
        # Center: thumbnail grid
        # Right sidebar: download queue
        # Bottom: status bar
        pass
```

---

## Important Constraints

### Network Performance
- **Must use HTTP keep-alive** - reuse connections
- Parallel downloads: 2-3 connections optimal for WiFi
- Large files: stream in chunks (don't load into memory)
- Expected speed: 10-30 Mbps on good WiFi

### Dashcam API Quirks
1. Must call `register_client()` before other operations
2. Must `stop` recording and `ENTER_PLAYBACK` mode to browse files
3. File paths use `sd//` prefix (double slash)
4. Some settings return `SvrFuncResult="-2222"` (unsupported)
5. Session ID is always "null" (ignored by dashcam)

### File Formats
- Videos: `.TS` (MPEG-TS, H.264 + AAC)
- Thumbnails: `.THM` (JPEG, same filename)
- GPS data: `.TXT` (same filename)
- Naming: `YYYY_MM_DD_HHMMSS_XX.TS`

---

## Testing Strategy

### Manual Testing
Connect actual dashcam and verify:
1. Discovery and connection
2. List videos from multiple directories
3. Download single video
4. Download multiple videos in parallel
5. Thumbnail caching
6. Playback downloaded videos

### Unit Tests
Mock API responses for offline testing:
```python
@pytest.fixture
def mock_api():
    with requests_mock.Mocker() as m:
        m.get('http://192.168.0.1/cgi-bin/hisnet/getwifi.cgi',
              text='var wifissid="Dashcam_A79500";')
        yield m

def test_parse_file_list(mock_api):
    api = DashcamAPI()
    files = api.get_dir_file_list_parsed("norm", 0, 10)
    assert len(files) > 0
```

---

## Dependencies

### Python Requirements
```txt
# requirements.txt
requests>=2.31.0
PyGObject>=3.46.0
Pillow>=10.0.0
python-vlc>=3.0.0
pytest>=7.4.0
requests-mock>=1.11.0
```

### System Requirements (Linux)
```bash
# Ubuntu/Debian
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 \
                 libgirepository1.0-dev libcairo2-dev \
                 gstreamer1.0-plugins-good

# Fedora
sudo dnf install python3-gobject gtk4 gtk4-devel
```

---

## Common Tasks for Claude CLI

When using Claude CLI, you can ask for help with:

### Setting Up Components
```bash
# Example commands you might use:
claude "Create the VideoFile and DownloadTask data models in src/api/models.py"
claude "Implement the CacheManager class in src/services/cache_manager.py"
claude "Build the main GTK4 window with header bar and grid layout"
```

### Implementing Features
```bash
claude "Add thumbnail grid view that loads from API and caches locally"
claude "Create download manager with queue, progress tracking, and parallel downloads"
claude "Implement settings panel that maps to API parameters"
```

### Debugging
```bash
claude "Why are my downloads slow? Check if keep-alive is working"
claude "Fix the thumbnail caching - images aren't persisting between runs"
claude "Handle connection errors gracefully when WiFi drops"
```

### Testing
```bash
claude "Write unit tests for VideoFile.from_filename() parsing"
claude "Create integration test for download manager with mocked API"
claude "Add pytest fixtures for common test scenarios"
```

---

## Device Information

**Dashcam Model**: HI3516CV610-S-FV-CARRECORDER
**Product**: LEISA_197
**Firmware**: 1.0.3.6.202E0627
**Manufacturer**: HUIYING
**WiFi**: Dashcam_A79500 (192.168.0.1)

**Capabilities**:
- Dual camera (front + rear)
- 4K recording
- GPS data logging
- G-sensor (collision detection)
- Parking mode
- Loop recording (1/3/5 minute segments)

**Storage**:
- SD card: 59.9 GB total, 18.8 GB free (from PCAP)
- Directories: norm, emr, back_norm, back_emr, photo, back_photo, GPSdata

---

## Next Steps

1. **Immediate**: Create project structure and data models
2. **This week**: Build basic GTK4 UI with connection manager
3. **Next week**: Implement video browser with thumbnail grid
4. **Following**: Add download manager with progress tracking

---

## Questions to Answer

As you work, consider:
- [ ] How should we handle network disconnections during downloads?
- [ ] What's the best way to organize cached thumbnails? (filesystem vs SQLite)
- [ ] Should we implement video playback in-app or launch external player?
- [ ] How much metadata should we cache? (duration, size, etc.)
- [ ] What's the UX for switching between front/back camera views?

---

## Resources

- **claude.md**: Complete design document and architecture
- **dashcam_api.py**: Working API client (reference implementation)
- **GTK4 Docs**: https://docs.gtk.org/gtk4/
- **PyGObject Tutorial**: https://pygobject.readthedocs.io/

---

## Success Criteria

The Linux prototype is done when:
- ✅ Connects to dashcam automatically
- ✅ Displays thumbnail grid of all videos
- ✅ Downloads videos with progress bar (>15 Mbps)
- ✅ Caches thumbnails for offline browsing
- ✅ Allows video playback
- ✅ Configures basic camera settings
- ✅ Handles connection errors gracefully

Then we're ready to port to Flutter! 🚀