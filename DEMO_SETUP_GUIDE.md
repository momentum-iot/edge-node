# PumpUp Gym Edge Service - Demo Setup Guide

## Overview

This guide will help you set up and demonstrate the PumpUp Gym Edge Service for your IoT project presentation.

## Prerequisites

### Hardware
- ✅ ESP32 WROOM development board
- ✅ PN532 NFC Reader module
- ✅ 3-Point Pulse Heart Rate Sensor
- ✅ NFC cards/tags for testing
- ✅ Breadboard and jumper wires
- ✅ Laptop (for running edge service)

### Software
- ✅ Python 3.13+ installed on laptop
- ✅ Arduino IDE with ESP32 board support
- ✅ WiFi network (for ESP32 to connect to laptop)

## Part 1: Edge Service Setup (Laptop)

### Step 1: Install Dependencies

```bash
cd smart-band-edge-service-master-master
pip install -r requirements.txt
```

### Step 2: Find Your Laptop's IP Address

**Windows (PowerShell):**
```powershell
ipconfig
# Look for IPv4 Address under your WiFi adapter
```

**Linux/Mac:**
```bash
ifconfig
# or
ip addr show
```

Note your IP address (e.g., `192.168.1.100`)

### Step 3: Start the Edge Service

```bash
python app.py
```

You should see:
```
✓ Test device created: gym-esp32-001
  API Key: gym-api-key-2025
✓ Test member created: John Doe (ID: 1)
  NFC UID: 04A1B2C3D4E5F6
  ...
Running on http://0.0.0.0:5000
```

**Keep this terminal open during the demo!**

### Step 4: Test the API (Optional)

Open a new terminal and test:

```bash
curl -X POST http://localhost:5000/api/v1/access/nfc-scan \
  -H "X-API-Key: gym-api-key-2025" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"gym-esp32-001","nfc_uid":"04A1B2C3D4E5F6"}'
```

You should get a check-in response.

## Part 2: ESP32 Hardware Setup

### Wiring Diagram

#### PN532 NFC Reader (I2C Mode)
```
PN532          ESP32
------         -----
VCC    ---->   3.3V
GND    ---->   GND
SDA    ---->   GPIO21 (SDA)
SCL    ---->   GPIO22 (SCL)
```

#### 3-Point Pulse Sensor
```
Pulse Sensor   ESP32
------------   -----
VCC    ---->   3.3V
GND    ---->   GND
Signal ---->   GPIO34 (Analog)
```

### PN532 Switch Configuration

Make sure PN532 is in **I2C mode**:
- Check the DIP switches on the back
- Typically: `ON OFF` or refer to your module's documentation

## Part 3: ESP32 Software Setup

### Step 1: Install Required Libraries

In Arduino IDE, install:
1. **ESP32 Board Support**
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://dl.espressif.com/dl/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "ESP32" → Install

2. **Libraries** (Sketch → Include Library → Manage Libraries)
   - `Adafruit PN532` (for NFC)
   - `ArduinoJson` (for HTTP communication)
   - `WiFi` (usually pre-installed with ESP32)

### Step 2: Configure ESP32 Code

1. Open `ESP32_CLIENT_EXAMPLE.ino`

2. Update these lines:
   ```cpp
   const char* WIFI_SSID = "YOUR_WIFI_SSID";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   const char* EDGE_SERVICE_URL = "http://192.168.1.100:5000";  // YOUR LAPTOP IP
   ```

3. Select board:
   - Tools → Board → ESP32 Arduino → ESP32 Dev Module

4. Select port:
   - Tools → Port → (your ESP32 COM port)

5. Upload:
   - Sketch → Upload

### Step 3: Monitor Serial Output

- Tools → Serial Monitor
- Set baud rate to **115200**

You should see:
```
=== PumpUp Gym ESP32 Client ===
Connecting to WiFi...
WiFi connected!
IP Address: 192.168.1.150
Initializing PN532...
Found PN532 with firmware version: ...
System ready!
Waiting for NFC card...
```

## Part 4: Register Your NFC Card

### Method 1: Read the UID First

1. Place your NFC card near the PN532
2. Check Serial Monitor - it will show the UID (e.g., `A1B2C3D4`)
3. Add it to the database

### Method 2: Add to Database

**Option A: Using Python** (while edge service is running)

Open a new terminal:

```python
python
```

Then:
```python
from iam.infrastructure.models import Member
from datetime import datetime, timedelta

Member.create(
    nfc_uid="A1B2C3D4",  # Your actual NFC UID
    name="Demo User",
    email="demo@pumpup.com",
    membership_status="active",
    membership_expiry=datetime.now() + timedelta(days=30),
    created_at=datetime.now()
)
print("Member added!")
exit()
```

**Option B: Use the test member**
- The system creates a test member with UID: `04A1B2C3D4E5F6`
- Program this UID into your NFC card if possible
- Or use the actual UID your card reports

## Part 5: Demo Workflow

