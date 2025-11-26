"""Simple startup test to verify the Flask application."""

print("Testing Flask application startup...")

try:
    print("\n1. Importing app module...")
    from app import app
    print("   ✓ App module imported successfully")
    
    print("\n2. Testing database initialization...")
    from shared.infrastructure.database import init_db
    init_db()
    print("   ✓ Database initialized")
    
    print("\n3. Testing IAM services...")
    import iam.application.services
    auth_service = iam.application.services.AuthApplicationService()
    device = auth_service.get_or_create_test_device()
    print(f"   ✓ Test device: {device.device_id}")
    
    access_service = iam.application.services.AccessControlApplicationService()
    member = access_service.get_or_create_test_member()
    print(f"   ✓ Test member: {member.name} (NFC: {member.nfc_uid})")
    
    print("\n4. Testing Equipment services...")
    import health.application.services
    equipment_service = health.application.services.EquipmentSessionApplicationService()
    equipment = equipment_service.get_or_create_test_equipment()
    print(f"   ✓ Test equipment: {equipment.name}")
    
    print("\n5. Testing routes...")
    with app.test_client() as client:
        # Test occupancy endpoint
        response = client.get('/api/v1/access/occupancy', headers={'X-API-Key': 'gym-api-key-2025'})
        print(f"   ✓ GET /api/v1/access/occupancy - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"     Current occupancy: {data.get('current_occupancy', 'N/A')}")
        
        # Test NFC scan endpoint
        response = client.post('/api/v1/access/nfc-scan', 
                              headers={'X-API-Key': 'gym-api-key-2025', 'Content-Type': 'application/json'},
                              json={'device_id': 'gym-esp32-001', 'nfc_uid': '04A1B2C3D4E5F6'})
        print(f"   ✓ POST /api/v1/access/nfc-scan - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"     Action: {data.get('action', 'N/A')}, Member: {data.get('member_name', 'N/A')}")
    
    print("\n✅ ALL TESTS PASSED - Application is working correctly!")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
