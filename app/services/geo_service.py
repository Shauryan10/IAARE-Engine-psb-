import requests


def get_geo_location(ip_address: str):
    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip_address}",
            timeout=5
        )

        data = response.json()

        if data.get("status") != "success":
            return unknown_geo(ip_address)

        return {
            "city": data.get("city", "Unknown"),
            "state": data.get("regionName", "Unknown"),
            "country": data.get("country", "Unknown"),
            "lat": data.get("lat", 0),
            "lon": data.get("lon", 0),
            "ip": ip_address,
            "isp": data.get("isp", "Unknown")
        }

    except Exception as e:
        print("Geo Error:", e)
        return unknown_geo(ip_address)


def unknown_geo(ip_address: str):
    return {
        "city": "Unknown",
        "state": "Unknown",
        "country": "Unknown",
        "lat": 0,
        "lon": 0,
        "ip": ip_address,
        "isp": "Unknown"
    }


def calculate_geo_risk(previous_geo: dict, current_geo: dict):
    risk_score = 0
    reasons = []

    if not previous_geo:
        return {
            "geo_risk_score": 0,
            "geo_risk_status": "safe",
            "reasons": ["First location recorded"]
        }

    if current_geo["country"] == "Unknown":
        risk_score += 25
        reasons.append("Unknown geo-location detected")

    elif previous_geo["country"] != current_geo["country"]:
        risk_score += 50
        reasons.append("Different country login detected")

    elif previous_geo["state"] != current_geo["state"]:
        risk_score += 20
        reasons.append("Different state login detected")

    elif previous_geo["city"] != current_geo["city"]:
        risk_score += 10
        reasons.append("Different city login detected")

    if risk_score >= 50:
        status = "high"
    elif risk_score >= 20:
        status = "medium"
    else:
        status = "safe"

    return {
        "geo_risk_score": risk_score,
        "geo_risk_status": status,
        "reasons": reasons
    }