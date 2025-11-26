
# PumpUp Gym Edge Service

> ✅ **VERSION 1.0 - COMPLETAMENTE FUNCIONAL Y PROBADO**

## Overview

**PumpUp Gym Edge Service** is a Python-based IoT edge application for managing gym access control and equipment usage tracking. It's designed to run locally on a laptop during demonstrations and interfaces with ESP32-based IoT devices.

This service is part of the **PumpUp** ecosystem - a comprehensive gym management solution for independent fitness centers.

**🎉 Estado Actual**: Sistema completo con 9/9 tests pasando exitosamente. Base de datos operativa con 4 check-ins, 3 sesiones de equipo y 15 lecturas de BPM registradas.

## Features

- ✅ **NFC Access Control**: Check-in/check-out members using PN532 NFC reader
- ✅ **Real-time Occupancy Tracking**: Monitor gym capacity in real-time
- ✅ **Equipment Usage Sessions**: Track member equipment usage
- ✅ **Heart Rate Monitoring**: Record BPM data during workouts via 3-point pulse sensor
- ✅ **Local SQLite Storage**: All data stored locally for offline operation
- ✅ **RESTful API**: Clean REST endpoints for ESP32 integration
- ✅ **DDD Architecture**: Domain-Driven Design with clear bounded contexts

## Hardware Requirements

This edge service is designed to work with:

- **ESP32 WROOM** - Main microcontroller
- **PN532 NFC Reader** - For member access control
- **3-Point Pulse Heart Rate Sensor** - For BPM monitoring during equipment use
- **Laptop** - To run the edge service locally (development/demo)

## 🚀 Quick Start (Probado y Funcionando)

```powershell
# 1. Instalar dependencias (si no lo has hecho)
pip install -r requirements.txt

# 2. Iniciar el servidor
python app.py

# 3. Ejecutar tests completos (en otra terminal)
.\run_tests.ps1

# 4. Verificar base de datos
python check_database.py
```

El servidor iniciará en `http://localhost:5000` y `http://192.168.1.40:5000`

**Credenciales de prueba:**
- Device ID: `gym-esp32-001`
- API Key: `gym-api-key-2025`
- NFC de prueba: `04A1B2C3D4E5F6` (miembro John Doe)

## Software Dependencies

- Python 3.13 or higher
- Flask 3.1.1 (web framework)
- Peewee 3.18.1 (SQLite ORM)
- python-dateutil 2.9.0 (date/time handling)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd smart-band-edge-service-master-master
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Service

```bash
python app.py
```

The service will:
- Initialize the SQLite database (`gym_edge.db`)
- Create test data (device, member, equipment)
- Start the Flask server on `http://localhost:5000`

## Quick Start

After starting the service, you'll see test credentials:

```
✓ Test device created: gym-esp32-001
  API Key: gym-api-key-2025
✓ Test member created: John Doe (ID: 1)
  NFC UID: 04A1B2C3D4E5F6
  Membership: active until 2025-12-26
✓ Test equipment created: Test Treadmill (ID: 1)
  Type: treadmill
```

### Test the API

#### 1. Check-in a Member
```bash
curl -X POST http://localhost:5000/api/v1/access/nfc-scan \
  -H "X-API-Key: gym-api-key-2025" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"gym-esp32-001","nfc_uid":"04A1B2C3D4E5F6"}'
```

#### 2. Start Equipment Session
```bash
curl -X POST http://localhost:5000/api/v1/equipment/session/start \
  -H "X-API-Key: gym-api-key-2025" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"gym-esp32-001","member_id":1,"equipment_id":1}'
```

#### 3. Record Heart Rate
```bash
curl -X POST http://localhost:5000/api/v1/equipment/heart-rate \
  -H "X-API-Key: gym-api-key-2025" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"gym-esp32-001","session_id":1,"member_id":1,"bpm":145.5}'
```

#### 4. Check Gym Occupancy
```bash
curl http://localhost:5000/api/v1/access/occupancy \
  -H "X-API-Key: gym-api-key-2025"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/access/nfc-scan` | Check-in/check-out with NFC card |
| GET | `/api/v1/access/occupancy` | Get current gym occupancy |
| POST | `/api/v1/equipment/session/start` | Start equipment usage session |
| POST | `/api/v1/equipment/session/end` | End equipment usage session |
| POST | `/api/v1/equipment/heart-rate` | Record heart rate measurement |

📖 **Full API Documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## Project Structure (Domain-Driven Design)

```
├── app.py                      # Flask application entry point
├── requirements.txt            # Python dependencies
├── gym_edge.db                 # SQLite database (generated)
│
├── shared/                     # Shared infrastructure
│   └── infrastructure/
│       └── database.py         # Database initialization
│
├── iam/                        # Identity & Access Management BC
│   ├── domain/
│   │   ├── entities.py         # Device, Member, CheckIn
│   │   └── services.py         # AuthService, AccessControlService
│   ├── application/
│   │   └── services.py         # Application layer orchestration
│   ├── infrastructure/
│   │   ├── models.py           # Peewee ORM models
│   │   └── repositories.py     # Data access
│   └── interfaces/
│       └── services.py         # REST API endpoints
│
└── health/                     # Equipment Usage BC
    ├── domain/
    │   ├── entities.py         # Equipment, Session, HeartRateRecord
    │   └── services.py         # Business logic
    ├── application/
    │   └── services.py         # Application orchestration
    ├── infrastructure/
    │   ├── models.py           # Peewee ORM models
    │   └── repositories.py     # Data access
    └── interfaces/
        └── services.py         # REST API endpoints
```

