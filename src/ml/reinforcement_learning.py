"""
Reinforcement Learning Module
Implements adaptive trading policies using Q-Learning and Deep Q-Network (DQN)
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from collections import deque
import pickle
import json
from pathlib import Path
from datetime import datetime


class TradingEnvironment:
    """
    Trading environment for RL agent
    Simulates market conditions and provides rewards
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # State space dimensions
        self.state_size = 15  # OHLC, indicators, position info
        
        # Action space: 0=HOLD, 1=BUY, 2=SELL, 3=CLOSE
        self.action_space = 4
        
        # Current state
        self.current_position = None  # 'long', 'short', or None
        self.entry_price = 0.0
        self.position_size = 0.0
        self.unrealized_pnl = 0.0
        
        # Episode tracking
        self.episode_trades = []
        self.episode_reward = 0.0
        
    def reset(self) -> np.ndarray:
        """Reset environment to initial state"""
        self.current_position = None
        self.entry_price = 0.0
        self.position_size = 0.0
        self.unrealized_pnl = 0.0
        self.episode_trades = []
        self.episode_reward = 0.0
        
        return self._get_initial_state()
    
    def _get_initial_state(self) -> np.ndarray:
        """Get initial state vector"""
        return np.zeros(self.state_size)
    
    def get_state(self, market_data: Dict) -> np.ndarray:
        """
        Convert market data to state vector
        
        State includes:
        - Price features (normalized)
        - Technical indicators
        - Position information
        - Market volatility
        """
        state = np.zeros(self.state_size)
        
        try:
            # Price features (normalized)
            close = market_data['close'][-1]
            open_price = market_data['open'][-1]
            high = market_data['high'][-1]
            low = market_data['low'][-1]
            
            # Normalize prices relative to close
            state[0] = (high - close) / close if close > 0 else 0
            state[1] = (close - low) / close if close > 0 else 0
            state[2] = (close - open_price) / close if close > 0 else 0
            
            # Technical indicators (normalized)
            if 'rsi' in market_data and len(market_data['rsi']) > 0:
                state[3] = market_data['rsi'][-1] / 100.0  # 0-1 range
            
            if 'macd' in market_data and len(market_data['macd']) > 0:
                state[4] = np.tanh(market_data['macd'][-1])  # -1 to 1
            
            if 'adx' in market_data and len(market_data['adx']) > 0:
                state[5] = market_data['adx'][-1] / 100.0  # 0-1 range
            
            if 'atr' in market_data and len(market_data['atr']) > 0:
      