# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComicView is a Python-based image archive viewer for viewing images from ZIP, RAR, CBR and CBZ files. The application is built using PyQt5 and provides a fullscreen slideshow interface for browsing image archives, primarily designed for comic book reading and photo collection viewing.

## Project Structure

- `src/image_archive_viewer/` - Main package directory
  - `viewer.py` - Single-file application containing all functionality
  - `__init__.py` - Empty package initialization file
- `tests/` - Test suite directory
  - `fixtures/` - Test fixture files and creation scripts
  - `test_*.py` - Unit test modules
  - `conftest.py` - Shared test fixtures and configuration
- `pyproject.toml` - Project configuration, dependencies, and build settings
- `uv.lock` - Dependency lock file (managed by `uv`)

## Development Commands

### Installation and Setup
```bash
# Install in development mode using uv (preferred)
uv pip install -e .

# Install from PyPI
pip install image-archive-viewer

# Install as a uv tool for global access
uv tool install image-archive-viewer
```

### Running the Application
```bash
# Run the installed command (opens file dialog)
comic_view

# Run with verbose logging (logs to console and image_archive_viewer.log)
comic_view -v
```

### Testing
The project has a test suite configured for pytest in `pyproject.toml` with `pythonpath = "src"`:
```bash
# Run all automated tests (safe for CI/headless)
pytest

# Run tests with verbose output
pytest -v

# Run specific test module
pytest tests/test_archive_reader.py

# Generate test fixtures (creates ZIP/CBZ archives)
cd tests/fixtures && python create_test_fixtures.py
```

#### Test Structure
- **`test_basic.py`**: Package imports and fixture validation
- **`test_archive_reader.py`**: Archive reading functionality (ZIP/CBZ/RAR/CBR)
- **Fixtures**: Sample archives in `tests/fixtures/` (ZIP, CBZ, RAR formats)

### Building and Distribution
```bash
# Build package for distribution
python -m build

# Using uv
uv build
```

## Architecture

### Core Components

1. **main()** (`viewer.py:535-562`) - Application entry point that:
   - Parses command line arguments (`-v` for verbose logging)
   - Sets up logging configuration
   - Opens file selection dialog
   - Creates and shows the slideshow widget

2. **setup_logging()** (`viewer.py:19-34`) - Configures dual logging:
   - Console output to stdout
   - File output to `image_archive_viewer.log`
   - Adjustable log levels based on verbose flag

3. **read_images()** (`viewer.py:37-89`) - Generator function that:
   - Determines archive type by file extension
   - Opens ZIP/CBZ files with `zipfile.ZipFile`
   - Opens RAR/CBR files with `rarfile.RarFile`
   - Sorts files alphabetically by name
   - Filters for PNG/JPG/JPEG extensions only
   - Converts PIL images to QPixmap via QImage with RGB888 format
   - Handles corrupt images gracefully with error logging

4. **ArchiveImageSlideshow** (`viewer.py:91-533`) - Main Qt widget class with:
   - Fullscreen frameless window design
   - Three-layer UI: main image, help overlay, startup overlay
   - Complete zoom/pan system with mouse wheel and keyboard support
   - Progressive image loading for responsive startup

### Key Implementation Details

#### Image Processing Pipeline
- Archives opened with appropriate library based on extension
- Images converted: PIL → QImage (RGB888) → QPixmap
- All images cached in memory as QPixmap objects
- Alphabetical sorting of archive contents

#### Zoom and Pan System
- `zoom_factor`: 1.0 = fit to window, >1.0 = zoomed in, minimum 0.2
- `pan_offset`: [x, y] pixel offsets from center
- Keyboard zoom: 1.2x rate for +/- keys
- Mouse wheel zoom: 1.05x rate, centered on cursor position
- `adjust_pan_for_zoom()` keeps zoom centered on specific point
- Pan disabled when zoom_factor == 1.0

#### UI Overlay System
- **Main image**: QLabel with black canvas background
- **Help overlay**: Semi-transparent white with HTML formatted text
- **Startup overlay**: Semi-transparent black with loading messages
- Overlays positioned with `raise_()` for proper z-ordering
- Dynamic resizing handled in `resizeEvent()`

#### Event Handling Details
- **Keyboard**: 13 different key bindings including WASD pan controls
- **Mouse**: Left button drag for panning (only when zoomed)
- **Wheel**: Zoom in/out with cursor-centered scaling
- **Startup overlay**: Hidden on any key press or mouse click

#### Progressive Loading Strategy
1. First image loaded immediately in `load_images()`
2. Remaining images loaded via `QTimer.singleShot(0, self.load_remaining_images)`
3. Startup overlay message updated when loading completes
4. Error handling for `rarfile.BadRarFile` with user-friendly message

### Control Mappings

#### Navigation Controls
- Right Arrow / Space: `next_image()`
- Left Arrow: `previous_image()`
- Q / Escape: Close application

#### Zoom Controls  
- + / =: `zoom_in()` (1.2x rate)
- -: `zoom_out()` (1.2x rate)
- 0: `reset_zoom()` (fit to window)
- Mouse wheel: zoom with 1.05x rate, cursor-centered

#### Pan Controls
- W: Pan down (50px)
- S: Pan up (50px)  
- A: Pan right (50px)
- D: Pan left (50px)
- Mouse drag: Real-time panning when zoomed

#### Other Controls
- H: Toggle help overlay
- O: Open new archive file dialog

### Dependencies and Requirements

- **PyQt5**: Complete GUI framework
- **Pillow**: Image processing (PIL.Image)
- **rarfile**: RAR/CBR archive support
- **External**: `unrar` command-line tool required for RAR files
- **Python**: 3.8+ (defined in pyproject.toml)

### Error Handling Patterns

- Graceful degradation for corrupt/unreadable images
- Specific error message for missing `unrar` dependency
- Comprehensive logging with debug info when verbose mode enabled
- Safe painter cleanup in `show_image()` method
- Empty archive handling with user feedback

### Memory Management

- All images cached as QPixmap objects in `self.images` list
- Images cleared in `closeEvent()` for proper cleanup
- No lazy loading - all archive images loaded into memory
- Canvas pixmap recreated on each `show_image()` call

## Development Notes

- Single-file architecture - all functionality in `viewer.py`
- Test suite with fixtures for all archive formats
- Frameless fullscreen window with manual overlay positioning
- Progressive loading prevents UI freezing on large archives
- Dual logging system supports both development and user debugging
- Comic book oriented (CBR/CBZ support) but works for any image archives