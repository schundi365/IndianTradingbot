# Implementation Plan: Indian Market Broker Integration

## Overview

This plan outlines the implementation of a broker abstraction layer to migrate the existing MT5 forex trading bot to support Indian stock market trading through Kite Connect API. The implementation preserves 90% of existing trading logic while replacing broker-specific components.

## Tasks

- [x] 1. Create broker abstraction layer
  - Create `broker_adapter.py` with abstract base class defining standard interface
  - Define methods: connect(), disconnect(), is_connected(), get_historical_data(), place_order(), modify_order(), cancel_order(), get_positions(), get_account_info(), get_instrument_info(), convert_timeframe()
  - Add comprehensive docstrings for each method
  - _Requirements: 1.1, 1.2, 1.5_

- [x] 1.1 Write property test for broker adapter routing
  - **Property 1: Broker Adapter Routing**
  - **Validates: Requirements 1.2**

- [ ] 2. Implement Kite Connect adapter
  - [x] 2.1 Create `kite_adapter.py` implementing BrokerAdapter interface
    - Implement authentication using token file
    - Implement connection management with health checks
    - Add instrument token caching for faster lookups
    - _Requirements: 2.1, 2.2_
  
  - [x] 2.2 Write property test for Kite authentication
    - **Property 2: Kite Authentication Token Validation**
    - **Validates: Requirements 2.2, 3.1**
  
  - [x] 2.3 Write property test for authentication failure handling
    - **Property 3: Authentication Failure Handling**
    - **Validates: Requirements 2.3, 3.3, 3.4**
  
  - [x] 2.4 Implement historical data fetching
    - Convert timeframes to Kite format
    - Fetch OHLCV data using Kite API
    - Convert to pandas DataFrame with correct column types
    - Handle date range calculations for different timeframes
    - _Requirements: 2.4, 4.1, 4.2_
  
  - [ ] 2.5 Write property test for historical data format
    - **Property 4: Historical Data Format Consistency**
    - **Validates: Requirements 2.4, 4.1, 4.2, 14.1, 14.2, 14.3, 14.4**
  
  - [x] 2.6 Implement order placement
    - Convert order types to Kite format
    - Place market, limit, SL, and SL-M orders
    - Return order ID for tracking
    - Handle bracket orders for SL/TP
    - _Requirements: 2.5, 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 2.7 Write property test for order placement
    - **Property 5: Order Placement Success**
    - **Validates: Requirements 2.5, 5.1, 5.2, 5.3, 5.4, 5.5**
  
  - [x] 2.8 Implement order modification and cancellation
    - Modify order parameters (price, quantity, trigger)
    - Cancel orders by order ID
    - Handle errors gracefully
    - _Requirements: 5.6, 5.7_
  
  - [ ] 2.9 Write property tests for order modification and cancellation
    - **Property 26: Order Modification Success**
    - **Property 27: Order Cancellation Success**
    - **Validates: Requirements 5.6, 5.7**
  
  - [x] 2.10 Implement position tracking
    - Fetch positions from Kite API
    - Convert to standard position format
    - Calculate P&L in absolute and percentage terms
    - Filter by symbol and magic number equivalent
    - _Requirements: 2.6, 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ] 2.11 Write property test for position data
    - **Property 6: Position Data Completeness**
    - **Validates: Requirements 2.6, 6.1, 6.2, 6.4**
  
  - [x] 2.12 Implement account information retrieval
    - Fetch margins from Kite API
    - Extract balance, equity, available margin, used margin
    - Handle API errors gracefully
    - _Requirements: 2.7_
  
  - [ ] 2.13 Write property test for account info
    - **Property 7: Account Information Retrieval**
    - **Validates: Requirements 2.7**
  
  - [x] 2.14 Implement instrument info retrieval
    - Fetch instrument details from Kite
    - Extract lot size, tick size, instrument token
    - Cache instrument data for performance
    - _Requirements: 2.8, 8.4_
  
  - [ ] 2.15 Write property test for symbol to token conversion
    - **Property 8: Symbol to Token Conversion**
    - **Validates: Requirements 2.8, 8.4**
  
  - [x] 2.16 Implement rate limiting and retry logic
    - Detect rate limit errors
    - Implement exponential backoff (2^attempt seconds)
    - Log retry attempts
    - _Requirements: 2.9, 4.4, 12.3_
  
  - [ ] 2.17 Write property test for rate limit retry
    - **Property 9: Rate Limit Retry Logic**
    - **Validates: Requirements 2.9, 4.4, 12.3**

