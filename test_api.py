# PumpUp Gym Edge Service - Test Script
# Run this after starting the edge service to verify all endpoints work correctly

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_KEY = "gym-api-key-2025"
DEVICE_ID = "gym-esp32-001"
TEST_NFC_UID = "04A1B2C3D4E5F6"  # Test member's NFC UID

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def print_test(test_name):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print('='*60)

def print_response(response):
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

# Test 1: Check-in
print_test("1. Member Check-in with NFC")
response = requests.post(
    f"{BASE_URL}/api/v1/access/nfc-scan",
    headers=headers,
    json={
        "device_id": DEVICE_ID,
        "nfc_uid": TEST_NFC_UID
    }
)
checkin_data = print_response(response)
member_id = checkin_data.get("member_id")

assert response.status_code == 200, "Check-in failed!"
assert checkin_data["success"], "Check-in was not successful!"
assert checkin_data["action"] == "check_in", "Expected check_in action!"
print("✓ Check-in successful!")

# Test 2: Get Occupancy
print_test("2. Get Current Occupancy")
response = requests.get(
    f"{BASE_URL}/api/v1/access/occupancy",
    headers=headers,
    params={"device_id": DEVICE_ID}
)
occupancy_data = print_response(response)

assert response.status_code == 200, "Occupancy check failed!"
assert occupancy_data["current_occupancy"] >= 1, "Occupancy should be at least 1!"
print(f"✓ Current occupancy: {occupancy_data['current_occupancy']}")

# Test 3: Start Equipment Session
print_test("3. Start Equipment Session")
response = requests.post(
    f"{BASE_URL}/api/v1/equipment/session/start",
    headers=headers,
    json={
        "device_id": DEVICE_ID,
        "member_id": member_id,
        "equipment_id": 1
    }
)
session_data = print_response(response)
session_id = session_data.get("session_id")

assert response.status_code == 201, "Session start failed!"
assert session_data["success"], "Session start was not successful!"
print(f"✓ Equipment session started! Session ID: {session_id}")

# Test 4: Record Heart Rate (multiple readings)
print_test("4. Record Heart Rate Data")
bpm_values = [72.5, 85.0, 92.5, 88.0, 95.5]

for i, bpm in enumerate(bpm_values, 1):
    response = requests.post(
        f"{BASE_URL}/api/v1/equipment/heart-rate",
        headers=headers,
        json={
            "device_id": DEVICE_ID,
            "session_id": session_id,
            "member_id": member_id,
            "bpm": bpm
        }
    )
    hr_data = print_response(response)
    
    assert response.status_code == 201, f"Heart rate recording {i} failed!"
    assert hr_data["success"], f"Heart rate recording {i} was not successful!"
    print(f"  ✓ Reading {i}: {bpm} BPM recorded")

print(f"✓ All {len(bpm_values)} heart rate readings recorded!")

# Test 5: End Equipment Session
print_test("5. End Equipment Session")
response = requests.post(
    f"{BASE_URL}/api/v1/equipment/session/end",
    headers=headers,
    json={
        "device_id": DEVICE_ID,
        "member_id": member_id
    }
)
end_session_data = print_response(response)

assert response.status_code == 200, "Session end failed!"
assert end_session_data["success"], "Session end was not successful!"
print("✓ Equipment session ended!")

# Test 6: Check-out
print_test("6. Member Check-out with NFC")
response = requests.post(
    f"{BASE_URL}/api/v1/access/nfc-scan",
    headers=headers,
    json={
        "device_id": DEVICE_ID,
        "nfc_uid": TEST_NFC_UID
    }
)
checkout_data = print_response(response)

assert response.status_code == 200, "Check-out failed!"
assert checkout_data["success"], "Check-out was not successful!"
assert checkout_data["action"] == "check_out", "Expected check_out action!"
print("✓ Check-out successful!")

# Test 7: Verify Occupancy is Zero
print_test("7. Verify Occupancy After Check-out")
response = requests.get(
    f"{BASE_URL}/api/v1/access/occupancy",
    headers=headers,
    params={"device_id": DEVICE_ID}
)
final_occupancy = print_response(response)

assert response.status_code == 200, "Final occupancy check failed!"
assert final_occupancy["current_occupancy"] == 0, "Occupancy should be 0 after check-out!"
print("✓ Occupancy is correctly 0!")

# Test 8: Invalid NFC UID (Access Denied)
print_test("8. Test Access Denied (Invalid NFC)")
response = requests.post(
    f"{BASE_URL}/api/v1/access/nfc-scan",
    headers=headers,
    json={
        "device_id": DEVICE_ID,
        "nfc_uid": "INVALID_UID_999"
    }
)
denied_data = print_response(response)

assert response.status_code == 403, "Should return 403 for invalid member!"
assert not denied_data["success"], "Should not succeed for invalid member!"
print("✓ Access correctly denied for invalid NFC!")

# Test 9: Invalid BPM (Out of Range)
print_test("9. Test Invalid BPM Value")
# First check-in and start session again
requests.post(
    f"{BASE_URL}/api/v1/access/nfc-scan",
    headers=headers,
    json={"device_id": DEVICE_ID, "nfc_uid": TEST_NFC_UID}
)
session_response = requests.post(
    f"{BASE_URL}/api/v1/equipment/session/start",
    headers=headers,
    json={"device_id": DEVICE_ID, "member_id": member_id, "equipment_id": 1}
)
new_session_id = session_response.json()["session_id"]

# Try invalid BPM
response = requests.post(
    f"{BASE_URL}/api/v1/equipment/heart-rate",
    headers=headers,
    json={
        "device_id": DEVICE_ID,
        "session_id": new_session_id,
        "member_id": member_id,
        "bpm": 250  # Invalid: too high
    }
)
invalid_bpm = print_response(response)

assert response.status_code == 400, "Should return 400 for invalid BPM!"
assert not invalid_bpm["success"], "Should not succeed for invalid BPM!"
print("✓ Invalid BPM correctly rejected!")

# Cleanup
requests.post(
    f"{BASE_URL}/api/v1/equipment/session/end",
    headers=headers,
    json={"device_id": DEVICE_ID, "member_id": member_id}
)
requests.post(
    f"{BASE_URL}/api/v1/access/nfc-scan",
    headers=headers,
    json={"device_id": DEVICE_ID, "nfc_uid": TEST_NFC_UID}
)

# Summary
print("\n" + "="*60)
print("ALL TESTS PASSED! ✓✓✓")
print("="*60)
print("\nThe PumpUp Gym Edge Service is working correctly!")
print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
