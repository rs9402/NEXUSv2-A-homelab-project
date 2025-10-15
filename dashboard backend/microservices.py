from flask import Flask, jsonify
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("OWM_API_KEY")
CITY = "Durban,ZA"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&units=metric&appid={API_KEY}"

@app.route("/weather")
def weather():
    try:
        response = requests.get(URL)
        data = response.json()

        weather_info = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "conditions": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
        }
        return jsonify(weather_info)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)