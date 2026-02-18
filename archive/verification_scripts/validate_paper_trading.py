"""
Paper Trading Validation Script
Validates broker connectivity, data fetching, and order placement in paper trading mode
Validates: Requirement 15.3
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_trading_validation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


def load_config(config_file: str = "config_paper_trading.json"):
    """Load configuration file."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        logging.info(f"✅ Configuration loaded from {config_file}")
        return config
    except FileNotFoundError:
        logging.error(f"❌ Configuration file not found: {config_file}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"❌ Invalid JSON in configuration file: {e}")
        return None


def validate_broker_connectivity(broker):
    """
    Validate broker connectivity.
    
    Args:
        broker: Broker adapter instance
    
    Returns:
        bool: True if connected successfully
    """
    logging.info("="*80)
    logging.info("STEP 1: Validating Broker Connectivity")
    logging.info("="*80)
    
    try:
        success = broker.connect()
        if success:
            logging.info("✅ Broker connection successful")
            
            # Check if connection is active
            if broker.is_connected():
                logging.info("✅ Broker connection is active")
                return True
            else:
                logging.error("❌ Broker connection is not active")
                return False
        else:
            logging.error("❌ Broker connection failed")
            return False
    except Exception as e:
        logging.error(f"❌ Broker connection error: {e}")
        return False


def validate_data_fetching(broker, symbols, timeframe=30):
    """
    Validate data fetching for all configured instruments.
    
    Args:
        broker: Broker adapter instance
        symbols: List of symbols to validate
        timeframe: Timeframe in minutes
    
    Returns:
        tuple: (success_count, total_count, failed_symbols)
    """
    logging.info("="*80)
    logging.info("STEP 2: Validating Data Fetching")
    logging.info("="*80)
    
    success_count = 0
    failed_symbols = []
    
    for symbol in symbols:
        logging.info(f"\nTesting data fetch for {symbol}...")
        
        try:
            # Convert timeframe to broker format
            broker_timeframe = broker.convert_timeframe(timeframe)
            
            # Fetch historical data
            df = broker.get_historical_data(symbol, broker_timeframe, 100)
            
            if df is not None and len(df) > 0:
                # Validate data format
                required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
                if all(col in df.columns for col in required_columns):
                    logging.info(f"✅ {symbol}: Fetched {len(df)} bars with correct format")
                    logging.info(f"   Latest close: {df.iloc[-1]['close']:.2f}")
                    success_count += 1
                else:
                    logging.error(f"❌ {symbol}: Missing required columns")
                    failed_symbols.append(symbol)
            else:
                logging.error(f"❌ {symbol}: No data returned")
                failed_symbols.append(symbol)
                
        except Exception as e:
            logging.error(f"❌ {symbol}: Data fetch error - {e}")
            failed_symbols.append(symbol)
    
    logging.info(f"\nData Fetch Summary: {success_count}/{len(symbols)} successful")
    return success_count, len(symbols), failed_symbols


def validate_paper_trading_orders(paper_engine, symbols):
    """
    Validate order placement in paper trading mode.
    
    Args:
        paper_engine: Paper trading engine instance
        symbols: List of symbols to test
    
    Returns:
        tuple: (success_count, total_count, failed_orders)
    """
    logging.info("="*80)
    logging.info("STEP 3: Validating Paper Trading Order Placement")
    logging.info("="*80)
    
    success_count = 0
    failed_orders = []
    test_orders = []
    
    # Test different order types
    test_cases = [
        {
            'symbol': symbols[0] if symbols else 'RELIANCE',
            'direction': 1,
            'quantity': 10,
            'order_type': 'MARKET',
            'current_price': 2500.0,
            'stop_loss': 2450.0,
            'take_profit': 2600.0
        },
        {
            'symbol': symbols[1] if len(symbols) > 1 else 'TCS',
            'direction': -1,
            'quantity': 5,
            'order_type': 'MARKET',
            'current_price': 3500.0,
            'stop_loss': 3550.0,
            'take_profit': 3400.0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logging.info(f"\nTest Case {i}: {test_case['symbol']} {'BUY' if test_case['direction'] == 1 else 'SELL'}")
        
        try:
            order_id = paper_engine.place_order(
                symbol=test_case['symbol'],
                direction=test_case['direction'],
                quantity=test_case['quantity'],
                order_type=test_case['order_type'],
                current_price=test_case['current_price'],
                stop_loss=test_case['stop_loss'],
                take_profit=test_case['take_profit'],
                product_type='MIS'
            )
            
            if order_id:
                logging.info(f"✅ Order placed successfully: {order_id}")
                test_orders.append(order_id)
                success_count += 1
            else:
                logging.error(f"❌ Order placement failed")
                failed_orders.append(test_case['symbol'])
                
        except Exception as e:
            logging.error(f"❌ Order placement error: {e}")
            failed_orders.append(test_case['symbol'])
    
    # Test position tracking
    logging.info("\nValidating Position Tracking...")
    positions = paper_engine.get_positions()
    logging.info(f"✅ Retrieved {len(positions)} open positions")
    
    for pos in positions:
        logging.info(f"   {pos['symbol']}: {pos['quantity']} @ {pos['entry_price']:.2f}, P&L: {pos['pnl']:.2f}")
    
    # Test account info
    logging.info("\nValidating Account Information...")
    account_info = paper_engine.get_account_info()
    logging.info(f"✅ Balance: ₹{account_info['balance']:,.2f}")
    logging.info(f"✅ Equity: ₹{account_info['equity']:,.2f}")
    logging.info(f"✅ Margin Available: ₹{account_info['margin_available']:,.2f}")
    logging.info(f"✅ Margin Used: ₹{account_info['margin_used']:,.2f}")
    
    # Test position closing
    if test_orders:
        logging.info("\nValidating Position Closing...")
        for order_id in test_orders:
            try:
                # Simulate price movement
                success = paper_engine.close_position(order_id, 2550.0)
                if success:
                    logging.info(f"✅ Position closed successfully: {order_id}")
                else:
                    logging.warning(f"⚠️  Position close failed: {order_id}")
            except Exception as e:
                logging.error(f"❌ Position close error: {e}")
    
    logging.info(f"\nOrder Placement Summary: {success_count}/{len(test_cases)} successful")
    return success_count, len(test_cases), failed_orders


def generate_validation_report(results):
    """
    Generate validation report.
    
    Args:
        results: Dictionary with validation results
    """
    logging.info("="*80)
    logging.info("VALIDATION REPORT")
    logging.info("="*80)
    
    report_file = f"paper_trading_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("PAPER TRADING VALIDATION REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        # Broker Connectivity
        f.write("1. BROKER CONNECTIVITY\n")
        f.write(f"   Status: {'✅ PASS' if results['broker_connected'] else '❌ FAIL'}\n\n")
        
        # Data Fetching
        f.write("2. DATA FETCHING\n")
        f.write(f"   Successful: {results['data_success']}/{results['data_total']}\n")
        if results['data_failed']:
            f.write(f"   Failed Symbols: {', '.join(results['data_failed'])}\n")
        f.write(f"   Status: {'✅ PASS' if results['data_success'] == results['data_total'] else '⚠️  PARTIAL'}\n\n")
        
        # Paper Trading Orders
        f.write("3. PAPER TRADING ORDER PLACEMENT\n")
        f.write(f"   Successful: {results['order_success']}/{results['order_total']}\n")
        if results['order_failed']:
            f.write(f"   Failed Orders: {', '.join(results['order_failed'])}\n")
        f.write(f"   Status: {'✅ PASS' if results['order_success'] == results['order_total'] else '⚠️  PARTIAL'}\n\n")
        
        # Overall Status
        f.write("="*80 + "\n")
        f.write("OVERALL STATUS\n")
        f.write("="*80 + "\n")
        
        all_passed = (
            results['broker_connected'] and
            results['data_success'] == results['data_total'] and
            results['order_success'] == results['order_total']
        )
        
        if all_passed:
            f.write("✅ ALL VALIDATIONS PASSED\n")
            f.write("The system is ready for paper trading.\n")
        else:
            f.write("⚠️  SOME VALIDATIONS FAILED\n")
            f.write("Please review the failed items above before proceeding.\n")
    
    logging.info(f"\n✅ Validation report saved to: {report_file}")
    
    # Print summary
    logging.info("\nVALIDATION SUMMARY:")
    logging.info(f"  Broker Connectivity: {'✅ PASS' if results['broker_connected'] else '❌ FAIL'}")
    logging.info(f"  Data Fetching: {results['data_success']}/{results['data_total']} ({'✅ PASS' if results['data_success'] == results['data_total'] else '⚠️  PARTIAL'})")
    logging.info(f"  Paper Trading Orders: {results['order_success']}/{results['order_total']} ({'✅ PASS' if results['order_success'] == results['order_total'] else '⚠️  PARTIAL'})")
    
    if all_passed:
        logging.info("\n✅ ALL VALIDATIONS PASSED - System ready for paper trading")
        return True
    else:
        logging.warning("\n⚠️  SOME VALIDATIONS FAILED - Review report before proceeding")
        return False


def main():
    """Main validation function."""
    logging.info("="*80)
    logging.info("PAPER TRADING VALIDATION SCRIPT")
    logging.info("="*80)
    
    # Load configuration
    config = load_config()
    if not config:
        logging.error("❌ Cannot proceed without valid configuration")
        sys.exit(1)
    
    # Ensure paper trading is enabled
    if not config.get('paper_trading', False):
        logging.error("❌ Paper trading is not enabled in configuration")
        logging.error("   Please set 'paper_trading': true in config file")
        sys.exit(1)
    
    logging.info("✅ Paper trading mode is enabled")
    
    # Initialize broker adapter
    broker_type = config.get('broker', 'kite')
    logging.info(f"Broker type: {broker_type}")
    
    if broker_type == 'kite':
        from src.kite_adapter import KiteAdapter
        broker = KiteAdapter(config)
    else:
        logging.error(f"❌ Unsupported broker type: {broker_type}")
        sys.exit(1)
    
    # Initialize paper trading engine
    from src.paper_trading import PaperTradingEngine
    initial_balance = config.get('paper_trading_initial_balance', 100000.0)
    paper_engine = PaperTradingEngine(initial_balance)
    
    # Get symbols from config
    symbols = config.get('symbols', ['RELIANCE', 'TCS', 'INFY'])
    logging.info(f"Testing with symbols: {symbols}")
    
    # Run validations
    results = {}
    
    # 1. Validate broker connectivity
    results['broker_connected'] = validate_broker_connectivity(broker)
    
    if not results['broker_connected']:
        logging.error("❌ Cannot proceed without broker connectivity")
        sys.exit(1)
    
    # 2. Validate data fetching
    data_success, data_total, data_failed = validate_data_fetching(
        broker, symbols, config.get('timeframe', 30)
    )
    results['data_success'] = data_success
    results['data_total'] = data_total
    results['data_failed'] = data_failed
    
    # 3. Validate paper trading orders
    order_success, order_total, order_failed = validate_paper_trading_orders(
        paper_engine, symbols
    )
    results['order_success'] = order_success
    results['order_total'] = order_total
    results['order_failed'] = order_failed
    
    # 4. Generate validation report
    all_passed = generate_validation_report(results)
    
    # Disconnect broker
    broker.disconnect()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
