# Simple Dashboard Restart Script
# Just stops and restarts Flask server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESTARTING DASHBOARD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop any running Flask processes
Write-Host "Stopping Flask server..." -ForegroundColor Yellow
$flaskProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*run_dashboard.py*" -or $_.CommandLine -like "*indian_dashboard.py*"
}

if ($flaskProcesses) {
    $flaskProcesses | Stop-Process -Force
    Write-Host "[OK] Flask server stopped" -ForegroundColor Green
} else {
    Write-Host "[OK] No Flask server was running" -ForegroundColor Green
}

Start-Sleep -Seconds 2

# Start Flask in a new window
Write-Host ""
Write-Host "Starting Flask server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python indian_dashboard/run_dashboard.py"

Write-Host "[OK] Flask server starting in new window" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Wait 5 seconds for server to start" -ForegroundColor White
Write-Host "2. Open browser in INCOGNITO mode:" -ForegroundColor Yellow
Write-Host "   Press: Ctrl+Shift+N" -ForegroundColor Yellow
Write-Host "3. Go to: http://127.0.0.1:8080" -ForegroundColor White
Write-Host ""
Write-Host "Incognito mode bypasses ALL cache!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
