import logging

from fastapi import FastAPI

from download import check_and_download_gaul_file
from geocoding import GAULGeocoder

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

app = FastAPI()

file_path = check_and_download_gaul_file()
if not file_path:
    raise FileNotFoundError("Geocoding source file couldn't be made available.")

geocoder = GAULGeocoder(gpkg_path=file_path)


@app.get("/")
async def home():
    """Test url"""
    return "Welcome to geocoding as service"


@app.get("/by_admin_units")
async def get_by_admin_units(admin_units: str):
    """Get the geometry based on admin units"""
    if not geocoder:
        logger.error("Geocoder is not set.")
        return {}
    result = geocoder.get_geometry_from_admin_units(admin_units)
    return result or {}


@app.get("/by_country_name")
async def get_by_country_name(country_name: str):
    """Get the geometry based on country name"""
    if not geocoder:
        logger.error("Geocoder is not set.")
        return {}
    result = geocoder.get_geometry_by_country_name(country_name)
    return result or {}
