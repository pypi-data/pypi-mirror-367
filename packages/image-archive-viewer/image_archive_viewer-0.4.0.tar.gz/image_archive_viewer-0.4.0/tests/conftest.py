"""
Shared test fixtures and configuration for pytest.
"""

import os
import sys
import pytest
import tempfile
import zipfile
from unittest.mock import Mock, patch
from PIL import Image
import io
import logging

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def test_fixtures_dir():
    """Return the path to the test fixtures directory."""
    return os.path.join(os.path.dirname(__file__), 'fixtures')

@pytest.fixture
def test_archive_zip(test_fixtures_dir):
    """Return path to the test ZIP archive with images."""
    return os.path.join(test_fixtures_dir, 'test_archive.zip')

@pytest.fixture
def empty_archive_zip(test_fixtures_dir):
    """Return path to an empty ZIP archive."""
    return os.path.join(test_fixtures_dir, 'empty_archive.zip')

@pytest.fixture
def no_images_archive_zip(test_fixtures_dir):
    """Return path to a ZIP archive with no image files."""
    return os.path.join(test_fixtures_dir, 'no_images_archive.zip')

@pytest.fixture
def mixed_content_archive_cbz(test_fixtures_dir):
    """Return path to a CBZ archive with mixed content including subdirectories."""
    return os.path.join(test_fixtures_dir, 'mixed_content_archive.cbz')

@pytest.fixture
def mixed_content_archive_rar(test_fixtures_dir):
    """Return path to a RAR archive with mixed content including subdirectories."""
    return os.path.join(test_fixtures_dir, 'mixed_content_archive.rar')

@pytest.fixture
def temp_zip_archive():
    """Create a temporary ZIP archive with sample images."""
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
        temp_path = temp_file.name
    
    # Create sample images
    images = {
        'image1.png': Image.new('RGB', (50, 50), 'red'),
        'image2.jpg': Image.new('RGB', (100, 100), 'blue'),
    }
    
    with zipfile.ZipFile(temp_path, 'w') as zipf:
        for filename, img in images.items():
            img_bytes = io.BytesIO()
            format_name = 'PNG' if filename.endswith('.png') else 'JPEG'
            img.save(img_bytes, format=format_name)
            img_bytes.seek(0)
            zipf.writestr(filename, img_bytes.read())
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass

@pytest.fixture
def mock_qapplication():
    """Mock QApplication for GUI tests that don't need a real GUI."""
    with patch('PyQt5.QtWidgets.QApplication') as mock_app:
        mock_instance = Mock()
        mock_app.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_qfiledialog():
    """Mock QFileDialog for testing file selection."""
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
        yield mock_dialog

@pytest.fixture
def caplog_with_propagation(caplog):
    """Enable log propagation for pytest caplog fixture."""
    # Store original values
    original_propagate = {}
    
    # Enable propagation for all relevant loggers
    loggers = ['image_archive_viewer', 'image_archive_viewer.viewer', 
               'image_archive_viewer.archive_reader', 'image_archive_viewer.logging_setup']
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        original_propagate[logger_name] = logger.propagate
        logger.propagate = True
    
    yield caplog
    
    # Restore original values
    for logger_name, propagate_value in original_propagate.items():
        logging.getLogger(logger_name).propagate = propagate_value

@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Set up logging for tests."""
    logging.basicConfig(level=logging.DEBUG)
    
@pytest.fixture
def invalid_archive_path():
    """Return path to a non-existent archive file."""
    return "/path/to/nonexistent/archive.zip"

@pytest.fixture
def corrupt_zip_archive():
    """Create a corrupted ZIP archive for error testing."""
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
        # Write invalid ZIP data
        temp_file.write(b"This is not a valid ZIP file")
        temp_path = temp_file.name
    
    yield temp_path
    
    try:
        os.unlink(temp_path)
    except OSError:
        pass