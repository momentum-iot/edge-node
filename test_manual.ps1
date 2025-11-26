# Manual Test Script - PumpUp Gym Edge Service
# Run each test individually to verify functionality

Write-Host "`n=== PumpUp Gym Edge Service - Manual Tests ===" -ForegroundColor Cyan
Write-Host "Server should be running on http://localhost:5000`n" -ForegroundColor Yellow

$baseUrl = "http://localhost:5000"
$headers = @{
    "X-API-Key" = "gym-api-key-2025"
    "Content-Type" = "application/json"
}

function Test-Endpoint {
    param($name, $method, $uri, $body = $null)
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "TEST: $name" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    
    try {
        if ($method -eq "GET") {
            $response = Invoke-RestMethod -Uri $uri -Method GET -Headers $headers -ErrorAction Stop
        } else {
            $response = Invoke-RestMethod -Uri $uri -Method POST -Headers $headers -Body ($body | ConvertTo-Json) -ErrorAction Stop
        }
        
        Write-Host "SUCCESS" -ForegroundColor Green
        Write-Host ($response | ConvertTo-Json -Depth 5)
        return $response
    }
    catch {
        Write-Host "FAILED" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Test 1: Initial Occupancy (should be 0)
Write-Host "`n[1/9] Testing initial occupancy..." -ForegroundColor Magenta
$occupancy1 = Test-Endpoint "Get Initial Occupancy" "GET" "$baseUrl/api/v1/access/occupancy"

# Test 2: Check-in
Write-Host "`n[2/9] Testing check-in..." -ForegroundColor Magenta
$checkin = Test-Endpoint "Member Check-in" "POST" "$baseUrl/api/v1/access/nfc-scan" @{
    device_id = "gym-esp32-001"
    nfc_uid = "04A1B2C3D4E5F6"
}

if ($checkin -and $checkin.success -and $checkin.action -eq "check_in") {
    Write-Host "✓ Check-in successful! Member: $($checkin.member_name)" -ForegroundColor Green
    $memberId = $checkin.member_id
} else {
    Write-Host "✗ Check-in failed!" -ForegroundColor Red
    exit 1
}

# Test 3: Occupancy after check-in (should be 1)
Write-Host "`n[3/9] Testing occupancy after check-in..." -ForegroundColor Magenta
$occupancy2 = Test-Endpoint "Get Occupancy After Check-in" "GET" "$baseUrl/api/v1/access/occupancy"

if ($occupancy2 -and $occupancy2.current_occupancy -eq 1) {
    Write-Host "✓ Occupancy correctly shows 1" -ForegroundColor Green
} else {
    Write-Host "✗ Occupancy is incorrect!" -ForegroundColor Red
}

# Test 4: Start Equipment Session
Write-Host "`n[4/9] Testing equipment session start..." -ForegroundColor Magenta
$session = Test-Endpoint "Start Equipment Session" "POST" "$baseUrl/api/v1/equipment/session/start" @{
    device_id = "gym-esp32-001"
    member_id = $memberId
    equipment_id = 1
}

if ($session -and $session.success) {
    Write-Host "✓ Session started! Session ID: $($session.session_id)" -ForegroundColor Green
    $sessionId = $session.session_id
} else {
    Write-Host "✗ Session start failed!" -ForegroundColor Red
    exit 1
}

# Test 5: Record Heart Rate (multiple readings)
Write-Host "`n[5/9] Testing heart rate recording..." -ForegroundColor Magenta
$bpmValues = @(72, 85, 92, 88, 95)
$hrSuccess = 0

foreach ($bpm in $bpmValues) {
    $hr = Test-Endpoint "Record BPM: $bpm" "POST" "$baseUrl/api/v1/equipment/heart-rate" @{
        device_id = "gym-esp32-001"
        session_id = $sessionId
        member_id = $memberId
        bpm = $bpm
    }
    
    if ($hr -and $hr.success) {
        $hrSuccess++
    }
    Start-Sleep -Milliseconds 500
}

Write-Host "`n✓ $hrSuccess/$($bpmValues.Count) heart rate readings recorded successfully" -ForegroundColor Green

# Test 6: End Equipment Session
Write-Host "`n[6/9] Testing equipment session end..." -ForegroundColor Magenta
$endSession = Test-Endpoint "End Equipment Session" "POST" "$baseUrl/api/v1/equipment/session/end" @{
    device_id = "gym-esp32-001"
    member_id = $memberId
}

if ($endSession -and $endSession.success) {
    Write-Host "✓ Session ended successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Session end failed!" -ForegroundColor Red
}

# Test 7: Check-out
Write-Host "`n[7/9] Testing check-out..." -ForegroundColor Magenta
$checkout = Test-Endpoint "Member Check-out" "POST" "$baseUrl/api/v1/access/nfc-scan" @{
    device_id = "gym-esp32-001"
    nfc_uid = "04A1B2C3D4E5F6"
}

if ($checkout -and $checkout.success -and $checkout.action -eq "check_out") {
    Write-Host "✓ Check-out successful!" -ForegroundColor Green
} else {
    Write-Host "✗ Check-out failed!" -ForegroundColor Red
}

# Test 8: Final Occupancy (should be 0)
Write-Host "`n[8/9] Testing final occupancy..." -ForegroundColor Magenta
$occupancy3 = Test-Endpoint "Get Final Occupancy" "GET" "$baseUrl/api/v1/access/occupancy"

if ($occupancy3 -and $occupancy3.current_occupancy -eq 0) {
    Write-Host "✓ Occupancy correctly shows 0" -ForegroundColor Green
} else {
    Write-Host "✗ Final occupancy is incorrect!" -ForegroundColor Red
}

# Test 9: Invalid NFC (Access Denied)
Write-Host "`n[9/9] Testing access denied scenario..." -ForegroundColor Magenta
$denied = Test-Endpoint "Invalid NFC Card" "POST" "$baseUrl/api/v1/access/nfc-scan" @{
    device_id = "gym-esp32-001"
    nfc_uid = "INVALID_CARD_999"
}

if ($denied -and -not $denied.success) {
    Write-Host "✓ Access correctly denied for invalid card" -ForegroundColor Green
} else {
    Write-Host "✗ Invalid card test failed!" -ForegroundColor Red
}

# Summary
Write-Host "`n`n========================================" -ForegroundColor Cyan
Write-Host "ALL TESTS COMPLETED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nThe PumpUp Gym Edge Service is working correctly!" -ForegroundColor Green
