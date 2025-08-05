import os
import zipfile
import rarfile
import io
import logging
from PIL import Image
from PyQt5.QtGui import QPixmap, QImage
from typing import Iterator

logger = logging.getLogger(__name__)


def read_images(archive_path: str) -> Iterator[Image.Image]:
    """
    Generator that yields images from a supported archive file.

    Args:
        archive_path (str): Path to the archive file.

    Yields:
        QPixmap: The next image in the archive as a QPixmap.
    
    Raises:
        ValueError: If the archive type is not supported.
        rarfile.BadRarFile: If RAR file is corrupted or unrar is missing.
    """
    
    ext = os.path.splitext(archive_path)[1].lower()
    if ext in ('.zip', '.cbz'):
        archive_opener = zipfile.ZipFile
    elif ext in ('.rar', '.cbr'):
        archive_opener = rarfile.RarFile
    else:
        raise ValueError(f"Unsupported archive type: {archive_path} (extension: {ext})")

    with archive_opener(archive_path, 'r') as archive:
        file_list = sorted(archive.namelist())
        for file_name in file_list:
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                logger.debug(f"Attempting to load: {file_name}")
                try:
                    with archive.open(file_name) as image_file:
                        image_data = image_file.read()
                        logger.debug(f"Read {len(image_data)} bytes from {file_name}")
                        pil_image = Image.open(io.BytesIO(image_data)).convert("RGB")
                        logger.debug(f"PIL image size: {pil_image.size}")

                        yield (file_name, pil_image)

                        logger.info(f"Successfully loaded: {file_name}")

                except (OSError, ValueError) as e:
                    logger.error(f"Failed to load {file_name}: {e}")
                    logger.debug("Exception info:", exc_info=True)
                    continue

