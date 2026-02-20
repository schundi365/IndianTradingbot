# Import Fix - validate_broker_type

## Problem
```
name 'validate_broker_type' is not defined
```

## Root Cause
The function `validate_broker_type` exists in `validators.py` but wasn't imported in `config.py`.

## Fix Applied
**File**: `indian_dashboard/api/config.py`

Added `validate_broker_type` to the imports:

```python
from validators import (
    validate_json_request,
    sanitize_request_data,
    validate_config_name,
    validate_path_param_string,
    sanitize_string,
    validate_required_fields,
    validate_list,
    validate_risk_percentage,
    validate_integer,
    validate_strategy,
    validate_timeframe,
    validate_broker_type  # <-- ADDED THIS
)
```

## Next Steps
1. Restart dashboard: `.\restart_dashboard.ps1`
2. Try saving configuration again
3. Should work now!

---

**Status**: ✅ Fixed - restart and test
