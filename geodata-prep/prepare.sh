#! /bin/sh

set -e
set -x

echo "Simplification tolerance is $TOLERANCE"
echo "Super Simplification tolerance is $HIGH_TOLERANCE"
echo "Data directory is at $DATA_DIR"

# PROCESS EMDAT GAUL

TMP_DIR="$DATA_DIR/tmp_gaul"
ZIP_NAME="gaul.zip"
ITEM_NAME="gaul2014_2015.gpkg"
FILE_NAME="gaul.gpkg"
SIMPLIFIED_FILE_NAME="simple.$FILE_NAME"
SUPER_SIMPLIFIED_FILE_NAME="super_simple.$FILE_NAME"

# Initialize
mkdir -p "$TMP_DIR"

# Get zipped GAUL file from EMDAT
curl --continue-at - --no-progress-meter --output "$TMP_DIR/$ZIP_NAME" "https://files.emdat.be/data/gaul_gpkg_and_license.zip"

# Unzip the GAUL file only
unzip -u "$TMP_DIR/$ZIP_NAME" "$ITEM_NAME" -d "$TMP_DIR"

# Simplify GAUL file while preserving the topology
ogr2ogr "$TMP_DIR/$SIMPLIFIED_FILE_NAME" "$TMP_DIR/$ITEM_NAME" -simplify $TOLERANCE
ogr2ogr "$TMP_DIR/$SUPER_SIMPLIFIED_FILE_NAME" "$TMP_DIR/$ITEM_NAME" -simplify $HIGH_TOLERANCE
# QT_QPA_PLATFORM=offscreen qgis_process plugins enable grassprovider
# QT_QPA_PLATFORM=offscreen qgis_process run grass7:v.generalize --input="$TMP_DIR/$ITEM_NAME" --output="$TMP_DIR/$SIMPLIFIED_FILE_NAME" --threshold=0.01 --type=1 --method=0 --error="$TMP_DIR/errors.qgis.log"

# Cleanup
mv "$TMP_DIR/$SIMPLIFIED_FILE_NAME" "$DATA_DIR"
mv "$TMP_DIR/$SUPER_SIMPLIFIED_FILE_NAME" "$DATA_DIR"

# PROCESS WAL

# FIXME: read this from environment
DATA_DIR=/geodata

TMP_DIR="$DATA_DIR/tmp_wab"
FILE_NAME="wab.fgb"
SIMPLIFIED_FILE_NAME="simple.$FILE_NAME"
SUPER_SIMPLIFIED_FILE_NAME="super_simple.$FILE_NAME"

# Initialize
mkdir -p "$TMP_DIR"

# Get WAB
curl --no-progress-meter --output "$TMP_DIR/$FILE_NAME" "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/world-administrative-boundaries/exports/fgb"

# Simplify GAUL file while preserving the topology
ogr2ogr "$TMP_DIR/$SIMPLIFIED_FILE_NAME" "$TMP_DIR/$FILE_NAME" -simplify $TOLERANCE
ogr2ogr "$TMP_DIR/$SUPER_SIMPLIFIED_FILE_NAME" "$TMP_DIR/$FILE_NAME" -simplify $HIGH_TOLERANCE

# Cleanup
mv "$TMP_DIR/$SIMPLIFIED_FILE_NAME" "$DATA_DIR"
mv "$TMP_DIR/$SUPER_SIMPLIFIED_FILE_NAME" "$DATA_DIR"
