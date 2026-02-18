"""
Property-Based Test for Paper Trading Order Logging
Feature: indian-market-broker-integration, Property 22: Paper Trading Order Logging
Validates: Requirements 15.2

Property: For any order placed in paper trading mode, the system should log the simulated 
order with all parameters and the simulated outcome.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from src.paper_trading import PaperTradingEngine
import logging
from io import StringIO


# Strategy for generating valid order parameters
@st.composite
def order_parameters(draw):
    """Generate valid order parameters for testing."""
    symbol = draw(st.sampled_from(["RELIANCE", "TCS", "INFY", "NIFTY", "BANKNIFTY"]))
    direction = draw(st.sampled_from([1, -1]))  # 1 for buy, -1 for sell
    # Limit quantity to ensure it fits within initial balance
    quantity = draw(st.integers(min_value=1, max_value=50))
    # Limit price to ensure order fits within initial balance
    current_price = draw(st.floats(min_value=100.0, max_value=1000.0))
    
    # Calculate stop loss and take profit based on direction
    if direction == 1:  # Buy
        stop_loss = current_price * draw(st.floats(min_value=0.95, max_value=0.99))
        take_profit = current_price * draw(st.floats(min_value=1.01, max_value=1.10))
    else:  # Sell
        stop_loss = current_price * draw(st.floats(min_value=1.01, max_value=1.05))
        take_profit = current_price * draw(st.floats(min_value=0.90, max_value=0.99))
    
    return {
        'symbol': symbol,
        'direction': direction,
        'quantity': quantity,
        'current_price': current_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit
    }


@given(params=order_parameters())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_paper_trading_order_placement_logging(params, caplog):
    """
    Property 22: Paper Trading Order Logging
    
    For any order placed in paper trading mode, the system should log:
    - Order ID
    - Symbol
    - Direction (BUY/SELL)
    - Quantity
    - Entry Price
    - Order Type
    - Product Type
    - Stop Loss (if provided)
    - Take Profit (if provided)
    - Margin Used
    - Remaining Balance
    
    Validates: Requirement 15.2
    """
    # Initialize paper trading engine
    initial_balance = 100000.0
    engine = PaperTradingEngine(initial_balance)
    
    # Capture logs
    with caplog.at_level(logging.INFO):
        # Place order
        order_id = engine.place_order(
            symbol=params['symbol'],
            direction=params['direction'],
            quantity=params['quantity'],
            order_type="MARKET",
            stop_loss=params['stop_loss'],
            take_profit=params['take_profit'],
            product_type="MIS",
            current_price=params['current_price']
        )
    
    # Property: Order should be placed successfully OR rejected with proper logging
    if order_id is None:
        # Order was rejected - check for rejection logging
        assert any("PAPER TRADE REJECTED" in record.message 
                   for record in caplog.records), \
            "Rejected orders should be logged with PAPER TRADE REJECTED marker"
        assert any("Insufficient margin" in record.message 
                   for record in caplog.records), \
            "Rejection reason should be logged"
        return  # Skip remaining checks for rejected orders
    
    # For successful orders, verify all logging requirements
    assert any("Order ID:" in record.message and order_id in record.message 
               for record in caplog.records), \
        "Order ID should be logged"
    
    # Property: Symbol should be logged
    assert any(params['symbol'] in record.message 
               for record in caplog.records), \
        f"Symbol {params['symbol']} should be logged"
    
    # Property: Direction should be logged
    direction_str = "BUY" if params['direction'] == 1 else "SELL"
    assert any(direction_str in record.message 
               for record in caplog.records), \
        f"Direction {direction_str} should be logged"
    
    # Property: Quantity should be logged
    assert any(f"Quantity: {params['quantity']}" in record.message 
               for record in caplog.records), \
        f"Quantity {params['quantity']} should be logged"
    
    # Property: Entry Price should be logged
    assert any("Entry Price:" in record.message 
               for record in caplog.records), \
        "Entry Price should be logged"
    
    # Property: Order Type should be logged
    assert any("Order Type: MARKET" in record.message 
               for record in caplog.records), \
        "Order Type should be logged"
    
    # Property: Product Type should be logged
    assert any("Product Type: MIS" in record.message 
               for record in caplog.records), \
        "Product Type should be logged"
    
    # Property: Stop Loss should be logged if provided
    assert any("Stop Loss:" in record.message 
               for record in caplog.records), \
        "Stop Loss should be logged when provided"
    
    # Property: Take Profit should be logged if provided
    assert any("Take Profit:" in record.message 
               for record in caplog.records), \
        "Take Profit should be logged when provided"
    
    # Property: Margin Used should be logged
    assert any("Margin Used:" in record.message 
               for record in caplog.records), \
        "Margin Used should be logged"
    
    # Property: Remaining Balance should be logged
    assert any("Remaining Balance:" in record.message 
               for record in caplog.records), \
        "Remaining Balance should be logged"
    
    # Property: Paper trade marker should be present
    assert any("PAPER TRADE" in record.message 
               for record in caplog.records), \
        "Paper trade marker should be present in logs"


@given(params=order_parameters())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_paper_trading_position_close_logging(params, caplog):
    """
    Property 22: Paper Trading Position Close Logging
    
    For any position closed in paper trading mode, the system should log:
    - Order ID
    - Symbol
    - Direction
    - Quantity
    - Entry Price
    - Exit Price
    - P&L (absolute and percentage)
    - New Balance
    - New Equity
    
    Validates: Requirement 15.2
    """
    # Initialize paper trading engine
    initial_balance = 100000.0
    engine = PaperTradingEngine(initial_balance)
    
    # Place order
    order_id = engine.place_order(
        symbol=params['symbol'],
        direction=params['direction'],
        quantity=params['quantity'],
        order_type="MARKET",
        stop_loss=params['stop_loss'],
        take_profit=params['take_profit'],
        product_type="MIS",
        current_price=params['current_price']
    )
    
    assert order_id is not None, "Order should be placed (if rejected, test parameters need adjustment)"
    
    # Simulate price movement
    if params['direction'] == 1:  # Long position
        # Price moves up for profit
        exit_price = params['current_price'] * 1.02
    else:  # Short position
        # Price moves down for profit
        exit_price = params['current_price'] * 0.98
    
    # Capture logs for position close
    with caplog.at_level(logging.INFO):
        success = engine.close_position(order_id, exit_price)
    
    # Property: Position should close successfully
    assert success, "Paper trading position should close successfully"
    
    # Property: Order ID should be logged
    assert any("Order ID:" in record.message and order_id in record.message 
               for record in caplog.records), \
        "Order ID should be logged on close"
    
    # Property: Symbol should be logged
    assert any(params['symbol'] in record.message 
               for record in caplog.records), \
        f"Symbol {params['symbol']} should be logged on close"
    
    # Property: Direction should be logged
    direction_str = "BUY" if params['direction'] == 1 else "SELL"
    assert any(direction_str in record.message 
               for record in caplog.records), \
        f"Direction {direction_str} should be logged on close"
    
    # Property: Entry Price should be logged
    assert any("Entry Price:" in record.message 
               for record in caplog.records), \
        "Entry Price should be logged on close"
    
    # Property: Exit Price should be logged
    assert any("Exit Price:" in record.message 
               for record in caplog.records), \
        "Exit Price should be logged on close"
    
    # Property: P&L should be logged
    assert any("P&L:" in record.message 
               for record in caplog.records), \
        "P&L should be logged on close"
    
    # Property: New Balance should be logged
    assert any("New Balance:" in record.message 
               for record in caplog.records), \
        "New Balance should be logged on close"
    
    # Property: New Equity should be logged
    assert any("New Equity:" in record.message 
               for record in caplog.records), \
        "New Equity should be logged on close"
    
    # Property: Paper trade closed marker should be present
    assert any("PAPER TRADE CLOSED" in record.message 
               for record in caplog.records), \
        "Paper trade closed marker should be present in logs"


@given(
    initial_balance=st.floats(min_value=10000.0, max_value=1000000.0),
    num_trades=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_paper_trading_all_trades_logged(initial_balance, num_trades, caplog):
    """
    Property 22: All Paper Trading Trades Logged
    
    For any sequence of paper trades, all trades should be logged with complete information.
    
    Validates: Requirement 15.2
    """
    engine = PaperTradingEngine(initial_balance)
    
    placed_orders = []
    
    with caplog.at_level(logging.INFO):
        # Place multiple orders
        for i in range(num_trades):
            order_id = engine.place_order(
                symbol="RELIANCE",
                direction=1 if i % 2 == 0 else -1,
                quantity=10,
                order_type="MARKET",
                current_price=2500.0,
                product_type="MIS"
            )
            
            if order_id:
                placed_orders.append(order_id)
    
    # Property: All placed orders should be logged
    for order_id in placed_orders:
        assert any(order_id in record.message 
                   for record in caplog.records), \
            f"Order {order_id} should be logged"
    
    # Property: Each order should have paper trade marker
    paper_trade_logs = [record for record in caplog.records 
                        if "PAPER TRADE" in record.message]
    assert len(paper_trade_logs) >= len(placed_orders), \
        "Each paper trade should have paper trade marker in logs"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