- [ ] 3. Create main Indian trading bot class
  - [x] 3.1 Create `indian_trading_bot.py` with IndianTradingBot class
    - Initialize with broker adapter
    - Copy configuration from MT5 bot
    - Initialize same components (adaptive risk, ML, volume analyzer, trend detection)
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [x] 3.2 Implement market hours checking
    - Check if current time is within NSE trading hours (9:15 AM - 3:30 PM IST)
    - Check if current day is a weekday
    - Handle market holidays
    - _Requirements: 7.1, 7.2, 7.5_
  
  - [ ] 3.3 Write property test for trading hours enforcement
    - **Property 10: Trading Hours Enforcement**
    - **Validates: Requirements 7.1, 7.5**
  
  - [x] 3.4 Implement data fetching using broker adapter
    - Convert MT5 timeframe to broker format
    - Call broker adapter's get_historical_data()
    - Return data in same format as MT5 bot
    - _Requirements: 4.1, 4.2, 4.7_
  
  - [x] 3.5 Copy indicator calculation methods from MT5 bot
    - Copy calculate_indicators() method exactly
    - Verify all indicators work with broker data
    - No changes needed to indicator logic
    - _Requirements: 10.1_
  
  - [x] 3.6 Copy signal generation methods from MT5 bot
    - Copy check_entry_signal() method exactly
    - Copy all signal detection logic (crossover, momentum, pullback, breakout)
    - No changes needed to signal logic
    - _Requirements: 10.2_
  
  - [x] 3.7 Adapt position sizing for Indian markets
    - Use broker adapter for account info
    - Respect instrument lot sizes
    - Respect instrument tick sizes
    - Ensure position size doesn't exceed available margin
    - Calculate risk based on equity
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 3.8 Write property tests for risk management
    - **Property 13: Position Size Lot Compliance**
    - **Property 14: Stop Loss Tick Size Compliance**
    - **Property 15: Margin Limit Enforcement**
    - **Property 16: Risk Calculation Based on Equity**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**
  
  - [x] 3.9 Implement position opening using broker adapter
    - Call broker adapter's place_order()
    - Store position info for tracking
    - Handle split orders if enabled
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 3.10 Copy position management from MT5 bot
    - Copy trailing stop logic
    - Copy break-even stop logic
    - Copy time-based exit logic
    - Adapt to use broker adapter for position updates
    - _Requirements: 10.4_
  
  - [x] 3.11 Implement main bot loop
    - Check market hours before each cycle
    - Iterate through configured symbols
    - Call run_strategy() for each symbol
    - Handle keyboard interrupt gracefully
    - _Requirements: 7.1, 7.2_

- [ ] 4. Checkpoint - Test core functionality
  - Ensure all tests pass, ask the user if questions arise.

- [-] 5. Implement configuration management
  - [x] 5.1 Create configuration migration utility
    - Read MT5 bot configuration
    - Map MT5 symbols to Indian equivalents (XAUUSD → GOLD futures, etc.)
    - Convert MT5 timeframes to broker format
    - Add Indian market specific settings
    - Preserve all indicator and risk parameters
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ] 5.2 Write property test for timeframe conversion
    - **Property 11: Timeframe Conversion**
    - **Validates: Requirements 7.6, 11.4**
  
  - [ ] 5.3 Write property test for symbol mapping
    - **Property 17: Symbol Mapping Consistency**
    - **Validates: Requirements 11.3**
  
  - [x] 5.4 Create default configurations for Indian instruments
    - Create config for NIFTY futures trading
    - Create config for BANKNIFTY futures trading
    - Create config for equity trading (RELIANCE, TCS, INFY)
    - Include recommended parameters for each
    - _Requirements: 11.2_
  
  - [x] 5.5 Implement instrument validation
    - Check if configured instruments exist
    - Check if instruments are tradable
    - Validate instrument parameters (lot size, tick size)
    - _Requirements: 8.3_
  
  - [ ] 5.6 Write property test for instrument validation
    - **Property 12: Instrument Validation**
    - **Validates: Requirements 8.3**
  
  - [ ] 5.7 Implement broker selection from configuration
    - Read broker type from config
    - Load appropriate broker adapter
    - Initialize adapter with broker-specific config
    - _Requirements: 13.4_
  
  - [ ] 5.8 Write property test for broker selection
    - **Property 20: Broker Selection from Configuration**
    - **Validates: Requirements 13.4**

