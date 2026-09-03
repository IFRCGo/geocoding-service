from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import init
import service
from geocoding import AdminGeometry, Country

# NOTE: TestClient(app) is used without entering it as a context manager so that
# the real `lifespan` (which downloads geodata and builds a real FastGeocoder)
# never runs. Endpoints only read `init.shared_mem`, so it's set up manually below.
client = TestClient(service.app)


@pytest.fixture(autouse=True)
def reset_shared_mem():
    yield
    init.shared_mem["geocoder"] = None
    init.shared_mem["super_simplified_geocoder"] = None


@pytest.fixture
def mock_geocoder():
    geocoder = MagicMock()
    init.shared_mem["geocoder"] = geocoder
    return geocoder


@pytest.fixture
def mock_super_simplified_geocoder():
    geocoder = MagicMock()
    init.shared_mem["super_simplified_geocoder"] = geocoder
    return geocoder


def test_home_returns_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World!"}


class TestGetIso3:
    def test_returns_country_when_found(self, mock_geocoder):
        mock_geocoder.get_iso3_from_geometry.return_value = Country(name="Countrya", iso3="AAA", iso2="AA")

        response = client.get("/country/iso3", params={"lat": 1, "lng": 2})

        assert response.status_code == 200
        assert response.json() == {"name": "Countrya", "iso3": "AAA", "iso2": "AA"}
        mock_geocoder.get_iso3_from_geometry.assert_called_once_with(lng=2, lat=1)

    def test_returns_404_when_not_found(self, mock_geocoder):
        mock_geocoder.get_iso3_from_geometry.return_value = None

        response = client.get("/country/iso3", params={"lat": 1, "lng": 2})

        assert response.status_code == 404

    def test_returns_500_when_geocoder_not_initialized(self):
        response = client.get("/country/iso3", params={"lat": 1, "lng": 2})

        assert response.status_code == 500

    def test_returns_500_on_unexpected_error(self, mock_geocoder):
        mock_geocoder.get_iso3_from_geometry.side_effect = RuntimeError("boom")

        response = client.get("/country/iso3", params={"lat": 1, "lng": 2})

        assert response.status_code == 500

    def test_returns_400_when_no_params_given(self, mock_geocoder):
        response = client.get("/country/iso3")

        assert response.status_code == 400

    def test_returns_iso3_by_country_name(self, mock_geocoder):
        mock_geocoder.get_iso3_from_country_name.return_value = "NPL"

        response = client.get("/country/iso3", params={"country_name": "Nepal"})

        assert response.status_code == 200
        assert response.json() == {"iso3": "NPL"}
        mock_geocoder.get_iso3_from_country_name.assert_called_once_with("Nepal")

    def test_returns_404_when_country_name_not_found(self, mock_geocoder):
        mock_geocoder.get_iso3_from_country_name.return_value = None

        response = client.get("/country/iso3", params={"country_name": "Atlantis"})

        assert response.status_code == 404

    def test_returns_iso3_by_iso2(self, mock_geocoder):
        mock_geocoder.get_iso3_from_iso2.return_value = "FRA"

        response = client.get("/country/iso3", params={"iso2": "FR"})

        assert response.status_code == 200
        assert response.json() == {"iso3": "FRA"}
        mock_geocoder.get_iso3_from_iso2.assert_called_once_with("FR")

    def test_returns_404_when_iso2_not_found(self, mock_geocoder):
        mock_geocoder.get_iso3_from_iso2.return_value = None

        response = client.get("/country/iso3", params={"iso2": "XX"})

        assert response.status_code == 404

    def test_returns_country_by_iso3(self, mock_geocoder):
        mock_geocoder.get_country_from_iso3.return_value = Country(name="Nepal", iso3="NPL", iso2="NP")

        response = client.get("/country/iso3", params={"iso3": "NPL"})

        assert response.status_code == 200
        assert response.json() == {"name": "Nepal", "iso3": "NPL", "iso2": "NP"}
        mock_geocoder.get_country_from_iso3.assert_called_once_with("NPL")

    def test_returns_404_when_iso3_not_found(self, mock_geocoder):
        mock_geocoder.get_country_from_iso3.return_value = None

        response = client.get("/country/iso3", params={"iso3": "ZZZ"})

        assert response.status_code == 404


class TestGetCountryGeometry:
    def test_returns_400_when_neither_iso3_nor_country_name_given(self, mock_geocoder):
        response = client.get("/country/geometry")

        assert response.status_code == 400

    def test_returns_geometry_by_iso3(self, mock_geocoder):
        mock_geocoder.get_geometry_from_iso3.return_value = AdminGeometry(
            bbox=(0.0, 0.0, 1.0, 1.0),
            geometry={"type": "Point", "coordinates": [0.123456, 0.654321]},
        )

        response = client.get("/country/geometry", params={"iso3": "AAA"})

        assert response.status_code == 200
        mock_geocoder.get_geometry_from_iso3.assert_called_once_with("aaa")
        # coordinates get rounded to 3 decimal places by round_geojson_coordinates
        assert response.json()["geometry"]["coordinates"] == [0.123, 0.654]

    def test_returns_geometry_by_country_name(self, mock_geocoder):
        mock_geocoder.get_geometry_from_country_name.return_value = AdminGeometry(
            bbox=(0.0, 0.0, 1.0, 1.0),
            geometry={"type": "Point", "coordinates": [0.0, 0.0]},
        )

        response = client.get("/country/geometry", params={"country_name": "  Nepal "})

        assert response.status_code == 200
        mock_geocoder.get_geometry_from_country_name.assert_called_once_with("nepal")

    def test_returns_404_when_geometry_not_found(self, mock_geocoder):
        mock_geocoder.get_geometry_from_iso3.return_value = None

        response = client.get("/country/geometry", params={"iso3": "ZZZ"})

        assert response.status_code == 404

    def test_uses_super_simplified_geocoder_when_simplified_flag_set(self, mock_geocoder, mock_super_simplified_geocoder):
        mock_super_simplified_geocoder.get_geometry_from_iso3.return_value = AdminGeometry(
            bbox=(0.0, 0.0, 1.0, 1.0),
            geometry={"type": "Point", "coordinates": [0.0, 0.0]},
        )

        response = client.get("/country/geometry", params={"iso3": "AAA", "simplified": True})

        assert response.status_code == 200
        mock_super_simplified_geocoder.get_geometry_from_iso3.assert_called_once()
        mock_geocoder.get_geometry_from_iso3.assert_not_called()


class TestGetAdmin2Geometries:
    def test_returns_400_when_no_codes_given(self, mock_geocoder):
        response = client.get("/admin2/geometries")

        assert response.status_code == 400

    def test_returns_geometry_for_given_codes(self, mock_geocoder):
        mock_geocoder.get_geometry_from_adm_codes.return_value = AdminGeometry(
            bbox=(0.0, 0.0, 1.0, 1.0),
            geometry={"type": "Point", "coordinates": [0.0, 0.0]},
        )

        response = client.get(
            "/admin2/geometries",
            params={"admin1_codes": [1, 2], "admin2_codes": [3]},
        )

        assert response.status_code == 200
        mock_geocoder.get_geometry_from_adm_codes.assert_called_once_with([1, 2], [3])

    def test_returns_404_when_geometry_not_found(self, mock_geocoder):
        mock_geocoder.get_geometry_from_adm_codes.return_value = None

        response = client.get("/admin2/geometries", params={"admin1_codes": [1]})

        assert response.status_code == 404
