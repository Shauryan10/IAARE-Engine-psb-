import json
from datetime import datetime

from app.services.geo_service import get_geo_location, calculate_geo_risk
from app.services.travel_service import detect_impossible_travel

def get_client_ip(request):
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")

    if real_ip:
        return real_ip

    return request.client.host

LOGIN_HISTORY_FILE = "app/storage/login_history.json"


def load_login_history():
    with open(LOGIN_HISTORY_FILE, "r") as file:
        return json.load(file)


def save_login_history(history):
    with open(LOGIN_HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)


def get_last_login(username: str):
    history = load_login_history()
    user_history = [item for item in history if item["username"] == username]

    if not user_history:
        return None

    return user_history[-1]


def calculate_ip_risk(previous_ip: str, current_ip: str):
    risk_score = 0
    reasons = []

    if not previous_ip:
        return {
            "ip_risk_score": 0,
            "ip_risk_status": "safe",
            "reasons": ["First IP recorded"]
        }

    if previous_ip != current_ip:
        risk_score += 10
        reasons.append("New IP address detected")

    if risk_score >= 20:
        status = "medium"
    elif risk_score >= 10:
        status = "low"
    else:
        status = "safe"

    return {
        "ip_risk_score": risk_score,
        "ip_risk_status": status,
        "reasons": reasons
    }


def analyze_network_risk(username: str, current_ip: str):
    previous_login = get_last_login(username)
    previous_ip = previous_login["ip_address"] if previous_login else None
    previous_geo = previous_login["geo"] if previous_login else None

    current_geo = get_geo_location(current_ip)

    ip_risk = calculate_ip_risk(previous_ip, current_ip)
    geo_risk = calculate_geo_risk(previous_geo, current_geo)
    travel_risk = detect_impossible_travel(previous_login, current_geo)

    total_network_risk = min(
        ip_risk["ip_risk_score"]
        + geo_risk["geo_risk_score"]
        + travel_risk["travel_risk_score"],
        100
    )

    if total_network_risk >= 80:
        network_status = "critical"
        decision = "block"
    elif total_network_risk >= 60:
        network_status = "high"
        decision = "require_otp_plus_authenticator"
    elif total_network_risk >= 30:
        network_status = "medium"
        decision = "require_otp"
    else:
        network_status = "safe"
        decision = "allow"

    login_record = {
        "username": username,
        "ip_address": current_ip,
        "geo": current_geo,
        "timestamp": datetime.now().isoformat(),
        "network_risk_score": total_network_risk,
        "network_risk_status": network_status
    }

    history = load_login_history()
    history.append(login_record)
    save_login_history(history)

    return {
        "ip_risk": ip_risk,
        "geo_risk": geo_risk,
        "travel_risk": travel_risk,
        "total_network_risk": total_network_risk,
        "network_status": network_status,
        "network_decision": decision,
        "current_geo": current_geo
    }