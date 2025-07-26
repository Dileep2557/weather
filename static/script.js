document.addEventListener('DOMContentLoaded', () => {
    const cityInput = document.getElementById('cityInput');
    const getWeatherBtn = document.getElementById('getWeatherBtn');
    const weatherResultDiv = document.getElementById('weatherResult');
    const errorMessageDiv = document.getElementById('errorMessage');

    const locationDisplay = document.getElementById('locationDisplay');
    const temperatureDisplay = document.getElementById('temperatureDisplay');
    const feelsLikeDisplay = document.getElementById('feelsLikeDisplay');
    const humidityDisplay = document.getElementById('humidityDisplay');
    const windSpeedDisplay = document.getElementById('windSpeedDisplay');
    const precipitationDisplay = document.getElementById('precipitationDisplay');
    const dayNightDisplay = document.getElementById('dayNightDisplay');
    const weatherDescriptionDisplay = document.getElementById('weatherDescriptionDisplay');

    function clearResults() {
        locationDisplay.textContent = '';
        temperatureDisplay.textContent = '';
        feelsLikeDisplay.textContent = '';
        humidityDisplay.textContent = '';
        windSpeedDisplay.textContent = '';
        precipitationDisplay.textContent = '';
        dayNightDisplay.textContent = '';
        weatherDescriptionDisplay.textContent = '';
        errorMessageDiv.textContent = '';
    }

    // This function now calls our Python backend's /get_weather endpoint
    async function fetchWeatherFromBackend() {
        clearResults();
        const cityName = cityInput.value.trim();

        if (!cityName) {
            errorMessageDiv.textContent = 'Please enter a city name.';
            return;
        }

        try {
            // Call our Python backend API endpoint
            const response = await fetch(`/get_weather?city=${encodeURIComponent(cityName)}`);
            const data = await response.json();

            if (!response.ok) {
                // Handle errors returned by our backend
                errorMessageDiv.textContent = data.error || 'An error occurred fetching weather data from backend.';
                return;
            }

            // Data received from our Python backend
            const location = data.location;
            const weather = data.weather;

            locationDisplay.textContent = `Location: ${location.name}, ${location.country} (${location.latitude.toFixed(2)}, ${location.longitude.toFixed(2)})`;
            temperatureDisplay.textContent = `Temperature: ${weather.temperature}°C`;
            feelsLikeDisplay.textContent = `Apparent Temperature: ${weather.apparent_temperature}°C (Feels like)`;
            humidityDisplay.textContent = `Humidity: ${weather.humidity}%`;
            windSpeedDisplay.textContent = `Wind Speed: ${weather.wind_speed} m/s`;
            precipitationDisplay.textContent = `Precipitation: ${weather.precipitation} mm`;
            dayNightDisplay.textContent = `Day/Night: ${weather.is_day ? 'Day' : 'Night'}`;
            weatherDescriptionDisplay.textContent = `Weather: ${weather.description} (Code: ${weather.weather_code})`;

        } catch (error) {
            console.error('Error fetching weather from backend:', error);
            errorMessageDiv.textContent = 'Network error or unable to connect to server. Please try again.';
        }
    }

    getWeatherBtn.addEventListener('click', fetchWeatherFromBackend);
    cityInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            fetchWeatherFromBackend();
        }
    });
});