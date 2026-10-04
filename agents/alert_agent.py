"""
Alert Agent — Generates school, office, and community alerts.
"""

from utils.rag import search_threshold
from utils.templates import generate_school_alert
from utils.database import create_alert


class AlertAgent:
    """Manages alerts based on AQI thresholds."""

    def __init__(self, kb: dict):
        self.name = "Alert Agent"
        self.kb = kb

    def check(self, city: str, aqi: int) -> dict:
        """Check AQI and generate alerts."""

        threshold = search_threshold(aqi, self.kb)

        school = generate_school_alert(aqi, threshold)

        alerts = {
            "city": city,
            "aqi": aqi,
            "level": threshold.get("level", "Unknown"),
            "color": threshold.get("color_hex", "#64748b"),
            "school_alert": school,
            "office_advisory": self._office_advisory(aqi),
            "mask_recommendation": threshold.get("mask", "Check advisory"),
            "outdoor_status": threshold.get("outdoor", "Check advisory"),
            "public_message": self._public_message(city, aqi, threshold),
        }

        # Log to database if severity high
        if aqi > 150:
            try:
                create_alert(
                    city=city,
                    aqi=aqi,
                    alert_type="AQI Threshold",
                    severity=school["status"],
                    message=school["message"],
                )
            except Exception:
                pass

        return alerts

    def _office_advisory(self, aqi: int) -> dict:
        if aqi > 300:
            return {
                "status": "WORK FROM HOME",
                "color": "#991b1b",
                "message": "Sab offices WFH karein. Emergency only.",
            }
        elif aqi > 200:
            return {
                "status": "WFH RECOMMENDED",
                "color": "#7c3aed",
                "message": "Possible ho to WFH karein. Mask mandatory.",
            }
        elif aqi > 150:
            return {
                "status": "CAUTION",
                "color": "#dc2626",
                "message": "Mask mandatory. Outdoor meetings avoid.",
            }
        elif aqi > 100:
            return {
                "status": "MODERATE",
                "color": "#f97316",
                "message": "Sensitive employees mask pehnein.",
            }
        else:
            return {
                "status": "NORMAL",
                "color": "#16a34a",
                "message": "Normal office operations.",
            }

    def _public_message(self, city: str, aqi: int, threshold: dict) -> str:
        level = threshold.get("level", "Unknown")
        advice = threshold.get("advice", "Check advisory")

        if aqi > 300:
            return f"🚨 {city} mein AQI {aqi} ({level}) — EMERGENCY! {advice}"
        elif aqi > 200:
            return f"⚠️ {city} mein AQI {aqi} ({level}) — Bahut kharab. {advice}"
        elif aqi > 150:
            return f"⚡ {city} mein AQI {aqi} ({level}) — Kharab. {advice}"
        else:
            return f"✅ {city} mein AQI {aqi} ({level}) — {advice}"

    def process(self, request: dict) -> dict:
        """Process alert check."""
        return self.check(
            request.get("city", "Lahore"),
            request.get("aqi", 100),
        )
