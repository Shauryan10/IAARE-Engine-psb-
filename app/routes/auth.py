from fastapi import APIRouter, HTTPException, Request
from app.services.ip_service import get_client_ip

from app.services.user_service import (
    register_user,
    login_user,
    request_login_otp,
    verify_login_otp,
    setup_authenticator,
    verify_authenticator,
    check_user_device,
    check_network_security,
    analyze_behavior,
    calculate_complete_risk,
    adaptive_login_decision,
    log_security_event,
    fetch_security_logs
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(data: dict):
    result = register_user(data)

    if result["status"] == "failed":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.post("/login")
def login(data: dict):
    result = login_user(data)

    if result["status"] == "failed":
        raise HTTPException(status_code=401, detail=result)

    if result["status"] == "blocked":
        raise HTTPException(status_code=403, detail=result["message"])

    return result

@router.post("/request-otp")
def request_otp(data: dict):
    username = data.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    result = request_login_otp(username)

    if result["status"] == "failed":
        raise HTTPException(status_code=404, detail=result["message"])

    return result


@router.post("/verify-otp")
def verify_otp_route(data: dict):
    username = data.get("username")
    otp = data.get("otp")

    if not username or not otp:
        raise HTTPException(status_code=400, detail="Username and OTP are required")

    result = verify_login_otp(username, otp)

    if result["status"] == "failed":
        raise HTTPException(status_code=401, detail=result)

    return result


@router.post("/setup-authenticator")
def setup_authenticator_route(data: dict):
    username = data.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    result = setup_authenticator(username)

    if result["status"] == "failed":
        raise HTTPException(status_code=404, detail=result["message"])

    return result


@router.post("/verify-authenticator")
def verify_authenticator_route(data: dict):
    username = data.get("username")
    totp_code = data.get("totp_code")

    if not username or not totp_code:
        raise HTTPException(status_code=400, detail="Username and TOTP code are required")

    result = verify_authenticator(username, totp_code)

    if result["status"] == "failed":
        raise HTTPException(status_code=401, detail=result)

    return result


@router.post("/check-device")
def check_device_route(data: dict):
    username = data.get("username")
    device_info = data.get("device_info")

    if not username or not device_info:
        raise HTTPException(
            status_code=400,
            detail="Username and device_info are required"
        )

    result = check_user_device(username, device_info)

    if result["status"] == "failed":
        raise HTTPException(status_code=404, detail=result["message"])

    return result


@router.post("/check-network")
def check_network_route(data: dict, request: Request):
    username = data.get("username")
    ip_address = data.get("ip_address")

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username is required"
        )

    if not ip_address:
        ip_address = get_client_ip(request)

    result = check_network_security(username, ip_address)

    if result["status"] == "failed":
        raise HTTPException(status_code=404, detail=result["message"])

    return result

@router.post("/analyze-behavior")
def analyze_behavior_route(data: dict):

    username = data.get("username")
    location = data.get("location")
    device_name = data.get("device_name")

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username required"
        )

    result = analyze_behavior(
        username,
        location,
        device_name
    )

    return result

@router.post("/calculate-risk")
def calculate_risk_route(data: dict):
    result = calculate_complete_risk(data)
    return result

@router.post("/adaptive-auth")
def adaptive_auth_route(data: dict):

    result = adaptive_login_decision(data)

    return result

@router.post("/security-log")
def security_log_route(data: dict):

    return log_security_event(data)


@router.get("/security-logs")
def security_logs_route():

    return fetch_security_logs()