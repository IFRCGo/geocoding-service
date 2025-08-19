import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # World Administrative Boundaries
    WAB_FILE_PATH: str = "./geodata-prep/geodata/wab.fgb"
    WAB_DOWNLOAD_URL: str = "https://github.com/IFRCGo/geocoding-service/releases/download/v1.0.0/wab.fgb"
    # EMDAT GAUL
    GAUL_FILE_PATH: str = "./geodata-prep/geodata/gaul.gpkg"
    GAUL_DOWNLOAD_URL: str = "https://github.com/IFRCGo/geocoding-service/releases/download/v1.0.0/gaul.gpkg"
    # World Administrative Boundaries
    SUPER_SIMPLIFIED_WAB_FILE_PATH: str = "./geodata-prep/geodata/super_simple.wab.fgb"
    SUPER_SIMPLIFIED_WAB_DOWNLOAD_URL: str = "https://github.com/IFRCGo/geocoding-service/releases/download/v1.0.0/wab.fgb"
    # EMDAT GAUL
    SUPER_SIMPLIFIED_GAUL_FILE_PATH: str = "./geodata-prep/geodata/super_simple.gaul.gpkg"
    SUPER_SIMPLIFIED_GAUL_DOWNLOAD_URL: str = "https://github.com/IFRCGo/geocoding-service/releases/download/v1.0.0/gaul.gpkg"


settings = Settings()


# Setup logging
# FIXME: Use hook to setup logging
logging.basicConfig(level=logging.INFO)
