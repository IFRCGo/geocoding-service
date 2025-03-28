import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # World Administrative Boundaries
    WAB_FILE_PATH: str = "./geodata-prep/geodata/wab.fgb"
    WAB_DOWNLOAD_URL: str = "https://github.com/IFRCGo/geocoding-service/releases/download/v1.0.0/wab.fgb"
    # EMDAT GAUL
    GAUL_FILE_PATH: str = "./geodata-prep/geodata/gaul.gpkg"
    GAUL_DOWNLOAD_URL: str = "https://github.com/IFRCGo/geocoding-service/releases/download/v1.0.0/gaul.gpkg"


settings = Settings()


# Setup logging
# FIXME: Use hook to setup logging
logging.basicConfig(level=logging.INFO)
