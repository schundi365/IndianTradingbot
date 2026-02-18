# Requirements Document

## Introduction

This document specifies the requirements for migrating an existing MT5 forex trading bot to support the Indian stock market using broker APIs, with Kite Connect (Zerodha) as the primary implementation. The system will maintain 90% of the existing bot logic (indicators, signals, risk management) while replacing the 10% that is broker-specific (connection, data fetching, order placement) through a flexible abstraction layer that supports multiple Indian broker APIs.

## Glossary

- **Trading_Bot**: The automated trading system that executes trades based on technical analysis
- **Broker_Adapter**: An abstraction layer that provides a uniform interface to different broker APIs
- **Kite_Connect**: Zerodha's official API for algorithmic trading in Indian markets
- **MT5**: MetaTrader 5 platform used for forex trading
- **Instrument**: A tradable security (stock, futures, options) in the Indian market
- **Position**: An open trade with entry price, stop loss, and take profit levels
- **Signal_Generator**: Component that analyzes market data and generates buy/sell signals
- **Risk_Manager**: Component that calculates position sizes and manages risk parameters
- **Market_Data_Provider**: Component that fetches historical and real-time market data
- **Order_Manager**: Component that places, modifies, and cancels orders
- **Access_Token**: Daily authentication token required by Kite Connect API
- **Instrument_Token**: Unique identifier for each tradable instrument in Kite Connect
- **NSE**: National Stock Exchange of India
- **BSE**: Bombay Stock Exchange
- **F&O**: Futures and Options segment
- **MIS**: Margin Intraday Square-off (intraday trading product type)
- **NRML**: Normal (delivery/carry forward product type)

## Requirements

### Requirement 1: Broker Abstraction Layer

**User Story:** As a trader, I want the bot to support multiple Indian broker APIs, so that I can switch brokers without rewriting my trading logic.

#### Acceptance Criteria

1. THE Broker_Adapter SHALL define a standard interface for all broker operations
2. WHEN a broker operation is requested, THE Broker_Adapter SHALL route it to the appropriate broker implementation
3. THE Trading_Bot SHALL interact only with the Broker_Adapter interface and not directly with broker-specific code
4. WHERE a new broker is added, THE system SHALL require only a new adapter implementation without modifying existing bot logic
5. THE Broker_Adapter SHALL support connection management, data fetching, order placement, position tracking, and account information retrieval

### Requirement 2: Kite Connect Primary Implementation

**User Story:** As a trader, I want to use Kite Connect as my primary broker, so that I can trade on India's most popular trading platform.

#### Acceptance Criteria

1. THE Kite_Adapter SHALL implement the Broker_Adapter interface for Kite Connect API
2. WHEN the system starts, THE Kite_Adapter SHALL authenticate using the access token from the login module
3. WHEN authentication fails, THE Kite_Adapter SHALL return a descriptive error and prevent trading operations
4. THE Kite_Adapter SHALL fetch historical data in OHLCV format for specified instruments and timeframes
5. THE Kite_Adapter SHALL place market orders, limit orders, stop-loss orders, and stop-loss market orders
6. THE Kite_Adapter SHALL retrieve current positions with entry price, quantity, and P&L information
7. THE Kite_Adapter SHALL retrieve account balance and available margin
8. THE Kite_Adapter SHALL convert instrument symbols to instrument tokens for API operations
9. WHEN rate limits are encountered, THE Kite_Adapter SHALL implement exponential backoff retry logic

### Requirement 3: Authentication and Token Management

**User Story:** As a trader, I want the bot to handle daily authentication automatically, so that I don't need to manually refresh tokens every day.

#### Acceptance Criteria

1. THE Authentication_Manager SHALL read the access token from the token file created by the login module
2. WHEN the token file is missing, THE Authentication_Manager SHALL return an error instructing the user to run the login script
3. WHEN the token file exists but is from a previous day, THE Authentication_Manager SHALL return an error instructing the user to re-authenticate
4. THE Authentication_Manager SHALL validate that the access token is valid before allowing trading operations
5. THE Authentication_Manager SHALL store the token date and time for validation purposes

### Requirement 4: Market Data Fetching

**User Story:** As a trader, I want to fetch historical and real-time market data from Indian brokers, so that my indicators can generate accurate signals.

#### Acceptance Criteria

