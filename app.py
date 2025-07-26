# app.py
from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__, static_folder='static')

# Base URL for Open-Meteo Geocoding API
GEOCODING_BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"
# Base URL for Open-Meteo Weather API
WEATHER_BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Helper function to map WMO weather codes (copied from previous Python example)
def get_weather_description(weather_code):
    descriptions = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Drizzle: Light", 53: "Drizzle: Moderate", 55: "Drizzle: Dense intensity",
        56: "Freezing Drizzle: Light", 57: "Freezing Drizzle: Dense intensity",
        61: "Rain: Slight", 63: "Rain: Moderate", 65: "Rain: Heavy intensity",
        66: "Freezing Rain: Light", 67: "Freezing Rain: Heavy intensity",
        71: "Snow fall: Slight", 73: "Snow fall: Moderate", 75: "Snow fall: Heavy intensity",
        77: "Snow grains",
        80: "Rain showers: Slight", 81: "Rain showers: Moderate", 82: "Rain showers: Violent",
        85: "Snow showers: Slight", 86: "Snow showers: Heavy",
        95: "Thunderstorm: Slight or moderate",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }
    return descriptions.get(weather_code, "Unknown weather code")

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/get_weather', methods=['GET'])
def get_weather():
    """
    API endpoint to fetch weather data from Open-Meteo based on city name.
    This endpoint is called by the JavaScript frontend.
    """
    city_name = request.args.get('city')
    if not city_name:
        return jsonify({"error": "City name is required"}), 400

    try:
        # Step 1: Get coordinates from Open-Meteo's geocoding API
        geocode_params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        geocode_response = requests.get(GEOCODING_BASE_URL, params=geocode_params)
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()

        if not geocode_data or not geocode_data.get('results'):
            return jsonify({"error": f"Could not find coordinates for '{city_name}'"}), 404

        location = geocode_data['results'][0]
        latitude = location['latitude']
        longitude = location['longitude']
        display_name = location['name']
        country = location['country']

        # Step 2: Get current weather data from Open-Meteo API
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m",
            "timezone": "auto",
            "forecast_days": 1
        }
        weather_response = requests.get(WEATHER_BASE_URL, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        if not weather_data or not weather_data.get('current'):
            return jsonify({"error": "Could not retrieve current weather data"}), 500

        current = weather_data['current']
        
        # Prepare data to send back to frontend
        response_data = {
            "location": {
                "name": display_name,
                "country": country,
                "latitude": latitude,
                "longitude": longitude
            },
            "weather": {
                "temperature": current.get('temperature_2m'),
                "apparent_temperature": current.get('apparent_temperature'),
                "humidity": current.get('relative_humidity_2m'),
                "wind_speed": current.get('wind_speed_10m'),
                "precipitation": current.get('precipitation'),
                "is_day": current.get('is_day') == 1,
                "weather_code": current.get('weather_code'),
                "description": get_weather_description(current.get('weather_code'))
            }
        }
        return jsonify(response_data), 200

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return jsonify({"error": "Error communicating with external weather API"}), 500
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)