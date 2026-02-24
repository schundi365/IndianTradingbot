import sqlite3
import os
from datetime import datetime

def check_detailed_errors(limit=20):
    paths = ["data/logs.db", "logs/logs.db"]
    output_file = "error_output.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        for db_path in paths:
            if not os.path.exists(db_path):
                continue
                
            f.write(f"\n--- ERRORS FROM {db_path} ---\n")
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Check if logs table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs';")
                if not cursor.fetchone():
                    f.write("Table 'logs' not found.\n")
                    continue
                
                # Get latest errors/warnings
                cursor.execute("SELECT timestamp, level, logger_name, message FROM logs WHERE level IN ('ERROR', 'WARNING') ORDER BY timestamp DESC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                
                for row in rows:
                    f.write(f"[{row['timestamp']}] {row['level']:7} | {row['logger_name']:20} | {row['message']}\n")
                    
                conn.close()
            except Exception as e:
                f.write(f"Error: {e}\n")
    
    print(f"Errors written to {output_file}")

if __name__ == "__main__":
    check_detailed_errors()