1. THE Market_Data_Provider SHALL fetch historical OHLCV data for specified instruments and timeframes
2. WHEN historical data is requested, THE Market_Data_Provider SHALL return data in a pandas DataFrame format compatible with existing indicator calculations
3. THE Market_Data_Provider SHALL support timeframes of 1 minute, 5 minutes, 15 minutes, 30 minutes, 60 minutes, and daily
4. WHEN data fetching fails, THE Market_Data_Provider SHALL retry up to 3 times with exponential backoff
5. THE Market_Data_Provider SHALL fetch sufficient historical bars (minimum 200) for indicator calculations
6. WHEN real-time data is needed, THE Market_Data_Provider SHALL support WebSocket connections for live price updates
7. THE Market_Data_Provider SHALL convert broker-specific data formats to the standard format used by the bot

### Requirement 5: Order Placement and Management

**User Story:** As a trader, I want to place and manage orders through Indian brokers, so that my trading signals are executed automatically.

#### Acceptance Criteria

1. THE Order_Manager SHALL place market orders with specified quantity and direction (buy/sell)
2. THE Order_Manager SHALL place limit orders with specified price, quantity, and direction
3. THE Order_Manager SHALL place stop-loss orders with trigger price, quantity, and direction
4. THE Order_Manager SHALL place bracket orders with entry, stop-loss, and take-profit levels
5. WHEN an order is placed, THE Order_Manager SHALL return the order ID for tracking
6. THE Order_Manager SHALL modify existing orders to update price, quantity, or order type
7. THE Order_Manager SHALL cancel pending orders by order ID
8. WHEN order placement fails, THE Order_Manager SHALL return a descriptive error message
9. THE Order_Manager SHALL validate order parameters (quantity, price, instrument) before submission

### Requirement 6: Position Tracking

**User Story:** As a trader, I want to track my open positions and their P&L, so that I can manage risk and trailing stops.

#### Acceptance Criteria

1. THE Position_Tracker SHALL retrieve all open positions for the trading account
2. WHEN positions are retrieved, THE Position_Tracker SHALL return entry price, current price, quantity, direction, and unrealized P&L
3. THE Position_Tracker SHALL filter positions by instrument symbol
4. THE Position_Tracker SHALL calculate position P&L in both absolute currency and percentage terms
5. THE Position_Tracker SHALL identify positions opened by the bot using a unique identifier (magic number equivalent)

### Requirement 7: Indian Market Specifics

**User Story:** As a trader, I want the bot to respect Indian market trading hours and instrument formats, so that it operates correctly in the Indian market context.

#### Acceptance Criteria

1. THE Trading_Bot SHALL only generate signals and place orders during NSE trading hours (9:15 AM - 3:30 PM IST)
2. WHEN outside trading hours, THE Trading_Bot SHALL enter a waiting state and log the next market open time
3. THE Trading_Bot SHALL support Indian instrument naming conventions (e.g., "RELIANCE", "NIFTY 50", "BANKNIFTY")
4. THE Trading_Bot SHALL support multiple market segments: equity (NSE/BSE), futures, options, and currency
5. THE Trading_Bot SHALL handle Indian market holidays by checking market status before trading
6. THE Trading_Bot SHALL convert timeframes from MT5 format (TIMEFRAME_M30) to broker-specific format ("30minute")

### Requirement 8: Instrument Configuration

**User Story:** As a trader, I want to configure which Indian instruments to trade, so that I can adapt my strategy to different markets.

#### Acceptance Criteria

1. THE Configuration_Manager SHALL allow specification of instrument symbols in the configuration file
2. THE Configuration_Manager SHALL support instrument lists for different market segments (equity, futures, options)
3. WHEN an instrument is configured, THE Configuration_Manager SHALL validate that it exists and is tradable
4. THE Configuration_Manager SHALL map instrument symbols to broker-specific identifiers (instrument tokens)
5. THE Configuration_Manager SHALL support instrument-specific parameters (lot size, tick size, margin requirements)

### Requirement 9: Risk Management Adaptation

**User Story:** As a trader, I want risk management to work with Indian market margin requirements, so that position sizing is appropriate for my capital.

#### Acceptance Criteria

