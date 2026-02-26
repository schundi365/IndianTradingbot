
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.managers.backtest_db_manager import BacktestDatabaseManager
import sqlite3
import json

def test_db_retrieval_fix():
    db_path = "/tmp/test_bt_retrieval.db"
    if os.path.exists(db_path): os.remove(db_path)
    
    db = BacktestDatabaseManager(db_path)
    
    # Manually insert a record with Infinity into the DB (simulating an old broken record)
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT INTO backtest_runs (id, name, symbols, config, profit_factor, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("broken_run", "Broken", '["TEST"]', "{}", float('inf'), "completed"))
        conn.commit()
    
    # Test get_run
    run = db.get_run("broken_run")
    print(f"Retrieved profit_factor: {run['profit_factor']}")
    assert run['profit_factor'] == 99.9
    
    # Test list_runs
    runs = db.list_runs()
    print(f"List retrieved profit_factor: {runs[0]['profit_factor']}")
    assert runs[0]['profit_factor'] == 99.9
    
    print("Database Retrieval Verification Successful!")

if __name__ == "__main__":
    test_db_retrieval_fix()
