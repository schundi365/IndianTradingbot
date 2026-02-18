# Task 10.1: Comprehensive Broker Adapter Integration Tests

## Overview
Comprehensive integration tests for all broker adapters (KiteAdapter and PaperTradingAdapter) with the dashboard's BrokerManager service.

## Test Coverage

### 1. PaperTradingAdapter Integration Tests

#### Test: Connection Management
- **test_paper_trading_connect**: Verifies connection and disconnection
- **Expected**: Connect succeeds, is_connected returns True, disconnect works

#### Test: Instrument Management
- **test_paper_trading_get_instruments**: Verifies mock instruments are available
- **Expected**: Returns list with RELIANCE, NIFTY 50, etc.

#### Test: Historical Data
- **test_paper_trading_get_historical_data**: Fetches 100 bars of 30-minute data
- **Expected**: Returns DataFrame with correct columns and OHLC relationships

#### Test: Order Placement
- **test_paper_trading_place_order**: Places market buy order
- **Expected**: Order ID returned, position created correctly

#### Test: Account Information
- **test_paper_trading_get_account_info**: Retrieves account balance and margins
- **Expected**: Returns dict with balance, equity, margin_available, margin_used

#### Test: Instrument Information
- **test_paper_trading_get_instrument_info**: Gets lot size and tick size
- **Expected**: Returns instrument details for RELIANCE

#### Test: Full Trade Cycle
- **test_paper_trading_full_trade_cycle**: Complete buy-sell cycle
- **Expected**: Position opens and closes correctly

### 2. KiteAdapter Integration Tests (Mocked)

#### Test: Connection with Valid Token
- **test_kite_connect_with_valid_token**: Connects using mock token file
- **Expected**: Connection succeeds with valid token

#### Test: Historical Data Fetching
- **test_kite_get_historical_data**: Fetches historical data via mocked API
- **Expected**: Returns 100 bars with correct structure

#### Test: Order Placement
- **test_kite_place_order**: Places order through mocked Kite API
- **Expected**: Returns order ID, API called correctly

#### Test: Position Retrieval
- **test_kite_get_positions**: Gets positions from mocked API
- **Expected**: Returns position list with correct format

#### Test: Account Information
- **test_kite_get_account_info**: Gets account margins
- **Expected**: Returns account info with balance and margins

### 3. BrokerManager Integration Tests

#### Test: Supported Brokers List
- **test_broker_manager_get_supported_brokers**: Lists available brokers
- **Expected**: Returns list including 'kite'

#### Test: Paper Trading Connection
- **test_broker_manager_paper_trading_connection**: Connects via BrokerManager
- **Expected**: Connection succeeds, adapter accessible, disconnect works

#### Test: Status Reporting
- **test_broker_manager_status**: Gets connection status
- **Expected**: Status reflects connection state correctly

#### Test: Connection Testing
- **test_broker_manager_test_connection**: Tests active connection
- **Expected**: Returns success with balance info

#### Test: Kite Connection
- **test_broker_manager_kite_connection**: Connects to Kite via manager
- **Expected**: OAuth flow works, user info retrieved

### 4. Cross-Adapter Compatibility Tests

#### Test: Interface Compliance
- **test_adapter_interface_compliance**: Verifies all adapters implement required methods
- **Expected**: All adapters have connect, disconnect, get_historical_data, etc.

#### Test: Historical Data Format
- **test_historical_data_format_consistency**: Checks data format consistency
- **Expected**: All adapters return same DataFrame structure

#### Test: Position Format
- **test_position_format_consistency**: Checks position format consistency
- **Expected**: All adapters return same position dictionary structure

#### Test: Account Info Format
- **test_account_info_format_consistency**: Checks account info consistency
- **Expected**: All adapters return same account info structure

### 5. Error Handling Tests

#### Test: Invalid Symbol
- **test_paper_trading_invalid_symbol**: Handles non-existent symbol
- **Expected**: Returns None gracefully

#### Test: Invalid Quantity
- **test_paper_trading_invalid_order_quantity**: Handles negative quantity
- **Expected**: Returns None, doesn't place order

#### Test: Unsupported Broker
- **test_broker_manager_unsupported_broker**: Handles unknown broker
- **Expected**: Returns error message

#### Test: Operations When Disconnected
- **test_operations_when_not_connected**: Operations fail gracefully
- **Expected**: Returns empty/zero values, doesn't crash

## Test Fixtures

### broker_manager
Creates a BrokerManager instance for testing

### paper_trading_config
Configuration dictionary for PaperTradingAdapter:
```python
{
    'initial_balance': 100000.0,
    'default_exchange': 'NSE'
}
```

### kite_config
Mock configuration for KiteAdapter:
```python
{
    'kite_api_key': 'test_api_key',
    'kite_token_file': 'test_kite_token.json',
    'default_exchange': 'NSE'
}
```

### mock_kite_token_file
Creates a temporary token file with today's date for testing

## Running the Tests

```bash
# Run all broker adapter integration tests
python -m pytest indian_dashboard/tests/test_broker_adapter_integration.py -v

# Run specific test class
python -m pytest indian_dashboard/tests/test_broker_adapter_integration.py::TestPaperTradingAdapterIntegration -v

# Run with coverage
python -m pytest indian_dashboard/tests/test_broker_adapter_integration.py --cov=services.broker_manager --cov=src.paper_trading_adapter --cov=src.kite_adapter

# Run with detailed output
python -m pytest indian_dashboard/tests/test_broker_adapter_integration.py -vv --tb=long
```

## Test Implementation Status

✅ Test structure defined
✅ All test cases documented
✅ Fixtures created
✅ Mock strategies defined
✅ Error handling covered
✅ Cross-adapter compatibility verified

## Integration Points Tested

1. **PaperTradingAdapter ↔ BrokerManager**
   - Connection management
   - Adapter retrieval
   - Status reporting

2. **KiteAdapter ↔ BrokerManager**
   - OAuth flow
   - Token management
   - API integration

3. **Adapter ↔ Dashboard Services**
   - InstrumentService uses adapters for data
   - BotController uses adapters for trading
   - API endpoints use BrokerManager

## Requirements Validated

- **Requirement 4.2**: Test with KiteAdapter ✅
- **Requirement 4.2**: Test with PaperTradingAdapter ✅
- **Requirement 4.2**: Handle adapter-specific quirks ✅

## Next Steps

1. Implement any missing adapter methods discovered during testing
2. Add performance tests for data fetching
3. Add stress tests for concurrent operations
4. Add integration tests with real Kite sandbox (if available)
5. Document any adapter-specific limitations or quirks

## Notes

- Kite tests use mocking to avoid requiring real API credentials
- Paper trading tests run against real PaperTradingEngine
- All tests are isolated and can run in any order
- Tests clean up after themselves (disconnect adapters)
- Mock data is deterministic for reproducible tests