1. THE Risk_Manager SHALL calculate position sizes based on available margin from the broker
2. THE Risk_Manager SHALL respect instrument-specific lot sizes (e.g., NIFTY futures = 50 units per lot)
3. WHEN calculating stop-loss distances, THE Risk_Manager SHALL use instrument-specific tick sizes
4. THE Risk_Manager SHALL prevent position sizes that exceed available margin
5. THE Risk_Manager SHALL calculate risk as a percentage of account equity, not just balance

### Requirement 10: Existing Bot Logic Preservation

**User Story:** As a trader, I want all my existing indicators, signals, and risk management logic to work unchanged, so that I don't lose my proven strategy.

#### Acceptance Criteria

1. THE Signal_Generator SHALL continue to use existing indicator calculations (RSI, MACD, EMA, ATR, ADX)
2. THE Signal_Generator SHALL continue to use existing signal detection logic (MA crossovers, momentum, pullback)
3. THE Risk_Manager SHALL continue to use existing risk management rules (position sizing, stop-loss, take-profit)
4. THE Trading_Bot SHALL continue to support existing features (trailing stops, split orders, adaptive risk, ML integration)
5. WHEN migrating to Indian brokers, THE system SHALL require changes only to broker-specific components (connection, data, orders)

### Requirement 11: Configuration Migration

**User Story:** As a trader, I want to easily migrate my MT5 configuration to Indian broker configuration, so that I can start trading quickly.

#### Acceptance Criteria

1. THE Configuration_Manager SHALL support a configuration format compatible with existing MT5 bot configuration
2. THE Configuration_Manager SHALL provide default configurations for popular Indian instruments (NIFTY, BANKNIFTY, RELIANCE)
3. WHEN migrating configuration, THE Configuration_Manager SHALL map MT5 symbols to Indian equivalents
4. THE Configuration_Manager SHALL map MT5 timeframes to broker-specific timeframe formats
5. THE Configuration_Manager SHALL preserve all indicator parameters, risk parameters, and trading rules

### Requirement 12: Error Handling and Logging

**User Story:** As a trader, I want comprehensive error handling and logging, so that I can diagnose issues and monitor bot performance.

#### Acceptance Criteria

1. WHEN a broker API error occurs, THE system SHALL log the error code, message, and context
2. WHEN authentication fails, THE system SHALL log clear instructions for re-authentication
3. WHEN rate limits are hit, THE system SHALL log the retry attempt and wait time
4. WHEN orders fail, THE system SHALL log the order parameters and failure reason
5. THE system SHALL log all trading decisions (signals, entries, exits) with timestamps and reasoning
6. THE system SHALL maintain separate log levels (DEBUG, INFO, WARNING, ERROR) for different verbosity needs

### Requirement 13: Extensibility for Other Brokers

**User Story:** As a trader, I want the architecture to support adding other Indian brokers (Alice Blue, Angel One, Upstox), so that I have flexibility in the future.

#### Acceptance Criteria

1. THE Broker_Adapter interface SHALL be generic enough to support different broker API designs
2. WHERE a new broker is added, THE system SHALL require only implementing the Broker_Adapter interface
3. THE system SHALL support broker-specific configuration sections in the configuration file
4. THE system SHALL allow runtime selection of broker through configuration
5. THE system SHALL document the steps required to add a new broker adapter

### Requirement 14: Data Format Compatibility

**User Story:** As a trader, I want market data from Indian brokers to be compatible with my existing indicator calculations, so that I don't need to rewrite my analysis code.

#### Acceptance Criteria

1. THE Market_Data_Provider SHALL return historical data with columns: time, open, high, low, close, volume
2. THE Market_Data_Provider SHALL ensure time column is in pandas datetime format
3. THE Market_Data_Provider SHALL ensure price columns are in float format
4. THE Market_Data_Provider SHALL ensure volume column is in integer format
5. THE Market_Data_Provider SHALL handle missing data by forward-filling or raising an error

### Requirement 15: Testing and Validation

**User Story:** As a trader, I want to test the bot with Indian brokers before going live, so that I can verify it works correctly.

#### Acceptance Criteria

1. THE system SHALL support a paper trading mode that simulates orders without placing real trades
2. WHEN in paper trading mode, THE system SHALL log all simulated orders and their outcomes
3. THE system SHALL provide a validation script that checks broker connectivity, data fetching, and order placement
4. THE system SHALL provide example configurations for testing with small position sizes
5. THE system SHALL document the testing process and recommended validation steps

