# Geocoder as a Service

This server is a FastAPI implementation of the Geocoder as a service. It exposes couple of endpoints which return the Geojson geometry.
This server loads a file from the following source url:

> Source URL: https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/world-administrative-boundaries/exports/fgb

## Endpoints

Following are the endpoints exposed:

### GET /iso3_by_geom?lat=lat,lng=lng

This GET request takes in a query parameter `lat` and `lng` and returns the Json response with name, iso3 and iso2 if available else an empty dict.

### GET /geom_by_country_name?country_name=country_name

This GET request takes in a query parameter `country_name` and returns the Geojson geometry polygon if available else an empty dict.

### GET /geom_by_iso3?iso3=iso3

This GET request takes in a query parameter `iso3` and returns the Geojson geometry polygon if available else an empty dict.

## Setting up the environment

Check the file `.env.sample` for reference.

- **SERVICE_PORT**: The port on which this server runs
- **DATA_PATH**: The path where the geodata is stored

## Local Deployment

### Build the image

$ docker compose build

### Run the container

$ docker compose up -d

### To view the logs

$ docker compose logs -f geocoding

## Production Deployment

We use CI and helm-charts to deploy the container in a pod through github actions in a Kubernetes environment.