## Bounded Contexts

### 1. Identity & Access Management (IAM)
- **Device authentication** (ESP32)
- **Member management** (NFC-based identification)
- **Access control** (check-in/check-out, membership validation)
- **Occupancy tracking**

### 2. Equipment Usage
- **Equipment registry** (gym machines)
- **Usage sessions** (member-equipment interaction)
- **Heart rate monitoring** (BPM tracking during sessions)

## Database Schema

### Tables

#### `devices`
- `device_id` (PK) - ESP32 identifier
- `api_key` - Authentication key
- `created_at` - Registration timestamp

#### `members`
- `id` (PK)
- `nfc_uid` (unique) - NFC card identifier
- `name` - Member name
- `email` - Contact email
- `membership_status` - active/expired/suspended
- `membership_expiry` - Expiration date
- `created_at` - Registration date

#### `check_ins`
- `id` (PK)
- `member_id` (FK)
- `nfc_uid` - Card used
- `check_in_time` - Entry timestamp
- `check_out_time` - Exit timestamp (nullable)
- `created_at` - Record creation

#### `equipment`
- `id` (PK)
- `name` - Equipment name
- `equipment_type` - Type (treadmill, bike, etc.)
- `created_at` - Registration date

#### `equipment_sessions`
- `id` (PK)
- `member_id` - Member using equipment
- `equipment_id` (FK)
- `start_time` - Session start
- `end_time` - Session end (nullable)
- `created_at` - Record creation

#### `heart_rate_records`
- `id` (PK)
- `session_id` (FK)
- `member_id` - Member ID
- `bpm` - Heart rate (30-220)
- `measured_at` - Measurement timestamp
- `created_at` - Record creation

## ESP32 Integration Guide

### Typical Workflow

1. **Initialize ESP32**
   - Connect to WiFi
   - Configure PN532 (I2C/SPI)
   - Configure pulse sensor (analog pin)

2. **Member Check-in**
   ```cpp
   // Read NFC UID
   String nfc_uid = readNFC();
   
   // Send to edge service
   POST /api/v1/access/nfc-scan
   {
     "device_id": "gym-esp32-001",
     "nfc_uid": nfc_uid
   }
   ```

3. **Start Equipment Session**
   ```cpp
   POST /api/v1/equipment/session/start
   {
     "device_id": "gym-esp32-001",
     "member_id": 1,
     "equipment_id": 1
   }
   // Save returned session_id
   ```

4. **Monitor Heart Rate**
   ```cpp
   // Every 5-10 seconds
   float bpm = readPulseSensor();
   
   POST /api/v1/equipment/heart-rate
   {
     "device_id": "gym-esp32-001",
     "session_id": saved_session_id,
     "member_id": 1,
     "bpm": bpm
   }
   ```

5. **End Session & Check-out**
   ```cpp
   // When member stops using equipment
   POST /api/v1/equipment/session/end
   
   // When member leaves gym
   POST /api/v1/access/nfc-scan (same NFC card)
   ```

## Development

### Adding New Members

You can add members directly to the database or create an endpoint. For testing:

```python
from iam.infrastructure.models import Member
from datetime import datetime, timedelta

Member.create(
    nfc_uid="YOUR_NFC_UID_HERE",
    name="Jane Smith",
    email="jane@example.com",
    membership_status="active",
    membership_expiry=datetime.now() + timedelta(days=30),
    created_at=datetime.now()
)
```

### Adding New Equipment

```python
from health.infrastructure.models import Equipment
from datetime import datetime

Equipment.create(
    name="Stationary Bike 1",
    equipment_type="bike",
    created_at=datetime.now()
)
```

## Testing

Use the provided cURL commands in `API_DOCUMENTATION.md` or tools like:
- **Postman**
- **Insomnia**
- **Thunder Client** (VS Code extension)

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
# Windows PowerShell:
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force

# Linux/Mac:
lsof -ti:5000 | xargs kill
```

### Database Issues
```bash
# Delete and recreate database
rm gym_edge.db
python app.py  # Will recreate on startup
```

## Future Enhancements

- [ ] Cloud synchronization (when connection available)
- [ ] Offline buffer for events
- [ ] Analytics dashboard
- [ ] Multi-gym support
- [ ] Advanced reporting
- [ ] Integration with PumpUp cloud platform

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Team - Momentum

**Universidad Peruana de Ciencias Aplicadas (UPC)**  
Course: IoT Solutions  
Cycle: 2025-1

- Daniel Mateo Del Castillo Bueno (U202211212)
- Carlos Sánchez Montero (U202015274)
- Alvaro Pinto Fuentes Rivera (U202213384)
- Leonardo José Solis Solis (U20211G163)
- Gustavo Arturo Poma Espinoza (U20221c138)

## Support

For questions or issues:
1. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. Review the code documentation
3. Contact the development team
