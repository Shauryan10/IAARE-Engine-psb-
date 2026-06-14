from datetime import datetime, timedelta


def create_sim_profile(mobile_number: str):
    return {
        "registered_mobile": mobile_number,
        "mobile_verified": True,

        "sim_changed_recently": False,
        "sim_changed_at": None,

        "mobile_change_requested": False,
        "mobile_change_requested_at": None,

        "cooling_period_active": False,
        "cooling_period_until": None,

        "otp_failed_attempts": 0,
        "otp_request_count": 0,

        "last_sim_check_status": "safe",
        "last_verified_at": datetime.now().isoformat()
    }


def mark_sim_changed(sim_profile: dict):
    sim_profile["sim_changed_recently"] = True
    sim_profile["sim_changed_at"] = datetime.now().isoformat()
    sim_profile["cooling_period_active"] = True
    sim_profile["cooling_period_until"] = (
        datetime.now() + timedelta(hours=24)
    ).isoformat()
    sim_profile["last_sim_check_status"] = "risky"
    return sim_profile


def request_mobile_change(sim_profile: dict, new_mobile_number: str):
    sim_profile["mobile_change_requested"] = True
    sim_profile["mobile_change_requested_at"] = datetime.now().isoformat()
    sim_profile["pending_mobile_number"] = new_mobile_number
    sim_profile["cooling_period_active"] = True
    sim_profile["cooling_period_until"] = (
        datetime.now() + timedelta(hours=24)
    ).isoformat()
    sim_profile["last_sim_check_status"] = "mobile_change_pending"
    return sim_profile


def is_cooling_period_active(sim_profile: dict):
    cooling_until = sim_profile.get("cooling_period_until")

    if not cooling_until:
        return False

    return datetime.now() < datetime.fromisoformat(cooling_until)


def calculate_sim_risk(sim_profile: dict, device_status: str = "known"):
    risk_score = 0
    reasons = []

    otp_failed_attempts = sim_profile.get("otp_failed_attempts", 0)
    otp_request_count = sim_profile.get("otp_request_count", 0)

    if sim_profile.get("sim_changed_recently"):
        risk_score += 50
        reasons.append("Recent SIM change detected")

    if sim_profile.get("mobile_change_requested"):
        risk_score += 40
        reasons.append("Mobile number change request detected")

    if is_cooling_period_active(sim_profile):
        risk_score += 30
        reasons.append("SIM/mobile cooling period is active")

    if otp_failed_attempts > 0:
        risk_score += min(otp_failed_attempts * 12, 60)
        reasons.append(f"{otp_failed_attempts} OTP failure(s) detected")

    if otp_request_count >= 3:

       risk_score += min(otp_request_count * 5, 40)
       reasons.append(f"High OTP request frequency detected: {otp_request_count} requests")

    if device_status == "unknown" and (
        sim_profile.get("sim_changed_recently") or sim_profile.get("mobile_change_requested")
    ):
        risk_score += 30
        reasons.append("Unknown device combined with SIM/mobile risk")

    risk_score = min(risk_score, 100)

    if risk_score >= 80:
        status = "critical"
        decision = "block"
    elif risk_score >= 60:
        status = "high"
        decision = "require_totp_plus_otp"
    elif risk_score >= 30:
        status = "medium"
        decision = "require_otp"
    else:
        status = "safe"
        decision = "allow"

    return {
        "sim_risk_score": risk_score,
        "sim_risk_status": status,
        "decision": decision,
        "reasons": reasons
    }
