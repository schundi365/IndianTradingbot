# Verify Cache Fix Implementation
# This script checks that all cache fix components are in place

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CACHE FIX VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check 1: Flask app has cache version endpoint
Write-Host "1. Checking Flask app for cache version endpoint..." -ForegroundColor Yellow
$flaskContent = Get-Content "indian_dashboard/indian_dashboard.py" -Raw
if ($flaskContent -match "@app\.route\('/api/cache-version'\)") {
    Write-Host "   [OK] Cache version endpoint found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Cache version endpoint NOT found" -ForegroundColor Red
    $allGood = $false
}

if ($flaskContent -match "cache_version = str\(int\(time\.time\(\)\)\)") {
    Write-Host "   [OK] Timestamp generation found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Timestamp generation NOT found" -ForegroundColor Red
    $allGood = $false
}

if ($flaskContent -match "render_template\('dashboard\.html', cache_version=cache_version\)") {
    Write-Host "   [OK] Cache version passed to template" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Cache version NOT passed to template" -ForegroundColor Red
    $allGood = $false
}

# Check 2: HTML template has dynamic versioning
Write-Host ""
Write-Host "2. Checking HTML template for dynamic versioning..." -ForegroundColor Yellow
$htmlContent = Get-Content "indian_dashboard/templates/dashboard.html" -Raw
if ($htmlContent -match '\?v=\{\{\s*cache_version\s*\}\}') {
    Write-Host "   [OK] Dynamic versioning found in template" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Dynamic versioning NOT found in template" -ForegroundColor Red
    $allGood = $false
}

if ($htmlContent -match '<style>') {
    Write-Host "   [OK] Inline critical styles found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Inline critical styles NOT found" -ForegroundColor Red
    $allGood = $false
}

# Check 3: JavaScript has cache clearing function
Write-Host ""
Write-Host "3. Checking JavaScript for cache clearing..." -ForegroundColor Yellow
$jsContent = Get-Content "indian_dashboard/static/js/app.js" -Raw
if ($jsContent -match "function forceCacheClear\(\)") {
    Write-Host "   [OK] forceCacheClear function found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] forceCacheClear function NOT found" -ForegroundColor Red
    $allGood = $false
}

if ($jsContent -match "MutationObserver") {
    Write-Host "   [OK] Mutation observer found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Mutation observer NOT found" -ForegroundColor Red
    $allGood = $false
}

if ($jsContent -match "forceCacheClear\(\);") {
    Write-Host "   [OK] forceCacheClear called on page load" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] forceCacheClear NOT called on page load" -ForegroundColor Red
    $allGood = $false
}

# Check 4: CSS has correct styles
Write-Host ""
Write-Host "4. Checking CSS for correct styles..." -ForegroundColor Yellow
$cssContent = Get-Content "indian_dashboard/static/css/gem-theme.css" -Raw
if ($cssContent -match 'color:\s*#000000') {
    Write-Host "   [OK] Tips box BLACK text style found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Tips box BLACK text style NOT found" -ForegroundColor Red
    $allGood = $false
}

if ($cssContent -match 'background:\s*#000000') {
    Write-Host "   [OK] Instrument tag BLACK background found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Instrument tag BLACK background NOT found" -ForegroundColor Red
    $allGood = $false
}

# Check 5: Scripts exist
Write-Host ""
Write-Host "5. Checking for cache clearing scripts..." -ForegroundColor Yellow
if (Test-Path "clear_cache_and_restart.ps1") {
    Write-Host "   [OK] PowerShell script found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] PowerShell script NOT found" -ForegroundColor Red
    $allGood = $false
}

if (Test-Path "clear_cache_and_restart.bat") {
    Write-Host "   [OK] Batch file found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Batch file NOT found" -ForegroundColor Red
    $allGood = $false
}

# Check 6: Documentation exists
Write-Host ""
Write-Host "6. Checking for documentation..." -ForegroundColor Yellow
if (Test-Path "CACHE_CLEARING_GUIDE.md") {
    Write-Host "   [OK] Cache clearing guide found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Cache clearing guide NOT found" -ForegroundColor Red
    $allGood = $false
}

if (Test-Path "QUICK_START_CACHE_FIX.md") {
    Write-Host "   [OK] Quick start guide found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Quick start guide NOT found" -ForegroundColor Red
    $allGood = $false
}

if (Test-Path "test_styles.html") {
    Write-Host "   [OK] Style test page found" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Style test page NOT found" -ForegroundColor Red
    $allGood = $false
}

# Final result
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "[SUCCESS] ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Cache fix is properly implemented." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Run: clear_cache_and_restart.bat" -ForegroundColor White
    Write-Host "2. Open browser in Incognito mode (Ctrl+Shift+N)" -ForegroundColor White
    Write-Host "3. Navigate to: http://127.0.0.1:8080" -ForegroundColor White
    Write-Host "4. Verify tips box has BLACK text on light yellow background" -ForegroundColor White
    Write-Host "5. Verify instrument tags have WHITE text on BLACK background" -ForegroundColor White
} else {
    Write-Host "[FAILED] SOME CHECKS FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please review the errors above and fix them." -ForegroundColor Red
    Write-Host "Check CACHE_FIX_SUMMARY.md for implementation details." -ForegroundColor Yellow
}
Write-Host ""
