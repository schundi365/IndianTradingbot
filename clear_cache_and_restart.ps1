# Clear Cache and Restart Dashboard Script
# This script stops the Flask server, clears browser cache data, and restarts

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CACHE CLEARING AND SERVER RESTART" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop any running Flask processes
Write-Host "Step 1: Stopping Flask server..." -ForegroundColor Yellow
$flaskProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*run_dashboard.py*" -or $_.CommandLine -like "*indian_dashboard.py*"
}

if ($flaskProcesses) {
    $flaskProcesses | Stop-Process -Force
    Write-Host "  [OK] Flask server stopped" -ForegroundColor Green
} else {
    Write-Host "  [OK] No Flask server running" -ForegroundColor Green
}

Start-Sleep -Seconds 2

# Step 2: Clear Chrome cache (if Chrome is running)
Write-Host ""
Write-Host "Step 2: Clearing Chrome cache..." -ForegroundColor Yellow
$chromeProcesses = Get-Process -Name chrome -ErrorAction SilentlyContinue

if ($chromeProcesses) {
    Write-Host "Chrome is running. Attempting to clear cache..." -ForegroundColor Yellow
    
    # Chrome cache locations
    $chromeCachePaths = @(
        "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache",
        "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Code Cache",
        "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\GPUCache",
        "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Service Worker\CacheStorage",
        "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Service Worker\ScriptCache"
    )
    
    foreach ($path in $chromeCachePaths) {
        if (Test-Path $path) {
            try {
                Remove-Item -Path "$path\*" -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  [OK] Cleared: $path" -ForegroundColor Green
            } catch {
                Write-Host "  [WARN] Could not clear: $path (Chrome may be using it)" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ""
    Write-Host "[IMPORTANT] For complete cache clearing:" -ForegroundColor Yellow
    Write-Host "  1. Close Chrome completely (all windows)" -ForegroundColor White
    Write-Host "  2. Press Ctrl+Shift+Delete in Chrome" -ForegroundColor White
    Write-Host "  3. Select 'All time' and check 'Cached images and files'" -ForegroundColor White
    Write-Host "  4. Click 'Clear data'" -ForegroundColor White
    Write-Host ""
    Write-Host "  OR use Incognito mode: Ctrl+Shift+N" -ForegroundColor White
} else {
    Write-Host "  [OK] Chrome is not running" -ForegroundColor Green
}

# Step 3: Clear Edge cache (if Edge is running)
Write-Host ""
Write-Host "Step 3: Clearing Edge cache..." -ForegroundColor Yellow
$edgeProcesses = Get-Process -Name msedge -ErrorAction SilentlyContinue

if ($edgeProcesses) {
    Write-Host "Edge is running. Attempting to clear cache..." -ForegroundColor Yellow
    
    $edgeCachePaths = @(
        "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache",
        "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Code Cache",
        "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\GPUCache"
    )
    
    foreach ($path in $edgeCachePaths) {
        if (Test-Path $path) {
            try {
                Remove-Item -Path "$path\*" -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  [OK] Cleared: $path" -ForegroundColor Green
            } catch {
                Write-Host "  [WARN] Could not clear: $path (Edge may be using it)" -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "  [OK] Edge is not running" -ForegroundColor Green
}

# Step 4: Clear Flask cache
Write-Host ""
Write-Host "Step 4: Clearing Flask cache..." -ForegroundColor Yellow
$flaskCachePaths = @(
    "indian_dashboard/__pycache__",
    "indian_dashboard/api/__pycache__",
    "indian_dashboard/services/__pycache__",
    "indian_dashboard/tests/__pycache__"
)

foreach ($path in $flaskCachePaths) {
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Cleared: $path" -ForegroundColor Green
    }
}

# Step 5: Restart Flask server
Write-Host ""
Write-Host "Step 5: Starting Flask server..." -ForegroundColor Yellow
Write-Host ""

# Start Flask in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python indian_dashboard/run_dashboard.py"

Write-Host "[OK] Flask server starting in new window..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Wait 5 seconds for server to start" -ForegroundColor White
Write-Host "2. Open browser in INCOGNITO/PRIVATE mode:" -ForegroundColor White
Write-Host "   - Chrome: Ctrl+Shift+N" -ForegroundColor Yellow
Write-Host "   - Edge: Ctrl+Shift+N" -ForegroundColor Yellow
Write-Host "3. Navigate to: http://127.0.0.1:8080" -ForegroundColor White
Write-Host ""
Write-Host "This will bypass ALL cache and show fresh styles!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
