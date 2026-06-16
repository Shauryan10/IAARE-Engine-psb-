def normalize_score(score: int):
    return min(score, 100)


def classify_risk(score: int):
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 30:
        return "medium"
    return "safe"


def decide_authentication_action(risk_level: str):
    if risk_level == "safe":
        return "allow"
    elif risk_level == "medium":
        return "require_otp"
    elif risk_level == "high":
        return "require_otp_plus_authenticator"
    return "block"


def calculate_final_risk(
    sim_risk_score: int = 0,
    device_risk_score: int = 0,
    network_risk_score: int = 0,
    behavior_risk_score: int = 0
):
    raw_score = (
        sim_risk_score
        + device_risk_score
        + network_risk_score
        + behavior_risk_score
    )

    final_score = normalize_score(raw_score)
    risk_level = classify_risk(final_score)
    decision = decide_authentication_action(risk_level)

    return {
        "raw_risk_score": raw_score,
        "final_risk_score": final_score,
        "risk_level": risk_level,
        "authentication_decision": decision,
        "risk_breakdown": {
            "sim_risk_score": sim_risk_score,
            "device_risk_score": device_risk_score,
            "network_risk_score": network_risk_score,
            "behavior_risk_score": behavior_risk_score
        }
    }