import requests

from .config import REQUEST_TIMEOUT


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def geocode_location(query):
    """
    Convert place name to latitude and longitude using Open-Meteo Geocoding API.
    """

    if not query:
        return {"error": "Location query is empty."}

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": query,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        results = response.json().get("results", [])

        if not results:
            return {"error": f"No location found for '{query}'."}

        item = results[0]

        return {
            "name": item.get("name"),
            "admin1": item.get("admin1"),
            "country": item.get("country"),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude")
        }

    except Exception as e:
        return {"error": f"Geocoding failed: {str(e)}"}


def get_weather_risk(latitude, longitude):
    """
    Get live and next 24-hour weather data from Open-Meteo.
    Compute simple flood risk score.
    """

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except Exception:
        return {"error": "latitude and longitude must be numbers."}

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,precipitation,weather_code",
        "hourly": "precipitation_probability,precipitation,weather_code",
        "forecast_days": 2,
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})

        times = hourly.get("time", [])
        precipitation = hourly.get("precipitation", [])
        precipitation_probability = hourly.get("precipitation_probability", [])

        current_time = current.get("time")

        start_idx = 0
        if current_time in times:
            start_idx = times.index(current_time)

        end_idx = min(len(times), start_idx + 24)

        window_precipitation = [
            _safe_float(x)
            for x in precipitation[start_idx:end_idx]
        ]

        window_probability = [
            _safe_float(x)
            for x in precipitation_probability[start_idx:end_idx]
        ]

        total_precipitation = sum(window_precipitation)
        max_probability = max(window_probability) if window_probability else 0.0
        current_precipitation = _safe_float(current.get("precipitation"))

        weather_code = current.get("weather_code")

        try:
            weather_code_int = int(weather_code)
        except Exception:
            weather_code_int = None

        score = 0

        if total_precipitation >= 50:
            score += 40
        elif total_precipitation >= 25:
            score += 30
        elif total_precipitation >= 10:
            score += 20
        elif total_precipitation >= 2:
            score += 10

        if max_probability >= 80:
            score += 30
        elif max_probability >= 60:
            score += 20
        elif max_probability >= 40:
            score += 10

        if current_precipitation >= 5:
            score += 20
        elif current_precipitation >= 1:
            score += 10

        if weather_code_int in [63, 65, 66, 67, 80, 81, 82, 95, 96, 99]:
            score += 10

        score = min(score, 100)

        if score >= 70:
            risk_level = "high"
        elif score >= 40:
            risk_level = "moderate"
        elif score >= 15:
            risk_level = "elevated"
        else:
            risk_level = "low"

        return {
            "latitude": latitude,
            "longitude": longitude,
            "current_time": current_time,
            "current_temperature_c": current.get("temperature_2m"),
            "current_precipitation_mm": current_precipitation,
            "weather_code": weather_code_int,
            "weather_description": WEATHER_CODES.get(weather_code_int, "Unknown"),
            "next_24h_total_precipitation_mm": round(total_precipitation, 1),
            "next_24h_max_precipitation_probability_percent": round(max_probability, 1),
            "risk_score": score,
            "risk_level": risk_level,
            "summary": (
                f"{risk_level.capitalize()} flood risk based on "
                f"{round(total_precipitation, 1)} mm expected rainfall "
                f"and maximum precipitation probability {round(max_probability, 1)}% "
                f"in the next 24 hours."
            )
        }

    except Exception as e:
        return {"error": f"Weather risk lookup failed: {str(e)}"}


def get_official_alerts(latitude, longitude):
    """
    Check official alerts using NWS API.
    Works best for United States coordinates.
    For non-US locations, returns fallback note.
    """

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except Exception:
        return {"error": "latitude and longitude must be numbers."}

    headers = {
        "User-Agent": "FloodGuardAI student project (contact@example.com)"
    }

    url = f"https://api.weather.gov/alerts/active?point={latitude},{longitude}"

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)

        if response.status_code != 200:
            return {
                "alerts": [],
                "note": (
                    "Official alert service returned "
                    f"status {response.status_code}. "
                    "This may happen outside the United States. "
                    "Use weather risk only."
                )
            }

        features = response.json().get("features", [])

        alerts = []

        keywords = [
            "flood",
            "flash",
            "river",
            "rain",
            "storm",
            "severe",
            "hurricane",
            "tropical"
        ]

        for feature in features:
            properties = feature.get("properties", {})

            event = properties.get("event", "")
            headline = properties.get("headline", "")

            text = f"{event} {headline}".lower()

            if any(keyword in text for keyword in keywords):
                alerts.append({
                    "event": event,
                    "headline": headline,
                    "severity": properties.get("severity"),
                    "instruction": properties.get("instruction"),
                    "area": properties.get("areaDesc"),
                    "expires": properties.get("expires")
                })

        if not alerts:
            return {
                "alerts": [],
                "note": "No active flood-related official alerts found for this point."
            }

        return {
            "alerts": alerts,
            "note": "Official alerts found."
        }

    except Exception as e:
        return {
            "alerts": [],
            "error": f"Official alert lookup failed: {str(e)}"
        }


def get_emergency_contacts(location=None):
    """
    Return emergency contact guidance.
    In production, replace with official location-specific contacts.
    """

    contacts = [
        {
            "service": "Emergency Services",
            "number": "Use local emergency number such as 911, 112, or 108."
        },
        {
            "service": "Local Disaster Management Authority",
            "number": "Check official local government website."
        },
        {
            "service": "Hospital/Ambulance",
            "number": "Use nearest emergency medical service."
        },
        {
            "service": "Family Emergency Contact",
            "number": "Keep one out-of-city contact person."
        }
    ]

    return {
        "location": location,
        "contacts": contacts,
        "note": "Replace with official local emergency contacts in production."
    }