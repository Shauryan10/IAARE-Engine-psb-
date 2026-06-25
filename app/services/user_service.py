import json
import uuid
from datetime import datetime
from app.services.audit_service import (
    create_security_log,
    get_security_logs
)
from app.services.integration_service import (
    run_complete_security_analysis
)
from app.services.risk_engine_service import calculate_final_risk
from app.services.adaptive_auth_service import (
    process_adaptive_authentication
)

from app.services.behavior_service import (
    calculate_behavior_risk,
    update_behavior
)

from app.services.ip_service import analyze_network_risk
from app.services.device_service import check_device_trust
from app.services.authenticator_service import (
    generate_totp_secret,
    generate_qr_code,
    verify_totp_code
)
from app.services.otp_service import create_otp, verify_otp

from app.services.password_service import hash_password, verify_password
from app.services.sim_security_service import create_sim_profile, calculate_sim_risk

USERS_FILE = "app/storage/users.json"


def load_users():
    with open(USERS_FILE, "r") as file:
        return json.load(file)


def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


def find_user_by_username(username):

    users = load_users()

    print("SEARCHING FOR:", username)
    print("TOTAL USERS:", len(users))

    for user in users:
        print("CHECKING USER:", user.get("username"))

        if user.get("username") == username:
            print("MATCH FOUND")
            return user

    print("NO MATCH FOUND")
    return None


def register_user(data: dict):

    print("REGISTER DATA RECEIVED:", data)

    username = data.get("username")
    password = data.get("password")
    mobile_number = data.get("mobile_number")

    print("USERNAME:", username)
    print("PASSWORD:", password)
    print("MOBILE:", mobile_number)

    existing_user = find_user_by_username(username)
    print("EXISTING USER:", existing_user)

    if existing_user:
        return {
            "status": "failed",
            "message": "Username already exists"
        }

    
    user = {
        "user_id": str(uuid.uuid4()),
        "username": username,
        "password_hash": hash_password(password),
        "mobile_number": mobile_number,
        "created_at": datetime.now().isoformat(),
        "sim_profile": create_sim_profile(mobile_number),
        "failed_login_attempts": 0,
        "locked": False
    }

    users = load_users()
    users.append(user)
    save_users(users)

    return {
        "status": "success",
        "message": "User registered successfully",
        "user_id": user["user_id"]
    }

def login_user(data: dict):
    username = data.get("username")
    password = data.get("password")

    user = find_user_by_username(username)

    if not user:
        return {
            "status": "failed",
            "message": "User not found"
        }

    if user.get("locked"):
        return {
            "status": "blocked",
            "message": "User account is locked"
        }

    if not verify_password(password, user["password_hash"]):
        user["failed_login_attempts"] += 1

        if user["failed_login_attempts"] >= 3:
            user["locked"] = True

        users = load_users()
        for index, existing_user in enumerate(users):
            if existing_user["username"] == username:
                users[index] = user
                break
        save_users(users)

        return {
            "status": "failed",
            "message": "Invalid password",
            "failed_login_attempts": user["failed_login_attempts"]
        }

    user["failed_login_attempts"] = 0

    users = load_users()
    for index, existing_user in enumerate(users):
        if existing_user["username"] == username:
            users[index] = user
            break
    save_users(users)

    sim_risk = calculate_sim_risk(user["sim_profile"])

    return {
        "status": "success",
        "message": "Password verified successfully",
        "user_id": user["user_id"],
        "username": user["username"],
        "password_verified": True,
        "sim_risk": sim_risk
    }

def update_user_record(updated_user):
    users = load_users()

    for index, user in enumerate(users):
        if user["username"] == updated_user["username"]:
            users[index] = updated_user
            break

    save_users(users)


def request_login_otp(username: str):
    user = find_user_by_username(username)

    if not user:
        return {
            "status": "failed",
            "message": "User not found"
        }

    user["sim_profile"]["otp_request_count"] += 1
    update_user_record(user)

    otp_record = create_otp(username)

    return {
        "status": "success",
        "message": "OTP generated successfully",
        "username": username,
        "demo_otp": otp_record["otp"],
        "expires_at": otp_record["expires_at"],
        "sim_profile": user["sim_profile"]
    }


def verify_login_otp(username: str, otp: str):
    user = find_user_by_username(username)

    if not user:
        return {
            "status": "failed",
            "message": "User not found"
        }

    result = verify_otp(username, otp)

    if result["status"] == "failed":
        user["sim_profile"]["otp_failed_attempts"] += 1
        update_user_record(user)

        sim_risk = calculate_sim_risk(user["sim_profile"])

        return {
            "status": "failed",
            "message": result["reason"],
            "sim_risk": sim_risk
        }

    user["sim_profile"]["otp_failed_attempts"] = 0
    update_user_record(user)

    sim_risk = calculate_sim_risk(user["sim_profile"])

    return {
        "status": "success",
        "message": "OTP verified successfully",
        "sim_risk": sim_risk
    }