- [-] 6. Implement error handling and logging
  - [x] 6.1 Add comprehensive error handling
    - Handle authentication errors with clear instructions
    - Handle connection errors with retry logic
    - Handle data errors with fallback options
    - Handle order errors with descriptive messages
    - Handle market errors (closed, halt, circuit breaker)
    - _Requirements: 12.1, 12.2, 12.3, 12.4_
  
  - [ ] 6.2 Write property tests for error logging
    - **Property 18: Error Logging Completeness**
    - **Property 28: Order Failure Error Messages**
    - **Validates: Requirements 12.1, 12.4, 5.8**
  
  - [x] 6.3 Implement trading decision logging
    - Log all signals with timestamp and reasoning
    - Log all order placements with parameters
    - Log all position updates
    - Log all exits with P&L
    - _Requirements: 12.5_
  
  - [ ] 6.4 Write property test for trading decision logging
    - **Property 19: Trading Decision Logging**
    - **Validates: Requirements 12.5**
  
  - [x] 6.5 Add order parameter validation
    - Validate quantity is positive and multiple of lot size
    - Validate price is positive and multiple of tick size
    - Validate instrument exists
    - Return descriptive errors for invalid parameters
    - _Requirements: 5.9_
  
  - [ ] 6.6 Write property test for order validation
    - **Property 25: Order Parameter Validation**
    - **Validates: Requirements 5.9**

- [x] 7. Implement paper trading mode
  - [x] 7.1 Add paper trading configuration option
    - Add "paper_trading" flag to configuration
    - Initialize paper trading state tracking
    - _Requirements: 15.1_
  
  - [x] 7.2 Implement simulated order execution
    - Simulate order placement without calling broker API
    - Generate simulated order IDs
    - Track simulated positions
    - Calculate simulated P&L
    - _Requirements: 15.1, 15.2_
  
  - [x] 7.3 Write property test for paper trading logging
    - **Property 22: Paper Trading Order Logging**
    - **Validates: Requirements 15.2**
  
  - [x] 7.4 Create validation script
    - Check broker connectivity
    - Check data fetching for all configured instruments
    - Check order placement in paper trading mode
    - Generate validation report
    - _Requirements: 15.3_

- [ ] 8. Checkpoint - Integration testing
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Create documentation and examples
  - [x] 9.1 Create migration guide
    - Document step-by-step migration process
    - Include configuration examples
    - Include troubleshooting section
    - _Requirements: 11.1_
  
  - [x] 9.2 Create example configurations
    - Example for NIFTY futures trading
    - Example for equity intraday trading
    - Example for options trading
    - Include comments explaining each parameter
    - _Requirements: 15.4_
  
  - [ ] 9.3 Create testing guide
    - Document paper trading setup
    - Document validation process
    - Document recommended testing steps
    - _Requirements: 15.5_
  
  - [ ] 9.4 Create broker adapter development guide
    - Document how to add new broker adapters
    - Include template adapter code
    - Document testing requirements for new adapters
    - _Requirements: 13.5_
  
  - [ ] 9.5 Update main README
    - Add Indian market trading section
    - Add Kite Connect setup instructions
    - Add daily authentication instructions
    - Add troubleshooting section

- [ ] 10. Final integration and testing
  - [ ] 10.1 Run full integration test suite
    - Test with real Kite Connect sandbox account
    - Test all configured instruments
    - Test during market hours and after hours
    - Test error scenarios
  
  - [ ] 10.2 Run paper trading for full trading day
    - Monitor all signals generated
    - Verify all orders simulated correctly
    - Verify position tracking accurate
    - Verify risk limits enforced
  
  - [ ] 10.3 Performance testing
    - Measure data fetch latency
    - Measure order placement latency
    - Measure signal generation time
    - Verify memory and CPU usage within limits
  
  - [ ] 10.4 Create deployment checklist
    - List all pre-deployment verification steps
    - Include rollback plan
    - Include monitoring recommendations

- [ ] 11. Final checkpoint - Production readiness
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The implementation preserves 90% of existing MT5 bot logic
- Only broker-specific components (10%) are replaced
- All existing features (adaptive risk, ML, volume analysis, trend detection) continue to work

