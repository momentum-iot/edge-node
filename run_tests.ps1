# Run Full System Test
Write-Host "=== Starting PumpUp Gym Edge Service Test ===" -ForegroundColor Cyan

# Start server in background
Write-Host "`nStarting Flask server..." -ForegroundColor Yellow
$server = Start-Process python -ArgumentList "app.py" -PassThru -WindowStyle Hidden

# Wait for server to start
Start-Sleep -Seconds 4

# Run tests
Write-Host "`nRunning tests..." -ForegroundColor Yellow
.\test_simple.ps1

# Stop server
Write-Host "`nStopping server..." -ForegroundColor Yellow
Stop-Process -Id $server.Id -Force

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