def setup_authenticator(username: str):
    user = find_user_by_username(username)

    if not user:
        return {
            "status": "failed",
            "message": "User not found"
        }

    secret = generate_totp_secret()
    qr_data = generate_qr_code(username, secret)

    user["totp_secret"] = secret
    user["authenticator_enabled"] = True

    update_user_record(user)

    return {
        "status": "success",
        "message": "Authenticator setup successful",
        "username": username,
        "totp_secret": secret,
        "qr_path": qr_data["qr_path"],
        "totp_uri": qr_data["totp_uri"]
    }


def verify_authenticator(username: str, totp_code: str):
    user = find_user_by_username(username)

    if not user:
        return {
            "status": "failed",
            "message": "User not found"
        }

    if not user.get("authenticator_enabled"):
        return {
            "status": "failed",
            "message": "Authenticator not enabled"
        }

    is_valid = verify_totp_code(user["totp_secret"], totp_code)

    if not is_valid:
        user["sim_profile"]["otp_failed_attempts"] += 1
        update_user_record(user)

        sim_risk = calculate_sim_risk(user["sim_profile"])

        return {
            "status": "failed",
            "message": "Invalid authenticator code",
            "sim_risk": sim_risk
        }

    sim_risk = calculate_sim_risk(user["sim_profile"])

    return {
        "status": "success",
        "message": "Authenticator verified successfully",
        "totp_verified": True,
        "sim_risk": sim_risk
    }

def check_user_device(username: str, device_info: dict):
    user = find_user_by_username(username)

    if not user:
        return {
            "status": "failed",
            "message": "User not found"
        }

    sim_risk = calculate_sim_risk(user["sim_profile"])
    device_result = check_device_trust(
        username,
        device_info,
        sim_risk["sim_risk_status"]
    )

    combined_risk_score = min(
        sim_risk["sim_risk_score"] + device_result["device_risk_score"],
        100
    )

    if combined_risk_score >= 80:
        decision = "block"
        risk_level = "critical"
    elif combined_risk_score >= 60:
        decision = "require_otp_plus_authenticator"
        risk_level = "high"
    elif combined_risk_score >= 30:
        decision = "require_otp"
        risk_level = "medium"
    else:
        decision = "allow"
        risk_level = "safe"

    return {
        "status": "success",
        "username": username,
        "sim_risk": sim_risk,
        "device_result": device_result,
        "combined_risk_score": combined_risk_score,
        "combined_risk_level": risk_level,
        "adaptive_decision": decision
    }

def check_network_security(username: str, ip_address: str):
    user = find_user_by_username(username)

    if not user:
        return {
            "status": "failed",
            "message": "User not found"
        }

    network_result = analyze_network_risk(username, ip_address)

    return {
        "status": "success",
        "username": username,
        "network_security": network_result
    }

def analyze_behavior(
    username,
    location,
    device_name
):
    current_hour = datetime.now().hour

    behavior_result = calculate_behavior_risk(
        username,
        current_hour,
        location,
        device_name
    )

    update_behavior(
        username,
        current_hour,
        location,
        device_name
    )

    return {
        "status": "success",
        "username": username,
        "behavior_analysis": behavior_result
    }

def calculate_complete_risk(data: dict):
    sim_risk_score = data.get("sim_risk_score", 0)
    device_risk_score = data.get("device_risk_score", 0)
    network_risk_score = data.get("network_risk_score", 0)
    behavior_risk_score = data.get("behavior_risk_score", 0)

    result = calculate_final_risk(
        sim_risk_score,
        device_risk_score,
        network_risk_score,
        behavior_risk_score
    )

    return {
        "status": "success",
        "message": "Final adaptive risk score calculated successfully",
        "final_risk_analysis": result
    }

def adaptive_login_decision(data: dict):

    risk_level = data.get("risk_level")

    result = process_adaptive_authentication(
        risk_level
    )

    return {
        "status": "success",
        "risk_level": risk_level,
        "adaptive_authentication": result
    }

def log_security_event(data: dict):

    result = create_security_log(
        username=data.get("username"),
        ip_address=data.get("ip_address"),
        location=data.get("location"),
        device_name=data.get("device_name"),
        sim_risk_score=data.get("sim_risk_score", 0),
        device_risk_score=data.get("device_risk_score", 0),
        network_risk_score=data.get("network_risk_score", 0),
        behavior_risk_score=data.get("behavior_risk_score", 0),
        final_risk_score=data.get("final_risk_score", 0),
        risk_level=data.get("risk_level"),
        authentication_decision=data.get(
            "authentication_decision"
        )
    )

    return {
        "status": "success",
        "message": "Security event logged successfully",
        "log": result
    }


def fetch_security_logs():
    return {
        "status": "success",
        "logs": get_security_logs()
    }

def complete_security_pipeline(data: dict):

    result = run_complete_security_analysis(data)

    return result