#!/usr/bin/env python3
"""
Script to create test fixtures for the image archive viewer tests.
Generates sample images and archives for testing purposes.
"""

import os
import zipfile
import tempfile
from PIL import Image
import io
try:
    import rarfile
    RARFILE_AVAILABLE = True
except ImportError:
    RARFILE_AVAILABLE = False

def create_sample_image(size=(100, 100), color='red'):
    """Create a simple colored image."""
    img = Image.new('RGB', size, color)
    return img

def create_test_fixtures():
    """Create test fixtures for the image archive viewer."""
    fixtures_dir = os.path.dirname(__file__)
    
    # Create sample images
    images = {
        'image3.jpeg': create_sample_image((150, 200), 'green'),
        'image1.png': create_sample_image((100, 100), 'red'),
        'image2.jpg': create_sample_image((200, 150), 'blue'),
        'not_an_image.txt': None,  # Text file to test filtering
    }
    
    # Create a ZIP archive with images
    zip_path = os.path.join(fixtures_dir, 'test_archive.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename, img in images.items():
            if img is not None:
                # Save image to bytes
                img_bytes = io.BytesIO()
                if filename.endswith('.png'):
                    img.save(img_bytes, format='PNG')
                else:
                    img.save(img_bytes, format='JPEG')
                img_bytes.seek(0)
                zipf.writestr(filename, img_bytes.read())
            else:
                # Create a text file
                zipf.writestr(filename, b"This is not an image file")
    
    # Create an empty ZIP archive
    empty_zip_path = os.path.join(fixtures_dir, 'empty_archive.zip')
    with zipfile.ZipFile(empty_zip_path, 'w') as zipf:
        pass
    
    # Create a ZIP archive with only non-image files
    no_images_zip_path = os.path.join(fixtures_dir, 'no_images_archive.zip')
    with zipfile.ZipFile(no_images_zip_path, 'w') as zipf:
        zipf.writestr('document.txt', b"This is a text document")
        zipf.writestr('data.json', b'{"key": "value"}')
    
    # Create a CBZ archive with mixed content including subdirectories
    mixed_zip_path = os.path.join(fixtures_dir, 'mixed_content_archive.cbz')
    with zipfile.ZipFile(mixed_zip_path, 'w') as zipf:
        # Root level images
        root_img = create_sample_image((120, 120), 'orange')
        img_bytes = io.BytesIO()
        root_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        zipf.writestr('root_image.png', img_bytes.read())
        
        # Image in subdirectory
        sub_img = create_sample_image((80, 80), 'purple')
        img_bytes = io.BytesIO()
        sub_img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        zipf.writestr('subdir/nested_image.jpg', img_bytes.read())
        
        # Non-image files
        zipf.writestr('readme.txt', b"Archive with mixed content")
        zipf.writestr('subdir/config.xml', b'<config></config>')
    
    print(f"Created test fixtures in {fixtures_dir}:")
    print(f"  - {zip_path}")
    print(f"  - {empty_zip_path}")
    print(f"  - {no_images_zip_path}")
    print(f"  - {mixed_zip_path}")
    print("Note: RAR test fixtures (mixed_content_archive.rar) must be created manually")

if __name__ == '__main__':
    create_test_fixtures()