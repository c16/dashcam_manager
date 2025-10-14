# Known Issues

## Sprint 2 - Video Browser

### ~~Issue: Thumbnails fail to load after switching to empty directories~~ [RESOLVED]

**Status:** ✅ FIXED

**Root Cause:**
The dashcam API returns error codes (`SvrFuncResult="-2222"` and `SvrFuncResult="-1"`) when calling `get_dir_file_list_parsed()` if the device is not in the correct state. After multiple directory switches, especially involving empty directories or rapid switching, the API state becomes corrupted and all subsequent directory list requests fail.

**Solution:**
Call `work_mode_cmd('stop')` before each directory load in `_load_directory_async()` to ensure the dashcam API is always in the correct state to return file lists.

**Implementation:**
Modified `src/ui/main_window.py` in the `_load_directory_async()` method (lines 407-411):
```python
# Stop recording before each directory load to ensure API is in correct state
try:
    api.work_mode_cmd('stop')
except Exception as e:
    logger.warning(f"Failed to stop recording before directory load: {e}")
```

**Test Results:**
- ✅ All directories now load consistently with correct file counts
- ✅ No more error responses from the API
- ✅ Works correctly after switching between directories multiple times
- ✅ Works correctly after disconnect/reconnect cycles
- ✅ Empty directories are handled correctly

**Original Symptoms:**
- Load a directory with videos (e.g., "Normal Videos") - thumbnails load fine
- Switch to a directory with no videos (e.g., "Back Camera" when empty)
- Switch back to the original directory with videos
- Thumbnails fail to load or show errors

**Date Resolved:** 2025-10-14
