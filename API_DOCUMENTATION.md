# PumpUp Gym Edge Service - API Documentation

## Overview

The PumpUp Gym Edge Service is an IoT edge solution for gym access control and equipment usage tracking. It runs locally on a laptop and interfaces with:

- **PN532 NFC Reader** (for member check-in/check-out)
- **Heart Rate Sensor** (3-point pulse sensor)
- **ESP32 WROOM** (main IoT device controller)

## Base URL

```
http://localhost:5000
```

## Authentication

All endpoints require authentication via HTTP headers:

```http
X-API-Key: gym-api-key-2025
```

And for most POST requests, include `device_id` in the JSON body:

```json
{
  "device_id": "gym-esp32-001",
  ...
}
```

## Endpoints

### 1. NFC Access Control

#### POST `/api/v1/access/nfc-scan`

Process NFC card scan for check-in or check-out. The system automatically determines whether to check-in or check-out based on the member's current status.

**Request:**
```http
POST /api/v1/access/nfc-scan
X-API-Key: gym-api-key-2025
Content-Type: application/json

{
  "device_id": "gym-esp32-001",
  "nfc_uid": "04A1B2C3D4E5F6"
}
```

**Response (Check-in):**
```json
{
  "success": true,
  "action": "check_in",
  "member_id": 1,
  "member_name": "John Doe",
  "check_in_id": 1,
  "check_in_time": "2025-11-26T10:30:00",
  "current_occupancy": 1
}
```

**Response (Check-out):**
```json
{
  "success": true,
  "action": "check_out",
  "member_id": 1,
  "member_name": "John Doe",
  "check_in_id": 1,
  "check_in_time": "2025-11-26T10:30:00",
  "check_out_time": "2025-11-26T11:45:00",
  "current_occupancy": 0
}
```

**Response (Access Denied):**
```json
{
  "success": false,
  "action": "denied",
  "reason": "Membership expired",
  "member_id": 1,
  "member_name": "John Doe"
}
```

---

### 2. Gym Occupancy

#### GET `/api/v1/access/occupancy`

Get the current number of people in the gym.

**Request:**
```http
GET /api/v1/access/occupancy?device_id=gym-esp32-001
X-API-Key: gym-api-key-2025
```

**Response:**
```json
{
  "current_occupancy": 5,
  "timestamp": "2025-11-26T11:00:00"
}
```

---

### 3. Equipment Session Management

#### POST `/api/v1/equipment/session/start`

Start a new equipment usage session when a member begins using a machine.

**Request:**
```http
POST /api/v1/equipment/session/start
X-API-Key: gym-api-key-2025
Content-Type: application/json

{
  "device_id": "gym-esp32-001",
  "member_id": 1,
  "equipment_id": 1
}
```

**Response (Success):**
```json
{
  "success": true,
  "session_id": 1,
  "member_id": 1,
  "equipment_id": 1,
  "start_time": "2025-11-26T10:35:00"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Member already has an active equipment session",
  "active_session_id": 1
}
```

---

#### POST `/api/v1/equipment/session/end`

End the current equipment usage session for a member.

**Request:**
```http
POST /api/v1/equipment/session/end
X-API-Key: gym-api-key-2025
Content-Type: application/json

{
  "device_id": "gym-esp32-001",
  "member_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "session_id": 1,
  "member_id": 1,
  "equipment_id": 1,
  "start_time": "2025-11-26T10:35:00",
  "end_time": "2025-11-26T11:00:00"
}
```

---

### 4. Heart Rate Recording

#### POST `/api/v1/equipment/heart-rate`

Record a heart rate measurement during an equipment session.

**Request:**
```http
POST /api/v1/equipment/heart-rate
X-API-Key: gym-api-key-2025
Content-Type: application/json

{
  "device_id": "gym-esp32-001",
  "session_id": 1,
  "member_id": 1,
  "bpm": 145.5
}
```

**Response:**
```json
{
  "success": true,
  "record_id": 1,
  "session_id": 1,
  "member_id": 1,
  "bpm": 145.5,
  "measured_at": "2025-11-26T10:40:00"
}
```

**Validation:**
- BPM must be between 30 and 220
- Session must be active (not ended)
- Member ID must match the session

---

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Missing device_id or X-API-Key"
}
```

### 400 Bad Request
```json
{
  "error": "Missing required field: nfc_uid"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "action": "denied",
  "reason": "Membership expired"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "No active session found for member"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal error: [details]"
}
```

---

## Typical Usage Flow

1. **Member arrives at gym:**
   - ESP32 reads NFC card via PN532
   - POST to `/api/v1/access/nfc-scan`
   - Member is checked in

2. **Member starts using equipment:**
   - POST to `/api/v1/equipment/session/start`
   - Session is created

3. **During workout:**
   - ESP32 continuously reads heart rate sensor
   - POST to `/api/v1/equipment/heart-rate` every 5-10 seconds
   - BPM data is recorded

4. **Member finishes workout:**
   - POST to `/api/v1/equipment/session/end`
   - Session is closed

5. **Member leaves gym:**
   - ESP32 reads NFC card via PN532
   - POST to `/api/v1/access/nfc-scan`
   - Member is checked out

6. **Check occupancy:**
   - GET `/api/v1/access/occupancy`
   - Returns current number of members in gym

---

## Testing with cURL

### Check-in
```bash
curl -X POST http://localhost:5000/api/v1/access/nfc-scan \
  -H "X-API-Key: gym-api-key-2025" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"gym-esp32-001","nfc_uid":"04A1B2C3D4E5F6"}'
```

### Start Session
```bash
curl -X POST http://localhost:5000/api/v1/equipment/session/start \
  -H "X-API-Key: gym-api-key-2025" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"gym-esp32-001","member_id":1,"equipment_id":1}'
```

### Record Heart Rate
```bash
curl -X POST http://localhost:5000/api/v1/equipment/heart-rate \
  -H "X-API-Key: gym-api-key-2025" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"gym-esp32-001","session_id":1,"member_id":1,"bpm":145.5}'
```

### End Session
```bash
curl -X POST http://localhost:5000/api/v1/equipment/session/end \
  -H "X-API-Key: gym-api-key-2025" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"gym-esp32-001","member_id":1}'
```

### Check Occupancy
```bash
curl -X GET "http://localhost:5000/api/v1/access/occupancy?device_id=gym-esp32-001" \
  -H "X-API-Key: gym-api-key-2025"
```

### Check-out
```bash
curl -X POST http://localhost:5000/api/v1/access/nfc-scan \
  -H "X-API-Key: gym-api-key-2025" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"gym-esp32-001","nfc_uid":"04A1B2C3D4E5F6"}'
```
