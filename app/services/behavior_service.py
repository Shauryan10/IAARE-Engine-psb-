import json
from datetime import datetime

BEHAVIOR_FILE = "app/storage/behavior_profiles.json"


def load_profiles():
    with open(BEHAVIOR_FILE, "r") as file:
        return json.load(file)


def save_profiles(profiles):
    with open(BEHAVIOR_FILE, "w") as file:
        json.dump(profiles, file, indent=4)


def get_user_profile(username):
    profiles = load_profiles()

    for profile in profiles:
        if profile["username"] == username:
            return profile

    return None


def create_profile(username):
    profile = {
        "username": username,
        "login_hours": [],
        "locations": [],
        "devices": []
    }

    profiles = load_profiles()
    profiles.append(profile)
    save_profiles(profiles)

    return profile


def update_behavior(username, login_hour, location, device):
    profile = get_user_profile(username)

    if not profile:
        profile = create_profile(username)

    profile["login_hours"].append(login_hour)
    profile["locations"].append(location)
    profile["devices"].append(device)

    profiles = load_profiles()

    for i, p in enumerate(profiles):
        if p["username"] == username:
            profiles[i] = profile
            break

    save_profiles(profiles)


def calculate_behavior_risk(username, current_hour, current_location, current_device):
    profile = get_user_profile(username)

    if not profile:
        return {
            "behavior_risk_score": 0,
            "behavior_status": "learning",
            "reasons": ["Building user behavior profile"]
        }

    risk_score = 0
    reasons = []

    if profile["login_hours"]:
        avg_hour = round(
            sum(profile["login_hours"]) / len(profile["login_hours"])
        )

        if abs(current_hour - avg_hour) >= 4:
            risk_score += 15
            reasons.append(
                f"Unusual login time detected (avg={avg_hour})"
            )

    if profile["locations"]:
        if current_location not in profile["locations"]:
            risk_score += 15
            reasons.append("New location detected")

    if profile["devices"]:
        if current_device not in profile["devices"]:
            risk_score += 20
            reasons.append("New device behavior detected")

    if risk_score >= 40:
        status = "high"
    elif risk_score >= 20:
        status = "medium"
    else:
        status = "safe"

    return {
        "behavior_risk_score": risk_score,
        "behavior_status": status,
        "reasons": reasons if reasons else [
            "User behavior matches established profile"
        ]
    }