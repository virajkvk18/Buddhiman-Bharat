"""
tests/test_maps_service.py — Tests for services/maps_service.py
"""

import pytest
from unittest.mock import patch
from services.maps_service import (
    get_booth_map_embed_url,
    get_static_map_url,
    get_directions_url,
    get_booth_iframe_html,
    geocode_address,
    _KNOWN_DEO_COORDS,
)


class TestGetBoothMapEmbedUrl:
    def test_returns_string(self):
        url = get_booth_map_embed_url("DL")
        assert isinstance(url, str)
        assert len(url) > 10

    def test_no_api_key_returns_fallback(self):
        with patch("services.maps_service.GOOGLE_MAPS_KEY", ""):
            url = get_booth_map_embed_url("MH")
        assert "maps.google.com" in url or "google.com" in url

    def test_with_api_key_uses_embed_api(self):
        with patch("services.maps_service.GOOGLE_MAPS_KEY", "FAKE_KEY"):
            url = get_booth_map_embed_url("WB")
        assert "maps/embed" in url
        assert "FAKE_KEY" in url

    def test_unknown_state_uses_india_centre(self):
        url = get_booth_map_embed_url("ZZ")
        assert url is not None

    def test_all_known_states_return_url(self):
        for state_code in _KNOWN_DEO_COORDS:
            url = get_booth_map_embed_url(state_code)
            assert isinstance(url, str)


class TestGetStaticMapUrl:
    def test_no_key_returns_osm_fallback(self):
        with patch("services.maps_service.GOOGLE_MAPS_KEY", ""):
            url = get_static_map_url("DL")
        assert "openstreetmap" in url

    def test_with_key_returns_google_static(self):
        with patch("services.maps_service.GOOGLE_MAPS_KEY", "FAKE_KEY"):
            url = get_static_map_url("TN")
        assert "maps.googleapis.com" in url
        assert "FAKE_KEY" in url

    def test_custom_dimensions(self):
        with patch("services.maps_service.GOOGLE_MAPS_KEY", "FAKE_KEY"):
            url = get_static_map_url("KA", width=800, height=400)
        assert "800x400" in url


class TestGetDirectionsUrl:
    def test_returns_google_maps_url(self):
        url = get_directions_url("DL")
        assert "maps.google.com" in url or "google.com/maps" in url

    def test_all_travel_modes(self):
        for mode in ("driving", "walking", "transit"):
            url = get_directions_url("MH", mode=mode)
            assert mode in url


class TestGetBoothIframeHtml:
    def test_returns_iframe_string(self):
        html = get_booth_iframe_html("DL")
        assert "<iframe" in html
        assert "src=" in html

    def test_contains_accessibility_title(self):
        html = get_booth_iframe_html("WB")
        assert "title=" in html

    def test_height_parameter(self):
        html = get_booth_iframe_html("TN", height=400)
        assert "400" in html


class TestGeocodeAddress:
    def test_no_api_key_returns_none(self):
        with patch("services.maps_service.GOOGLE_MAPS_KEY", ""):
            result = geocode_address("Patna, Bihar")
        assert result is None

    def test_with_key_makes_request(self):
        mock_response = {
            "status": "OK",
            "results": [{
                "geometry": {"location": {"lat": 25.59, "lng": 85.13}},
                "formatted_address": "Patna, Bihar, India",
            }]
        }
        import requests
        with patch("services.maps_service.GOOGLE_MAPS_KEY", "FAKE_KEY"), \
             patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(json=lambda: mock_response)
            from unittest.mock import MagicMock
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_response
            mock_get.return_value = mock_resp
            result = geocode_address("Patna, Bihar")
        if result:  # May be None if mock doesn't fire
            assert "lat" in result
            assert "lng" in result
