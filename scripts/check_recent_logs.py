
import sqlite3
import pandas as pd
import os
from datetime import datetime

def check_recent_logs(limit=50):
    paths = ["data/logs.db", "logs/logs.db"]
    for db_path in paths:
        if not os.path.exists(db_path):
            print(f"Path not found: {db_path}")
            continue
            
        print(f"\n--- Checking {db_path} ---")
        try:
            conn = sqlite3.connect(db_path)
            # Get table names first
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Tables: {tables}")
            
            if not tables or ('logs',) not in tables:
                print(f"Table 'logs' not found in {db_path}")
                conn.close()
                continue
                
            # Get most recent logs
            query = f"SELECT * FROM logs ORDER BY timestamp DESC LIMIT {limit}"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            print(f"--- Most Recent {limit} Logs (Newest First) ---")
            for index, row in df.iterrows():
                print(f"{row['timestamp']} | {row['level']} | {row['logger_name']} | {row['message']}")
            
            # Also check for specific error/warning messages related to orders
            print("\n--- Recent Errors/Warnings ---")
            conn = sqlite3.connect(db_path)
            query = "SELECT * FROM logs WHERE level IN ('ERROR', 'WARNING') ORDER BY timestamp DESC LIMIT 20"
            df_err = pd.read_sql_query(query, conn)
            for index, row in df_err.iterrows():
                print(f"{row['timestamp']} | {row['level']} | {row['message']}")
            conn.close()
            
        except Exception as e:
            print(f"Error checking {db_path}: {e}")

if __name__ == "__main__":
    check_recent_logs()
