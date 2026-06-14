from fastapi import APIRouter, HTTPException
from app.services.user_service import (
    register_user,
    login_user,
    request_login_otp,
    verify_login_otp,
    setup_authenticator,
    verify_authenticator,
    check_user_device,
    check_network_security
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
def check_network_route(data: dict):
    username = data.get("username")
    ip_address = data.get("ip_address")

    if not username or not ip_address:
        raise HTTPException(
            status_code=400,
            detail="Username and ip_address are required"
        )

    result = check_network_security(username, ip_address)

    if result["status"] == "failed":
        raise HTTPException(status_code=404, detail=result["message"])

    return result

    