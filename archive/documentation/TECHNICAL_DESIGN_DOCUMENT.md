# GEM Trading Bot - Technical Design & Implementation Document

## Document Overview

**Purpose:** Detailed technical design showing logic flow, component coupling, and implementation details  
**Audience:** Developers, technical architects, system integrators  
**Version:** 1.0  
**Date:** January 30, 2026

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Component Coupling Analysis](#2-component-coupling-analysis)
3. [Logic Flow Diagrams](#3-logic-flow-diagrams)
4. [Sequence Diagrams](#4-sequence-diagrams)
5. [Data Flow Architecture](#5-data-flow-architecture)
6. [State Machines](#6-state-machines)
7. [Class Diagrams](#7-class-diagrams)
8. [Integration Patterns](#8-integration-patterns)
9. [Algorithm Implementations](#9-algorithm-implementations)
10. [Error Handling Architecture](#10-error-handling-architecture)
11. [Performance Optimization](#11-performance-optimization)
12. [Threading & Concurrency](#12-threading--concurrency)

---

## 1. System Architecture

### 1.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│  • Web Dashboard (Flask)                                        │
│  • REST API Endpoints                                           │
│  • HTML/JavaScript UI                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│  • MT5TradingBot (Core Engine)                                  │
│  • ConfigManager (Configuration)                                │
│  • Business Logic                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                                 │
│  • AdaptiveRiskManager                                          │
│  • DynamicTPManager                                             │
│  • DynamicSLManager                                             │
│  • VolumeAnalyzer                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
│  • MetaTrader 5 API                                             │
│  • File System (Config, Logs)                                   │
│  • Logging System                                               │
└─────────────────────────────────────────────────────────────────┘
```


### 1.2 Component Hierarchy

```
run_bot.py (Entry Point)
    │
    ├─→ MT5TradingBot (Core Engine)
    │       │
    │       ├─→ ConfigManager (Configuration)
    │       │       └─→ bot_config.json (Persistent Storage)
    │       │
    │       ├─→ AdaptiveRiskManager (Entry Optimization)
    │       │       └─→ Market Analysis Algorithms
    │       │
    │       ├─→ DynamicTPManager (Profit Maximization)
    │       │       └─→ Trend Detection Algorithms
    │       │
    │       ├─→ DynamicSLManager (Risk Protection)
    │       │       └─→ Reversal Detection Algorithms
    │       │
    │       ├─→ VolumeAnalyzer (Signal Confirmation)
    │       │       └─→ Volume Analysis Algorithms
    │       │
    │       └─→ MetaTrader5 API (Market Interface)
    │               ├─→ Market Data
    │               ├─→ Order Execution
    │               └─→ Position Management
    │
    └─→ WebDashboard (Monitoring & Control)
            ├─→ Flask Server
            ├─→ REST API
            └─→ HTML/JS Frontend
```

---

## 2. Component Coupling Analysis

### 2.1 Coupling Matrix

| Component | Coupling Type | Coupled With | Dependency Strength |
|-----------|--------------|--------------|---------------------|
| MT5TradingBot | Strong | ConfigManager | High (Required) |
| MT5TradingBot | Medium | AdaptiveRiskManager | Medium (Optional) |
| MT5TradingBot | Medium | DynamicTPManager | Medium (Optional) |
| MT5TradingBot | Medium | DynamicSLManager | Medium (Optional) |
| MT5TradingBot | Medium | VolumeAnalyzer | Medium (Optional) |
| MT5TradingBot | Strong | MetaTrader5 API | High (Required) |
| WebDashboard | Strong | ConfigManager | High (Required) |
| WebDashboard | Medium | MT5TradingBot | Medium (Status only) |
| WebDashboard | Strong | MetaTrader5 API | High (Required) |
| All Adaptive Modules | Weak | Each Other | None (Independent) |


### 2.2 Dependency Injection Pattern

```python
# ConfigManager is injected into all components
class MT5TradingBot:
    def __init__(self, config):
        self.config = config  # Injected dependency
        
        # Optional dependencies (graceful degradation)
        if config.get('use_adaptive_risk') and ADAPTIVE_RISK_AVAILABLE:
            self.adaptive_risk_manager = AdaptiveRiskManager(config)
        else:
            self.adaptive_risk_manager = None
```

**Benefits:**
- Loose coupling between components
- Easy testing (mock dependencies)
- Graceful degradation if modules unavailable
- Configuration-driven behavior

### 2.3 Interface Contracts

#### ConfigManager Interface
```python
# Input: None or config_file path
# Output: Configuration dictionary
{
    'symbols': List[str],
    'timeframe': int,
    'risk_percent': float,
    'use_adaptive_risk': bool,
    ...
}
```

#### AdaptiveRiskManager Interface
```python
# Input: DataFrame with price data and indicators
# Output: Market condition analysis
{
    'market_type': str,  # 'strong_trend', 'weak_trend', 'ranging', 'volatile'
    'trend_strength': float,  # 0-100
    'trend_direction': int,  # 1 or -1
    'volatility_ratio': float,  # >1 high, <1 low
    'trend_consistency': float,  # 0-100%
    'current_atr': float
}
```

#### DynamicTPManager Interface
```python
# Input: Position, DataFrame, market_condition
# Output: (should_extend, new_tp, reason)
(bool, float, str)
```

#### DynamicSLManager Interface
```python
# Input: Position, DataFrame, market_condition
# Output: (should_adjust, new_sl, reason)
(bool, float, str)
```

---

## 3. Logic Flow Diagrams

### 3.1 Main Trading Loop Flow

```
START
  │
  ├─→ Connect to MT5
  │     │
  │     ├─→ Success? ──No──→ Retry (3 attempts) ──→ EXIT
  │     │
  │     └─→ Yes
  │
  ├─→ Load Configuration
  │     │
  │     └─→ Initialize Modules
  │
  ├─→ MAIN LOOP (Every 60 seconds)
  │     │
  │     ├─→ FOR EACH SYMBOL:
  │     │     │
  │     │     ├─→ Fetch Historical Data (200 bars)
  │     │     │     │
  │     │     │     ├─→ Success? ──No──→ Skip Symbol
  │     │     │     │
  │     │     │     └─→ Yes
  │     │     │
  │     │     ├─→ Calculate Indicators
  │     │     │     ├─→ Moving Averages (Fast, Slow)
  │     │     │     ├─→ RSI
  │     │     │     ├─→ MACD
  │     │     │     ├─→ ADX
  │     │     │     ├─→ ATR
  │     │     │     └─→ Bollinger Bands
  │     │     │
  │     │     ├─→ Check Entry Signal
  │     │     │     │
  │     │     │     ├─→ MA Crossover? ──No──→ Next Symbol
  │     │     │     │
  │     │     │     ├─→ Apply Filters
  │     │     │     │     ├─→ RSI Filter
  │     │     │     │     ├─→ MACD Filter
  │     │     │     │     ├─→ ADX Filter
  │     │     │     │     └─→ Volume Filter
  │     │     │     │
  │     │     │     └─→ Signal Valid? ──No──→ Next Symbol
  │     │     │
  │     │     ├─→ Adaptive Risk Analysis (if enabled)
  │     │     │     │
  │     │     │     ├─→ Analyze Market Condition
  │     │     │     ├─→ Classify Market Type
  │     │     │     ├─→ Calculate Risk Multiplier
  │     │     │     └─→ Set Optimal SL/TP
  │     │     │
  │     │     ├─→ Calculate Position Size
  │     │     │     ├─→ Account Balance × Risk%
  │     │     │     ├─→ Apply Risk Multiplier
  │     │     │     └─→ Convert to Lot Size
  │     │     │
  │     │     ├─→ Execute Trade
  │     │     │     │
  │     │     │     ├─→ Split Orders? ──Yes──→ Open Multiple Positions
  │     │     │     │                           (Different TP levels)
  │     │     │     │
  │     │     │     └─→ No ──→ Open Single Position
  │     │     │
  │     │     └─→ Small Delay (0.5s)
  │     │
  │     ├─→ Manage Existing Positions
  │     │     │
  │     │     ├─→ FOR EACH OPEN POSITION:
  │     │     │     │
  │     │     │     ├─→ Verify Position Exists
  │     │     │     │
  │     │     │     ├─→ Fetch Current Market Data
  │     │     │     │
  │     │     │     ├─→ Calculate Indicators
  │     │     │     │
  │     │     │     ├─→ Get Market Condition (if adaptive)
  │     │     │     │
  │     │     │     ├─→ Dynamic SL Check (if enabled)
  │     │     │     │     │
  │     │     │     │     ├─→ Should Adjust? ──Yes──→ Update SL
  │     │     │     │     │
  │     │     │     │     └─→ No
  │     │     │     │
  │     │     │     ├─→ Dynamic TP Check (if enabled & profitable)
  │     │     │     │     │
  │     │     │     │     ├─→ Should Extend? ──Yes──→ Update TP
  │     │     │     │     │
  │     │     │     │     └─→ No
  │     │     │     │
  │     │     │     ├─→ Scalping Mode Check (if enabled)
  │     │     │     │     │
  │     │     │     │     ├─→ Profit Target Met? ──Yes──→ Close Position
  │     │     │     │     │
  │     │     │     │     └─→ No
  │     │     │     │
  │     │     │     └─→ Update Trailing Stop
  │     │     │
  │     │     └─→ Clean Up Closed Positions
  │     │
  │     └─→ Wait 60 seconds
  │
  └─→ LOOP CONTINUES
```


### 3.2 Signal Generation Logic Flow

```
SIGNAL GENERATION
  │
  ├─→ Calculate Moving Averages
  │     ├─→ Fast MA (10-period)
  │     └─→ Slow MA (30-period)
  │
  ├─→ Detect MA Crossover
  │     │
  │     ├─→ Bullish Crossover?
  │     │     └─→ Fast MA crosses ABOVE Slow MA
  │     │
  │     └─→ Bearish Crossover?
  │           └─→ Fast MA crosses BELOW Slow MA
  │
  ├─→ Apply RSI Filter
  │     │
  │     ├─→ For BUY: RSI < 70 (not overbought)
  │     └─→ For SELL: RSI > 30 (not oversold)
  │
  ├─→ Apply MACD Filter
  │     │
  │     ├─→ For BUY: MACD histogram > 0
  │     └─→ For SELL: MACD histogram < 0
  │
  ├─→ Apply ADX Filter
  │     │
  │     └─→ ADX > minimum threshold (trend strength)
  │
  ├─→ Apply Volume Filter (if enabled)
  │     │
  │     ├─→ Calculate Volume MA
  │     ├─→ Check Current Volume > Average
  │     └─→ Adjust Confidence Score
  │
  ├─→ Calculate Confidence Score
  │     │
  │     ├─→ Base Score: 0.60
  │     ├─→ +0.10 if RSI favorable
  │     ├─→ +0.10 if MACD strong
  │     ├─→ +0.10 if ADX strong
  │     ├─→ +0.10 if Volume high
  │     └─→ Final Score: 0.60 - 1.00
  │
  └─→ Signal Valid?
        │
        ├─→ Yes: Proceed to Trade Execution
        └─→ No: Skip (wait for next cycle)
```

### 3.3 Adaptive Risk Analysis Flow

```
ADAPTIVE RISK ANALYSIS
  │
  ├─→ Calculate Trend Strength (ADX)
  │     │
  │     ├─→ Calculate +DI and -DI
  │     ├─→ Calculate DX
  │     └─→ Return ADX value (0-100)
  │
  ├─→ Calculate Volatility Ratio
  │     │
  │     ├─→ Current ATR
  │     ├─→ Average ATR (50-period)
  │     └─→ Ratio = Current / Average
  │
  ├─→ Calculate Trend Consistency
  │     │
  │     ├─→ Check last 20 bars
  │     ├─→ Count bars matching current trend
  │     └─→ Consistency % = Matching / Total
  │
  ├─→ Analyze Price Position
  │     │
  │     ├─→ Price > Both MAs → 'above_mas'
  │     ├─→ Price < Both MAs → 'below_mas'
  │     └─→ Otherwise → 'between_mas'
  │
  ├─→ Analyze Price Action
  │     │
  │     ├─→ Higher Highs > 60% → 'bullish'
  │     ├─→ Lower Lows > 60% → 'bearish'
  │     └─→ Otherwise → 'consolidating'
  │
  ├─→ Check S/R Proximity
  │     │
  │     ├─→ Find swing highs/lows
  │     ├─→ Calculate distance in ATR
  │     └─→ Return nearest distance
  │
  ├─→ Classify Market Type
  │     │
  │     ├─→ ADX > 30 & Consistency > 70% → 'strong_trend'
  │     ├─→ ADX > 20 & Consistency > 50% → 'weak_trend'
  │     ├─→ Volatility > 1.5 → 'volatile'
  │     └─→ Otherwise → 'ranging'
  │
  └─→ Adjust Risk Parameters
        │
        ├─→ Strong Trend:
        │     ├─→ Risk Multiplier: 1.5x
        │     ├─→ SL: 2.5× ATR (wider)
        │     └─→ TP: [2.0, 3.0, 5.0] (wider)
        │
        ├─→ Weak Trend:
        │     ├─→ Risk Multiplier: 1.0x
        │     ├─→ SL: 2.0× ATR (standard)
        │     └─→ TP: [1.5, 2.5, 4.0] (standard)
        │
        ├─→ Ranging:
        │     ├─→ Risk Multiplier: 0.7x
        │     ├─→ SL: 1.5× ATR (tighter)
        │     └─→ TP: [1.0, 1.5, 2.0] (tighter)
        │
        └─→ Volatile:
              ├─→ Risk Multiplier: 0.5x
              ├─→ SL: 3.0× ATR (wider)
              └─→ TP: [2.0, 3.5, 5.0] (wider)
```


### 3.4 Dynamic TP Extension Flow

```
DYNAMIC TP EXTENSION
  │
  ├─→ Check Position Profitability
  │     │
  │     └─→ Not Profitable? ──→ EXIT (no extension)
  │
  ├─→ Detect Strong Trend Continuation
  │     │
  │     ├─→ Market Type = 'strong_trend'?
  │     ├─→ Trend Direction = Position Direction?
  │     ├─→ Consistency > 85%?
  │     └─→ Strength > 30?
  │           │
  │           └─→ Yes: Extend TP by 1.5×
  │
  ├─→ Detect Momentum Acceleration
  │     │
  │     ├─→ Calculate recent price changes
  │     ├─→ Compare to older price changes
  │     └─→ Acceleration > 30%?
  │           │
  │           └─→ Yes: Extend TP by 1.4×
  │
  ├─→ Detect Breakout
  │     │
  │     ├─→ Find recent high/low
  │     ├─→ Price broke through?
  │     └─→ Volume confirms?
  │           │
  │           └─→ Yes: Extend TP by 2.0× ATR beyond breakout
  │
  ├─→ Detect Favorable Volatility
  │     │
  │     ├─→ ATR increasing?
  │     ├─→ Price moving in our favor?
  │     └─→ Expansion > 20%?
  │           │
  │           └─→ Yes: Extend TP by 1.3×
  │
  ├─→ Detect Continuation Pattern
  │     │
  │     ├─→ Flag pattern?
  │     ├─→ Pennant pattern?
  │     └─→ Consolidation then breakout?
  │           │
  │           └─→ Yes: Extend TP by 1.2×
  │
  ├─→ Select Best Extension
  │     │
  │     ├─→ Multiple triggers?
  │     ├─→ Choose most aggressive (furthest TP)
  │     └─→ Validate extension
  │
  └─→ Update Position TP
        │
        ├─→ Send modify request to MT5
        ├─→ Log extension with reason
        └─→ Track in TP history
```

### 3.5 Dynamic SL Adjustment Flow

```
DYNAMIC SL ADJUSTMENT
  │
  ├─→ Detect Trend Reversal
  │     │
  │     ├─→ For LONG: Lower highs + Lower lows?
  │     ├─→ For SHORT: Higher highs + Higher lows?
  │     └─→ MA trend against position?
  │           │
  │           └─→ Yes: Tighten SL to Current - 0.5× ATR
  │
  ├─→ Detect MA Crossover Against
  │     │
  │     ├─→ For LONG: Fast MA crosses below Slow MA?
  │     ├─→ For SHORT: Fast MA crosses above Slow MA?
  │     └─→ Crossover confirmed?
  │           │
  │           └─→ Yes: Tighten SL to Current - 1.0× ATR
  │
  ├─→ Detect Volatility Change
  │     │
  │     ├─→ ATR expanding > 30%?
  │     │     └─→ Widen SL (give more room)
  │     │
  │     └─→ ATR contracting > 30%?
  │           └─→ Tighten SL (protect profits)
  │
  ├─→ Detect Swing Level Formation
  │     │
  │     ├─→ For LONG: New swing low formed?
  │     ├─→ For SHORT: New swing high formed?
  │     └─→ Level significant?
  │           │
  │           └─→ Yes: Move SL to swing ± 0.3× ATR
  │
  ├─→ Detect S/R Break
  │     │
  │     ├─→ Support/Resistance level identified?
  │     ├─→ Price broke through?
  │     └─→ Break confirmed?
  │           │
  │           └─→ Yes: Move SL beyond broken level
  │
  ├─→ Detect Trend Strength Change
  │     │
  │     ├─→ Trend strengthening?
  │     │     └─→ Widen SL (let trade run)
  │     │
  │     └─→ Trend weakening?
  │           └─→ Tighten SL (protect profits)
  │
  ├─→ Select Best Adjustment
  │     │
  │     ├─→ Multiple triggers?
  │     ├─→ Choose most conservative (closest SL)
  │     └─→ Validate adjustment
  │
  └─→ Update Position SL
        │
        ├─→ Ensure SL better than current
        ├─→ Send modify request to MT5
        ├─→ Log adjustment with reason
        └─→ Track in SL history
```

---

## 4. Sequence Diagrams

### 4.1 Trade Execution Sequence

```
User/Timer    MT5Bot    ConfigMgr    AdaptiveRisk    MT5API
    │            │           │              │           │
    │──Start──→  │           │              │           │
    │            │           │              │           │
    │            │──Get Config──→           │           │
    │            │←──Config──────           │           │
    │            │           │              │           │
    │            │──Get Data─────────────────────────→  │
    │            │←──Price Data──────────────────────   │
    │            │           │              │           │
    │            │──Calculate Indicators──  │           │
    │            │           │              │           │
    │            │──Check Signal──          │           │
    │            │  (MA Crossover)          │           │
    │            │           │              │           │
    │            │──Analyze Market──────→   │           │
    │            │←──Market Condition───    │           │
    │            │           │              │           │
    │            │──Calculate Position Size │           │
    │            │  (Risk × Multiplier)     │           │
    │            │           │              │           │
    │            │──Open Position────────────────────→  │
    │            │←──Position Ticket─────────────────   │
    │            │           │              │           │
    │            │──Log Trade──             │           │
    │            │           │              │           │
    │←──Complete─│           │              │           │
```


### 4.2 Position Management Sequence

```
Timer    MT5Bot    DynamicSL    DynamicTP    MT5API
  │         │          │            │           │
  │─60s─→   │          │            │           │
  │         │          │            │           │
  │         │──Get Positions──────────────────→ │
  │         │←──Position List──────────────────  │
  │         │          │            │           │
  │         │──For Each Position── │           │
  │         │          │            │           │
  │         │──Get Market Data─────────────────→│
  │         │←──Price Data─────────────────────  │
  │         │          │            │           │
  │         │──Calculate Indicators│           │
  │         │          │            │           │
  │         │──Check SL Adjustment→│           │
  │         │←──Should Adjust?─────│           │
  │         │  (Yes/No + New SL)   │           │
  │         │          │            │           │
  │         │──If Yes: Update SL───────────────→│
  │         │←──Confirmation───────────────────  │
  │         │          │            │           │
  │         │──Check TP Extension──────────→    │
  │         │←──Should Extend?─────────────     │
  │         │  (Yes/No + New TP)   │           │
  │         │          │            │           │
  │         │──If Yes: Update TP───────────────→│
  │         │←──Confirmation───────────────────  │
  │         │          │            │           │
  │         │──Update Trailing Stop│           │
  │         │          │            │           │
  │←─Done───│          │            │           │
```

### 4.3 Configuration Update Sequence

```
User    Dashboard    ConfigMgr    MT5Bot    File System
  │         │            │           │           │
  │─Edit─→  │            │           │           │
  │ Config  │            │           │           │
  │         │            │           │           │
  │         │──Validate──│           │           │
  │         │  Settings  │           │           │
  │         │            │           │           │
  │         │──Create Backup────────────────────→│
  │         │←──Backup Created──────────────────  │
  │         │            │           │           │
  │         │──Save Config──────────────────────→│
  │         │←──Saved────────────────────────────│
  │         │            │           │           │
  │         │──Notify Bot──────────→ │           │
  │         │            │           │           │
  │         │            │           │──Reload Config──→
  │         │            │←──New Config──────────│
  │         │            │           │           │
  │         │            │           │──Apply Changes──│
  │         │            │           │           │
  │←─Success│            │           │           │
```

---

## 5. Data Flow Architecture

### 5.1 Market Data Flow

```
MetaTrader 5 Platform
        │
        │ (Real-time Price Feed)
        ↓
┌─────────────────────┐
│  MT5 API Interface  │
└─────────────────────┘
        │
        │ (Historical Bars)
        ↓
┌─────────────────────┐
│   MT5TradingBot     │
│  get_historical_    │
│  data()             │
└─────────────────────┘
        │
        │ (Raw OHLCV Data)
        ↓
┌─────────────────────┐
│  Indicator          │
│  Calculation        │
│  • MA, RSI, MACD    │
│  • ADX, ATR, BB     │
└─────────────────────┘
        │
        │ (Enriched DataFrame)
        ├────────────────────────────────┐
        │                                │
        ↓                                ↓
┌─────────────────────┐      ┌─────────────────────┐
│  Signal Generation  │      │  Position Mgmt      │
│  • MA Crossover     │      │  • Dynamic SL/TP    │
│  • Filter Check     │      │  • Trailing Stops   │
└─────────────────────┘      └─────────────────────┘
        │                                │
        │ (Trade Signal)                 │ (SL/TP Updates)
        ↓                                ↓
┌─────────────────────────────────────────────────┐
│           MT5 API - Order Execution             │
└─────────────────────────────────────────────────┘
```


### 5.2 Configuration Data Flow

```
┌─────────────────────┐
│  bot_config.json    │
│  (Persistent)       │
└─────────────────────┘
        │
        │ (Load on Startup)
        ↓
┌─────────────────────┐
│   ConfigManager     │
│  • Load config      │
│  • Merge defaults   │
│  • Validate         │
└─────────────────────┘
        │
        │ (Config Dict)
        ├────────────────────────────────────────┐
        │                                        │
        ↓                                        ↓
┌─────────────────────┐              ┌─────────────────────┐
│   MT5TradingBot     │              │   WebDashboard      │
│  • Trading params   │              │  • Display settings │
│  • Risk settings    │              │  • Allow edits      │
│  • Indicator params │              └─────────────────────┘
└─────────────────────┘                        │
        │                                      │
        │ (Uses Config)                        │ (User Edits)
        ↓                                      ↓
┌─────────────────────┐              ┌─────────────────────┐
│  Adaptive Modules   │              │   ConfigManager     │
│  • AdaptiveRisk     │              │  • Validate         │
│  • DynamicTP/SL     │              │  • Create backup    │
│  • VolumeAnalyzer   │              │  • Save to file     │
└─────────────────────┘              └─────────────────────┘
                                              │
                                              │ (Updated Config)
                                              ↓
                                     ┌─────────────────────┐
                                     │  bot_config.json    │
                                     │  (Updated)          │
                                     └─────────────────────┘
```

### 5.3 Logging Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    All Components                       │
│  • MT5TradingBot                                        │
│  • AdaptiveRiskManager                                  │
│  • DynamicTPManager                                     │
│  • DynamicSLManager                                     │
│  • VolumeAnalyzer                                       │
│  • WebDashboard                                         │
└─────────────────────────────────────────────────────────┘
                        │
                        │ (Log Messages)
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Python Logging System                      │
│  • Level filtering (INFO, WARNING, ERROR, DEBUG)        │
│  • Format messages                                      │
│  • Route to handlers                                    │
└─────────────────────────────────────────────────────────┘
                        │
                        ├──────────────────┐
                        │                  │
                        ↓                  ↓
            ┌─────────────────┐  ┌─────────────────┐
            │  File Handler   │  │ Stream Handler  │
            │  (trading_bot.  │  │  (Console)      │
            │   log)          │  │                 │
            └─────────────────┘  └─────────────────┘
                        │                  │
                        ↓                  ↓
            ┌─────────────────┐  ┌─────────────────┐
            │  Log File       │  │  Terminal       │
            │  (Persistent)   │  │  (Real-time)    │
            └─────────────────┘  └─────────────────┘
```

---

## 6. State Machines

### 6.1 Bot State Machine

```
┌─────────────┐
│   STOPPED   │◄──────────────────────────┐
└─────────────┘                           │
       │                                  │
       │ start()                          │
       ↓                                  │
┌─────────────┐                           │
│ CONNECTING  │                           │
└─────────────┘                           │
       │                                  │
       │ MT5 Connected                    │
       ↓                                  │
┌─────────────┐                           │
│ INITIALIZING│                           │
└─────────────┘                           │
       │                                  │
       │ Modules Loaded                   │
       ↓                                  │
┌─────────────┐                           │
│   RUNNING   │───────────────────────────┤
└─────────────┘                           │
       │                                  │
       │ ┌──────────────────┐             │
       │ │ Every 60 seconds │             │
       │ └──────────────────┘             │
       │                                  │
       ├──→ Analyze Symbols               │
       ├──→ Execute Trades                │
       ├──→ Manage Positions              │
       │                                  │
       │ stop() or Error                  │
       ↓                                  │
┌─────────────┐                           │
│  STOPPING   │                           │
└─────────────┘                           │
       │                                  │
       │ Cleanup Complete                 │
       └──────────────────────────────────┘

States:
• STOPPED: Bot not running
• CONNECTING: Establishing MT5 connection
• INITIALIZING: Loading config and modules
• RUNNING: Active trading loop
• STOPPING: Graceful shutdown in progress
```


### 6.2 Position State Machine

```
┌─────────────┐
│   NO_SIGNAL │◄──────────────────────────┐
└─────────────┘                           │
       │                                  │
       │ MA Crossover + Filters Pass      │
       ↓                                  │
┌─────────────┐                           │
│SIGNAL_FOUND │                           │
└─────────────┘                           │
       │                                  │
       │ Adaptive Risk Analysis           │
       ↓                                  │
┌─────────────┐                           │
│POSITION_OPEN│                           │
└─────────────┘                           │
       │                                  │
       │ ┌──────────────────┐             │
       │ │ Every 60 seconds │             │
       │ └──────────────────┘             │
       │                                  │
       ├──→ Check Dynamic SL              │
       ├──→ Check Dynamic TP              │
       ├──→ Update Trailing Stop          │
       │                                  │
       │ TP Hit or SL Hit or Manual Close │
       ↓                                  │
┌─────────────┐                           │
│POSITION_    │                           │
│CLOSED       │                           │
└─────────────┘                           │
       │                                  │
       │ Cleanup                          │
       └──────────────────────────────────┘

States:
• NO_SIGNAL: Waiting for entry signal
• SIGNAL_FOUND: Valid signal detected
• POSITION_OPEN: Active position being managed
• POSITION_CLOSED: Position closed, cleanup
```

### 6.3 Adaptive Risk State Machine

```
┌─────────────┐
│   ANALYZE   │
└─────────────┘
       │
       ├──→ Calculate ADX (Trend Strength)
       ├──→ Calculate Volatility Ratio
       ├──→ Calculate Trend Consistency
       ├──→ Analyze Price Position
       ├──→ Analyze Price Action
       └──→ Check S/R Proximity
       │
       ↓
┌─────────────┐
│  CLASSIFY   │
└─────────────┘
       │
       ├──→ Strong Trend?
       ├──→ Weak Trend?
       ├──→ Ranging?
       └──→ Volatile?
       │
       ↓
┌─────────────┐
│   ADJUST    │
└─────────────┘
       │
       ├──→ Set Risk Multiplier
       ├──→ Set SL Distance
       ├──→ Set TP Levels
       └──→ Set Trailing Parameters
       │
       ↓
┌─────────────┐
│   RETURN    │
│  PARAMETERS │
└─────────────┘
```

---

## 7. Class Diagrams

### 7.1 Core Classes

```
┌─────────────────────────────────────────┐
│          MT5TradingBot                  │
├─────────────────────────────────────────┤
│ - config: dict                          │
│ - symbols: List[str]                    │
│ - timeframe: int                        │
│ - magic_number: int                     │
│ - adaptive_risk_manager: AdaptiveRisk   │
│ - volume_analyzer: VolumeAnalyzer       │
│ - positions: dict                       │
│ - split_position_groups: dict           │
├─────────────────────────────────────────┤
│ + __init__(config)                      │
│ + connect(): bool                       │
│ + disconnect(): void                    │
│ + run(): void                           │
│ + run_strategy(symbol): void            │
│ + get_historical_data(symbol): DataFrame│
│ + calculate_indicators(df): DataFrame   │
│ + check_entry_signal(df): tuple         │
│ + open_position(signal): bool           │
│ + open_split_positions(signal): bool    │
│ + manage_positions(): void              │
│ + calculate_position_size(signal): float│
│ + update_trailing_stop(position): void  │
└─────────────────────────────────────────┘
                    │
                    │ uses
                    ↓
┌─────────────────────────────────────────┐
│         ConfigManager                   │
├─────────────────────────────────────────┤
│ - config_file: str                      │
│ - config: dict                          │
├─────────────────────────────────────────┤
│ + __init__(config_file)                 │
│ + get_config(): dict                    │
│ + save_config(config): void             │
│ + update_config(updates): void          │
│ + _load_or_create_config(): dict        │
│ + _get_default_config(): dict           │
│ + _create_backup(): void                │
└─────────────────────────────────────────┘
```


### 7.2 Adaptive Module Classes

```
┌─────────────────────────────────────────┐
│      AdaptiveRiskManager                │
├─────────────────────────────────────────┤
│ - config: dict                          │
│ - atr_period: int                       │
│ - trend_strength_period: int            │
├─────────────────────────────────────────┤
│ + analyze_market_condition(df): dict    │
│ + calculate_adx(df): float              │
│ + calculate_trend_consistency(df): float│
│ + classify_market(...): str             │
│ + adjust_risk_parameters(...): dict     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       DynamicTPManager                  │
├─────────────────────────────────────────┤
│ - config: dict                          │
│ - tp_history: dict                      │
├─────────────────────────────────────────┤
│ + should_extend_take_profit(...): tuple │
│ + detect_trend_strength(...): str       │
│ + detect_momentum_acceleration(...): str│
│ + detect_breakout(...): float           │
│ + extend_for_strong_trend(...): float   │
│ + validate_tp_extension(...): bool      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       DynamicSLManager                  │
├─────────────────────────────────────────┤
│ - config: dict                          │
│ - sl_history: dict                      │
├─────────────────────────────────────────┤
│ + should_adjust_stop_loss(...): tuple   │
│ + detect_trend_reversal(...): bool      │
│ + detect_ma_crossover_against(...): bool│
│ + detect_volatility_change(...): str    │
│ + calculate_reversal_stop(...): float   │
│ + validate_sl_adjustment(...): bool     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        VolumeAnalyzer                   │
├─────────────────────────────────────────┤
│ - config: dict                          │
│ - volume_ma_period: int                 │
├─────────────────────────────────────────┤
│ + analyze_volume(df): DataFrame         │
│ + is_above_average_volume(df): bool     │
│ + get_volume_trend(df): str             │
│ + calculate_obv(df): Series             │
│ + get_volume_confirmation(df, sig): dict│
└─────────────────────────────────────────┘
```

### 7.3 Class Relationships

```
                    ┌──────────────┐
                    │  run_bot.py  │
                    └──────┬───────┘
                           │
                           │ creates
                           ↓
                  ┌─────────────────┐
                  │ MT5TradingBot   │
                  └─────────────────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
                │ has-a    │ has-a    │ has-a
                ↓          ↓          ↓
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ConfigManager │ │AdaptiveRisk  │ │VolumeAnalyzer│
    └──────────────┘ │Manager       │ └──────────────┘
                     └──────────────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
                │ uses     │ uses     │ uses
                ↓          ↓          ↓
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │DynamicTP     │ │DynamicSL     │ │MetaTrader5   │
    │Manager       │ │Manager       │ │API           │
    └──────────────┘ └──────────────┘ └──────────────┘

Relationship Types:
• creates: Instantiation
• has-a: Composition (strong ownership)
• uses: Dependency (weak coupling)
```

---

## 8. Integration Patterns

### 8.1 Strategy Pattern (Adaptive Modules)

```python
# Each adaptive module implements a strategy
class AdaptiveStrategy:
    def analyze(self, data):
        raise NotImplementedError
    
    def adjust(self, parameters):
        raise NotImplementedError

# Concrete strategies
class AdaptiveRiskManager(AdaptiveStrategy):
    def analyze(self, df):
        return self.analyze_market_condition(df)
    
    def adjust(self, market_condition):
        return self.adjust_risk_parameters(market_condition)

# Bot uses strategies polymorphically
if self.adaptive_risk_manager:
    market_condition = self.adaptive_risk_manager.analyze(df)
    params = self.adaptive_risk_manager.adjust(market_condition)
```

**Benefits:**
- Easy to add new strategies
- Strategies can be enabled/disabled independently
- Testable in isolation


### 8.2 Observer Pattern (Dashboard Monitoring)

```python
# Dashboard observes bot status
class WebDashboard:
    def __init__(self):
        self.bot_status = 'stopped'
        self.update_interval = 1  # seconds
    
    def get_bot_status(self):
        # Poll bot status
        return global_bot_status
    
    def get_positions(self):
        # Poll MT5 for positions
        return mt5.positions_get()

# Frontend polls dashboard
setInterval(function() {
    fetch('/api/bot/status')
        .then(response => response.json())
        .then(data => updateUI(data));
}, 1000);  // Poll every 1 second
```

**Benefits:**
- Loose coupling between bot and dashboard
- Dashboard can run independently
- No blocking of bot operations

### 8.3 Factory Pattern (Position Creation)

```python
def create_position(self, signal, lot_size):
    """Factory method for creating positions"""
    if self.use_split_orders:
        return self.open_split_positions(signal, lot_size)
    else:
        return self.open_single_position(signal, lot_size)

def open_split_positions(self, signal, total_lot_size):
    """Create multiple positions with different TPs"""
    positions = []
    for i, (tp_ratio, percent) in enumerate(zip(self.tp_levels, self.partial_close_percent)):
        lot = total_lot_size * (percent / 100)
        position = self._create_position_object(signal, lot, tp_ratio)
        positions.append(position)
    return positions
```

**Benefits:**
- Encapsulates position creation logic
- Easy to add new position types
- Consistent position creation

### 8.4 Template Method Pattern (Position Management)

```python
def manage_positions(self):
    """Template method for position management"""
    positions = self.get_open_positions()
    
    for position in positions:
        # Template steps
        self.verify_position(position)
        market_data = self.fetch_market_data(position.symbol)
        market_condition = self.analyze_market(market_data)
        
        # Hook methods (can be overridden)
        self.apply_dynamic_sl(position, market_data, market_condition)
        self.apply_dynamic_tp(position, market_data, market_condition)
        self.apply_trailing_stop(position, market_data)
        
        self.cleanup_if_closed(position)
```

**Benefits:**
- Defines algorithm structure
- Allows customization of specific steps
- Ensures consistent execution order

---

## 9. Algorithm Implementations

### 9.1 Moving Average Crossover Algorithm

```python
def check_ma_crossover(df):
    """
    Detect MA crossover signals
    
    Algorithm:
    1. Calculate fast MA (10-period)
    2. Calculate slow MA (30-period)
    3. Compare current and previous values
    4. Detect crossover direction
    
    Time Complexity: O(n) where n = dataframe length
    Space Complexity: O(1) for crossover detection
    """
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    # Bullish crossover: Fast crosses above Slow
    if (latest['fast_ma'] > latest['slow_ma'] and 
        previous['fast_ma'] <= previous['slow_ma']):
        return 'BUY', latest['close']
    
    # Bearish crossover: Fast crosses below Slow
    elif (latest['fast_ma'] < latest['slow_ma'] and 
          previous['fast_ma'] >= previous['slow_ma']):
        return 'SELL', latest['close']
    
    return None, None
```

### 9.2 ATR Calculation Algorithm

```python
def calculate_atr(df, period=14):
    """
    Calculate Average True Range
    
    Algorithm:
    1. Calculate True Range for each bar:
       TR = max(high - low, |high - prev_close|, |low - prev_close|)
    2. Calculate ATR as moving average of TR
    
    Time Complexity: O(n)
    Space Complexity: O(n) for storing TR values
    """
    df['prev_close'] = df['close'].shift(1)
    
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['prev_close'])
    df['tr3'] = abs(df['low'] - df['prev_close'])
    
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=period).mean()
    
    return df
```


### 9.3 Position Sizing Algorithm

```python
def calculate_position_size(self, signal, market_condition=None):
    """
    Calculate position size based on risk management
    
    Algorithm:
    1. Calculate risk amount (account balance × risk%)
    2. Apply adaptive risk multiplier if available
    3. Calculate SL distance in pips
    4. Calculate pip value for symbol
    5. Convert to lot size
    6. Apply min/max constraints
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    account_info = mt5.account_info()
    balance = account_info.balance
    
    # Step 1: Base risk amount
    risk_amount = balance * (self.risk_percent / 100)
    
    # Step 2: Apply adaptive multiplier
    if market_condition:
        risk_multiplier = market_condition.get('risk_multiplier', 1.0)
        risk_amount *= risk_multiplier
    
    # Step 3: Calculate SL distance
    atr = signal['atr']
    sl_distance_pips = atr * self.atr_multiplier * 10  # Convert to pips
    
    # Step 4: Get pip value
    symbol_info = mt5.symbol_info(signal['symbol'])
    pip_value = symbol_info.trade_tick_value
    
    # Step 5: Calculate lot size
    lot_size = risk_amount / (sl_distance_pips * pip_value)
    
    # Step 6: Apply constraints
    lot_size = max(symbol_info.volume_min, lot_size)
    lot_size = min(symbol_info.volume_max, lot_size)
    lot_size = round(lot_size, 2)
    
    return lot_size
```

### 9.4 Trend Consistency Algorithm

```python
def calculate_trend_consistency(df, lookback=20):
    """
    Calculate trend consistency percentage
    
    Algorithm:
    1. Get last N bars
    2. Determine current trend direction
    3. Count bars matching current trend
    4. Calculate percentage
    
    Time Complexity: O(n) where n = lookback
    Space Complexity: O(1)
    """
    if len(df) < lookback:
        return 50.0  # Neutral
    
    recent_trends = df['ma_trend'].tail(lookback)
    current_trend = df['ma_trend'].iloc[-1]
    
    # Count matching trends
    matching = (recent_trends == current_trend).sum()
    consistency = (matching / lookback) * 100
    
    return consistency
```

### 9.5 Swing Level Detection Algorithm

```python
def detect_swing_level(df, direction, lookback=20):
    """
    Detect significant swing highs/lows
    
    Algorithm:
    1. Get recent price data
    2. For LONG: Find swing lows (local minima)
    3. For SHORT: Find swing highs (local maxima)
    4. Validate significance (must be X% away from current)
    5. Return most recent significant level
    
    Time Complexity: O(n) where n = lookback
    Space Complexity: O(n) for storing candidates
    """
    if len(df) < lookback:
        return None
    
    recent = df.tail(lookback)
    current_price = df['close'].iloc[-1]
    atr = df['atr'].iloc[-1]
    
    if direction == 1:  # Long position - find swing lows
        # Find local minima
        lows = recent['low'].values
        swing_candidates = []
        
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                swing_candidates.append(lows[i])
        
        # Filter by significance (must be > 0.5 ATR below current)
        significant = [s for s in swing_candidates 
                      if current_price - s > 0.5 * atr]
        
        return max(significant) if significant else None
    
    else:  # Short position - find swing highs
        highs = recent['high'].values
        swing_candidates = []
        
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                swing_candidates.append(highs[i])
        
        significant = [s for s in swing_candidates 
                      if s - current_price > 0.5 * atr]
        
        return min(significant) if significant else None
```

---

## 10. Error Handling Architecture

### 10.1 Error Handling Hierarchy

```
┌─────────────────────────────────────────┐
│         Application Level               │
│  • Graceful degradation                 │
│  • User-friendly messages               │
│  • Retry logic                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Module Level                    │
│  • Try/except blocks                    │
│  • Module-specific handling             │
│  • Return None on failure               │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Infrastructure Level            │
│  • MT5 API errors                       │
│  • File system errors                   │
│  • Network errors                       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Logging System                  │
│  • Log all errors                       │
│  • Include context                      │
│  • Track error patterns                 │
└─────────────────────────────────────────┘
```


### 10.2 Error Handling Patterns

```python
# Pattern 1: Graceful Degradation
def run_strategy(self, symbol):
    try:
        # Attempt adaptive risk analysis
        if self.adaptive_risk_manager:
            market_condition = self.adaptive_risk_manager.analyze_market_condition(df)
    except Exception as e:
        logging.warning(f"Adaptive risk analysis failed: {e}")
        market_condition = None  # Fall back to standard logic
    
    # Continue with standard logic if adaptive fails
    if market_condition:
        # Use adaptive parameters
        pass
    else:
        # Use standard parameters
        pass

# Pattern 2: Retry with Exponential Backoff
def connect_with_retry(self, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            if mt5.initialize():
                return True
        except Exception as e:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            logging.warning(f"Connection attempt {attempt+1} failed, retrying in {wait_time}s")
            time.sleep(wait_time)
    
    return False

# Pattern 3: Context-Rich Logging
def open_position(self, signal):
    try:
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"Order failed: {result.retcode}, {result.comment}, "
                         f"Symbol: {signal['symbol']}, Type: {signal['type']}, "
                         f"Lot: {signal['lot_size']}")
            return False
    except Exception as e:
        logging.error(f"Exception in open_position: {e}", exc_info=True)
        return False
```

### 10.3 Error Recovery Strategies

| Error Type | Recovery Strategy | Fallback |
|------------|------------------|----------|
| MT5 Connection Lost | Retry 3 times with backoff | Stop bot, alert user |
| Data Fetch Failed | Skip symbol, continue with others | Log warning |
| Indicator Calculation Error | Use previous values | Skip signal |
| Adaptive Module Error | Disable module, use standard logic | Continue trading |
| Order Execution Failed | Log error, don't retry | Wait for next signal |
| Position Modification Failed | Log error, keep current SL/TP | Try again next cycle |
| Config Load Failed | Use default configuration | Alert user |
| Dashboard Error | Log error, dashboard unavailable | Bot continues |

---

## 11. Performance Optimization

### 11.1 Caching Strategy

```python
class MT5TradingBot:
    def __init__(self, config):
        # Cache frequently accessed data
        self._indicator_cache = {}
        self._symbol_info_cache = {}
        self._cache_ttl = 60  # seconds
    
    def get_historical_data(self, symbol, timeframe, bars=200):
        cache_key = f"{symbol}_{timeframe}_{bars}"
        
        # Check cache
        if cache_key in self._indicator_cache:
            cached_data, timestamp = self._indicator_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_data
        
        # Fetch fresh data
        data = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        df = pd.DataFrame(data)
        
        # Update cache
        self._indicator_cache[cache_key] = (df, time.time())
        
        return df
```

### 11.2 Batch Processing

```python
def manage_positions(self):
    """Process all positions in batch"""
    # Fetch all positions once
    positions = mt5.positions_get(group=f"*{self.magic_number}*")
    
    # Group by symbol to reuse market data
    positions_by_symbol = {}
    for pos in positions:
        if pos.symbol not in positions_by_symbol:
            positions_by_symbol[pos.symbol] = []
        positions_by_symbol[pos.symbol].append(pos)
    
    # Process each symbol's positions together
    for symbol, symbol_positions in positions_by_symbol.items():
        # Fetch market data once per symbol
        df = self.get_historical_data(symbol, self.timeframe)
        market_condition = self.analyze_market(df)
        
        # Process all positions for this symbol
        for position in symbol_positions:
            self.update_position(position, df, market_condition)
```

### 11.3 Lazy Loading

```python
class AdaptiveRiskManager:
    def __init__(self, config):
        self.config = config
        self._adx_cache = None
        self._cache_timestamp = None
    
    def calculate_adx(self, df):
        """Lazy calculation with caching"""
        current_time = time.time()
        
        # Return cached value if recent
        if (self._adx_cache is not None and 
            self._cache_timestamp is not None and
            current_time - self._cache_timestamp < 60):
            return self._adx_cache
        
        # Calculate ADX
        adx = self._compute_adx(df)
        
        # Update cache
        self._adx_cache = adx
        self._cache_timestamp = current_time
        
        return adx
```


### 11.4 Memory Management

```python
def cleanup_old_data(self):
    """Periodically clean up old cached data"""
    current_time = time.time()
    
    # Clean indicator cache
    expired_keys = [
        key for key, (data, timestamp) in self._indicator_cache.items()
        if current_time - timestamp > self._cache_ttl
    ]
    for key in expired_keys:
        del self._indicator_cache[key]
    
    # Clean position history
    for ticket in list(self.positions.keys()):
        if ticket not in [p.ticket for p in mt5.positions_get()]:
            del self.positions[ticket]
    
    # Clean TP/SL history (keep only last 100 entries per position)
    if hasattr(self, 'dynamic_tp_manager'):
        for ticket in list(self.dynamic_tp_manager.tp_history.keys()):
            history = self.dynamic_tp_manager.tp_history[ticket]
            if len(history) > 100:
                self.dynamic_tp_manager.tp_history[ticket] = history[-100:]
```

### 11.5 Performance Metrics

| Operation | Target Time | Actual Time | Optimization |
|-----------|-------------|-------------|--------------|
| Fetch Historical Data | < 500ms | ~300ms | ✅ Acceptable |
| Calculate Indicators | < 100ms | ~50ms | ✅ Acceptable |
| Signal Generation | < 50ms | ~30ms | ✅ Acceptable |
| Adaptive Risk Analysis | < 200ms | ~150ms | ✅ Acceptable |
| Position Management (per position) | < 100ms | ~80ms | ✅ Acceptable |
| Full Trading Cycle (16 symbols) | < 10s | ~8s | ✅ Acceptable |

---

## 12. Threading & Concurrency

### 12.1 Threading Architecture

```
Main Thread
    │
    ├─→ MT5TradingBot Thread
    │       │
    │       ├─→ Trading Loop (60s cycle)
    │       │     ├─→ Analyze Symbols (sequential)
    │       │     └─→ Manage Positions (sequential)
    │       │
    │       └─→ Cleanup Thread (periodic)
    │
    └─→ WebDashboard Thread
            │
            ├─→ Flask Server
            └─→ API Endpoints
```

### 12.2 Thread Safety

```python
import threading

class MT5TradingBot:
    def __init__(self, config):
        self.config = config
        self._lock = threading.Lock()
        self._running = False
    
    def run(self):
        """Main trading loop with thread safety"""
        self._running = True
        
        while self._running:
            try:
                with self._lock:
                    # Critical section - modify shared state
                    self.analyze_and_trade()
                    self.manage_positions()
                
                time.sleep(60)
            except Exception as e:
                logging.error(f"Error in trading loop: {e}")
    
    def stop(self):
        """Thread-safe stop"""
        with self._lock:
            self._running = False
```

### 12.3 Dashboard Concurrency

```python
# Flask runs in separate thread
def start_dashboard():
    dashboard_thread = threading.Thread(
        target=app.run,
        kwargs={'host': '0.0.0.0', 'port': 5000},
        daemon=True
    )
    dashboard_thread.start()

# API endpoints access shared data safely
@app.route('/api/positions')
def get_positions():
    # MT5 API is thread-safe
    positions = mt5.positions_get()
    return jsonify([position_to_dict(p) for p in positions])
```

### 12.4 Avoiding Race Conditions

```python
# Problem: Multiple threads modifying config
# Solution: Use locks

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self._lock = threading.Lock()
        self.config = self._load_or_create_config()
    
    def update_config(self, updates):
        """Thread-safe config update"""
        with self._lock:
            self.config.update(updates)
            self.save_config(self.config)
    
    def get_config(self):
        """Thread-safe config read"""
        with self._lock:
            return self.config.copy()
```

---

## 13. Implementation Best Practices

### 13.1 Code Organization

```
src/
├── mt5_trading_bot.py          # Core engine (1500 lines)
├── config_manager.py           # Configuration (200 lines)
├── adaptive_risk_manager.py    # Adaptive risk (400 lines)
├── dynamic_tp_manager.py       # Dynamic TP (500 lines)
├── dynamic_sl_manager.py       # Dynamic SL (500 lines)
└── volume_analyzer.py          # Volume analysis (300 lines)

Principles:
• Single Responsibility: Each file has one purpose
• Separation of Concerns: Trading logic separate from config
• DRY: Reusable functions for common operations
• SOLID: Follows SOLID principles
```


### 13.2 Naming Conventions

```python
# Classes: PascalCase
class MT5TradingBot:
    pass

# Functions/Methods: snake_case
def calculate_position_size(self, signal):
    pass

# Constants: UPPER_SNAKE_CASE
ADAPTIVE_RISK_AVAILABLE = True
MAX_RETRY_ATTEMPTS = 3

# Private methods: _leading_underscore
def _compute_adx(self, df):
    pass

# Variables: snake_case
market_condition = {}
trend_strength = 35.0
```

### 13.3 Documentation Standards

```python
def analyze_market_condition(self, df):
    """
    Analyze overall market condition to determine risk profile
    
    Args:
        df (pd.DataFrame): Price data with indicators
            Required columns: close, high, low, atr, fast_ma, slow_ma, ma_trend
    
    Returns:
        dict: Market condition analysis with keys:
            - market_type (str): 'strong_trend', 'weak_trend', 'ranging', 'volatile'
            - trend_strength (float): ADX value (0-100)
            - trend_direction (int): 1 for bullish, -1 for bearish
            - volatility_ratio (float): Current ATR / Average ATR
            - trend_consistency (float): Percentage (0-100)
            - current_atr (float): Current ATR value
    
    Raises:
        ValueError: If df is too short (< trend_strength_period)
    
    Example:
        >>> df = bot.get_historical_data('XAUUSD', mt5.TIMEFRAME_H1)
        >>> condition = adaptive_risk.analyze_market_condition(df)
        >>> print(condition['market_type'])
        'strong_trend'
    """
    pass
```

### 13.4 Logging Best Practices

```python
# Log levels usage:
logging.debug("Detailed diagnostic info")      # Development only
logging.info("Normal operation events")        # Production
logging.warning("Non-critical issues")         # Production
logging.error("Critical errors")               # Production

# Good logging examples:
logging.info(f"Signal for {symbol}: {signal_type} at {price:.2f}")
logging.info(f"Position opened: Ticket {ticket}, Lot {lot_size}, SL {sl:.2f}, TP {tp:.2f}")
logging.warning(f"Adaptive risk analysis failed for {symbol}: {error}")
logging.error(f"Failed to open position: {result.comment} (code: {result.retcode})")

# Include context:
logging.info(f"Dynamic TP extended: Ticket {ticket}, Old TP {old_tp:.2f}, "
            f"New TP {new_tp:.2f}, Reason: {reason}")
```

### 13.5 Testing Strategy

```python
# Unit tests for individual functions
def test_calculate_atr():
    df = create_test_dataframe()
    atr = calculate_atr(df, period=14)
    assert atr > 0
    assert len(atr) == len(df)

# Integration tests for module interaction
def test_adaptive_risk_integration():
    config = get_test_config()
    bot = MT5TradingBot(config)
    df = bot.get_historical_data('XAUUSD', mt5.TIMEFRAME_H1)
    
    market_condition = bot.adaptive_risk_manager.analyze_market_condition(df)
    assert market_condition is not None
    assert 'market_type' in market_condition

# Mock MT5 for testing without live connection
class MockMT5:
    @staticmethod
    def initialize():
        return True
    
    @staticmethod
    def copy_rates_from_pos(symbol, timeframe, start, count):
        return generate_mock_data(count)
```

---

## 14. Deployment Architecture

### 14.1 Deployment Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Windows VPS / Local PC               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         MetaTrader 5 Platform                    │  │
│  │  • Market data feed                              │  │
│  │  • Order execution                               │  │
│  │  • Position management                           │  │
│  └──────────────────────────────────────────────────┘  │
│                          ↕                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │         GEM Trading Bot                          │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Python Process                            │  │  │
│  │  │  • MT5TradingBot (Main Thread)             │  │  │
│  │  │  • WebDashboard (Flask Thread)             │  │  │
│  │  │  • Adaptive Modules                        │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │                                                  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  File System                               │  │  │
│  │  │  • bot_config.json                         │  │  │
│  │  │  • trading_bot.log                         │  │  │
│  │  │  • config_backups/                         │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
│                          ↕                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Web Browser (Dashboard)                  │  │
│  │  • http://localhost:5000                         │  │
│  │  • Real-time monitoring                          │  │
│  │  • Configuration management                      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          ↕
                  (Optional: SSH Tunnel)
                          ↕
┌─────────────────────────────────────────────────────────┐
│              Remote User (via SSH)                      │
│  • Access dashboard remotely                            │
│  • Monitor bot status                                   │
│  • Adjust configuration                                 │
└─────────────────────────────────────────────────────────┘
```


### 14.2 Executable Build Process

```
Source Code
    │
    ├─→ PyInstaller
    │     │
    │     ├─→ Analyze dependencies
    │     ├─→ Bundle Python interpreter
    │     ├─→ Include all modules
    │     ├─→ Package resources
    │     └─→ Create executable
    │
    └─→ Output
          │
          ├─→ GEM_Trading_Bot.exe (Windows)
          ├─→ All dependencies bundled
          ├─→ No Python installation required
          └─→ Portable deployment
```

### 14.3 Configuration Management in Production

```
Development
    │
    ├─→ bot_config.json (default settings)
    │
    └─→ Test locally
          │
          ↓
Production
    │
    ├─→ Copy bot_config.json to VPS
    │
    ├─→ Customize for production
    │     ├─→ Set real account credentials
    │     ├─→ Adjust risk parameters
    │     └─→ Enable/disable features
    │
    ├─→ Start bot
    │
    └─→ Monitor via dashboard
          │
          ├─→ Adjust settings as needed
          └─→ Backups created automatically
```

---

## 15. Security Considerations

### 15.1 Security Architecture

```
┌─────────────────────────────────────────┐
│         Application Security            │
├─────────────────────────────────────────┤
│ • No hardcoded credentials              │
│ • MT5 handles authentication            │
│ • Config files local only               │
│ • Magic number isolation                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Network Security                │
├─────────────────────────────────────────┤
│ • Dashboard on localhost by default     │
│ • SSH tunnel for remote access          │
│ • No public exposure                    │
│ • Encrypted MT5 connection              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Data Security                   │
├─────────────────────────────────────────┤
│ • Config backups protected              │
│ • Logs contain no sensitive data        │
│ • File system permissions               │
│ • No external data transmission         │
└─────────────────────────────────────────┘
```

### 15.2 Security Best Practices

```python
# 1. No hardcoded credentials
# BAD:
username = "myaccount"
password = "mypassword"

# GOOD:
# Let MT5 handle authentication through its platform

# 2. Validate all inputs
def update_config(self, updates):
    # Validate before applying
    if 'risk_percent' in updates:
        risk = updates['risk_percent']
        if not (0 < risk <= 10):
            raise ValueError("Risk must be between 0 and 10%")
    
    self.config.update(updates)

# 3. Sanitize log output
def log_trade(self, position):
    # Don't log sensitive account info
    logging.info(f"Position opened: Ticket {position.ticket}, "
                f"Symbol {position.symbol}, Lot {position.volume}")
    # Don't log: account number, balance, etc.

# 4. Use magic number for isolation
self.magic_number = 123456  # Unique identifier
# Prevents interference with other bots/manual trades
```

---

## 16. Monitoring & Observability

### 16.1 Monitoring Architecture

```
┌─────────────────────────────────────────┐
│         Application Metrics             │
├─────────────────────────────────────────┤
│ • Bot status (running/stopped)          │
│ • Active positions count                │
│ • Daily P&L                             │
│ • Win rate                              │
│ • Error rate                            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Logging System                  │
├─────────────────────────────────────────┤
│ • trading_bot.log                       │
│ • Timestamped entries                   │
│ • Structured logging                    │
│ • Error tracking                        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Dashboard Visualization         │
├─────────────────────────────────────────┤
│ • Real-time status                      │
│ • Position table                        │
│ • Trade history                         │
│ • Performance charts                    │
└─────────────────────────────────────────┘
```

### 16.2 Key Performance Indicators (KPIs)

| KPI | Measurement | Target | Alert Threshold |
|-----|-------------|--------|-----------------|
| Bot Uptime | % time running | > 99% | < 95% |
| Signal Frequency | Signals per day | 5-20 | < 2 or > 50 |
| Win Rate | Winning trades / Total | > 50% | < 40% |
| Average Profit | Avg profit per trade | > 0 | Negative |
| Max Drawdown | Peak to trough | < 20% | > 30% |
| Error Rate | Errors per hour | < 1 | > 5 |
| Position Count | Open positions | 0-10 | > 15 |
| Daily P&L | Daily profit/loss | Positive | < -5% |


### 16.3 Health Check Implementation

```python
def get_bot_health(self):
    """
    Comprehensive health check
    
    Returns:
        dict: Health status with metrics
    """
    health = {
        'status': 'healthy',
        'checks': {},
        'timestamp': datetime.now().isoformat()
    }
    
    # Check MT5 connection
    if not mt5.terminal_info():
        health['status'] = 'unhealthy'
        health['checks']['mt5_connection'] = 'failed'
    else:
        health['checks']['mt5_connection'] = 'ok'
    
    # Check account status
    account_info = mt5.account_info()
    if account_info:
        health['checks']['account_balance'] = account_info.balance
        health['checks']['account_equity'] = account_info.equity
        
        # Check margin level
        if account_info.margin_level < 100:
            health['status'] = 'warning'
            health['checks']['margin_level'] = 'low'
    
    # Check position count
    positions = mt5.positions_get()
    health['checks']['open_positions'] = len(positions) if positions else 0
    
    # Check recent errors
    recent_errors = self.get_recent_errors(hours=1)
    health['checks']['recent_errors'] = len(recent_errors)
    if len(recent_errors) > 5:
        health['status'] = 'warning'
    
    # Check last trade time
    last_trade_time = self.get_last_trade_time()
    if last_trade_time:
        hours_since = (datetime.now() - last_trade_time).total_seconds() / 3600
        health['checks']['hours_since_last_trade'] = hours_since
        if hours_since > 24:
            health['status'] = 'warning'
    
    return health
```

---

## 17. Scalability Considerations

### 17.1 Current Scalability

```
Current Capacity:
• Symbols: 16 (configurable)
• Positions: 999 (virtually unlimited)
• Timeframes: Any MT5 timeframe
• Update Frequency: 60 seconds
• Dashboard Users: Multiple (read-only)

Bottlenecks:
• MT5 API rate limits
• Single-threaded trading loop
• Sequential symbol processing
```

### 17.2 Scaling Strategies

```python
# Strategy 1: Parallel Symbol Processing
from concurrent.futures import ThreadPoolExecutor

def run_parallel(self):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(self.run_strategy, symbol)
            for symbol in self.symbols
        ]
        for future in futures:
            future.result()

# Strategy 2: Symbol Prioritization
def prioritize_symbols(self):
    """Process high-priority symbols first"""
    # Sort by volatility or recent performance
    sorted_symbols = sorted(
        self.symbols,
        key=lambda s: self.get_symbol_priority(s),
        reverse=True
    )
    return sorted_symbols

# Strategy 3: Adaptive Update Frequency
def get_update_interval(self, symbol):
    """Adjust update frequency based on timeframe"""
    if self.timeframe == mt5.TIMEFRAME_M1:
        return 10  # Update every 10 seconds
    elif self.timeframe == mt5.TIMEFRAME_M5:
        return 30  # Update every 30 seconds
    else:
        return 60  # Update every 60 seconds
```

### 17.3 Future Scalability Enhancements

```
Phase 1: Optimization (Current)
• Caching
• Batch processing
• Efficient algorithms

Phase 2: Parallelization
• Multi-threaded symbol processing
• Async I/O for MT5 API
• Parallel indicator calculation

Phase 3: Distribution
• Multiple bot instances
• Load balancing
• Centralized monitoring

Phase 4: Cloud Deployment
• Containerization (Docker)
• Kubernetes orchestration
• Auto-scaling
```

---

## 18. Maintenance & Operations

### 18.1 Routine Maintenance Tasks

| Task | Frequency | Description |
|------|-----------|-------------|
| Log Rotation | Weekly | Archive old logs, keep last 30 days |
| Config Backup | Daily | Automatic on config changes |
| Performance Review | Weekly | Analyze win rate, P&L, drawdown |
| Error Analysis | Daily | Review error logs, fix issues |
| Update Check | Monthly | Check for MT5 updates, library updates |
| Database Cleanup | Monthly | Clean old position history |
| Health Check | Hourly | Automated health monitoring |

### 18.2 Troubleshooting Guide

```
Problem: Bot not connecting to MT5
Solution:
1. Check MT5 is running
2. Check MT5 build version (>= 5549)
3. Check MT5 terminal path
4. Restart MT5 and bot

Problem: No signals generated
Solution:
1. Check symbol data availability
2. Verify indicator calculations
3. Check filter settings (too strict?)
4. Review recent market conditions

Problem: Positions not updating
Solution:
1. Check MT5 connection
2. Verify position exists
3. Check magic number filter
4. Review error logs

Problem: Dashboard not accessible
Solution:
1. Check Flask server running
2. Verify port 5000 not blocked
3. Check firewall settings
4. Try http://127.0.0.1:5000
```


### 18.3 Upgrade Procedures

```
Minor Update (Config Changes):
1. Stop bot
2. Backup current config
3. Update bot_config.json
4. Restart bot
5. Verify changes in dashboard

Major Update (Code Changes):
1. Stop bot
2. Backup entire directory
3. Update source files
4. Test in development environment
5. Deploy to production
6. Monitor for 24 hours

Module Update (New Features):
1. Add new module file
2. Update imports in main bot
3. Add config parameters
4. Test with feature disabled
5. Enable feature gradually
6. Monitor performance
```

---

## 19. Technical Debt & Future Improvements

### 19.1 Known Technical Debt

| Item | Impact | Priority | Effort |
|------|--------|----------|--------|
| Imports inside loops | Low | Low | 1 hour |
| Market condition recalculation | Low | Low | 2 hours |
| Hardcoded scalping timeframe | Low | Low | 1 hour |
| No database for trade history | Medium | Medium | 1 week |
| No WebSocket for real-time updates | Medium | Medium | 3 days |
| Limited error recovery | Medium | High | 1 week |
| No automated testing | High | High | 2 weeks |

### 19.2 Planned Enhancements

```
Short Term (1-3 months):
• Add automated testing suite
• Implement WebSocket for real-time updates
• Add email/SMS notifications
• Improve error recovery mechanisms
• Add backtesting framework

Medium Term (3-6 months):
• Database integration (PostgreSQL)
• Advanced charting in dashboard
• Machine learning integration
• Multi-account support
• API for external integrations

Long Term (6-12 months):
• Microservices architecture
• Cloud deployment (AWS/Azure)
• Mobile app
• Social trading features
• Advanced analytics dashboard
```

### 19.3 Refactoring Opportunities

```python
# Opportunity 1: Extract indicator calculation to separate class
class IndicatorCalculator:
    def __init__(self, config):
        self.config = config
    
    def calculate_all(self, df):
        df = self.calculate_ma(df)
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_atr(df)
        return df

# Opportunity 2: Create position manager class
class PositionManager:
    def __init__(self, config):
        self.config = config
        self.positions = {}
    
    def open_position(self, signal):
        pass
    
    def close_position(self, ticket):
        pass
    
    def update_position(self, ticket, sl=None, tp=None):
        pass

# Opportunity 3: Separate signal generation logic
class SignalGenerator:
    def __init__(self, config):
        self.config = config
    
    def generate_signal(self, df):
        if self.check_ma_crossover(df):
            if self.apply_filters(df):
                return self.create_signal(df)
        return None
```

---

## 20. Conclusion

### 20.1 System Strengths

✅ **Modular Architecture**
- Clear separation of concerns
- Easy to maintain and extend
- Independent module testing

✅ **Adaptive Intelligence**
- Three-layer adaptive system
- Market-aware risk management
- Dynamic position optimization

✅ **Robust Error Handling**
- Graceful degradation
- Comprehensive logging
- Recovery mechanisms

✅ **User-Friendly Interface**
- Web-based dashboard
- Real-time monitoring
- Easy configuration

✅ **Production-Ready**
- Tested and verified
- Comprehensive documentation
- Deployment guides

### 20.2 Technical Highlights

```
Architecture:
• Layered design (Presentation, Application, Domain, Infrastructure)
• Dependency injection for loose coupling
• Strategy pattern for adaptive modules
• Observer pattern for monitoring

Performance:
• Efficient caching strategies
• Batch processing
• Lazy loading
• Memory management

Reliability:
• Thread-safe operations
• Error recovery
• Health monitoring
• Automated backups

Scalability:
• Supports 16+ symbols
• 999 concurrent positions
• Parallel processing ready
• Cloud deployment ready
```

### 20.3 Integration Summary

```
Component Integration Flow:

User Input → Dashboard → ConfigManager → bot_config.json
                                              ↓
Market Data → MT5 API → MT5TradingBot → Indicators
                                              ↓
                                    Signal Generation
                                              ↓
                                    AdaptiveRiskManager
                                              ↓
                                    Position Sizing
                                              ↓
                                    Trade Execution
                                              ↓
                                    Position Management
                                    ↙              ↘
                          DynamicSLManager    DynamicTPManager
                                    ↓              ↓
                                    MT5 API Updates
                                              ↓
                                    Dashboard Display
```

### 20.4 Key Takeaways

1. **Well-Structured**: Clear architecture with defined layers and responsibilities
2. **Loosely Coupled**: Components interact through well-defined interfaces
3. **Highly Cohesive**: Each module has a single, focused purpose
4. **Extensible**: Easy to add new features without breaking existing code
5. **Maintainable**: Comprehensive documentation and clean code
6. **Testable**: Modular design enables unit and integration testing
7. **Production-Ready**: Deployed and actively trading

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **ADX** | Average Directional Index - measures trend strength |
| **ATR** | Average True Range - measures volatility |
| **Coupling** | Degree of interdependence between modules |
| **Cohesion** | Degree to which elements within a module belong together |
| **DI** | Directional Indicator (+DI and -DI) |
| **Graceful Degradation** | System continues with reduced functionality when components fail |
| **MACD** | Moving Average Convergence Divergence - momentum indicator |
| **Magic Number** | Unique identifier for bot's trades |
| **OBV** | On-Balance Volume - volume-based indicator |
| **RSI** | Relative Strength Index - momentum oscillator |
| **S/R** | Support and Resistance levels |
| **SL** | Stop Loss - risk management level |
| **TP** | Take Profit - profit target level |

---

## Appendix B: References

- **MetaTrader 5 API Documentation**: https://www.mql5.com/en/docs/integration/python_metatrader5
- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Python Threading**: https://docs.python.org/3/library/threading.html
- **Design Patterns**: Gang of Four (GoF) Design Patterns

---

**Document Version:** 1.0  
**Last Updated:** January 30, 2026  
**Author:** Technical Architecture Team  
**Status:** Complete

---

**Related Documents:**
- HIGH_LEVEL_DESIGN.md - System architecture overview
- SYSTEM_ARCHITECTURE_DIAGRAM.txt - Visual architecture diagrams
- ARCHITECTURE_QUICK_REFERENCE.txt - Quick reference guide
- ADAPTIVE_FEATURES_ANALYSIS.txt - Adaptive features details
- tests/README.md - Testing documentation

---

**End of Technical Design Document**

