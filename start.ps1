# Quick Start Script for PumpUp Gym Edge Service

Write-Host "=== PumpUp Gym Edge Service - Quick Start ===" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python OK" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "2. Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing dependencies!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Check if port 5000 is available
Write-Host "3. Checking if port 5000 is available..." -ForegroundColor Yellow
$port = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($port) {
    Write-Host "Warning: Port 5000 is already in use. Attempting to free it..." -ForegroundColor Yellow
    Stop-Process -Id $port.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}
Write-Host "✓ Port 5000 is available" -ForegroundColor Green
Write-Host ""

# Start the service
Write-Host "4. Starting PumpUp Gym Edge Service..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Service will start on: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Your IP: http://$($(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike '*Loopback*'} | Select-Object -First 1).IPAddress):5000" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

python app.py
