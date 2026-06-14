GEO_MOCK_DATA = {
    "49.36.10.10": {
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "lat": 28.7041,
        "lon": 77.1025
    },
    "49.36.20.20": {
        "city": "Noida",
        "state": "Uttar Pradesh",
        "country": "India",
        "lat": 28.5355,
        "lon": 77.3910
    },
    "103.21.58.10": {
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "lat": 12.9716,
        "lon": 77.5946
    },
    "51.140.10.10": {
        "city": "London",
        "state": "England",
        "country": "United Kingdom",
        "lat": 51.5072,
        "lon": -0.1276
    },
    "8.8.8.8": {
        "city": "Mountain View",
        "state": "California",
        "country": "United States",
        "lat": 37.3861,
        "lon": -122.0839
    }
}


def get_geo_location(ip_address: str):
    return GEO_MOCK_DATA.get(
        ip_address,
        {
            "city": "Unknown",
            "state": "Unknown",
            "country": "Unknown",
            "lat": 0,
            "lon": 0
        }
    )


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