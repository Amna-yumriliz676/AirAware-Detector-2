"""
AQI Agent — Fetches live AQI data (mock generator).
"""

from utils.mock_data import get_aqi, get_history, get_forecast, get_all_cities


class AQIAgent:
    """Fetches AQI data for a city."""

    def __init__(self):
        self.name = "AQI Agent"
        self.cache = {}
        self.cache_ttl = 60  # seconds

    def fetch(self, city: str) -> dict:
        """Fetch current AQI for a city."""
        import time
        now = time.time()

        cache_key = f"aqi_{city}"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if now - cached_time < self.cache_ttl:
                return cached_data

        data = get_aqi(city)
        self.cache[cache_key] = (now, data)
        return data

    def history(self, city: str, days: int = 7) -> list:
        """Get AQI history."""
        return get_history(city, days)

    def forecast(self, city: str, days: int = 3) -> list:
        """Get AQI forecast."""
        return get_forecast(city, days)

    def cities(self) -> list:
        """Get list of available cities."""
        return get_all_cities()

    def process(self, request: dict) -> dict:
        """Process a request — main entry point."""
        action = request.get("action", "fetch")
        city = request.get("city", "Lahore")

        if action == "fetch":
            return self.fetch(city)
        elif action == "history":
            return {"history": self.history(city, request.get("days", 7))}
        elif action == "forecast":
            return {"forecast": self.forecast(city, request.get("days", 3))}
        elif action == "cities":
            return {"cities": self.cities()}
        else:
            return {"error": f"Unknown action: {action}"}
