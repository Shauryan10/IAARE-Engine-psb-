from datetime import datetime

from app.services.behavior_service import (
    calculate_behavior_risk,
    update_behavior
)

from app.services.risk_engine_service import (
    calculate_final_risk
)

from app.services.adaptive_auth_service import (
    process_adaptive_authentication
)

from app.services.audit_service import (
    create_security_log
)


def run_complete_security_analysis(data: dict):

    username = data.get("username")
    location = data.get("location")
    device_name = data.get("device_name")
    ip_address = data.get("ip_address")

    sim_risk_score = data.get("sim_risk_score", 0)
    device_risk_score = data.get("device_risk_score", 0)
    network_risk_score = data.get("network_risk_score", 0)

    current_hour = datetime.now().hour

    behavior_result = calculate_behavior_risk(
        username,
        current_hour,
        location,
        device_name
    )

    behavior_risk_score = behavior_result[
        "behavior_risk_score"
    ]

    update_behavior(
        username,
        current_hour,
        location,
        device_name
    )

    risk_result = calculate_final_risk(
        sim_risk_score,
        device_risk_score,
        network_risk_score,
        behavior_risk_score
    )

    adaptive_result = process_adaptive_authentication(
        risk_result["risk_level"]
    )

    create_security_log(
        username=username,
        ip_address=ip_address,
        location=location,
        device_name=device_name,
        sim_risk_score=sim_risk_score,
        device_risk_score=device_risk_score,
        network_risk_score=network_risk_score,
        behavior_risk_score=behavior_risk_score,
        final_risk_score=risk_result["final_risk_score"],
        risk_level=risk_result["risk_level"],
        authentication_decision=adaptive_result[
            "authentication_required"
        ]
    )

    return {
        "status": "success",
        "username": username,
        "behavior_analysis": behavior_result,
        "risk_analysis": risk_result,
        "adaptive_authentication": adaptive_result
    }