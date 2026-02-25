"""
Backtest Database Manager
=========================
SQLite persistence for backtest and forward-test runs.
Tables: backtest_runs, backtest_trades, backtest_metrics
"""

import csv
import io
import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class BacktestDatabaseManager:
    """Manage SQLite persistence for backtest / forward-test results."""

    def __init__(self, db_path: str = "data/backtests.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS backtest_runs (
                    id              TEXT PRIMARY KEY,
                    name            TEXT NOT NULL,
                    mode            TEXT NOT NULL DEFAULT 'backtest',
                    symbols         TEXT NOT NULL,
                    config          TEXT NOT NULL,
                    from_date       TEXT,
                    to_date         TEXT,
                    initial_capital REAL,
                    final_capital   REAL,
                    total_return_pct REAL,
                    max_drawdown_pct REAL,
                    sharpe_ratio    REAL,
                    total_trades    INTEGER,
                    win_rate        REAL,
                    profit_factor   REAL,
                    status          TEXT DEFAULT 'pending',
                    error           TEXT,
                    duration_seconds REAL,
                    created_at      TEXT,
                    equity_curve    TEXT
                );

                CREATE TABLE IF NOT EXISTS backtest_trades (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id          TEXT NOT NULL,
                    symbol          TEXT NOT NULL,
                    direction       TEXT NOT NULL,
                    entry_time      TEXT,
                    entry_price     REAL,
                    exit_time       TEXT,
                    exit_price      REAL,
                    quantity        REAL,
                    pnl             REAL,
                    pnl_pct         REAL,
                    exit_reason     TEXT,
                    bars_held       INTEGER,
                    FOREIGN KEY (run_id) REFERENCES backtest_runs(id)
                );

                CREATE TABLE IF NOT EXISTS backtest_metrics (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id          TEXT NOT NULL,
                    symbol          TEXT NOT NULL,
                    total_trades    INTEGER,
                    winning_trades  INTEGER,
                    losing_trades   INTEGER,
                    win_rate        REAL,
                    total_pnl       REAL,
                    total_return_pct REAL,
                    max_drawdown_pct REAL,
                    profit_factor   REAL,
                    avg_trade_pnl   REAL,
                    best_trade_pnl  REAL,
                    worst_trade_pnl REAL,
                    avg_bars_held   REAL,
                    sharpe_ratio    REAL,
                    FOREIGN KEY (run_id) REFERENCES backtest_runs(id)
                );

                CREATE INDEX IF NOT EXISTS idx_bt_runs_created ON backtest_runs(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_bt_trades_run ON backtest_trades(run_id);
                CREATE INDEX IF NOT EXISTS idx_bt_metrics_run ON backtest_metrics(run_id);
            """)
            conn.commit()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save_run(self, result) -> bool:
        """Persist a BacktestResult (completed or failed)."""
        try:
            from src.core.backtest_engine import BacktestResult, BacktestTrade, SymbolMetrics  # noqa

            with self._connect() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO backtest_runs
                    (id, name, mode, symbols, config, from_date, to_date,
                     initial_capital, final_capital, total_return_pct,
                     max_drawdown_pct, sharpe_ratio, total_trades, win_rate,
                     profit_factor, status, error, duration_seconds,
                     created_at, equity_curve)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    result.run_id,
                    result.name,
                    result.mode,
                    json.dumps(result.symbols),
                    json.dumps(result.config),
                    result.from_date,
                    result.to_date,
                    result.initial_capital,
                    result.final_capital,
                    result.total_return_pct,
                    result.max_drawdown_pct,
                    result.sharpe_ratio,
                    result.total_trades,
                    result.win_rate,
                    result.profit_factor,
                    result.status,
                    result.error,
                    result.duration_seconds,
                    result.created_at,
                    json.dumps(result.equity_curve),
                ))

                # Trades
                if result.trades:
                    conn.executemany("""
                        INSERT INTO backtest_trades
                        (run_id, symbol, direction, entry_time, entry_price,
                         exit_time, exit_price, quantity, pnl, pnl_pct,
                         exit_reason, bars_held)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    """, [
                        (result.run_id, t.symbol, t.direction, t.entry_time,
                         t.entry_price, t.exit_time, t.exit_price, t.quantity,
                         t.pnl, t.pnl_pct, t.exit_reason, t.bars_held)
                        for t in result.trades
                    ])

                # Per-symbol metrics
                if result.symbol_metrics:
                    conn.executemany("""
                        INSERT INTO backtest_metrics
                        (run_id, symbol, total_trades, winning_trades,
                         losing_trades, win_rate, total_pnl, total_return_pct,
                         max_drawdown_pct, profit_factor, avg_trade_pnl,
                         best_trade_pnl, worst_trade_pnl, avg_bars_held,
                         sharpe_ratio)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, [
                        (result.run_id, m.symbol, m.total_trades, m.winning_trades,
                         m.losing_trades, m.win_rate, m.total_pnl, m.total_return_pct,
                         m.max_drawdown_pct, m.profit_factor, m.avg_trade_pnl,
                         m.best_trade_pnl, m.worst_trade_pnl, m.avg_bars_held,
                         m.sharpe_ratio)
                        for m in result.symbol_metrics
                    ])

                conn.commit()
            return True
        except Exception as e:
            print(f"[BacktestDB] Error saving run: {e}")
            return False

    def create_pending_run(self, run_id: str, name: str, mode: str,
                           symbols: List[str], config: Dict, from_date: str,
                           to_date: str, initial_capital: float):
        """Insert a pending placeholder so progress can be polled."""
        try:
            with self._connect() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO backtest_runs
                    (id, name, mode, symbols, config, from_date, to_date,
                     initial_capital, status, created_at)
                    VALUES (?,?,?,?,?,?,?,?,'running',?)
                """, (run_id, name, mode, json.dumps(symbols),
                      json.dumps(config), from_date, to_date,
                      initial_capital, datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            print(f"[BacktestDB] Error creating pending run: {e}")

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def list_runs(self, mode: Optional[str] = None, limit: int = 50) -> List[Dict]:
        query = """SELECT id, name, mode, symbols, from_date, to_date,
                          initial_capital, final_capital, total_return_pct,
                          max_drawdown_pct, sharpe_ratio, total_trades,
                          win_rate, profit_factor, status, created_at,
                          duration_seconds
                   FROM backtest_runs"""
        params = []
        if mode:
            query += " WHERE mode = ?"
            params.append(mode)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        try:
            with self._connect() as conn:
                rows = conn.execute(query, params).fetchall()
                result = []
                for row in rows:
                    d = dict(row)
                    d["symbols"] = json.loads(d["symbols"] or "[]")
                    result.append(d)
                return result
        except Exception as e:
            print(f"[BacktestDB] Error listing runs: {e}")
            return []

    def get_run(self, run_id: str) -> Optional[Dict]:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT * FROM backtest_runs WHERE id=?", (run_id,)
                ).fetchone()
                if not row:
                    return None
                d = dict(row)
                d["symbols"] = json.loads(d.get("symbols") or "[]")
                d["config"] = json.loads(d.get("config") or "{}")
                d["equity_curve"] = json.loads(d.get("equity_curve") or "[]")

                # Trades
                trades = conn.execute(
                    "SELECT * FROM backtest_trades WHERE run_id=? ORDER BY entry_time",
                    (run_id,)
                ).fetchall()
                d["trades"] = [dict(t) for t in trades]

                # Metrics
                metrics = conn.execute(
                    "SELECT * FROM backtest_metrics WHERE run_id=?", (run_id,)
                ).fetchall()
                d["symbol_metrics"] = [dict(m) for m in metrics]

                return d
        except Exception as e:
            print(f"[BacktestDB] Error getting run {run_id}: {e}")
            return None

    def delete_run(self, run_id: str) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM backtest_trades WHERE run_id=?", (run_id,))
                conn.execute("DELETE FROM backtest_metrics WHERE run_id=?", (run_id,))
                conn.execute("DELETE FROM backtest_runs WHERE id=?", (run_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"[BacktestDB] Error deleting run {run_id}: {e}")
            return False

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_csv(self, run_id: str) -> Optional[str]:
        """Return trades as CSV string."""
        run = self.get_run(run_id)
        if not run:
            return None
        output = io.StringIO()
        fieldnames = [
            "symbol", "direction", "entry_time", "entry_price",
            "exit_time", "exit_price", "quantity", "pnl", "pnl_pct",
            "exit_reason", "bars_held",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for t in run.get("trades", []):
            writer.writerow({k: t.get(k, "") for k in fieldnames})
        return output.getvalue()

    def export_json(self, run_id: str) -> Optional[str]:
        """Return full run as JSON string."""
        run = self.get_run(run_id)
        if not run:
            return None
        return json.dumps(run, indent=2, default=str)
