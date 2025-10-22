from typing import Any

from geocoding import AdminGeometry


def round_geojson_coordinates(obj: Any, precision: int = 3):
    """
    Recursively round all numeric coordinates in a GeoJSON-like structure
    to the given number of decimal places (default: 3).
    """
    if isinstance(obj, (list, tuple)):
        return [round_geojson_coordinates(x, precision) for x in obj]
    elif isinstance(obj, float):
        return round(obj, precision)
    elif isinstance(obj, dict):
        return {k: round_geojson_coordinates(v, precision) for k, v in obj.items()}
    elif isinstance(obj, AdminGeometry):
        return {k: round_geojson_coordinates(v, precision) for k, v in obj.model_dump().items()}
    else:
        return obj
