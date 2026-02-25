"""
Backtest / Forward-test API endpoints
======================================
Blueprint prefix: /api/backtest
"""

import logging
from datetime import datetime
from flask import Blueprint, Response, jsonify, request

logger = logging.getLogger(__name__)

backtest_bp = Blueprint("backtest", __name__, url_prefix="/api/backtest")


def init_backtest_api(backtest_service):
    """Attach the BacktestService to this blueprint."""
    backtest_bp._service = backtest_service
    return backtest_bp


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _svc():
    return backtest_bp._service


def _err(msg: str, code: int = 400):
    return jsonify({"success": False, "error": msg}), code


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@backtest_bp.route("/run", methods=["POST"])
def start_run():
    """
    POST /api/backtest/run
    Body: {
        "name": str,
        "symbols": [str, ...],
        "config": {...},
        "from_date": "YYYY-MM-DD",
        "to_date":   "YYYY-MM-DD",
        "initial_capital": float,
        "mode": "backtest" | "forward"   (optional, default backtest)
    }
    """
    data = request.get_json(silent=True) or {}
    symbols = data.get("symbols", [])
    config = data.get("config", {})
    from_date = data.get("from_date", "")
    to_date = data.get("to_date", "")
    initial_capital = float(data.get("initial_capital", 500_000))
    mode = data.get("mode", "backtest").lower()
    name = data.get("name") or f"{'Backtest' if mode=='backtest' else 'Forward Test'} {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    if not symbols:
        return _err("symbols list is required")
    if mode == "backtest" and not from_date:
        return _err("from_date is required for backtest mode")

    # For forward test, default to date range from today onward
    if mode == "forward":
        from_date = from_date or datetime.now().strftime("%Y-%m-%d")
        to_date = to_date or (datetime.now().strftime("%Y-%m-%d"))

    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")

    try:
        run_id = _svc().start_run(
            name=name,
            symbols=symbols,
            config=config,
            from_date=from_date,
            to_date=to_date,
            initial_capital=initial_capital,
            mode=mode,
        )
        return jsonify({"success": True, "run_id": run_id, "name": name, "mode": mode}), 202
    except Exception as e:
        logger.error(f"Error starting backtest: {e}", exc_info=True)
        return _err(str(e), 500)


@backtest_bp.route("/status/<run_id>", methods=["GET"])
def get_status(run_id: str):
    """GET /api/backtest/status/<run_id>  — poll progress (0-100%)"""
    progress = _svc().get_progress(run_id)
    if progress is None:
        # Maybe already completed — check DB
        run = _svc().get_result(run_id)
        if run:
            return jsonify({"success": True, "run_id": run_id,
                            "pct": 100, "status": run.get("status", "completed")}), 200
        return _err("Run not found", 404)
    return jsonify({"success": True, "run_id": run_id, **progress}), 200


@backtest_bp.route("/results", methods=["GET"])
def list_results():
    """GET /api/backtest/results?mode=backtest|forward"""
    mode = request.args.get("mode")
    runs = _svc().list_runs(mode=mode)
    return jsonify({"success": True, "runs": runs, "count": len(runs)}), 200


@backtest_bp.route("/results/<run_id>", methods=["GET"])
def get_result(run_id: str):
    """GET /api/backtest/results/<run_id>  — full detail with trades + metrics"""
    result = _svc().get_result(run_id)
    if not result:
        return _err("Run not found", 404)
    return jsonify({"success": True, "result": result}), 200


@backtest_bp.route("/results/<run_id>", methods=["DELETE"])
def delete_result(run_id: str):
    """DELETE /api/backtest/results/<run_id>"""
    ok = _svc().delete_run(run_id)
    if ok:
        return jsonify({"success": True, "message": "Run deleted"}), 200
    return _err("Failed to delete run", 500)


@backtest_bp.route("/export/<run_id>", methods=["GET"])
def export_result(run_id: str):
    """
    GET /api/backtest/export/<run_id>?format=csv|json
    Returns file download.
    """
    fmt = request.args.get("format", "csv").lower()
    content = _svc().export(run_id, fmt)
    if content is None:
        return _err("Run not found or no data to export", 404)

    if fmt == "json":
        return Response(
            content,
            mimetype="application/json",
            headers={"Content-Disposition": f'attachment; filename="backtest_{run_id[:8]}.json"'},
        )
    # CSV
    return Response(
        content,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="backtest_{run_id[:8]}.csv"'},
    )
