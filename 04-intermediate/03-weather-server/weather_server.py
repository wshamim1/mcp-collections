"""
Weather MCP Server — REST API Integration
==========================================
Demonstrates wrapping an external REST API (OpenWeatherMap) as MCP tools.
Also shows how to cache results and handle API errors gracefully.

Features:
- get_current_weather — Current conditions for any city
- get_weather_forecast — 5-day forecast
- compare_cities      — Compare weather across multiple cities
- get_weather_alerts  — Severe weather alerts

Uses: Open-Meteo API (free, no API key needed!)

Run with:
    python weather_server.py
"""

import json
from datetime import datetime
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")

# Using Open-Meteo — completely free, no API key needed
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# WMO Weather code descriptions
WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Heavy thunderstorm with hail",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _geocode(city: str) -> Optional[dict]:
    """Convert city name to lat/lon coordinates."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(GEOCODING_URL, params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        })
        response.raise_for_status()
        data = response.json()

    results = data.get("results", [])
    if not results:
        return None

    r = results[0]
    return {
        "name": r["name"],
        "country": r.get("country", ""),
        "latitude": r["latitude"],
        "longitude": r["longitude"],
        "timezone": r.get("timezone", "UTC"),
    }


async def _fetch_weather(lat: float, lon: float, hourly: bool = False, days: int = 1) -> dict:
    """Fetch weather data for coordinates."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "precipitation", "weather_code", "wind_speed_10m", "wind_direction_10m",
            "uv_index", "is_day",
        ],
        "timezone": "auto",
        "forecast_days": min(days, 7),
    }

    if hourly or days > 1:
        params["daily"] = [
            "weather_code", "temperature_2m_max", "temperature_2m_min",
            "precipitation_sum", "wind_speed_10m_max", "sunrise", "sunset",
        ]

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(WEATHER_URL, params=params)
        response.raise_for_status()
        return response.json()


# ─── Tools ────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_current_weather(city: str, units: str = "celsius") -> dict:
    """
    Get current weather conditions for a city.

    Args:
        city: City name (e.g., "Tokyo", "New York", "Paris").
        units: Temperature units — "celsius" or "fahrenheit".

    Returns:
        Current temperature, conditions, humidity, wind speed, and UV index.
    """
    location = await _geocode(city)
    if not location:
        return {"error": f"City '{city}' not found. Try a different spelling or nearby city."}

    data = await _fetch_weather(location["latitude"], location["longitude"])
    current = data.get("current", {})

    temp_c = current.get("temperature_2m")
    feels_c = current.get("apparent_temperature")

    if units == "fahrenheit":
        temperature = round(temp_c * 9 / 5 + 32, 1) if temp_c is not None else None
        feels_like = round(feels_c * 9 / 5 + 32, 1) if feels_c is not None else None
        unit_symbol = "°F"
    else:
        temperature = temp_c
        feels_like = feels_c
        unit_symbol = "°C"

    wmo = current.get("weather_code", 0)
    condition = WMO_CODES.get(wmo, "Unknown")

    return {
        "city": location["name"],
        "country": location["country"],
        "temperature": f"{temperature}{unit_symbol}",
        "feels_like": f"{feels_like}{unit_symbol}",
        "condition": condition,
        "humidity": f"{current.get('relative_humidity_2m')}%",
        "wind_speed": f"{current.get('wind_speed_10m')} km/h",
        "uv_index": current.get("uv_index"),
        "is_day": bool(current.get("is_day")),
        "updated_at": current.get("time"),
    }


@mcp.tool()
async def get_weather_forecast(city: str, days: int = 5) -> dict:
    """
    Get a multi-day weather forecast for a city.

    Args:
        city: City name.
        days: Number of forecast days (1-7, default: 5).

    Returns:
        Daily forecast with high/low temps, conditions, and precipitation.
    """
    days = max(1, min(days, 7))

    location = await _geocode(city)
    if not location:
        return {"error": f"City '{city}' not found."}

    data = await _fetch_weather(location["latitude"], location["longitude"], days=days)

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    wmo_codes = daily.get("weather_code", [])
    precip = daily.get("precipitation_sum", [])
    sunrises = daily.get("sunrise", [])
    sunsets = daily.get("sunset", [])

    forecast = []
    for i, date in enumerate(dates):
        forecast.append({
            "date": date,
            "day": datetime.fromisoformat(date).strftime("%A"),
            "condition": WMO_CODES.get(wmo_codes[i] if i < len(wmo_codes) else 0, "Unknown"),
            "high_c": max_temps[i] if i < len(max_temps) else None,
            "low_c": min_temps[i] if i < len(min_temps) else None,
            "precipitation_mm": precip[i] if i < len(precip) else None,
            "sunrise": sunrises[i].split("T")[1] if i < len(sunrises) else None,
            "sunset": sunsets[i].split("T")[1] if i < len(sunsets) else None,
        })

    return {
        "city": location["name"],
        "country": location["country"],
        "forecast_days": len(forecast),
        "forecast": forecast,
    }


@mcp.tool()
async def compare_cities_weather(cities: list[str]) -> dict:
    """
    Compare current weather across multiple cities.

    Args:
        cities: List of city names to compare (max 5).

    Returns:
        Side-by-side weather comparison for all cities.
    """
    if len(cities) > 5:
        return {"error": "Maximum 5 cities at a time."}

    results = []
    for city in cities:
        weather = await get_current_weather(city)
        results.append(weather)

    return {"comparison": results, "city_count": len(results)}


if __name__ == "__main__":
    print("Weather MCP Server (using Open-Meteo — no API key needed)")
    mcp.run()
