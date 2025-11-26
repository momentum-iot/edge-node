# Simple Test Script - PumpUp Gym Edge Service
Write-Host "=== PumpUp Gym Edge Service - Tests ===" -ForegroundColor Cyan

$base = "http://localhost:5000"
$key = "gym-api-key-2025"
$nfc = "04A1B2C3D4E5F6"

# Test 1: Check Occupancy
Write-Host "`n[TEST 1] Get Initial Occupancy..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$base/api/v1/access/occupancy" -Headers @{"X-API-Key"=$key}
    Write-Host "SUCCESS: Occupancy = $($result.current_occupancy)" -ForegroundColor Green
    Write-Host ($result | ConvertTo-Json)
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Check-in
Write-Host "`n[TEST 2] Member Check-in with NFC..." -ForegroundColor Yellow
try {
    $body = @{device_id="gym-esp32-001"; nfc_uid=$nfc} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$base/api/v1/access/nfc-scan" -Method POST -Headers @{"X-API-Key"=$key; "Content-Type"="application/json"} -Body $body
    Write-Host "SUCCESS: Action = $($result.action), Member = $($result.member_name)" -ForegroundColor Green
    Write-Host ($result | ConvertTo-Json)
    $memberId = $result.member_id
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Check Occupancy Again
Write-Host "`n[TEST 3] Get Occupancy After Check-in..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$base/api/v1/access/occupancy" -Headers @{"X-API-Key"=$key}
    Write-Host "SUCCESS: Occupancy = $($result.current_occupancy)" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Start Equipment Session
Write-Host "`n[TEST 4] Start Equipment Session..." -ForegroundColor Yellow
try {
    $body = @{device_id="gym-esp32-001"; member_id=$memberId; equipment_id=1} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$base/api/v1/equipment/session/start" -Method POST -Headers @{"X-API-Key"=$key; "Content-Type"="application/json"} -Body $body
    Write-Host "SUCCESS: Session ID = $($result.session_id)" -ForegroundColor Green
    Write-Host ($result | ConvertTo-Json)
    $sessionId = $result.session_id
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 5: Record Heart Rates
Write-Host "`n[TEST 5] Record Heart Rate Data..." -ForegroundColor Yellow
$bpms = @(72, 85, 92, 88, 95)
$success = 0
foreach ($bpm in $bpms) {
    try {
        $body = @{device_id="gym-esp32-001"; session_id=$sessionId; member_id=$memberId; bpm=$bpm} | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$base/api/v1/equipment/heart-rate" -Method POST -Headers @{"X-API-Key"=$key; "Content-Type"="application/json"} -Body $body
        Write-Host "  - BPM $bpm recorded (ID: $($result.record_id))" -ForegroundColor Green
        $success++
    } catch {
        Write-Host "  - BPM $bpm FAILED" -ForegroundColor Red
    }
}
Write-Host "SUCCESS: $success/$($bpms.Count) readings recorded" -ForegroundColor Green

# Test 6: End Session
Write-Host "`n[TEST 6] End Equipment Session..." -ForegroundColor Yellow
try {
    $body = @{device_id="gym-esp32-001"; member_id=$memberId} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$base/api/v1/equipment/session/end" -Method POST -Headers @{"X-API-Key"=$key; "Content-Type"="application/json"} -Body $body
    Write-Host "SUCCESS: Session ended" -ForegroundColor Green
    Write-Host ($result | ConvertTo-Json)
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Check-out
Write-Host "`n[TEST 7] Member Check-out..." -ForegroundColor Yellow
try {
    $body = @{device_id="gym-esp32-001"; nfc_uid=$nfc} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$base/api/v1/access/nfc-scan" -Method POST -Headers @{"X-API-Key"=$key; "Content-Type"="application/json"} -Body $body
    Write-Host "SUCCESS: Action = $($result.action)" -ForegroundColor Green
    Write-Host ($result | ConvertTo-Json)
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 8: Final Occupancy
Write-Host "`n[TEST 8] Get Final Occupancy..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$base/api/v1/access/occupancy" -Headers @{"X-API-Key"=$key}
    Write-Host "SUCCESS: Occupancy = $($result.current_occupancy)" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 9: Invalid NFC
Write-Host "`n[TEST 9] Test Invalid NFC Card..." -ForegroundColor Yellow
try {
    $body = @{device_id="gym-esp32-001"; nfc_uid="INVALID999"} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$base/api/v1/access/nfc-scan" -Method POST -Headers @{"X-API-Key"=$key; "Content-Type"="application/json"} -Body $body
    Write-Host "UNEXPECTED: Should have been denied" -ForegroundColor Red
} catch {
    Write-Host "SUCCESS: Access correctly denied" -ForegroundColor Green
}

Write-Host "`n=== ALL TESTS COMPLETED ===" -ForegroundColor Cyan
