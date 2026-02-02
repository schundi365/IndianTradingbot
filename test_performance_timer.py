#!/usr/bin/env python3
"""
Test performance_timer function directly
"""

import sys
import time
import logging
import inspect
import functools
from pathlib import Path

def performance_timer(operation_name):
    """Decorator to automatically time function execution"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Get caller info
                frame = inspect.currentframe()
                filename = Path(frame.f_code.co_filename).name
                
                logger = logging.getLogger(__name__)
                logger.info(f"⏱️ {operation_name} ({func.__name__}) completed in {duration:.3f}s", extra={
                    'pathname': frame.f_code.co_filename,
                    'lineno': frame.f_lineno
                })
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger = logging.getLogger(__name__)
                logger.error(f"❌ {operation_name} ({func.__name__}) failed after {duration:.3f}s: {str(e)}", extra={
                    'pathname': frame.f_code.co_filename,
                    'lineno': frame.f_lineno
                })
                raise
        return wrapper
    return decorator

@performance_timer("Test Operation")
def test_function():
    """Test function"""
    time.sleep(0.1)
    return "success"

if __name__ == "__main__":
    print("🔍 Testing performance_timer function...")
    try:
        result = test_function()
        print(f"✅ Test successful: {result}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()