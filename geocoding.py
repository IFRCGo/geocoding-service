import typing

import fiona
import pydantic
from shapely.geometry import Point, mapping, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

WAB_LAYER = "Layer1"


class Country(pydantic.BaseModel):
    name: str
    iso3: str
    iso2: str


class AdminGeometry(pydantic.BaseModel):
    bbox: tuple[float, float, float, float]
    geometry: dict[str, typing.Any]


class Iso3Response(pydantic.BaseModel):
    iso3: str


class FastGeocoder:
    _wab_path: str
    _gaul_path: str

    def __init__(self, wab_path: str, gaul_path: str) -> None:
        self._wab_path = wab_path
        self._gaul_path = gaul_path

        # wab
        self._geom_from_country_name_cache: dict[str, AdminGeometry] = {}
        self._geom_from_iso3_cache: dict[str, AdminGeometry] = {}
        self._geom_from_adm_names_cache: dict[str, AdminGeometry] = {}
        self._iso3_from_country_name_cache: dict[str, str] = {}
        self._iso3_from_iso2_cache: dict[str, str] = {}
        self._country_from_iso3_cache: dict[str, Country] = {}

        # gaul
        self._adm1_to_geometry_mapping: dict[int, BaseGeometry] = {}
        self._adm2_to_geometry_mapping: dict[int, BaseGeometry] = {}

        self._init_adm_mapping()

    def _init_adm_mapping(self):
        with fiona.open(self._gaul_path, layer="level2") as src:
            for feature in src:
                properties = feature["properties"]
                geometry = feature["geometry"]
                adm2 = properties["ADM2_CODE"]
                self._adm2_to_geometry_mapping[adm2] = shape(geometry)

        with fiona.open(self._gaul_path, layer="level1") as src:
            for feature in src:
                properties = feature["properties"]
                geometry = feature["geometry"]
                adm1 = properties["ADM1_CODE"]
                self._adm1_to_geometry_mapping[adm1] = shape(geometry)

    def get_iso3_from_geometry(self, lng: float, lat: float) -> Country | None:
        point = Point(lng, lat)
        with fiona.open(self._wab_path, layer=WAB_LAYER) as src:
            for feature in src:
                geometry: dict[str, typing.Any] = feature["geometry"]
                properties: dict[str, typing.Any] = feature["properties"]
                if shape(geometry).contains(point):
                    return Country(
                        name=properties["name"],
                        iso3=properties["iso3"],
                        iso2=properties["iso_3166_1_alpha_2_codes"],
                    )
        return None

    def get_iso3_from_country_name(self, country_name: str) -> str | None:
        key = country_name.lower().strip()
        from_cache = self._iso3_from_country_name_cache.get(key)
        if from_cache:
            return from_cache

        with fiona.open(self._wab_path, layer=WAB_LAYER) as src:
            for feature in src:
                properties: dict[str, typing.Any] = feature["properties"]
                if properties["name"].lower().strip() == key:
                    iso3 = properties["iso3"]
                    self._iso3_from_country_name_cache[key] = iso3
                    return iso3
        return None

    def get_iso3_from_iso2(self, iso2: str) -> str | None:
        key = iso2.lower().strip()
        from_cache = self._iso3_from_iso2_cache.get(key)
        if from_cache:
            return from_cache

        with fiona.open(self._wab_path, layer=WAB_LAYER) as src:
            for feature in src:
                properties: dict[str, typing.Any] = feature["properties"]
                iso2_from_feature = properties["iso_3166_1_alpha_2_codes"]
                if not iso2_from_feature:
                    continue
                if iso2_from_feature.lower().strip() == key:
                    iso3 = properties["iso3"]
                    self._iso3_from_iso2_cache[key] = iso3
                    return iso3
        return None

    def get_country_from_iso3(self, iso3: str) -> Country | None:
        key = iso3.lower().strip()
        from_cache = self._country_from_iso3_cache.get(key)
        if from_cache:
            return from_cache

        with fiona.open(self._wab_path, layer=WAB_LAYER) as src:
            for feature in src:
                properties: dict[str, typing.Any] = feature["properties"]
                iso3_from_feature = properties["iso3"]
                if not iso3_from_feature:
                    continue
                if iso3_from_feature.lower().strip() == key:
                    country = Country(
                        name=properties["name"],
                        iso3=iso3_from_feature,
                        iso2=properties["iso_3166_1_alpha_2_codes"],
                    )
                    self._country_from_iso3_cache[key] = country
                    return country
        return None

    def get_geometry_from_country_name(self, country_name: str) -> AdminGeometry | None:
        from_cache = self._geom_from_country_name_cache.get(country_name)
        if from_cache:
            return from_cache

        with fiona.open(self._wab_path, layer=WAB_LAYER) as src:
            for feature in src:
                if feature["properties"]["name"].lower().strip() == country_name:
                    geom = shape(feature["geometry"])
                    val = AdminGeometry(
                        geometry=mapping(geom),
                        bbox=geom.bounds,
                    )
                    self._geom_from_country_name_cache[country_name] = val
                    return val
        return None

    def get_geometry_from_adm_codes(self, adm1: list[int], adm2: list[int]):
        adm1_set = set(adm1)
        adm2_set = set(adm2)

        key = "adm1:" + ",".join(map(str, sorted(adm1_set))) + "|adm2:" + ",".join(map(str, sorted(adm2_set)))

        from_cache = self._geom_from_adm_names_cache.get(key)
        if from_cache:
            return from_cache

        features: list[BaseGeometry] = []
        for adm1_code in adm1_set:
            geometry = self._adm1_to_geometry_mapping.get(adm1_code)
            if geometry:
                features.append(geometry)
        for adm2_code in adm2_set:
            geometry = self._adm2_to_geometry_mapping.get(adm2_code)
            if geometry:
                features.append(geometry)

        if not features:
            return None

        combined_feature = unary_union(features)
        val = AdminGeometry(
            geometry=mapping(combined_feature),
            bbox=combined_feature.bounds,
        )
        self._geom_from_adm_names_cache[key] = val
        return val

    def get_geometry_from_iso3(self, iso3: str) -> AdminGeometry | None:
        from_cache = self._geom_from_iso3_cache.get(iso3)
        if from_cache:
            return from_cache
        with fiona.open(self._wab_path, layer=WAB_LAYER) as src:
            for feature in src:
                properties: dict[str, typing.Any] = feature["properties"]
                geometry: dict[str, typing.Any] = feature["geometry"]
                iso3_from_feature = properties["iso3"]
                if not iso3_from_feature:
                    continue
                if iso3_from_feature.lower().strip() == iso3:
                    geom = shape(geometry)
                    val = AdminGeometry(
                        geometry=mapping(geom),
                        bbox=geom.bounds,
                    )
                    self._geom_from_iso3_cache[iso3] = val
                    return val
            return None
