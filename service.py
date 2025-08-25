import logging
import time
from typing import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Query, Request
from starlette.responses import Response

import geocoding
from init import lifespan, shared_mem

app = FastAPI(lifespan=lifespan)
logger = logging.getLogger(__name__)

# TODO:
# - Add decorator to cache requests
# - Add decorator to handle HTTPExceptions
# - Support GAUL files (need to size it down)


@app.middleware("http")
async def add_timing_information(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    start_time = time.perf_counter()  # Start timing
    response = await call_next(request)  # Process request
    end_time = time.perf_counter()  # End timing

    process_time = end_time - start_time

    # Add timing info to response headers (optional)
    response.headers["X-Process-Time"] = str(process_time)

    return response


@app.get("/")
async def home():
    """Health check"""
    return {"message": "Hello World!"}


@app.get("/country/iso3")
async def get_iso3(lat: float, lng: float) -> geocoding.Country:
    """Get the iso3 based on coordinate"""
    try:
        geocoder = shared_mem["geocoder"]
        if not geocoder:
            raise Exception("Geocoder is not initialized")
        result = geocoder.get_iso3_from_geometry(lat, lng)
        if not result:
            raise HTTPException(status_code=404, detail="iso3 not found.")
        return result
    except HTTPException:
        raise
    except Exception:
        logger.error("Encountered an unexpected error.", exc_info=True)
        raise HTTPException(status_code=500, detail="Some error occured.")


@app.get("/country/geometry")
async def get_country_geometry(
    country_name: str | None = None, iso3: str | None = None, simplified: bool = False
) -> geocoding.AdminGeometry:
    """Get the country geometry based on country name or iso3"""
    try:
        geocoder = shared_mem["geocoder"] if not simplified else shared_mem["super_simplified_geocoder"]
        if not geocoder:
            raise Exception("Geocoder is not initialized")
        if iso3:
            result = geocoder.get_geometry_from_iso3(iso3.lower().strip())
        elif country_name:
            result = geocoder.get_geometry_from_country_name(country_name.lower().strip())
        else:
            raise HTTPException(status_code=400, detail="Either iso3 or country_name is required.")

        if not result:
            raise HTTPException(status_code=404, detail="Geometry not found.")
        return result
    except HTTPException:
        raise
    except Exception:
        logger.error("Encountered an unexpected error.", exc_info=True)
        raise HTTPException(status_code=500, detail="Some error occured.")


@app.get("/admin2/geometries")
async def get_admin2_geometries(
    admin1_codes: list[int] = Query(default=[]), admin2_codes: list[int] = Query(default=[]), simplified: bool = False
) -> geocoding.AdminGeometry:
    """Get the admin 2 geometries based on admin 1 codes or admin 2 codes"""
    try:
        geocoder = shared_mem["geocoder"] if not simplified else shared_mem["super_simplified_geocoder"]
        if not geocoder:
            raise Exception("Geocoder is not initialized")
        if admin1_codes or admin2_codes:
            result = geocoder.get_geometry_from_adm_codes(admin1_codes, admin2_codes)
        else:
            raise HTTPException(status_code=400, detail="Either admin 1 codes or admin 2 codes is required.")

        if not result:
            raise HTTPException(status_code=404, detail="Geometry not found.")
        return result
    except HTTPException:
        raise
    except Exception:
        logger.error("Encountered an unexpected error.", exc_info=True)
        raise HTTPException(status_code=500, detail="Some error occured.")
