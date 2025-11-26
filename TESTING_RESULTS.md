# PumpUp Gym Edge Service - Quick Start Guide

## 🎯 Sistema Funcionando Correctamente

Esta primera versión del edge service está completamente funcional y lista para integrarse con el ESP32.

## ✅ Tests Ejecutados y Aprobados

**9/9 tests pasaron exitosamente:**

1. ✅ **Ocupación inicial** - 0 personas en el gimnasio
2. ✅ **Check-in con NFC** - Miembro "John Doe" ingresó correctamente
3. ✅ **Ocupación actualizada** - 1 persona en el gimnasio
4. ✅ **Inicio de sesión en equipo** - Sesión iniciada en Treadmill (ID: 1)
5. ✅ **Registro de ritmo cardíaco** - 5 lecturas BPM (72, 85, 92, 88, 95)
6. ✅ **Fin de sesión en equipo** - Sesión cerrada correctamente
7. ✅ **Check-out con NFC** - Miembro salió del gimnasio
8. ✅ **Ocupación final** - 0 personas en el gimnasio
9. ✅ **NFC inválido** - Acceso denegado correctamente

## 🗄️ Persistencia de Datos Verificada

La base de datos SQLite (`gym_edge.db`) almacena correctamente:

- **Devices**: ESP32 registrado (gym-esp32-001)
- **Members**: Miembros con NFC UID
- **Check-ins**: Historial de entradas/salidas con timestamps
- **Equipment**: Equipos disponibles (Treadmill)
- **Sessions**: Sesiones de uso de equipos con inicio/fin
- **Heart Rate**: Registros de BPM por sesión

## 🚀 Cómo Iniciar el Servicio

### Opción 1: Inicio Manual
```powershell
python app.py
```
El servidor inicia en `http://localhost:5000` y `http://192.168.1.40:5000`

### Opción 2: Ejecutar Tests Completos
```powershell
.\run_tests.ps1
```
Inicia el servidor, ejecuta todos los tests y detiene el servidor automáticamente.

### Opción 3: Verificar Base de Datos
```powershell
python check_database.py
```
Muestra el contenido completo de todas las tablas.

## 📡 Configuración para ESP32

**Credenciales de prueba:**
- Device ID: `gym-esp32-001`
- API Key: `gym-api-key-2025`
- NFC de prueba: `04A1B2C3D4E5F6` (John Doe)

**Servidor URL:**
- Local: `http://192.168.1.40:5000`
- Localhost: `http://127.0.0.1:5000`

**Archivo de referencia:** `ESP32_CLIENT_EXAMPLE.ino`

## 🔧 Arquitectura Implementada

### Bounded Contexts (DDD)
1. **IAM (Identity & Access Management)**
   - Autenticación de dispositivos
   - Gestión de miembros
   - Control de acceso con NFC
   - Check-in/Check-out automático

2. **Equipment (Gestión de Equipos)**
   - Registro de equipos
   - Sesiones de uso
   - Monitoreo de ritmo cardíaco

### Endpoints REST API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/access/nfc-scan` | Check-in/out con tarjeta NFC |
| GET | `/api/v1/access/occupancy` | Ocupación actual del gimnasio |
| POST | `/api/v1/equipment/session/start` | Iniciar uso de equipo |
| POST | `/api/v1/equipment/session/end` | Terminar uso de equipo |
| POST | `/api/v1/equipment/heart-rate` | Registrar lectura de BPM |

## 📊 Flujo de Trabajo del Sistema

```
1. Miembro escanea NFC → Check-in automático
2. Sistema registra entrada y actualiza ocupación
3. Miembro usa equipo → Inicia sesión
4. Sistema monitorea BPM cada 5 segundos
5. Miembro termina ejercicio → Cierra sesión
6. Miembro escanea NFC → Check-out automático
```

## ✨ Características Implementadas

- ✅ Arquitectura Domain-Driven Design (DDD)
- ✅ Patrón Repository para acceso a datos
- ✅ Separación de capas (Domain/Application/Infrastructure/Interface)
- ✅ Validación de membresías activas
- ✅ Control de acceso con autenticación por API Key
- ✅ Validación de rangos BPM (30-220)
- ✅ Gestión automática de check-in/check-out
- ✅ Tracking de ocupación en tiempo real
- ✅ Historial completo de sesiones
- ✅ Base de datos SQLite para persistencia local

## 📝 Próximos Pasos

1. **Integración Hardware**: Flashear el código ESP32_CLIENT_EXAMPLE.ino al ESP32
2. **Configurar WiFi**: Actualizar SSID y password en el sketch
3. **Conectar Sensores**: 
   - PN532 NFC (I2C en GPIO 21/22)
   - Pulse Sensor (Analog en GPIO 34)
4. **Probar Flujo Completo**: Escanear NFC, medir BPM, verificar en base de datos

## 🎉 Estado del Proyecto

**VERSIÓN 1.0 - EDGE SERVICE FUNCIONAL**

El sistema está completamente operativo y listo para la demo con hardware real.
Todos los componentes de software han sido probados y validados.

---
*PumpUp Gym Management System - Edge IoT Service*
*Ciclo 8 - IoT - UPC 2025*
