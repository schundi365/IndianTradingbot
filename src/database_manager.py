"""
SQLite Database Manager for Logs
Handles all database operations for log persistence
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class LogDatabaseManager:
    """
    Manager for the SQLite log database.
    Provides thread-safe access to log storage and retrieval.
    """
    
    def __init__(self, db_path: str = "data/logs.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_dir()
        self.init_db()
    
    def _ensure_dir(self):
        """Ensure the directory for the database exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _get_connection(self):
        """Get a thread-local connection to the database"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize the database schema"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    logger_name TEXT NOT NULL,
                    message TEXT NOT NULL,
                    symbol TEXT,
                    level_no INTEGER NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_level ON logs(level)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON logs(symbol)")
            conn.commit()
    
    def insert_log(self, level: str, level_no: int, logger_name: str, message: str, symbol: Optional[str] = None):
        """
        Insert a log record into the database.
        
        Args:
            level: Log level name (e.g., INFO, ERROR)
            level_no: Log level number (e.g., 20, 40)
            logger_name: Name of the logger
            message: Log message
            symbol: Trading symbol related to the log (optional)
        """
        try:
            timestamp = datetime.now().isoformat()
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO logs (timestamp, level, logger_name, message, symbol, level_no) VALUES (?, ?, ?, ?, ?, ?)",
                    (timestamp, level, logger_name, message, symbol, level_no)
                )
                conn.commit()
        except Exception as e:
            # Avoid infinite recursion if logging fails
            print(f"Error inserting log into DB: {e}")
    
    def get_logs(self, limit: int = 100, offset: int = 0, level: Optional[str] = None, 
                 search: Optional[str] = None, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve logs from the database with filtering and pagination.
        
        Args:
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            level: Filter by log level
            search: Search in message or logger_name
            symbol: Filter by symbol
            
        Returns:
            List of log dictionaries
        """
        query = "SELECT id, timestamp, level, logger_name, message, symbol, level_no FROM logs WHERE 1=1"
        params = []
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
            
        if search:
            query += " AND (message LIKE ? OR logger_name LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
            
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        logs = []
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                for row in cursor:
                    logs.append(dict(row))
        except Exception as e:
            print(f"Error retrieving logs from DB: {e}")
            
        return logs

    def get_log_count(self, level: Optional[str] = None, search: Optional[str] = None, 
                     symbol: Optional[str] = None) -> int:
        """Get total count of logs matching filters"""
        query = "SELECT COUNT(*) FROM logs WHERE 1=1"
        params = []
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
            
        if search:
            query += " AND (message LIKE ? OR logger_name LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
            
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(query, params)
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error counting logs in DB: {e}")
            return 0

    def clear_logs(self):
        """Clear all logs from the database"""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM logs")
            conn.commit()
