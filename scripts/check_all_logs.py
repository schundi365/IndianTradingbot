import sqlite3
import os
from datetime import datetime

def check_all_recent_logs(limit=100):
    paths = ["data/logs.db", "logs/logs.db"]
    output_file = "all_recent_logs.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        for db_path in paths:
            if not os.path.exists(db_path):
                continue
                
            f.write(f"\n--- LOGS FROM {db_path} ---\n")
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Check if logs table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs';")
                if not cursor.fetchone():
                    f.write("Table 'logs' not found.\n")
                    continue
                
                # Get latest logs
                cursor.execute("SELECT timestamp, level, logger_name, message FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                
                for row in rows:
                    f.write(f"[{row['timestamp']}] {row['level']:7} | {row['logger_name']:20} | {row['message']}\n")
                    
                conn.close()
            except Exception as e:
                f.write(f"Error: {e}\n")
    
    print(f"All logs written to {output_file}")

if __name__ == "__main__":
    check_all_recent_logs()
