"""Flask application entry point for the PumpUp Gym Edge Service."""

from flask import Flask

import iam.application.services
import health.application.services
from health.interfaces.services import equipment_api
from iam.interfaces.services import iam_api
from shared.infrastructure.database import init_db

app = Flask(__name__)
app.register_blueprint(iam_api)
app.register_blueprint(equipment_api)

def initialize_service():
    """Initialize the database and create test data."""
    init_db()
    
    # Create test device (ESP32)
    auth_service = iam.application.services.AuthApplicationService()
    device = auth_service.get_or_create_test_device()
    print(f"✓ Test device created: {device.device_id}")
    print(f"  API Key: {device.api_key}")
    
    # Create test member
    access_service = iam.application.services.AccessControlApplicationService()
    member = access_service.get_or_create_test_member()
    print(f"✓ Test member created: {member.name} (ID: {member.id})")
    print(f"  NFC UID: {member.nfc_uid}")
    print(f"  Membership: {member.membership_status} until {member.membership_expiry.date()}")
    
    # Create test equipment
    equipment_service = health.application.services.EquipmentSessionApplicationService()
    equipment = equipment_service.get_or_create_test_equipment()
    print(f"✓ Test equipment created: {equipment.name} (ID: {equipment.id})")
    print(f"  Type: {equipment.equipment_type}")
    
    print("\n=== PumpUp Gym Edge Service Ready ===")
    print("Available endpoints:")
    print("  POST /api/v1/access/nfc-scan - Check-in/Check-out with NFC")
    print("  GET  /api/v1/access/occupancy - Get current gym occupancy")
    print("  POST /api/v1/equipment/session/start - Start equipment session")
    print("  POST /api/v1/equipment/session/end - End equipment session")
    print("  POST /api/v1/equipment/heart-rate - Record heart rate data")

if __name__ == "__main__":
    initialize_service()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
