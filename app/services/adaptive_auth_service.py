def process_adaptive_authentication(risk_level: str):

    risk_level = risk_level.lower()

    if risk_level == "safe":
        return {
            "access_granted": True,
            "authentication_required": "none",
            "message": "Login approved"
        }

    elif risk_level == "medium":
        return {
            "access_granted": False,
            "authentication_required": "otp",
            "message": "OTP verification required"
        }

    elif risk_level == "high":
        return {
            "access_granted": False,
            "authentication_required": "otp_and_authenticator",
            "message": "OTP and Authenticator verification required"
        }

    elif risk_level == "critical":
        return {
            "access_granted": False,
            "authentication_required": "blocked",
            "message": "Login blocked due to critical risk"
        }

    return {
        "access_granted": False,
        "authentication_required": "unknown",
        "message": "Invalid risk level"
    }