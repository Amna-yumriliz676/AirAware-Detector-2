"""
Health Agent — Generates personalized health advice using RAG + templates.
"""

from utils.rag import search_health, search_threshold
from utils.templates import generate_health_advice, parse_guideline


class HealthAgent:
    """Generates personalized health advice."""

    def __init__(self, kb: dict):
        self.name = "Health Agent"
        self.kb = kb

    def advise(self, aqi: int, condition: str) -> dict:
        """Generate health advice for a condition at a given AQI."""

        # Step 1: Find guideline via RAG
        health_results = search_health(condition, self.kb)
        guideline = parse_guideline(health_results[0]["text"]) if health_results else {}

        # Step 2: Find threshold info via RAG
        threshold = search_threshold(aqi, self.kb)

        # Step 3: Generate advice via templates
        advice = generate_health_advice(aqi, condition, threshold, guideline)

        return advice

    def process(self, request: dict) -> dict:
        """Process a request."""
        aqi = request.get("aqi", 100)
        condition = request.get("condition", "Healthy Adult")
        return self.advise(aqi, condition)
