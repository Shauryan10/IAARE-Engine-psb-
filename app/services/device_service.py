import json
import hashlib
from datetime import datetime

DEVICE_FILE = "app/storage/device_profiles.json"


def load_devices():
    with open(DEVICE_FILE, "r") as file:
        return json.load(file)


def save_devices(devices):
    with open(DEVICE_FILE, "w") as file:
        json.dump(devices, file, indent=4)


def generate_device_fingerprint(device_info: dict):
    fingerprint_source = json.dumps(device_info, sort_keys=True)
    return hashlib.sha256(fingerprint_source.encode()).hexdigest()


def find_user_devices(username: str):
    devices = load_devices()
    return [device for device in devices if device["username"] == username]


def register_trusted_device(username: str, device_info: dict):
    fingerprint = generate_device_fingerprint(device_info)

    device_record = {
        "username": username,
        "device_name": device_info.get("device_name", "Unknown Device"),
        "device_fingerprint": fingerprint,
        "device_info": device_info,
        "trusted": True,
        "created_at": datetime.now().isoformat(),
        "last_seen_at": datetime.now().isoformat()
    }

    devices = load_devices()
    devices.append(device_record)
    save_devices(devices)

    return device_record


def compare_device_similarity(old_info: dict, new_info: dict):
    total_fields = 0
    matched_fields = 0

    for key, old_value in old_info.items():
        total_fields += 1

        if new_info.get(key) == old_value:
            matched_fields += 1

    if total_fields == 0:
        return 0

    similarity = matched_fields / total_fields
    return similarity


def check_device_trust(username: str, device_info: dict, sim_risk_status: str = "safe"):
    current_fingerprint = generate_device_fingerprint(device_info)
    user_devices = find_user_devices(username)

    if not user_devices:
        new_device = register_trusted_device(username, device_info)

        return {
            "device_status": "first_device_registered",
            "device_risk_score": 0,
            "message": "First device registered as trusted",
            "device_fingerprint": new_device["device_fingerprint"]
        }

    for device in user_devices:
        if device["device_fingerprint"] == current_fingerprint:
            device["last_seen_at"] = datetime.now().isoformat()

            devices = load_devices()
            for index, stored_device in enumerate(devices):
                if (
                    stored_device["username"] == username
                    and stored_device["device_fingerprint"] == current_fingerprint
                ):
                    devices[index] = device
                    break

            save_devices(devices)

            return {
                "device_status": "trusted",
                "device_risk_score": 0,
                "message": "Known trusted device",
                "device_fingerprint": current_fingerprint
            }

    highest_similarity = 0

    for device in user_devices:
        similarity = compare_device_similarity(device["device_info"], device_info)

        if similarity > highest_similarity:
            highest_similarity = similarity

    if highest_similarity >= 0.6:
        risk_score = 20
        status = "known_device_changed_fingerprint"
        message = "Known device detected but fingerprint changed"

    else:
        risk_score = 30
        status = "unknown_device"
        message = "Completely unknown device detected"

    if sim_risk_status in ["high", "critical"]:
        risk_score += 30
        message += " with elevated SIM risk"

    risk_score = min(risk_score, 100)

    return {
        "device_status": status,
        "device_risk_score": risk_score,
        "similarity_score": round(highest_similarity, 2),
        "message": message,
        "device_fingerprint": current_fingerprint
    }