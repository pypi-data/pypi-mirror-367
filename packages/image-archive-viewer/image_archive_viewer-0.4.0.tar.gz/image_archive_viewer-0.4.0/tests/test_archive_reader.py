"""
Unit tests for the archive_reader module.
"""

import pytest
import zipfile
import tempfile
import os
from PIL import Image
from unittest.mock import patch, Mock
import rarfile

from image_archive_viewer.archive_reader import read_images


class TestReadImages:
    """Test cases for the read_images function."""
    
    def test_read_images_from_zip(self, test_archive_zip):
        """Test reading images from a ZIP archive."""
        images = list(read_images(test_archive_zip))
        
        # Should have 3 images (PNG, JPG, JPEG)
        assert len(images) == 3
        
        # Check that we get tuples of (filename, PIL Image)
        for filename, pil_image in images:
            assert isinstance(filename, str)
            assert isinstance(pil_image, Image.Image)
            assert pil_image.mode == 'RGB'
        
        # Check specific filenames are present
        filenames = [filename for filename, _ in images]
        assert 'image1.png' in filenames
        assert 'image2.jpg' in filenames
        assert 'image3.jpeg' in filenames
    
    def test_read_images_from_cbz(self, temp_zip_archive):
        """Test reading images from a CBZ archive (same as ZIP)."""
        # Rename to .cbz extension
        cbz_path = temp_zip_archive.replace('.zip', '.cbz')
        os.rename(temp_zip_archive, cbz_path)
        
        try:
            images = list(read_images(cbz_path))
            assert len(images) == 2  # image1.png and image2.jpg
            
            for filename, pil_image in images:
                assert isinstance(pil_image, Image.Image)
                assert pil_image.mode == 'RGB'
        finally:
            # Cleanup
            try:
                os.unlink(cbz_path)
            except OSError:
                pass
    
    def test_read_images_empty_archive(self, empty_archive_zip):
        """Test reading from an empty archive."""
        images = list(read_images(empty_archive_zip))
        assert len(images) == 0
    
    def test_read_images_no_image_files(self, no_images_archive_zip):
        """Test reading from archive with no image files."""
        images = list(read_images(no_images_archive_zip))
        assert len(images) == 0
    
    def test_read_images_unsupported_extension(self):
        """Test error handling for unsupported file extensions."""
        with pytest.raises(ValueError, match="Unsupported archive type"):
            list(read_images("test.tar.gz"))
    
    def test_read_images_nonexistent_file(self):
        """Test error handling for non-existent files."""
        with pytest.raises(FileNotFoundError):
            list(read_images("/path/to/nonexistent/file.zip"))
    
    def test_read_images_corrupt_zip(self, corrupt_zip_archive):
        """Test error handling for corrupted ZIP files."""
        with pytest.raises(zipfile.BadZipFile):
            list(read_images(corrupt_zip_archive))
    
    def test_read_images_filters_non_images(self, test_archive_zip):
        """Test that non-image files are filtered out."""
        images = list(read_images(test_archive_zip))
        filenames = [filename for filename, _ in images]
        
        # Should not include the .txt file
        assert 'not_an_image.txt' not in filenames
        
        # Should only include image extensions
        for filename in filenames:
            assert filename.lower().endswith(('.png', '.jpg', '.jpeg'))
    
    def test_read_images_sorts_alphabetically(self, test_archive_zip):
        """Test that images are returned in alphabetical order."""
        images = list(read_images(test_archive_zip))
        filenames = [filename for filename, _ in images]
        
        # Should be sorted alphabetically
        assert filenames == sorted(filenames)
    
    @pytest.mark.skipif(not hasattr(rarfile, 'RarFile'), reason="rarfile not available")
    def test_read_images_from_rar(self, mixed_content_archive_rar):
        """Test reading images from a RAR archive with mixed content including subdirectories."""
        if not os.path.exists(mixed_content_archive_rar):
            pytest.skip("RAR test fixture not available")
            
        images = list(read_images(mixed_content_archive_rar))
        
        # Should have exactly 2 images (root_image.png and subdir/nested_image.jpg)
        assert len(images) == 2
        
        # Check that we get tuples of (filename, PIL Image)
        for filename, pil_image in images:
            assert isinstance(filename, str)
            assert isinstance(pil_image, Image.Image)
            assert pil_image.mode == 'RGB'
        
        # Check specific filenames are present
        filenames = [filename for filename, _ in images]
        assert 'root_image.png' in filenames
        assert 'subdir/nested_image.jpg' in filenames
        
        # Verify files are sorted alphabetically
        assert filenames == sorted(filenames)
        
        # Should not include non-image files
        assert 'readme.txt' not in filenames
        assert 'subdir/config.xml' not in filenames
        assert 'subdir/' not in filenames  # Directory entry should be filtered out
    
    def test_read_images_bad_rar_file(self):
        """Test error handling for bad RAR files."""
        with tempfile.NamedTemporaryFile(suffix='.rar', delete=False) as temp_file:
            temp_file.write(b"Not a valid RAR file")
            temp_path = temp_file.name
        
        try:
            with pytest.raises((rarfile.BadRarFile, rarfile.NotRarFile)):
                list(read_images(temp_path))
        finally:
            os.unlink(temp_path)
    
    def test_read_images_handles_corrupt_images(self, caplog_with_propagation):
        """Test that corrupt images within archives are skipped gracefully."""
        # Create a ZIP with a corrupt image
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            with zipfile.ZipFile(temp_path, 'w') as zipf:
                # Add a valid image
                valid_img = Image.new('RGB', (10, 10), 'red')
                import io
                img_bytes = io.BytesIO()
                valid_img.save(img_bytes, format='JPEG')
                zipf.writestr('valid.jpg', img_bytes.getvalue())
                
                # Add invalid image data
                zipf.writestr('corrupt.jpg', b'This is not image data')
            
            images = list(read_images(temp_path))
            
            # Should have skipped the corrupt image but loaded the valid one
            assert len(images) == 1
            assert images[0][0] == 'valid.jpg'
            
            # Should have logged an error for the corrupt image
            assert 'Failed to load corrupt.jpg' in caplog_with_propagation.text
            
        finally:
            os.unlink(temp_path)
    
    def test_read_images_case_insensitive_extensions(self):
        """Test that file extension matching is case insensitive."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            with zipfile.ZipFile(temp_path, 'w') as zipf:
                # Add images with uppercase extensions
                img = Image.new('RGB', (10, 10), 'blue')
                import io
                
                for ext in ['PNG', 'JPG', 'JPEG']:
                    img_bytes = io.BytesIO()
                    format_name = 'PNG' if ext == 'PNG' else 'JPEG'
                    img.save(img_bytes, format=format_name)
                    zipf.writestr(f'image.{ext}', img_bytes.getvalue())
            
            images = list(read_images(temp_path))
            assert len(images) == 3
            
        finally:
            os.unlink(temp_path)
    
    def test_read_images_mixed_content_with_subdirectories(self, mixed_content_archive_cbz):
        """Test reading images from CBZ archive with mixed content including subdirectories."""
        images = list(read_images(mixed_content_archive_cbz))
        
        # Should have 2 images (root_image.png and subdir/nested_image.jpg)
        assert len(images) == 2
        
        # Check that we get tuples of (filename, PIL Image)
        for filename, pil_image in images:
            assert isinstance(filename, str)
            assert isinstance(pil_image, Image.Image)
            assert pil_image.mode == 'RGB'
        
        # Check specific filenames are present
        filenames = [filename for filename, _ in images]
        assert 'root_image.png' in filenames
        assert 'subdir/nested_image.jpg' in filenames
        
        # Verify files are sorted alphabetically
        assert filenames == sorted(filenames)
        
        # Should not include non-image files
        assert 'readme.txt' not in filenames
        assert 'subdir/config.xml' not in filenames