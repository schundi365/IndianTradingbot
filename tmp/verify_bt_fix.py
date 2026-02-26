
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.backtest_engine import BacktestTrade, SymbolMetrics, BacktestResult
from src.managers.backtest_db_manager import BacktestDatabaseManager
import json

def test_infinity_fix():
    # Mock a result with only winners
    trades = [
        BacktestTrade("TEST", "buy", "2025-01-01", 100, "2025-01-01", 110, 10, 100, 10, "tp", 1)
    ]
    metrics = SymbolMetrics("TEST", 1, 1, 0, 100.0, 100.0, 10.0, 0.0, float('inf'), 100.0, 100.0, 100.0, 1.0, 0.0)
    
    # The engine calculate_metrics would now return 99.9, but let's test the DB manager's safety too
    result = BacktestResult(
        run_id="test_run",
        mode="backtest",
        name="Test",
        symbols=["TEST"],
        config={},
        from_date="2025-01-01",
        to_date="2025-01-01",
        initial_capital=1000,
        final_capital=1100,
        total_return_pct=10.0,
        max_drawdown_pct=0.0,
        sharpe_ratio=0.0,
        total_trades=1,
        win_rate=100.0,
        profit_factor=float('inf'), # Force infinity to test exporter
        trades=trades,
        symbol_metrics=[metrics],
        equity_curve=[{"time": "2025-01-01", "equity": 1100}],
        status="completed",
        error=None,
        duration_seconds=1.0,
        created_at="2025-02-26"
    )
    
    db = BacktestDatabaseManager("/tmp/test_bt.db")
    db.save_run(result)
    
    json_str = db.export_json("test_run")
    print("Exported JSON:")
    print(json_str)
    
    # Load and check
    data = json.loads(json_str)
    print(f"Profit Factor in JSON: {data['profit_factor']}")
    assert data['profit_factor'] == 99.9
    print("Verification Successful!")

if __name__ == "__main__":
    test_infinity_fix()
