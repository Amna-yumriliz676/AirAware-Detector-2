"""
Mock AQI data generator with realistic patterns.
No API needed - simulates real-world AQI behavior.
"""

import random
from datetime import datetime


CITY_BASE_AQI = {
    "Lahore": 280,
    "Karachi": 180,
    "Islamabad": 120,
    "Rawalpindi": 200,
    "Faisalabad": 250,
    "Multan": 260,
    "Peshawar": 220,
    "Quetta": 150,
}

POLLUTANT_RATIOS = {
    "pm25": 0.55,
    "pm10": 0.25,
    "o3": 0.08,
    "no2": 0.07,
    "so2": 0.03,
    "co": 0.02,
}


def get_aqi(city: str = "Lahore", hour: int = None) -> dict:
    """
    Generate realistic AQI for a city.
    Patterns:
    - Morning (7-10 AM): high (traffic)
    - Evening (5-7 PM): high (traffic)
    - Night (11 PM - 5 AM): low
    - Winter months: high (smog)
    """
    if hour is None:
        hour = datetime.now().hour

    base = CITY_BASE_AQI.get(city, 200)

    # Time factor
    if 7 <= hour <= 10:
        time_factor = 1.3  # morning rush
    elif 17 <= hour <= 19:
        time_factor = 1.25  # evening rush
    elif 23 <= hour or hour <= 5:
        time_factor = 0.7  # night (low)
    else:
        time_factor = 1.0

    # Season factor (winter smog in Pakistan)
    month = datetime.now().month
    if month in [11, 12, 1]:
        season_factor = 1.6
    elif month in [2, 10]:
        season_factor = 1.3
    elif month in [6, 7, 8]:
        season_factor = 0.8  # monsoon
    else:
        season_factor = 1.0

    # Random noise
    noise = random.randint(-40, 40)

    aqi = int(base * time_factor * season_factor + noise)
    aqi = max(30, min(500, aqi))

    # Pollutant breakdown
    pollutants = {}
    for pollutant, ratio in POLLUTANT_RATIOS.items():
        pollutants[pollutant] = round(aqi * ratio * random.uniform(0.8, 1.2), 1)

    return {
        "city": city,
        "aqi": aqi,
        "pollutants": pollutants,
        "temperature": round(random.uniform(18, 32), 1),
        "humidity": random.randint(40, 75),
        "timestamp": datetime.now().isoformat(),
        "hour": hour,
    }


def get_history(city: str = "Lahore", days: int = 7) -> list:
    """Generate mock AQI history for last N days."""
    from datetime import timedelta

    history = []
    today = datetime.now()
    base = CITY_BASE_AQI.get(city, 200)

    for i in range(days, 0, -1):
        date = today - timedelta(days=i)
        noise = random.randint(-60, 60)
        aqi = max(50, min(500, base + noise))
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%a"),
            "aqi": aqi,
        })
    return history


def get_forecast(city: str = "Lahore", days: int = 3) -> list:
    """Simple 3-day forecast based on history."""
    from datetime import timedelta

    history = get_history(city, 7)
    avg = sum(h["aqi"] for h in history) / len(history)

    forecast = []
    today = datetime.now()
    for i in range(1, days + 1):
        date = today + timedelta(days=i)
        predicted = int(avg + random.randint(-40, 40))
        predicted = max(50, min(500, predicted))
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%a"),
            "aqi": predicted,
        })
    return forecast


def get_all_cities() -> list:
    """Return all available cities."""
    return list(CITY_BASE_AQI.keys())
