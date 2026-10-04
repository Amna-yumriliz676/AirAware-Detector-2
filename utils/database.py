"""
SQLite database operations for community reports and alerts.
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "airaware.db"


def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Community reports
    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            report_id TEXT PRIMARY KEY,
            zone TEXT,
            city TEXT,
            aqi INTEGER,
            condition TEXT,
            description TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    # Alerts sent
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id TEXT PRIMARY KEY,
            city TEXT,
            aqi INTEGER,
            alert_type TEXT,
            severity TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def create_report(zone, city, aqi, condition, description):
    """Insert a new community report."""
    report_id = "RPT-" + str(uuid.uuid4())[:6].upper()
    now = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (report_id, zone, city, aqi, condition, description, "Active", now),
    )
    conn.commit()
    conn.close()
    return report_id


def get_all_reports():
    """Get all community reports (newest first)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM reports ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def create_alert(city, aqi, alert_type, severity, message):
    """Log an alert."""
    alert_id = "ALT-" + str(uuid.uuid4())[:6].upper()
    now = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO alerts VALUES (?, ?, ?, ?, ?, ?, ?)",
        (alert_id, city, aqi, alert_type, severity, message, now),
    )
    conn.commit()
    conn.close()
    return alert_id


def get_recent_alerts(limit=20):
    """Get recent alerts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_stats():
    """Get aggregate stats."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    stats = {}
    c.execute("SELECT COUNT(*) FROM reports")
    stats["total_reports"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM alerts")
    stats["total_alerts"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM alerts WHERE severity = 'Extreme'")
    stats["extreme_alerts"] = c.fetchone()[0]

    conn.close()
    return stats
