# Testing Guide for ComicView

This directory contains the test suite for the ComicView image archive viewer.

## Test Structure

### Automated Tests (Safe to run in CI/headless)
- `test_basic.py` - Basic package imports and fixture validation
- `test_archive_reader.py` - Archive reading functionality (ZIP/CBZ/RAR/CBR handling)

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage Report
```bash
pytest --cov-report=html
```

### Run Specific Test Files
```bash
# Test archive reading functionality
pytest tests/test_archive_reader.py

# Test basic functionality
pytest tests/test_basic.py
```

## Coverage Reports

After running tests with coverage, reports are generated in:
- `htmlcov/index.html` - Interactive HTML coverage report
- Terminal output shows coverage summary
- `coverage.xml` - XML format for CI systems

## Manual Testing

For GUI functionality that cannot be easily automated:

1. **Application Startup**
   ```bash
   comic_view
   ```
   - Test file dialog opens
   - Select an image archive (ZIP/RAR/CBZ/CBR)
   - Verify fullscreen slideshow starts

2. **Keyboard Controls**
   - Arrow keys for navigation
   - +/- for zoom
   - WASD for panning
   - H for help overlay
   - O for opening new file
   - Q/Escape to quit

3. **Mouse Controls**
   - Mouse wheel for zooming
   - Click and drag for panning when zoomed
   - Click to dismiss startup overlay

4. **Error Handling**
   - Try opening corrupted archives
   - Test with archives containing no images
   - Test RAR files without `unrar` installed

## Troubleshooting

### RAR File Tests
RAR/CBR tests may fail if `unrar` is not installed:
```bash
# macOS
brew install unrar

# Ubuntu/Debian
sudo apt-get install unrar

```
