
import sqlite3
import json
import os
import sys

# Ensure UTF-8 output even on Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = os.path.join('logs', 'logs.db')
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get the most recent 100 logs of level ERROR or WARNING
cursor.execute('SELECT * FROM logs WHERE level IN ("ERROR", "WARNING") ORDER BY timestamp DESC LIMIT 200')
rows = cursor.fetchall()

if not rows:
    print("No ERROR or WARNING logs found.")
else:
    for row in rows:
        d = dict(row)
        print(f"[{d['timestamp']}] {d['level']} - {d['logger_name']}: {d['message']}")

conn.close()
