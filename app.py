"""Flask application entry point for the PumpUp Gym Edge Service."""

import os
from pathlib import Path


def load_env_file(path: str = ".env") -> None:
    """Load key=value pairs from a .env file into os.environ if not already set."""
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        os.environ.setdefault(key, value)


load_env_file()

from flask import Flask  # noqa: E402

import iam.application.services  # noqa: E402
from health.interfaces.services import equipment_api  # noqa: E402
from iam.interfaces.services import iam_api  # noqa: E402
from shared.infrastructure.database import init_db  # noqa: E402

app = Flask(__name__)
app.register_blueprint(iam_api)
app.register_blueprint(equipment_api)


def initialize_service():
    """Initialize the database and create test data."""
    init_db()

    # Create test device (ESP32)
    auth_service = iam.application.services.AuthApplicationService()
    device = auth_service.get_or_create_test_device()
    print(f"* Test device created: {device.device_id}")
    print(f"  API Key: {device.api_key}")

    # Create test member
    access_service = iam.application.services.AccessControlApplicationService()
    member = access_service.get_or_create_test_member()
    print(f"* Test member created: {member.name} (ID: {member.id})")
    print(f"  NFC UID: {member.nfc_uid}")
    print(f"  Membership: {member.membership_status} until {member.membership_expiry.date()}")

    print("\n=== PumpUp Gym Edge Service Ready ===")
    print("Available endpoints:")
    print("  POST /api/v1/access/nfc-scan - Check-in/Check-out with NFC")
    print("  GET  /api/v1/access/occupancy - Get current gym occupancy")
    print("  POST /api/check/out - Proxy check-in/out to backend")
    print("  POST /api/heart-rate/<member_id> - Proxy heart rate data to backend")


if __name__ == "__main__":
    initialize_service()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=False, use_reloader=False)
