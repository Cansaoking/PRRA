# Cache Management Feature

## Overview

Added comprehensive cache management to clean AI models, temporary files, and Python cache when closing the application or on demand.

## Problem Statement

User requested (Comment #3745606445): "Habría que implementar que al cerrar la aplicación se borrara todo el cache y los archivos temporales" (Need to implement that when closing the application, all cache and temporary files are deleted).

## Solution

Implemented a complete cache management system with automatic and manual cleanup options.

## Implementation

### 1. Cache Manager Module (`src/cache_manager.py`)

New module with `CacheManager` class providing:

#### Core Methods

**`get_cache_directories()`**
- Finds HuggingFace and Torch cache directories
- Returns list of Path objects
- Typically: `~/.cache/huggingface`, `~/.cache/torch`

**`get_pycache_directories(base_path)`**
- Recursively finds all `__pycache__` directories
- Scans from application base path
- Returns list of all Python cache dirs

**`calculate_cache_size(directories)`**
- Calculates total size of cache directories
- Returns size in bytes
- Handles file access errors gracefully

**`format_size(size_bytes)`**
- Formats bytes to human-readable format
- Examples: "1.5 GB", "245 MB", "7.3 KB"
- Uses appropriate unit (B, KB, MB, GB, TB, PB)

**`clean_cache(clean_models, clean_pycache, base_path)`**
- Main cleanup function
- Parameters:
  - `clean_models`: Remove AI model caches
  - `clean_pycache`: Remove Python cache files
  - `base_path`: Base path for finding __pycache__
- Returns dict with results:
  - `success`: Overall success status
  - `errors`: List of error messages
  - `cleaned`: List of cleaned paths
  - `size_freed`: Total bytes freed

**`get_cache_info(base_path)`**
- Returns detailed cache information
- Structure:
  - `model_cache`: List of model cache items
  - `pycache`: List of __pycache__ items
  - `total_size`: Total size in bytes
  - `total_size_str`: Formatted size string

### 2. UI Integration (`src/ui_main.py`)

#### Configuration Tab Options

**Checkbox: "Clean cache on exit"**
```python
self.clean_cache_checkbox = QCheckBox("Clean cache on exit (models, temporary files)")
```
- Tooltip: "Automatically remove downloaded models and temporary files when closing"
- Default: Unchecked (user must opt-in)
- Saved preference for user control

**Button: "🗑️ Clean Cache Now..."**
```python
btn_clean_cache = QPushButton("🗑️ Clean Cache Now...")
btn_clean_cache.clicked.connect(self.clean_cache_now)
```
- Manual cleanup without closing application
- Shows cache size before cleaning
- Confirms action with detailed dialog
- Reports results after cleanup

**Button: "📊 View Cache Info"**
```python
btn_view_cache = QPushButton("📊 View Cache Info")
btn_view_cache.clicked.connect(self.view_cache_info)
```
- Shows current cache usage
- Lists all cache directories
- Displays sizes for each category
- Non-destructive information view

#### Close Event Handler

**`closeEvent(event)`**
Enhanced application close handling:

1. **Worker Check**: 
   - If review in progress, confirms exit
   - Stops worker gracefully

2. **Cache Cleanup** (if enabled):
   - Confirms with user
   - Shows what will be cleaned
   - Displays estimated space to free
   - Shows progress indicator
   - Reports results (size freed, items cleaned)

3. **Error Handling**:
   - Graceful failure handling
   - Partial cleanup reports
   - User feedback on errors

#### Handler Methods

**`view_cache_info()`**
- Retrieves cache information
- Formats display message
- Shows in information dialog
- Categories:
  - AI Models Cache (HuggingFace, Torch)
  - Python Cache (__pycache__)
  - Total size

**`clean_cache_now()`**
- Gets current cache info
- Confirms with detailed dialog
- Shows progress during cleanup
- Reports results with size freed
- Logs to application log
- Handles errors gracefully

## User Experience

### Automatic Cleanup on Exit

**Workflow:**
1. User enables "Clean cache on exit" checkbox
2. User works with application normally
3. On close, dialog appears:
   ```
   Do you want to clean all cache and temporary files?
   
   This will remove:
   - Downloaded AI models (will need to re-download next time)
   - Python cache files (__pycache__)
   - Torch/HuggingFace cache
   
   This may free up several GB of disk space.
   ```
4. User confirms (Yes/No)
5. If Yes:
   - Progress indicator shows
   - Cache cleaned in background
   - Results dialog: "Successfully cleaned cache! Space freed: 2.3 GB"
6. Application closes

### Manual Cleanup

**Workflow:**
1. User clicks "🗑️ Clean Cache Now..."
2. Dialog shows current cache info:
   ```
   This will remove all cache and temporary files.
   
   Current cache size: 2.3 GB
   
   Items to clean:
   - AI models (HuggingFace/Torch): 2 directories
   - Python cache files: 15 directories
   
   Warning: Downloaded AI models will need to be re-downloaded.
   
   Continue?
   ```
3. User confirms
4. Progress dialog: "Cleaning cache and temporary files..."
5. Results dialog: "Successfully cleaned cache! Space freed: 2.3 GB, Items cleaned: 17"
6. Application continues running

### View Cache Info

**Workflow:**
1. User clicks "📊 View Cache Info"
2. Dialog displays:
   ```
   Total Cache Size: 2.3 GB
   
   AI Models Cache:
     • /home/user/.cache/huggingface
       Size: 2.1 GB
     • /home/user/.cache/torch
       Size: 150 MB
   
   Python Cache (__pycache__):
     • 15 directories
     • Total size: 7.3 KB
   ```
3. User reviews information
4. No action taken, dialog closes

## What Gets Cleaned

### AI Model Caches
- **HuggingFace Models**: `~/.cache/huggingface`
  - Downloaded transformer models
  - Tokenizers
  - Model weights
  - Typically 1-3 GB per model

- **Torch Cache**: `~/.cache/torch`
  - PyTorch hub models
  - JIT compiled modules
  - Typically 100-500 MB

### Python Cache
- **__pycache__** directories
  - Compiled Python bytecode (.pyc files)
  - Found throughout application
  - Typically KB-MB total
  - Automatically recreated on next run

## Benefits

1. **Disk Space Management**
   - Free up several GB when models not needed
   - Useful for systems with limited storage
   - Clean between different model experiments

2. **Fresh Start**
   - Remove potentially corrupted cache
   - Force re-download of latest model versions
   - Clean slate for troubleshooting

3. **User Control**
   - Optional feature (opt-in)
   - Manual cleanup available anytime
   - View before cleaning
   - Informed decisions with size info

4. **Privacy**
   - Remove downloaded models
   - Clear temporary data
   - Clean system footprint

## Safety Features

1. **Confirmation Dialogs**
   - Always confirms before cleaning
   - Shows what will be removed
   - Warns about re-download requirement

2. **Error Handling**
   - Graceful failure on locked files
   - Continues on partial errors
   - Reports what succeeded/failed

3. **User Information**
   - Shows size before and after
   - Lists cleaned items
   - Progress indicators
   - Clear messaging

4. **Non-Destructive Options**
   - View info doesn't modify anything
   - Can cancel at any time
   - Application data never touched

## Technical Details

### Directory Scanning
```python
# Finds all cache directories recursively
for root, dirs, files in os.walk(base_path):
    if '__pycache__' in dirs:
        pycache_dirs.append(Path(root) / '__pycache__')
```

### Safe Deletion
```python
try:
    shutil.rmtree(cache_dir)  # Removes directory tree
    results['cleaned'].append(str(cache_dir))
except Exception as e:
    results['errors'].append(f"Error: {str(e)}")
    # Continue with other directories
```

### Size Calculation
```python
total_size = 0
for root, dirs, files in os.walk(directory):
    for file in files:
        try:
            file_path = Path(root) / file
            total_size += file_path.stat().st_size
        except (OSError, FileNotFoundError):
            continue  # Skip inaccessible files
```

## Testing

Tested scenarios:
- ✅ Get cache info with no cache
- ✅ Get cache info with existing cache
- ✅ Clean cache successfully
- ✅ Handle errors during cleanup
- ✅ Format sizes correctly (B, KB, MB, GB)
- ✅ Cancel cleanup operations
- ✅ Application close with cleanup enabled
- ✅ Application close with cleanup disabled

## Future Enhancements (Out of Scope)

- Scheduled cleanup (e.g., clean weekly)
- Selective model cleanup (keep specific models)
- Cache size warnings/notifications
- Automatic cleanup on low disk space
- Cleanup statistics/history

## Conclusion

This feature provides users with complete control over cache management, addressing the need to clean downloaded models and temporary files. The implementation is safe, user-friendly, and provides clear information at every step.

**Commit**: 9cf7fb9
**Files Created**: 1 (cache_manager.py)
**Files Modified**: 2 (ui_main.py, README.md)
**Lines Added**: ~445
**Features**: 3 (auto cleanup, manual cleanup, view info)
