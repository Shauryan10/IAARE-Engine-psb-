import json
import random
from datetime import datetime, timedelta

OTP_FILE = "app/storage/otp_store.json"
OTP_EXPIRY_MINUTES = 5


def load_otps():
    with open(OTP_FILE, "r") as file:
        return json.load(file)


def save_otps(otps):
    with open(OTP_FILE, "w") as file:
        json.dump(otps, file, indent=4)


def generate_otp():
    return str(random.randint(100000, 999999))


def create_otp(username: str):
    otp = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otps = load_otps()

    otps = [item for item in otps if item["username"] != username]

    otp_record = {
        "username": username,
        "otp": otp,
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at.isoformat(),
        "verified": False
    }

    otps.append(otp_record)
    save_otps(otps)

    return otp_record


def verify_otp(username: str, entered_otp: str):
    otps = load_otps()

    for otp_record in otps:
        if otp_record["username"] == username:
            expires_at = datetime.fromisoformat(otp_record["expires_at"])

            if datetime.now() > expires_at:
                return {
                    "status": "failed",
                    "reason": "OTP expired"
                }

            if otp_record["otp"] != entered_otp:
                return {
                    "status": "failed",
                    "reason": "Invalid OTP"
                }

            otp_record["verified"] = True
            save_otps(otps)

            return {
                "status": "success",
                "message": "OTP verified successfully"
            }

    return {
        "status": "failed",
        "reason": "OTP not found"
    }