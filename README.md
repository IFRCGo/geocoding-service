# Geocoder as a Service

This server is a FastAPI implementation of the Geocoder as a service. It exposes couple of endpoints which return the Geojson geometry.
This server loads a file from the following source url:

## Getting started

```bash
# Prepare data for the geocoder
cd geodata-prep
docker compose build
docker compose up

# Run geocoder
cd ..
docker compose build
docker compose up
```

## API documentation

The documentaiton is available at `/docs`

## Production Deployment

We use CI and helm-charts to deploy the container in a pod through github actions in a Kubernetes environment.
