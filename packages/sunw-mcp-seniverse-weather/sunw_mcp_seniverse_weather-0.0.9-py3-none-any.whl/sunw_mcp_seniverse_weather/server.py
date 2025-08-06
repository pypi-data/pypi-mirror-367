import os
from typing import Any, Dict
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
def current_weather(city: str) -> Dict[str, Any]:
    """Query the current weather by city name"""
    api_key = os.getenv("SENIVERSE_API_KEY")
    if not api_key:
        raise ValueError("SENIVERSE_API_KEY environment variable is required")

    try:
        weather_response = requests.get(
             "https://api.seniverse.com/v3/weather/now.json",
            params={
                "key": api_key,
                "location": city,
                "language": "zh-Hans",
                "unit": "c"
            }
        )
        weather_response.raise_for_status()
        data = weather_response.json()
        results = data["results"][0]

        if not results:
            return {"error": f"Could not find weather data for city: {city}"}

        return results
    except requests.exceptions.RequestException as e:
        error_message = f"Weather API error: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                if 'message' in error_data:
                    error_message = f"Weather API error: {error_data['message']}"
            except ValueError:
                pass
        return {"error": error_message}