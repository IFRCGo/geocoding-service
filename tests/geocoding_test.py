"""Tests using real-world values (names, iso3/adm codes, bounding boxes, city coordinates)
pulled from the actual super_simple.wab.fgb / super_simple.gaul.gpkg datasets, instead of the
synthetic squares used in test_geocoding.py. fiona.open is still mocked (feature geometries are
simplified to their real bounding-box rectangles) so these run offline without the large geodata
files.
"""

from unittest.mock import patch

import pytest
from shapely.geometry import Point, box, mapping, shape
from shapely.ops import unary_union

from geocoding import WAB_LAYER, AdminGeometry, Country, FastGeocoder

# Real-world city coordinates (lng, lat)
KATHMANDU = (85.3240, 27.7172)
PARIS = (2.3522, 48.8566)
PACIFIC_OCEAN = (-160, 0)  # open water, inside no country

# Real bounding boxes from super_simple.wab.fgb (Layer1)
NEPAL_BBOX = (80.05220000000008, 26.42020000000008, 88.14279000000005, 30.424720000000036)
FRANCE_BBOX = (-4.7766699999999105, 41.36492000000004, 9.55257000000006, 51.09111000000007)

WAB_FEATURES = [
    {
        "geometry": mapping(box(*NEPAL_BBOX)),
        "properties": {"name": "Nepal", "iso3": "NPL", "iso_3166_1_alpha_2_codes": "NP"},
    },
    {
        "geometry": mapping(box(*FRANCE_BBOX)),
        "properties": {"name": "France", "iso3": "FRA", "iso_3166_1_alpha_2_codes": "FR"},
    },
]

# Real ADM1_CODE bounding boxes from super_simple.gaul.gpkg (level1)
NEPAL_CENTRAL_ADM1 = 2152
NEPAL_CENTRAL_BBOX = (83.94014022400006, 26.615127683000026, 86.56555938700006, 28.327451706000033)
NEPAL_EASTERN_ADM1 = 2153
NEPAL_EASTERN_BBOX = (86.17319767600009, 26.36357107500004, 88.19607761300006, 28.070936698000025)

LEVEL1_FEATURES = [
    {"geometry": mapping(box(*NEPAL_CENTRAL_BBOX)), "properties": {"ADM1_CODE": NEPAL_CENTRAL_ADM1}},
    {"geometry": mapping(box(*NEPAL_EASTERN_BBOX)), "properties": {"ADM1_CODE": NEPAL_EASTERN_ADM1}},
]

# Real ADM2_CODE bounding boxes from super_simple.gaul.gpkg (level2)
NEPAL_BAGMATI_ADM2 = 22351  # contains Kathmandu; part of Central (2152)
NEPAL_BAGMATI_BBOX = (84.62908935500008, 27.32787895200005, 86.06520910200004, 28.32015609700005)
NEPAL_KOSHI_ADM2 = 22354  # part of Eastern (2153)
NEPAL_KOSHI_BBOX = (86.91545105000006, 26.407305567000037, 87.76473999000007, 27.952205598000035)

LEVEL2_FEATURES = [
    {"geometry": mapping(box(*NEPAL_BAGMATI_BBOX)), "properties": {"ADM2_CODE": NEPAL_BAGMATI_ADM2}},
    {"geometry": mapping(box(*NEPAL_KOSHI_BBOX)), "properties": {"ADM2_CODE": NEPAL_KOSHI_ADM2}},
]


class FakeFionaSource(list):
    """A list that also behaves like the context manager fiona.open() returns."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def _fake_fiona_open(path, layer=None, **kwargs):
    if layer == WAB_LAYER:
        return FakeFionaSource(WAB_FEATURES)
    if layer == "level1":
        return FakeFionaSource(LEVEL1_FEATURES)
    if layer == "level2":
        return FakeFionaSource(LEVEL2_FEATURES)
    raise ValueError(f"Unexpected layer requested in test: {layer}")


@pytest.fixture
def geocoder():
    with patch("geocoding.fiona.open", side_effect=_fake_fiona_open):
        yield FastGeocoder(wab_path="fake_wab.fgb", gaul_path="fake_gaul.gpkg")


class TestGetIso3FromGeometryRealData:
    def test_kathmandu_resolves_to_nepal(self, geocoder):
        lng, lat = KATHMANDU
        result = geocoder.get_iso3_from_geometry(lng=lng, lat=lat)
        assert result == Country(name="Nepal", iso3="NPL", iso2="NP")

    def test_paris_resolves_to_france(self, geocoder):
        lng, lat = PARIS
        result = geocoder.get_iso3_from_geometry(lng=lng, lat=lat)
        assert result == Country(name="France", iso3="FRA", iso2="FR")

    def test_open_ocean_point_resolves_to_no_country(self, geocoder):
        lng, lat = PACIFIC_OCEAN
        assert geocoder.get_iso3_from_geometry(lng=lng, lat=lat) is None


class TestGetGeometryFromCountryNameRealData:
    def test_returns_real_nepal_geometry(self, geocoder):
        result = geocoder.get_geometry_from_country_name("nepal")
        assert isinstance(result, AdminGeometry)
        assert result.bbox == NEPAL_BBOX
        assert shape(result.geometry).contains(Point(*KATHMANDU))

    def test_returns_none_when_not_found(self, geocoder):
        assert geocoder.get_geometry_from_country_name("atlantis") is None


class TestGetGeometryFromIso3RealData:
    def test_returns_real_france_geometry(self, geocoder):
        result = geocoder.get_geometry_from_iso3("fra")
        assert result is not None
        assert result.bbox == FRANCE_BBOX
        assert shape(result.geometry).contains(Point(*PARIS))

    def test_returns_none_for_unknown_iso3(self, geocoder):
        assert geocoder.get_geometry_from_iso3("xyz") is None


class TestGetGeometryFromAdmCodesRealData:
    def test_adm1_only_returns_real_nepal_central_region(self, geocoder):
        result = geocoder.get_geometry_from_adm_codes([NEPAL_CENTRAL_ADM1], [])
        assert result is not None
        assert result.bbox == NEPAL_CENTRAL_BBOX

    def test_adm2_only_returns_bagmati_region_containing_kathmandu(self, geocoder):
        result = geocoder.get_geometry_from_adm_codes([], [NEPAL_BAGMATI_ADM2])
        assert result is not None
        assert result.bbox == NEPAL_BAGMATI_BBOX
        assert shape(result.geometry).contains(Point(*KATHMANDU))

    def test_combines_multiple_real_admin_regions(self, geocoder):
        result = geocoder.get_geometry_from_adm_codes([NEPAL_CENTRAL_ADM1, NEPAL_EASTERN_ADM1], [NEPAL_KOSHI_ADM2])
        assert result is not None
        expected_bbox = unary_union(
            [
                box(*NEPAL_CENTRAL_BBOX),
                box(*NEPAL_EASTERN_BBOX),
                box(*NEPAL_KOSHI_BBOX),
            ]
        ).bounds
        assert result.bbox == expected_bbox

    def test_returns_none_when_no_codes_match(self, geocoder):
        assert geocoder.get_geometry_from_adm_codes([999999], [999999]) is None
