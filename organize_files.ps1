# Script to organize files - move non-essential files to archive

Write-Host "Starting file organization..." -ForegroundColor Green

# Create archive subdirectories
$archiveDirs = @(
    "archive/analysis_scripts",
    "archive/config_backups",
    "archive/debug_scripts",
    "archive/fix_scripts",
    "archive/test_scripts",
    "archive/verification_scripts",
    "archive/build_scripts",
    "archive/documentation",
    "archive/old_configs",
    "archive/logs"
)

foreach ($dir in $archiveDirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Write-Host "Archive directories created" -ForegroundColor Yellow

# Move analysis scripts
$analysisScripts = @(
    "analyze_*.py",
    "check_*.py",
    "diagnose_*.py",
    "monitor_*.py",
    "trace_*.py",
    "watch_*.py",
    "comprehensive_trade_analysis.py",
    "explore_tgadise_directory.py",
    "extract_training_data_from_logs.py",
    "find_*.py",
    "show_*.py"
)

foreach ($pattern in $analysisScripts) {
    Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item $_.FullName "archive/analysis_scripts/" -Force
        Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
    }
}

# Move debug scripts
$debugScripts = @(
    "debug_*.py",
    "emergency_*.py",
    "force_*.py",
    "surgical_*.py"
)

foreach ($pattern in $debugScripts) {
    Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item $_.FullName "archive/debug_scripts/" -Force
        Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
    }
}

# Move fix scripts
$fixScripts = @(
    "fix_*.py",
    "apply_*.py",
    "implement_*.py",
    "integrate_*.py",
    "restore_*.py",
    "enable_*.py",
    "complete_*.py",
    "comprehensive_*.py",
    "update_*.py",
    "sync_*.py",
    "standardize_*.py",
    "reduce_*.py",
    "reset_*.py"
)

foreach ($pattern in $fixScripts) {
    Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item $_.FullName "archive/fix_scripts/" -Force
        Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
    }
}

# Move test scripts
$testScripts = @(
    "test_*.py",
    "test_*.html"
)

foreach ($pattern in $testScripts) {
    Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item $_.FullName "archive/test_scripts/" -Force
        Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
    }
}

# Move verification scripts
$verifyScripts = @(
    "verify_*.py",
    "validate_*.py",
    "audit_*.py",
    "compare_*.py"
)

foreach ($pattern in $verifyScripts) {
    Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item $_.FullName "archive/verification_scripts/" -Force
        Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
    }
}

# Move build scripts
$buildScripts = @(
    "build_*.py",
    "build_*.bat",
    "build_*.sh",
    "*.spec",
    "setup.py",
    "deploy_*.py",
    "deploy_*.bat",
    "prepare_*.py",
    "install_*.py"
)

foreach ($pattern in $buildScripts) {
    Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item $_.FullName "archive/build_scripts/" -Force
        Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
    }
}

# Move old config templates
Get-ChildItem -Path . -Filter "config_*.json.template" -File -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "archive/old_configs/" -Force
    Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
}

Get-ChildItem -Path . -Filter "config_backup_*.json.template" -File -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "archive/old_configs/" -Force
    Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
}

# Move documentation files (keep main README.md)
$docFiles = @(
    "*_GUIDE.md",
    "*_SUMMARY.md",
    "*_STATUS.md",
    "*_COMPLETE.md",
    "*_ANALYSIS.md",
    "*_REPORT.md",
    "*_INSTRUCTIONS.txt",
    "*_NOTICE.md",
    "*_CHECKLIST.md",
    "*_REFERENCE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "PROJECT_STATUS_COMPLETE.md",
    "TECHNICAL_DESIGN_DOCUMENT.md",
    "HIGH_LEVEL_DESIGN.md",
    "SYSTEM_ARCHITECTURE_DIAGRAM.txt"
)

foreach ($pattern in $docFiles) {
    Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.Name -ne "README.md" -and $_.Name -ne "USER_GUIDE.md") {
            Move-Item $_.FullName "archive/documentation/" -Force
            Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
        }
    }
}

# Move text status files
Get-ChildItem -Path . -Filter "*.txt" -File -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.Name -ne "requirements.txt" -and $_.Name -ne "requirements_ml.txt" -and $_.Name -ne "requirements_web.txt") {
        Move-Item $_.FullName "archive/documentation/" -Force
        Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
    }
}

# Move batch files (except essential ones)
Get-ChildItem -Path . -Filter "*.bat" -File -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "archive/build_scripts/" -Force
    Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
}

# Move shell scripts
Get-ChildItem -Path . -Filter "*.sh" -File -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "archive/build_scripts/" -Force
    Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
}

# Move log files
Get-ChildItem -Path . -Filter "*.log" -File -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "archive/logs/" -Force
    Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
}

# Move backup files
Get-ChildItem -Path . -Filter "*.backup.*" -File -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "archive/config_backups/" -Force
    Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
}

# Move old dashboard files
$oldDashboardFiles = @(
    "web_dashboard.py",
    "web_dashboard_backup.py",
    "dashboard_minimal_working.html",
    "minimal_test.html",
    "add_dashboard_javascript.py"
)

foreach ($file in $oldDashboardFiles) {
    if (Test-Path $file) {
        Move-Item $file "archive/build_scripts/" -Force
        Write-Host "Moved: $file" -ForegroundColor Gray
    }
}

# Move old directories to archive
$oldDirs = @(
    "Bugs",
    "config_backups",
    "ml_training",
    "RSI_IMPLEMENTATION_GUIDE",
    "static",
    "templates"
)

foreach ($dir in $oldDirs) {
    if (Test-Path $dir) {
        Move-Item $dir "archive/" -Force
        Write-Host "Moved directory: $dir" -ForegroundColor Gray
    }
}

Write-Host "`nFile organization complete!" -ForegroundColor Green
Write-Host "`nEssential files kept in root:" -ForegroundColor Cyan
Write-Host "  - README.md" -ForegroundColor White
Write-Host "  - USER_GUIDE.md" -ForegroundColor White
Write-Host "  - requirements.txt" -ForegroundColor White
Write-Host "  - requirements_ml.txt" -ForegroundColor White
Write-Host "  - requirements_web.txt" -ForegroundColor White
Write-Host "  - kite_login.py" -ForegroundColor White
Write-Host "  - kite_token.json" -ForegroundColor White
Write-Host "  - run_bot.py" -ForegroundColor White
Write-Host "  - start_dashboard.py" -ForegroundColor White
Write-Host "`nEssential directories:" -ForegroundColor Cyan
Write-Host "  - src/ (core bot code)" -ForegroundColor White
Write-Host "  - indian_dashboard/ (web dashboard)" -ForegroundColor White
Write-Host "  - configs/ (configuration files)" -ForegroundColor White
Write-Host "  - tests/ (test suite)" -ForegroundColor White
Write-Host "  - examples/ (example configs)" -ForegroundColor White
Write-Host "  - data/ (runtime data)" -ForegroundColor White
Write-Host "  - logs/ (log files)" -ForegroundColor White
Write-Host "  - models/ (ML models)" -ForegroundColor White
Write-Host "  - docs/ (documentation)" -ForegroundColor White
Write-Host "`nArchived files in:" -ForegroundColor Cyan
Write-Host "  - archive/ (all non-essential files)" -ForegroundColor White
