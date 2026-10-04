"""
Route Agent — Suggests least polluted routes using zone data.
"""

import random
from utils.rag import search_zone
from utils.templates import generate_route_advice


class RouteAgent:
    """Plans routes based on AQI zones."""

    def __init__(self, kb: dict):
        self.name = "Route Agent"
        self.kb = kb

    def plan(self, start_zone: str, end_zone: str, city: str = "Lahore") -> dict:
        """Generate 3 routes with AQI estimates."""

        start_info = search_zone(start_zone, self.kb)
        end_info = search_zone(end_zone, self.kb)

        start_aqi = int(start_info.get("base_aqi", 250))
        end_aqi = int(end_info.get("base_aqi", 250))

        routes = [
            {
                "name": f"Via Main Road",
                "distance": round(random.uniform(8, 15), 1),
                "time": random.randint(20, 35),
                "aqi": int((start_aqi + end_aqi) / 2 * 1.2),
                "description": "Direct route, high traffic",
            },
            {
                "name": f"Via Canal Road",
                "distance": round(random.uniform(10, 18), 1),
                "time": random.randint(25, 40),
                "aqi": int((start_aqi + end_aqi) / 2 * 0.9),
                "description": "Longer but less polluted",
            },
            {
                "name": f"Via Ring Road",
                "distance": round(random.uniform(15, 22), 1),
                "time": random.randint(35, 50),
                "aqi": int((start_aqi + end_aqi) / 2 * 0.6),
                "description": "Cleanest route — highways",
            },
        ]

        best = min(routes, key=lambda r: r["aqi"])

        advice = generate_route_advice(routes)

        return {
            "start": start_zone,
            "end": end_zone,
            "city": city,
            "routes": routes,
            "recommended": best["name"],
            "advice": advice,
        }

    def process(self, request: dict) -> dict:
        """Process route request."""
        return self.plan(
            request.get("start", "Gulberg"),
            request.get("end", "DHA"),
            request.get("city", "Lahore"),
        )
