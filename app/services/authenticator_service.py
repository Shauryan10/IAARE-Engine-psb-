import pyotp
import qrcode
import os


QR_FOLDER = "app/storage/qr_codes"


def ensure_qr_folder():
    if not os.path.exists(QR_FOLDER):
        os.makedirs(QR_FOLDER)


def generate_totp_secret():
    return pyotp.random_base32()


def generate_qr_code(username: str, secret: str):
    ensure_qr_folder()

    issuer_name = "SecureBank IAARE"

    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name=issuer_name
    )

    qr_path = f"{QR_FOLDER}/{username}_totp_qr.png"

    img = qrcode.make(totp_uri)
    img.save(qr_path)

    return {
        "totp_uri": totp_uri,
        "qr_path": qr_path
    }


def verify_totp_code(secret: str, code: str):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)