import json
from datetime import datetime

LOG_FILE = "app/storage/security_logs.json"


def load_logs():
    with open(LOG_FILE, "r") as file:
        return json.load(file)


def save_logs(logs):
    with open(LOG_FILE, "w") as file:
        json.dump(logs, file, indent=4)


def create_security_log(
    username,
    ip_address,
    location,
    device_name,
    sim_risk_score,
    device_risk_score,
    network_risk_score,
    behavior_risk_score,
    final_risk_score,
    risk_level,
    authentication_decision
):
    logs = load_logs()

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "ip_address": ip_address,
        "location": location,
        "device_name": device_name,
        "sim_risk_score": sim_risk_score,
        "device_risk_score": device_risk_score,
        "network_risk_score": network_risk_score,
        "behavior_risk_score": behavior_risk_score,
        "final_risk_score": final_risk_score,
        "risk_level": risk_level,
        "authentication_decision": authentication_decision
    }

    logs.append(log_entry)

    save_logs(logs)

    return log_entry


def get_security_logs():
    return load_logs()