"""
Template engine for generating personalized health advice.
Replaces LLM with rule-based templates.
"""


def generate_health_advice(aqi: int, condition: str, threshold: dict, guideline: dict) -> dict:
    """Generate personalized health advice."""

    risk = classify_risk(aqi, condition)
    actions = guideline.get("actions", [])
    mask = threshold.get("mask", "Check advisory")

    advice = {
        "condition": condition,
        "aqi": aqi,
        "risk": risk,
        "level": threshold.get("level", "Unknown"),
        "color": threshold.get("color_hex", "#64748b"),
        "mask": mask,
        "actions": actions,
        "summary": build_summary(condition, aqi, risk, threshold),
        "dos": build_dos(condition, aqi, risk),
        "donts": build_donts(condition, aqi, risk),
    }
    return advice


def classify_risk(aqi: int, condition: str) -> str:
    """Classify risk based on AQI and condition."""
    condition_thresholds = {
        "Asthma": 100,
        "Heart Patient": 80,
        "Pregnant Women": 80,
        "Children": 80,
        "Elderly": 80,
        "Healthy Adult": 150,
    }
    threshold = condition_thresholds.get(condition, 150)

    if aqi < threshold:
        return "Low"
    elif aqi < threshold + 50:
        return "Moderate"
    elif aqi < threshold + 150:
        return "High"
    else:
        return "Extreme"


def build_summary(condition: str, aqi: int, risk: str, threshold: dict) -> str:
    """Build a one-line summary."""
    level = threshold.get("level", "Unknown")
    if risk == "Extreme":
        return f"⚠️ CRITICAL: Aap {condition} ke liye AQI {aqi} ({level}) EXTREME RISK hai. Emergency actions lein."
    elif risk == "High":
        return f"⚠️ Aap {condition} ke liye AQI {aqi} ({level}) HIGH RISK hai. Bahar na niklein."
    elif risk == "Moderate":
        return f"⚡ Aap {condition} ke liye AQI {aqi} ({level}) MODERATE hai. Ehtiyat karein."
    else:
        return f"✅ Aap {condition} ke liye AQI {aqi} ({level}) LOW RISK hai. Normal rahein."


def build_dos(condition: str, aqi: int, risk: str) -> list:
    """Build Do's list."""
    base = ["Hydrated rahein — paani zyada piyein", "Indoor air purifier use karein"]

    if risk in ["Extreme", "High"]:
        base.extend([
            "Ghar ke andar rahein",
            "Windows aur doors band rakhein",
            "N95 mask pehnein agar bahar jana zaroori ho",
        ])

    if condition == "Asthma":
        base.append("Inhaler saath rakhein")
    elif condition == "Heart Patient":
        base.append("BP aur heart rate monitor karein")
    elif condition == "Pregnant Women":
        base.append("Regular checkup jari rakhein")
    elif condition == "Children":
        base.append("Indoor activities karein")
    elif condition == "Elderly":
        base.append("Regular doctor checkup karwayein")

    return base


def build_donts(condition: str, aqi: int, risk: str) -> list:
    """Build Don'ts list."""
    base = ["Outdoor exercise avoid karein"]

    if risk in ["Extreme", "High"]:
        base.extend([
            "Bahar walk ya jogging na karein",
            "Burning (kachra, patte) na karein",
            "Smoking bilkul nahi",
        ])

    if condition == "Asthma":
        base.append("Dusty areas se door rahein")
    elif condition == "Heart Patient":
        base.append("Heavy physical activity avoid karein")
    elif condition == "Pregnant Women":
        base.append("Traffic wale areas avoid karein")
    elif condition == "Children":
        base.append("Outdoor sports avoid karein")
    elif condition == "Elderly":
        base.append("Early morning walks avoid karein")

    return base


def generate_route_advice(routes: list) -> str:
    """Generate advice for route selection."""
    if not routes:
        return "Koi route available nahi."

    best = min(routes, key=lambda r: r["aqi"])

    if best["aqi"] < 100:
        return f"✅ Best route: {best['name']} — AQI {best['aqi']} (Safe)"
    elif best["aqi"] < 200:
        return f"⚡ Best route: {best['name']} — AQI {best['aqi']} (Mask pehnein)"
    else:
        return f"⚠️ Sab routes polluted hain. Best: {best['name']} (AQI {best['aqi']}). Ghar par rahein."


def generate_school_alert(aqi: int, threshold: dict) -> dict:
    """Generate school alert."""
    schools = threshold.get("schools", "Open")

    if aqi > 300:
        status = "CLOSE"
        color = "#991b1b"
        message = "Sab schools band karein. Online classes recommend."
    elif aqi > 200:
        status = "CONSIDER CLOSURE"
        color = "#7c3aed"
        message = "Schools closure consider karein. Outdoor activities band."
    elif aqi > 150:
        status = "OUTDOOR BANNED"
        color = "#dc2626"
        message = "Outdoor sports banned. Mask mandatory."
    elif aqi > 100:
        status = "CAUTION"
        color = "#f97316"
        message = "Outdoor activities reduce karein. Sensitive students ghar."
    else:
        status = "OPEN"
        color = "#16a34a"
        message = "Normal school activities. Safe."

    return {
        "status": status,
        "color": color,
        "message": message,
        "threshold_info": schools,
    }


# ============================================================
# NEW: parse_guideline function (RAG integration ke liye)
# ============================================================
def parse_guideline(text: str) -> dict:
    """
    Parse a health guideline block from the RAG knowledge base.
    
    Input format (from data/health_guidelines.txt):
        CONDITION: Asthma
        AQI_THRESHOLD: 150
        RISK_LEVEL: Extreme
        ACTIONS: Ghar par rahein|N95 mask pehnein|Inhaler saath rakhein
        SEVERITY: High
    
    Output: dict with keys: condition, aqi_threshold, risk_level, actions, severity
    """
    result = {}
    for line in text.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()

            if key == "actions":
                # Pipe-separated actions
                result["actions"] = [a.strip() for a in val.split("|") if a.strip()]
            else:
                result[key] = val

    return result


# ============================================================
# Helper: parse_threshold (bonus — consistent with parse_guideline)
# ============================================================
def parse_threshold(text: str) -> dict:
    """
    Parse an AQI threshold block from the RAG knowledge base.
    
    Input format (from data/aqi_thresholds.txt):
        RANGE: 0-50
        LEVEL: Good
        COLOR: Green
        COLOR_HEX: #16a34a
        MASK: Not needed
        SCHOOLS: Open
        OUTDOOR: Safe
        ADVICE: Normal outdoor activity safe hai
    
    Output: dict with keys: range, level, color, color_hex, mask, schools, outdoor, advice
    """
    result = {}
    for line in text.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            result[key] = val
    return result


# ============================================================
# Helper: parse_zone (bonus — for route agent)
# ============================================================
def parse_zone(text: str) -> dict:
    """
    Parse a city zone block from the RAG knowledge base.
    
    Input format (from data/city_zones.txt):
        ZONE: Gulberg
        CITY: Lahore
        TYPE: Commercial
        BASE_AQI: 350
        PEAK_HOURS: 8-10 AM, 5-7 PM
        DESCRIPTION: Commercial area with heavy traffic
    
    Output: dict with keys: zone, city, type, base_aqi, peak_hours, description
    """
    result = {}
    for line in text.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            result[key] = val
    return result
