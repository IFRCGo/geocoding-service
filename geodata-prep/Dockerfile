# FIXME: We might not need the whole qgis dependencies anymore
FROM qgis/qgis:3.42-noble AS base

LABEL maintainer="Montandon Dev"
LABEL org.opencontainers.image.source="https://github.com/IFRCGo/geocoding-service/"

WORKDIR /code

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        # Build required packages
        curl \
        ca-certificates \
        unzip \
    && apt-get remove -y gcc libc-dev libproj-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . /code/
