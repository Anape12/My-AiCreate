import requests


def get_train_info():
    return "現在の運行情報は遅延なし（テスト用）"


def get_weather(query=""):
    lat, lon = extract_city(query)

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

    try:
        res = requests.get(url)
        data = res.json()
        w = data["current_weather"]

        return f"現在の気温は{w['temperature']}℃、風速は{w['windspeed']}km/hです"

    except:
        return "天気情報の取得に失敗しました"


TOOLS = {
    "train": get_train_info,
    "weather": get_weather
}


def get_weather(city="Tokyo"):
    # 簡易：東京固定（後で拡張）
    lat = 35.6762
    lon = 139.6503

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

    try:
        res = requests.get(url)
        data = res.json()

        weather = data["current_weather"]

        return f"気温: {weather['temperature']}℃, 風速: {weather['windspeed']}km/h"

    except:
        return "天気情報の取得に失敗しました"


def extract_city(query):
    if "東京" in query:
        return (35.6762, 139.6503)
    elif "大阪" in query:
        return (34.6937, 135.5023)
    else:
        return (35.6762, 139.6503)