### Scenario: Complete Gym Visit

#### 1. Member Check-In
- **Action**: Place NFC card near PN532
- **Expected**:
  - ESP32 Serial: "✓ Check-in successful! Member: Demo User"
  - LED blinks 2 times
  - Edge Service logs the check-in

#### 2. Start Equipment Session
- **Action**: Happens automatically after check-in
- **Expected**:
  - ESP32 Serial: "✓ Equipment session started! Session ID: 1"
  - LED blinks 1 time

#### 3. Heart Rate Monitoring
- **Action**: Place finger on pulse sensor
- **Expected**:
  - ESP32 Serial shows: "Heart Rate: 75 BPM" (every 5 seconds)
  - Edge service logs each BPM reading

#### 4. Member Check-Out
- **Action**: Place same NFC card near PN532 again
- **Expected**:
  - ESP32 Serial: "✓ Check-out successful!"
  - Equipment session automatically ends
  - LED blinks 2 times

### Check Occupancy

While someone is checked in:

```bash
curl http://localhost:5000/api/v1/access/occupancy \
  -H "X-API-Key: gym-api-key-2025"
```

Response:
```json
{
  "current_occupancy": 1,
  "timestamp": "2025-11-26T14:30:00"
}
```

## Part 6: Viewing the Data

### SQLite Database

Install SQLite browser or use command line:

```bash
sqlite3 gym_edge.db

# View members
SELECT * FROM members;

# View check-ins
SELECT * FROM check_ins;

# View equipment sessions
SELECT * FROM equipment_sessions;

# View heart rate records
SELECT * FROM heart_rate_records ORDER BY measured_at DESC LIMIT 10;

# Exit
.exit
```

### Example Queries

**Active check-ins:**
```sql
SELECT m.name, ci.check_in_time, ci.check_out_time
FROM check_ins ci
JOIN members m ON ci.member_id = m.id
WHERE ci.check_out_time IS NULL;
```

**Session with BPM data:**
```sql
SELECT 
    es.id as session_id,
    m.name,
    e.name as equipment,
    es.start_time,
    es.end_time,
    COUNT(hr.id) as bpm_readings,
    AVG(hr.bpm) as avg_bpm
FROM equipment_sessions es
JOIN members m ON es.member_id = m.id
JOIN equipment e ON es.equipment_id = e.id
LEFT JOIN heart_rate_records hr ON hr.session_id = es.id
GROUP BY es.id;
```

## Troubleshooting

### ESP32 Can't Connect to WiFi
- ✅ Check SSID and password
- ✅ Ensure 2.4GHz network (ESP32 doesn't support 5GHz)
- ✅ Check if laptop and ESP32 are on same network

### PN532 Not Detected
- ✅ Check wiring (especially SDA/SCL)
- ✅ Verify I2C mode switches
- ✅ Try different I2C pins if needed

### "Device not found" Error
- ✅ Check API key in ESP32 code matches edge service
- ✅ Verify device_id is correct
- ✅ Ensure edge service is running

### Pulse Sensor Not Reading
- ✅ Check wiring to GPIO34
- ✅ Place finger firmly on sensor
- ✅ Adjust reading formula in code if needed

### "Member not found" Error
- ✅ Check NFC UID matches database
- ✅ Verify member was created successfully
- ✅ Try rescanning the card

## Demo Presentation Tips

### What to Show

1. **Architecture Diagram**
   - Show `docs/architecture-diagram.puml`
   - Explain DDD bounded contexts

2. **Live Demo**
   - Start with laptop showing running edge service
   - Show ESP32 serial monitor
   - Demonstrate full workflow

3. **Database Queries**
   - Show real-time data being stored
   - Display occupancy tracking
   - Show BPM trends

4. **Code Walkthrough**
   - Brief overview of domain entities
   - Show API endpoints
   - Demonstrate offline capabilities (disconnect WiFi briefly)

### Talking Points

- ✅ **Local-first architecture**: Runs on laptop, no cloud needed for demo
- ✅ **Domain-Driven Design**: Clean separation of concerns
- ✅ **RESTful API**: Easy integration with any client
- ✅ **Real IoT hardware**: Not just simulation
- ✅ **Practical use case**: Solves real gym management problems

## Reset Demo Data

To start fresh:

```bash
# Stop the edge service (Ctrl+C)

# Delete database
rm gym_edge.db

# Restart service
python app.py
```

This recreates test data automatically.

## Additional Resources

- **Full API Documentation**: `API_DOCUMENTATION.md`
- **Project README**: `README.md`
- **Architecture Diagram**: `docs/architecture-diagram.puml`
- **ESP32 Example Code**: `ESP32_CLIENT_EXAMPLE.ino`

## Support

If you encounter issues during setup:
1. Check this guide thoroughly
2. Review error messages in serial monitor
3. Check edge service logs
4. Verify all connections and configurations

---

**Good luck with your demo! 🎉**
