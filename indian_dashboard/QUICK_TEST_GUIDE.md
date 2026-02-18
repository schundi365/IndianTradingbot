# Quick Test Guide

Fast reference for running deployment tests.

## Quick Verification (30 seconds)

```bash
cd indian_dashboard
python verify_deployment.py
```

Expected output:
```
Checks Passed: 40/40
Success Rate: 100.0%
✓ Deployment verification PASSED
```

## Full Test Suite (5 minutes)

### Option 1: Automated (Windows)
```bash
cd indian_dashboard
run_deployment_tests.bat
```

### Option 2: Manual Steps

**Terminal 1 - Start Server:**
```bash
cd indian_dashboard
python run_dashboard.py
```

**Terminal 2 - Run Tests:**
```bash
cd indian_dashboard/tests
python test_deployment.py
python test_broker_deployment.py
```

## Quick Manual Test (2 minutes)

1. Start server: `python run_dashboard.py`
2. Open browser: http://localhost:8080
3. Check each tab loads
4. Test paper trading connection:
   - Go to Broker tab
   - Select "Paper Trading"
   - Click Connect
   - Should connect without credentials

## Test Results

Check these files:
- `tests/deployment_test_report.json`
- `tests/broker_deployment_test_report.json`

## Common Issues

**Server won't start:**
```bash
# Check if port is in use
netstat -ano | findstr :8080

# Use different port
python run_dashboard.py --port 8081
```

**Tests fail:**
```bash
# Make sure server is running first
# Check logs/dashboard.log for errors
```

**Import errors:**
```bash
# Install dependencies
pip install -r requirements.txt
```

## Success Indicators

✓ Verification shows 40/40 checks passed
✓ Server starts without errors
✓ Dashboard loads in browser
✓ Paper trading connects
✓ All test categories pass

## Need Help?

See detailed guides:
- `DEPLOYMENT_TEST_GUIDE.md` - Complete testing guide
- `DEPLOYMENT_VERIFICATION_CHECKLIST.md` - Detailed checklist
- `TROUBLESHOOTING_REFERENCE.md` - Troubleshooting help
