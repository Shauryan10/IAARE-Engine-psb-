import math
from datetime import datetime


def calculate_distance_km(lat1, lon1, lat2, lon2):
    radius = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)   
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radius * c


def detect_impossible_travel(previous_login: dict, current_geo: dict):
    if not previous_login:
        return {
            "travel_risk_score": 0,
            "impossible_travel": False,
            "reasons": ["No previous login history"]
        }

    previous_geo = previous_login["geo"]
    previous_time = datetime.fromisoformat(previous_login["timestamp"])
    current_time = datetime.now()

    distance = calculate_distance_km(
        previous_geo["lat"],
        previous_geo["lon"],
        current_geo["lat"],
        current_geo["lon"]
    )

    time_diff_hours = (current_time - previous_time).total_seconds() / 3600

    if time_diff_hours <= 0:
        time_diff_hours = 0.01

    speed = distance / time_diff_hours

    if speed > 1000:
        return {
            "travel_risk_score": 70,
            "impossible_travel": True,
            "distance_km": round(distance, 2),
            "time_diff_hours": round(time_diff_hours, 2),
            "estimated_speed_kmph": round(speed, 2),
            "reasons": ["Impossible travel detected"]
        }

    return {
        "travel_risk_score": 0,
        "impossible_travel": False,
        "distance_km": round(distance, 2),
        "time_diff_hours": round(time_diff_hours, 2),
        "estimated_speed_kmph": round(speed, 2),
        "reasons": ["Travel pattern acceptable"]
    }