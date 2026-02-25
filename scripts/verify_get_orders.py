import sys
from pathlib import Path
from typing import Dict

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.paper_trading_adapter import PaperTradingAdapter
from src.kite_adapter import KiteAdapter

def test_paper_trading_get_orders():
    print("Testing PaperTradingAdapter.get_orders()...")
    config = {'initial_balance': 100000.0}
    adapter = PaperTradingAdapter(config)
    adapter.connect()
    
    # Place a simulated order
    order_id = adapter.place_order(
        symbol='RELIANCE',
        direction=1,
        quantity=1,
        order_type='MARKET'
    )
    
    orders = adapter.get_orders()
    print(f"Orders found: {len(orders)}")
    for order in orders:
        print(f" - Order ID: {order['order_id']}, Status: {order['status']}, Symbol: {order['symbol']}")
    
    assert len(orders) > 0, "No orders found"
    assert 'order_id' in orders[0]
    assert 'status' in orders[0]
    print("PaperTradingAdapter test PASSED\n")

if __name__ == "__main__":
    try:
        test_paper_trading_get_orders()
    except Exception as e:
        print(f"Test FAILED: {e}")
        sys.exit(1)
