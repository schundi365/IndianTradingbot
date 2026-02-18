# PowerShell script to move MT5-related files and backups from src/ to archive/
# This completes the repository organization for Indian market focus

Write-Host "Starting cleanup of MT5 and backup files from src/ directory..." -ForegroundColor Cyan
Write-Host ""

# Create archive subdirectories if they don't exist
$archiveDirs = @(
    "archive/mt5_bot",
    "archive/old_configs"
)

foreach ($dir in $archiveDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

# Move all MT5 trading bot files
Write-Host ""
Write-Host "Moving MT5 trading bot files..." -ForegroundColor Yellow

$mt5Files = @(
    "src/mt5_trading_bot.py",
    "src/mt5_trading_bot_corrupted.py",
    "src/mt5_trading_bot_backup_*.py",
    "src/mt5_trading_bot.py_backup*",
    "src/mt5_trading_bot.py.backup",
    "src/mt5_trading_bot.py.working.preipcfix.py"
)

$movedMT5Count = 0
foreach ($pattern in $mt5Files) {
    $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $destination = "archive/mt5_bot/$($file.Name)"
        Move-Item -Path $file.FullName -Destination $destination -Force
        Write-Host "  Moved: $($file.Name)" -ForegroundColor Gray
        $movedMT5Count++
    }
}

Write-Host "Moved $movedMT5Count MT5 bot files" -ForegroundColor Green

# Move old config backups
Write-Host ""
Write-Host "Moving old config backup files..." -ForegroundColor Yellow

$configBackups = @(
    "src/config_backup_*.py",
    "src/config_m1_experimental.py",
    "src/config_migration_temp.py",
    "src/config_optimized.py",
    "src/config_profitable_balanced.py"
)

$movedConfigCount = 0
foreach ($pattern in $configBackups) {
    $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $destination = "archive/old_configs/$($file.Name)"
        Move-Item -Path $file.FullName -Destination $destination -Force
        Write-Host "  Moved: $($file.Name)" -ForegroundColor Gray
        $movedConfigCount++
    }
}

Write-Host "Moved $movedConfigCount config backup files" -ForegroundColor Green

# Move other backup files
Write-Host ""
Write-Host "Moving other backup files..." -ForegroundColor Yellow

$otherBackups = @(
    "src/adaptive_risk_manager.py_backup_*"
)

$movedOtherCount = 0
foreach ($pattern in $otherBackups) {
    $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $destination = "archive/$($file.Name)"
        Move-Item -Path $file.FullName -Destination $destination -Force
        Write-Host "  Moved: $($file.Name)" -ForegroundColor Gray
        $movedOtherCount++
    }
}

Write-Host "Moved $movedOtherCount other backup files" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total files moved: $($movedMT5Count + $movedConfigCount + $movedOtherCount)" -ForegroundColor White
Write-Host "  - MT5 bot files: $movedMT5Count" -ForegroundColor White
Write-Host "  - Config backups: $movedConfigCount" -ForegroundColor White
Write-Host "  - Other backups: $movedOtherCount" -ForegroundColor White
Write-Host ""
Write-Host "The src/ directory now contains only Indian market bot files." -ForegroundColor Green
Write-Host ""
