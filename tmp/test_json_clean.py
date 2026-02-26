import json
import math

def _clean_metrics(obj):
    """Recursively replace Infinity/NaN with JSON-safe values."""
    if isinstance(obj, float):
        if math.isinf(obj):
            return 99.9 if obj > 0 else -99.9
        if math.isnan(obj):
            return 0.0
        return obj
    if isinstance(obj, dict):
        return {k: _clean_metrics(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_metrics(x) for x in obj]
    return obj

def test():
    data = {
        "profit_factor": float('inf'),
        "win_rate": float('nan'),
        "nested": {
            "val": float('-inf'),
            "list": [1.0, float('inf'), 2.0]
        }
    }
    
    # Current implementation in backtest_db_manager.py (but I'll use math for better check)
    cleaned = _clean_metrics(data)
    print(f"Cleaned: {cleaned}")
    
    try:
        json_str = json.dumps(cleaned)
        print(f"JSON: {json_str}")
    except Exception as e:
        print(f"Error: {e}")

    # Check if original implementation (if I can't import it) works
    # obj == float('inf') should work too.
    inf_val = float('inf')
    print(f"inf_val == float('inf'): {inf_val == float('inf')}")

if __name__ == "__main__":
    test()
