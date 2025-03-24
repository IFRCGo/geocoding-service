import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException

from geocoding import WorldAdministrativeBoundariesGeocoder

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Life span handler"""
    # scheduler.add_job(scheduled_task, CronTrigger(day="1", hour="0", minute="0"))
    scheduler.start()
    yield
    logger.info("The service is shutting down.")


# FIXME: read from env later
geocoder = WorldAdministrativeBoundariesGeocoder("./geodata/world-administrative-boundaries.fgb")
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def home():
    """Test url"""
    return {"message": "Welcome to geocoding service"}


@app.get("/iso3_by_geom")
async def get_iso3_from_geometry(lat: str, lng: str):
    """Get the geometry based on admin units"""
    try:
        result = geocoder.get_iso3_from_geometry(lat, lng)
        return result or {"iso3": None, "iso2": None}
    except Exception:
        raise HTTPException(status_code=500, detail="Some error occured.")


@app.get("/geom_by_country_name")
async def get_geometry_from_country_name(country_name: str):
    """Get the geometry based on country name"""
    try:
        result = geocoder.get_geometry_from_country_name(country_name)
        return result or {"geometry": None, "bbox": None}
    except Exception:
        raise HTTPException(status_code=500, detail="Some error occured.")


@app.get("/geom_by_iso3")
async def get_geometry_from_iso3(iso3: str):
    try:
        result = geocoder.get_geometry_from_iso3(iso3)
        return result or {"geometry": None, "bbox": None}
    except Exception:
        raise HTTPException(status_code=500, detail="Some error occured.")
