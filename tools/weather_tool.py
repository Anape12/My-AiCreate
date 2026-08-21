import requests

from .tool import Tool


class WeatherTool(Tool):
    name = "weather"
    description = "Gets current weather for a requested Japanese city."
    requires_online = True

    CITIES = {"東京": (35.6762, 139.6503), "横浜": (35.4437, 139.6380), "大阪": (34.6937, 135.5023)}

    def execute(self, input: str) -> str:
        city, coordinates = next(
            ((name, point) for name, point in self.CITIES.items() if name in input),
            ("東京", self.CITIES["東京"]),
        )
        latitude, longitude = coordinates
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",
                "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "Asia/Tokyo",
                "forecast_days": 2,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if "明日" in input and len(data["daily"]["time"]) > 1:
            daily = data["daily"]
            return (
                f"{city}の明日（{daily['time'][1]}）の予報: "
                f"最低 {daily['temperature_2m_min'][1]}℃、最高 {daily['temperature_2m_max'][1]}℃、"
                f"降水確率 {daily['precipitation_probability_max'][1]}%。"
            )
        weather = data["current_weather"]
        return f"{city}の現在の天気: 気温 {weather['temperature']}℃、風速 {weather['windspeed']} km/h"
