import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from download import check_and_download_gaul_file
from geocoding import GAULGeocoder
from utils import iso3_to_country_name

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Life span handler"""
    # Run every first day of the month (midnight)
    scheduler.add_job(scheduled_task, CronTrigger(day="1", hour="0", minute="0"))
    scheduler.start()

    yield

    logger.info("The service is shutting down.")


app = FastAPI(lifespan=lifespan)

file_path = check_and_download_gaul_file()
if not file_path:
    raise FileNotFoundError("Geocoding source file couldn't be made available.")

geocoder = GAULGeocoder(gpkg_path=file_path)


def scheduled_task():
    """Scheduled Task"""
    global file_path, geocoder
    file_path = check_and_download_gaul_file(scheduler_trigger=True)
    if not file_path:
        raise FileNotFoundError("Geocoding source file couldn't be made available.")

    geocoder = GAULGeocoder(gpkg_path=file_path)


@app.get("/")
async def home():
    """Test url"""
    return {"message": "Welcome to geocoding as service"}


@app.get("/by_admin_units")
async def get_by_admin_units(admin_units: str):
    """Get the geometry based on admin units"""
    if not geocoder:
        logger.error("Geocoder is not set.")
        return {}
    result = geocoder.get_geometry_from_admin_units(admin_units)
    return result or {"geometry": {}}


@app.get("/by_country_name")
async def get_by_country_name(country_name: str):
    """Get the geometry based on country name"""
    if not geocoder:
        logger.error("Geocoder is not set.")
        return {}
    result = geocoder.get_geometry_by_country_name(country_name)
    return result or {"geometry": {}}


@app.get("/by_iso3")
async def get_by_iso3(iso3: str):
    """Get the geometry based on iso3"""
    if not geocoder:
        logger.error("Geocoder is not set.")
        return {}
    country_name = iso3_to_country_name.get(iso3, None)
    if not country_name:
        return {}
    result = geocoder.get_geometry_by_country_name(country_name=country_name)
    return result or {"geometry": {}}
