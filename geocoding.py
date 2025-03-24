import zipfile
from typing import Any, Dict, List, Optional

import fiona  # type: ignore
from shapely.geometry import Point, mapping, shape  # type: ignore


class WorldAdministrativeBoundariesGeocoder:
    def __init__(self, fgb_path: str, simplify_tolerance: float = 0.01) -> None:
        self.fgb_path = fgb_path
        self._path = None

        self._layer = "Layer1"

        self._simplify_tolerance = simplify_tolerance

        # self._cache: Dict[str, Union[Dict[str, Any], int, None]] = {}
        # self.iso3_from_geometry_cache: dict = {}

        self.geometry_from_country_name_cache: dict = {}
        self.geometry_from_iso3_cache: dict = {}

        self._initialize_path()

    def _initialize_path(self) -> None:
        if self._is_zip_file(self.fgb_path):
            fgb_name = self._find_fgb_in_zip(self.fgb_path)
            if not fgb_name:
                raise ValueError("No .fgb file found in ZIP archive")
            self._path = f"zip://{self.fgb_path}!/{fgb_name}"
        else:
            self._path = self.fgb_path

    def _is_zip_file(self, file_path: str) -> bool:
        """Check if a file is a ZIP file"""
        try:
            with zipfile.ZipFile(file_path, "r"):
                return True
        except zipfile.BadZipFile:
            return False

    def _find_fgb_in_zip(self, zip_path: str) -> Optional[str]:
        """Find the first .fgb file in a ZIP archive"""
        with zipfile.ZipFile(zip_path, "r") as zf:
            names: List[str] = zf.namelist()
            for name in names:
                if name.lower().endswith(".fgb"):
                    return name
        return None

    def get_iso3_from_geometry(self, lng: float, lat: float) -> Optional[str]:
        if not lng or not lat or not self._path:
            return None

        try:
            # point = shape(geometry)
            point = Point(lng, lat)
            with fiona.open(self._path, layer=self._layer) as src:
                for feature in src:
                    if shape(feature["geometry"]).contains(point):
                        return {
                            "name": feature["properties"].get("name"),
                            "iso3": feature["properties"].get("iso3"),
                            "iso2": feature["properties"].get("iso_3166_1_alpha_2_codes"),
                        }
        except Exception as e:
            print(f"Error getting ISO3 from geometry: {str(e)}")
            return None

        return None

    def get_geometry_from_country_name(self, country_name: str) -> Optional[Dict[str, Any]]:
        if not country_name or not self._path:
            return None

        country_name = country_name.lower().strip()

        from_cache = self.geometry_from_country_name_cache.get(country_name)
        if from_cache:
            return from_cache

        try:
            with fiona.open(self._path, layer=self._layer) as src:
                for feature in src:
                    if feature["properties"]["name"].lower().strip() == country_name:
                        geom = shape(feature["geometry"]).simplify(
                            self._simplify_tolerance,
                            preserve_topology=True,
                        )
                        val = {"geometry": mapping(geom), "bbox": list(geom.bounds)}
                        self.geometry_from_country_name_cache[country_name] = val
                        return val
        except Exception as e:
            print(f"Error getting geometry from country name: {str(e)}")
            return None

        return None

    def get_geometry_from_iso3(self, iso3: str) -> Optional[Dict[str, Any]]:
        if not iso3 or not self._path:
            return None

        iso3 = iso3.lower().strip()

        from_cache = self.geometry_from_iso3_cache.get(iso3)
        if from_cache:
            return from_cache

        try:
            with fiona.open(self._path, layer=self._layer) as src:
                for feature in src:
                    if feature["properties"]["iso3"] is None:
                        continue

                    if feature["properties"]["iso3"].lower().strip() == iso3:
                        geom = shape(feature["geometry"]).simplify(
                            self._simplify_tolerance,
                            preserve_topology=True,
                        )
                        val = {"geometry": mapping(geom), "bbox": list(geom.bounds)}
                        self.geometry_from_iso3_cache[iso3] = val
                        return val
        except Exception as e:
            print(f"Error getting geometry from ISO3: {str(e)}")
            return None

        return None
