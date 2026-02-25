"""
BacktestService
===============
Bridges the Flask API and BacktestEngine.
Runs backtests in a background thread so the API is non-blocking.
Progress is tracked per run_id and returned to polling clients.
"""

import logging
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BacktestService:
    """
    Service layer that manages running backtests / forward-tests
    asynchronously and persists results via BacktestDatabaseManager.
    """

    def __init__(self, db_manager, broker_manager):
        self.db = db_manager
        self.broker_manager = broker_manager
        # In-memory progress store: {run_id: {"pct": 0-100, "status": "running|done|failed"}}
        self._progress: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # API-facing methods
    # ------------------------------------------------------------------

    def start_run(
        self,
        name: str,
        symbols: list,
        config: dict,
        from_date: str,
        to_date: str,
        initial_capital: float,
        mode: str = "backtest",
    ) -> str:
        """
        Kick off a backtest/forward-test run in a background thread.

        Returns:
            run_id string that the caller can use to poll progress.
        """
        run_id = str(uuid.uuid4())

        # Register as pending in DB immediately
        self.db.create_pending_run(
            run_id=run_id,
            name=name,
            mode=mode,
            symbols=symbols,
            config=config,
            from_date=from_date,
            to_date=to_date,
            initial_capital=initial_capital,
        )

        with self._lock:
            self._progress[run_id] = {"pct": 0, "status": "running"}

        thread = threading.Thread(
            target=self._run_in_background,
            args=(run_id, name, symbols, config, from_date, to_date, initial_capital, mode),
            daemon=True,
            name=f"backtest-{run_id[:8]}",
        )
        thread.start()
        logger.info(f"[BacktestService] Started {mode} run {run_id} in background thread")
        return run_id

    def get_progress(self, run_id: str) -> Optional[Dict]:
        with self._lock:
            return self._progress.get(run_id)

    def list_runs(self, mode: Optional[str] = None) -> list:
        return self.db.list_runs(mode=mode)

    def get_result(self, run_id: str) -> Optional[Dict]:
        return self.db.get_run(run_id)

    def delete_run(self, run_id: str) -> bool:
        with self._lock:
            self._progress.pop(run_id, None)
        return self.db.delete_run(run_id)

    def export(self, run_id: str, fmt: str = "csv") -> Optional[str]:
        if fmt == "json":
            return self.db.export_json(run_id)
        return self.db.export_csv(run_id)

    # ------------------------------------------------------------------
    # Background worker
    # ------------------------------------------------------------------

    def _run_in_background(
        self,
        run_id: str,
        name: str,
        symbols: list,
        config: dict,
        from_date: str,
        to_date: str,
        initial_capital: float,
        mode: str,
    ):
        try:
            from src.core.backtest_engine import BacktestEngine

            # Get broker adapter for real data (if connected)
            broker_adapter = None
            try:
                if self.broker_manager and self.broker_manager.is_connected():
                    broker_adapter = self.broker_manager.get_adapter()
            except Exception as e:
                logger.debug(f"[BacktestService] Could not get broker adapter: {e}")

            engine = BacktestEngine(config=config, broker_adapter=broker_adapter)

            def _progress_cb(pct: float):
                with self._lock:
                    if run_id in self._progress:
                        self._progress[run_id]["pct"] = min(int(pct), 99)

            result = engine.run(
                run_id=run_id,
                name=name,
                symbols=symbols,
                from_date=from_date,
                to_date=to_date,
                initial_capital=initial_capital,
                mode=mode,
                progress_callback=_progress_cb,
            )

            self.db.save_run(result)

            with self._lock:
                self._progress[run_id] = {
                    "pct": 100,
                    "status": result.status,
                    "error": result.error,
                }

            logger.info(f"[BacktestService] Run {run_id} completed — status={result.status}")

        except Exception as e:
            logger.error(f"[BacktestService] Background run {run_id} crashed: {e}", exc_info=True)
            with self._lock:
                self._progress[run_id] = {"pct": 0, "status": "failed", "error": str(e)}
