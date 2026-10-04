"""
Orchestrator — Coordinates all agents.
"""

from agents.aqi_agent import AQIAgent
from agents.health_agent import HealthAgent
from agents.route_agent import RouteAgent
from agents.alert_agent import AlertAgent


class Orchestrator:
    """Boss agent that coordinates all sub-agents."""

    def __init__(self, kb: dict):
        self.name = "Orchestrator"
        self.kb = kb
        self.aqi_agent = AQIAgent()
        self.health_agent = HealthAgent(kb)
        self.route_agent = RouteAgent(kb)
        self.alert_agent = AlertAgent(kb)

    def get_full_report(self, city: str = "Lahore", condition: str = "Healthy Adult") -> dict:
        """Get complete report: AQI + Health + Alerts."""
        aqi_data = self.aqi_agent.fetch(city)
        aqi = aqi_data["aqi"]

        health = self.health_agent.advise(aqi, condition)
        alerts = self.alert_agent.check(city, aqi)

        return {
            "aqi_data": aqi_data,
            "health": health,
            "alerts": alerts,
            "city": city,
            "condition": condition,
        }

    def process(self, request: dict) -> dict:
        """Route request to appropriate agent(s)."""
        action = request.get("action", "full_report")

        if action == "aqi":
            return self.aqi_agent.process(request)
        elif action == "health":
            return self.health_agent.process(request)
        elif action == "route":
            return self.route_agent.process(request)
        elif action == "alerts":
            return self.alert_agent.process(request)
        elif action == "full_report":
            return self.get_full_report(
                request.get("city", "Lahore"),
                request.get("condition", "Healthy Adult"),
            )
        else:
            return {"error": f"Unknown action: {action}"}
