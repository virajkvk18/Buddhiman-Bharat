"""
services/maps_service.py — Google Maps & Places API integration for Buddhiman Bharat.

Provides:
  - Polling booth map embed URLs (Google Maps Embed API)
  - Constituency boundary geocoding (Maps Geocoding API)
  - Nearby booth finder by PIN / lat-long (Places API)
  - Static map URLs for fallback display
"""

import logging
import urllib.parse
from typing import Optional
from config.settings import GOOGLE_MAPS_KEY

logger = logging.getLogger(__name__)

# Base URLs
_EMBED_BASE = "https://www.google.com/maps/embed/v1"
_GEOCODE_BASE = "https://maps.googleapis.com/maps/api/geocode/json"
_PLACES_BASE = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
_STATIC_BASE = "https://maps.googleapis.com/maps/api/staticmap"
_DIRECTIONS_BASE = "https://www.google.com/maps/dir"

# Known ECI district election office coordinates (lat, lng) for major cities
_KNOWN_DEO_COORDS: dict[str, tuple[float, float]] = {
    "DL": (28.6139, 77.2090),   # New Delhi
    "MH": (18.9220, 72.8347),   # Mumbai
    "WB": (22.5726, 88.3639),   # Kolkata
    "TN": (13.0827, 80.2707),   # Chennai
    "KA": (12.9716, 77.5946),   # Bengaluru
    "GJ": (23.0225, 72.5714),   # Ahmedabad
    "TS": (17.3850, 78.4867),   # Hyderabad
    "AP": (13.6288, 79.4192),   # Amaravati
    "KL": (8.5241, 76.9366),    # Thiruvananthapuram
    "RJ": (26.9124, 75.7873),   # Jaipur
    "MP": (23.2599, 77.4126),   # Bhopal
    "UP": (26.8467, 80.9462),   # Lucknow
    "BR": (25.5941, 85.1376),   # Patna
    "HR": (29.0588, 76.0856),   # Chandigarh (shared)
    "PB": (30.7333, 76.7794),   # Chandigarh
    "AS": (26.1445, 91.7362),   # Guwahati
    "OD": (20.2961, 85.8245),   # Bhubaneswar
    "JH": (23.3441, 85.3096),   # Ranchi
    "CG": (21.2514, 81.6296),   # Raipur
    "HP": (31.1048, 77.1734),   # Shimla
    "UK": (30.3165, 78.0322),   # Dehradun
    "GA": (15.2993, 74.1240),   # Panaji
}


def get_booth_map_embed_url(
    state_code: str = "DL",
    constituency: str = "",
    zoom: int = 13,
) -> Optional[str]:
    """
    Return a Google Maps Embed API URL centred on the DEO for the state.
    Falls back to a generic India election map if no key is set.
    """
    if not GOOGLE_MAPS_KEY:
        # Public embed fallback — no key required
        query = urllib.parse.quote(
            f"Election Commission of India {constituency or state_code}"
        )
        return f"https://maps.google.com/maps?q={query}&output=embed"

    coords = _KNOWN_DEO_COORDS.get(state_code, (20.5937, 78.9629))  # India centre
    lat, lng = coords
    query_label = urllib.parse.quote(
        f"District Election Office {constituency or state_code} India"
    )
    url = (
        f"{_EMBED_BASE}/place?"
        f"key={GOOGLE_MAPS_KEY}"
        f"&q={query_label}"
        f"&center={lat},{lng}"
        f"&zoom={zoom}"
        f"&maptype=roadmap"
        f"&language=en"
    )
    logger.debug("Maps embed URL built for state=%s", state_code)
    return url


def get_static_map_url(
    state_code: str = "DL",
    width: int = 600,
    height: int = 300,
) -> Optional[str]:
    """Return a static map image URL (no API key needed for basic embed)."""
    coords = _KNOWN_DEO_COORDS.get(state_code, (20.5937, 78.9629))
    lat, lng = coords

    if not GOOGLE_MAPS_KEY:
        # OpenStreetMap fallback tile (no key)
        return (
            f"https://www.openstreetmap.org/export/embed.html"
            f"?bbox={lng-0.5},{lat-0.5},{lng+0.5},{lat+0.5}"
            f"&layer=mapnik"
            f"&marker={lat},{lng}"
        )

    return (
        f"{_STATIC_BASE}?"
        f"center={lat},{lng}"
        f"&zoom=11"
        f"&size={width}x{height}"
        f"&maptype=roadmap"
        f"&markers=color:orange%7Clabel:E%7C{lat},{lng}"
        f"&key={GOOGLE_MAPS_KEY}"
    )


def get_directions_url(
    destination_state_code: str = "DL",
    mode: str = "driving",
) -> str:
    """Return a Google Maps directions URL to the nearest DEO (opens in browser)."""
    coords = _KNOWN_DEO_COORDS.get(destination_state_code, (20.5937, 78.9629))
    lat, lng = coords
    dest = urllib.parse.quote(f"District Election Office {destination_state_code} India")
    return (
        f"{_DIRECTIONS_BASE}/?api=1"
        f"&destination={lat},{lng}"
        f"&travelmode={mode}"
    )


def get_booth_iframe_html(state_code: str, constituency: str = "", height: int = 300) -> str:
    """Return an HTML iframe string embedding a Google/fallback map."""
    url = get_booth_map_embed_url(state_code, constituency)
    if not url:
        return "<p style='color:#9BA3BC;'>Map unavailable.</p>"

    return (
        f'<iframe src="{url}" '
        f'width="100%" height="{height}" '
        f'style="border:0;border-radius:12px;" '
        f'allowfullscreen="" loading="lazy" '
        f'referrerpolicy="no-referrer-when-downgrade" '
        f'title="Polling booth location map for {state_code}">'
        f'</iframe>'
    )


def geocode_address(address: str) -> Optional[dict]:
    """
    Geocode an Indian address via Google Geocoding API.
    Returns dict with lat, lng, formatted_address or None on failure.
    """
    if not GOOGLE_MAPS_KEY:
        logger.debug("No Maps key — geocoding unavailable")
        return None

    try:
        import requests
        params = {
            "address": f"{address}, India",
            "key": GOOGLE_MAPS_KEY,
            "region": "in",
            "language": "en",
        }
        resp = requests.get(_GEOCODE_BASE, params=params, timeout=5)
        data = resp.json()
        if data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            loc = result["geometry"]["location"]
            return {
                "lat": loc["lat"],
                "lng": loc["lng"],
                "formatted_address": result.get("formatted_address", address),
            }
    except Exception as exc:
        logger.warning("Geocoding failed: %s", exc)
    return None
