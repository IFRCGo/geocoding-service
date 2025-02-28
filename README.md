# Geocoder as a Service

This server is a FastAPI implementation of the Geocoder as a service. It exposes couple of endpoints which return the Geojson geometry.
This server loads a file from the following source url:

> Source URL: https://files.emdat.be/data/gaul_gpkg_and_license.zip

## Endpoints

Following are the endpoints exposed:

- GET /by_admin_units?admin_units=location_name

This GET request takes in a query parameter `admin_units` and returns the Geojson geometry polygon if available else an empty dict.

- GET /by_country_name?country_name=country_name

This GET request takes in a query parameter `country_name` and returns the Geojson geometry polygon if available else an empty dict.


## Scheduled job

Apart from the endpoint implementation, this server also runs a scheduled task that pulls the Zip file from the above source in a monthly (first day) basis.
This ensures we are using a latest file for this service.

## Setting up the environment

There are two environment variables that needs to be setup before the deployment. Check the file `.env.sample` for reference.
* **SERVICE_PORT**: The port on which this server runs
* **GPKG_DIR_BASE_PATH**: The path of the directory where the download file(above) resides.


## Local Deployment

### Build the image

$ docker compose build

### Run the container

$ docker compose up -d

### To view the logs

$ docker compose logs -f geocoding

## Production Deployment

We use CI and helm-charts to deploy the container in a pod through github actions in a Kubernetes environment.