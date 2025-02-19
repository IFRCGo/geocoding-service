import logging
import os
import zipfile
from typing import Optional

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

URL = "https://files.emdat.be/data/gaul_gpkg_and_license.zip"


def check_and_download_gaul_file(filename: str = "gaul_gpkg.zip", chunk_size: int = 128, timeout: int = 30) -> Optional[str]:
    """
    Checks and Downloads the gaul file
    if it doesn't exist and returns the file path
    """
    zip_file_path = f"/tmp/{filename}"
    files_extraction_path = "/code/extracted_files"
    gaul_file_path = "/code/extracted_files/gaul2014_2015.gpkg"

    if os.path.exists(gaul_file_path):
        logger.info("The file already exists in the path.")
        return gaul_file_path

    logging.info("File Download has started.")

    response = requests.get(url=URL, stream=True, timeout=timeout)
    if response.status_code == 200:
        with open(zip_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)
        logger.info("File downloaded successfully.")
        logger.info("Extracting zip contents.")
        try:
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(files_extraction_path)
        except zipfile.BadZipFile:
            logger.error("Couldn't extract the zip contents.")
            return None
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)
        logger.info("Extraction done successfully.")
        return gaul_file_path

    logger.error("Failed to download file. Status code: %s", response.status_code)
    return None
