import logging
import os
import pathlib
import typing
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI

from config import settings
from geocoding import FastGeocoder


class SharedMem(typing.TypedDict):
    geocoder: FastGeocoder | None


shared_mem: SharedMem = {"geocoder": None}
logger = logging.getLogger(__name__)


def _download_file(
    *,
    url: str,
    dest: str,
    timeout: int = 60,
    chunk_size: int = 128,
):
    response = requests.get(url=url, stream=True, timeout=timeout)
    response.raise_for_status()

    with open(dest, "wb") as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            file.write(chunk)


def _download_geodata(
    *,
    name: str,
    file_path: str,
    url_path: str,
):
    dir_path = pathlib.Path(os.path.dirname(file_path))
    dir_path.mkdir(parents=True, exist_ok=True)

    if not os.path.exists(file_path):
        logger.info(f"Downloading resources for {name}.")
        _download_file(url=url_path, dest=file_path)
        logger.info("Download complete for {name}.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("The service is starting.")

    _download_geodata(
        name="WAB",
        url_path=settings.WAB_DOWNLOAD_URL,
        file_path=settings.WAB_FILE_PATH,
    )

    _download_geodata(
        name="GAUL",
        url_path=settings.WAB_DOWNLOAD_URL,
        file_path=settings.WAB_FILE_PATH,
    )

    logger.info("Initializing geocoder")
    geocoder = FastGeocoder(
        settings.WAB_FILE_PATH,
        settings.GAUL_FILE_PATH,
    )
    shared_mem["geocoder"] = geocoder
    logger.info("Initialization for geocoder complete.")

    yield

    logger.info("The service is shutting down.")


__all__ = ["lifespan", "shared_mem"]
