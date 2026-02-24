"""
Custom Logging Handler for Database Persistence
Intercepts log records and stores them in SQLite
"""

import logging
import threading
from queue import Queue
from typing import Optional
from src.database_manager import LogDatabaseManager


class DatabaseHandler(logging.Handler):
    """
    Logging handler that sends log records to an SQLite database.
    Uses a background thread to avoid blocking application execution.
    """
    
    def __init__(self, db_path: str = "data/logs.db", level=logging.NOTSET):
        """
        Initialize the database handler.
        
        Args:
            db_path: Path to the SQLite database
            level: Logging level
        """
        super().__init__(level)
        self.db_manager = LogDatabaseManager(db_path)
        self.queue = Queue()
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
    
    def emit(self, record):
        """
        Queue a log record for insertion into the database.
        
        Args:
            record: The LogRecord to emit
        """
        try:
            # We don't want to log the database operations themselves to the database
            if record.name == "src.database_manager" or record.name == "src.db_logging_handler":
                return
                
            # Extract symbol if present in record attributes (extra)
            symbol = getattr(record, 'symbol', None)
            
            # If not in extra, try to extract from message if it's a known format
            if not symbol and '|' in record.getMessage():
                parts = record.getMessage().split('|')
                if len(parts) > 1:
                    potential_symbol = parts[1].strip()
                    # Basic heuristic for symbols (usually uppercase, no spaces, reasonable length)
                    if potential_symbol.isupper() and ' ' not in potential_symbol and 2 <= len(potential_symbol) <= 20:
                        symbol = potential_symbol
            
            # Prep the log data
            log_data = {
                'level': record.levelname,
                'level_no': record.levelno,
                'logger_name': record.name,
                'message': self.format(record),
                'symbol': symbol
            }
            
            self.queue.put(log_data)
        except Exception:
            self.handleError(record)
    
    def _worker(self):
        """Background thread worker that processes the log queue"""
        while not self.stop_event.is_set():
            try:
                # Wait for a log entry with a timeout
                log_data = self.queue.get(timeout=1.0)
                
                # Insert into database
                self.db_manager.insert_log(
                    level=log_data['level'],
                    level_no=log_data['level_no'],
                    logger_name=log_data['logger_name'],
                    message=log_data['message'],
                    symbol=log_data['symbol']
                )
                
                self.queue.task_done()
            except Exception:
                # Ignore errors in the worker thread to prevent crashing
                pass
                
    def close(self):
        """Shut down the background thread and close the database"""
        self.stop_event.set()
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        super().close()
