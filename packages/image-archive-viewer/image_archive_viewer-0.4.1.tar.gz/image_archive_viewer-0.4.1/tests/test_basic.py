"""
Basic tests to verify the package can be imported and core functions work.
"""

import pytest
import os


def test_package_import():
    """Test that the package can be imported."""
    import image_archive_viewer
    assert image_archive_viewer is not None


def test_archive_reader_import():
    """Test that archive_reader module can be imported."""
    from image_archive_viewer import archive_reader
    assert hasattr(archive_reader, 'read_images')


def test_viewer_module_import():
    """Test that viewer module can be imported (may fail in headless environments)."""
    try:
        from image_archive_viewer import viewer
        assert hasattr(viewer, 'main')
        assert hasattr(viewer, 'ArchiveImageSlideshow')
    except ImportError as e:
        # Qt may not be available in all test environments
        pytest.skip(f"Qt not available: {e}")


def test_test_fixtures_exist(test_fixtures_dir):
    """Test that our test fixtures were created properly."""
    assert os.path.exists(test_fixtures_dir)
    
    # Check for the test archives
    test_archive = os.path.join(test_fixtures_dir, 'test_archive.zip')
    empty_archive = os.path.join(test_fixtures_dir, 'empty_archive.zip')
    no_images_archive = os.path.join(test_fixtures_dir, 'no_images_archive.zip')
    mixed_archive = os.path.join(test_fixtures_dir, 'mixed_content_archive.cbz')
    
    assert os.path.exists(test_archive)
    assert os.path.exists(empty_archive)
    assert os.path.exists(no_images_archive)
    assert os.path.exists(mixed_archive)
    
    # Check that the test archive has content
    assert os.path.getsize(test_archive) > 0
    assert os.path.getsize(empty_archive) >= 0  # Could be minimal size
    assert os.path.getsize(no_images_archive) > 0
    assert os.path.getsize(mixed_archive) > 0