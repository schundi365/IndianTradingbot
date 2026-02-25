"""
Reinforcement Learning Log Trainer
Extracts trading experiences from logs and trains RL agent
"""

import re
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import json
import pickle


class TradingLogParser:
    """
    Parses trading logs to extract experiences for RL training
    """
    
    def __init__(self, log_file: str = "trading_bot.log"):
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        
        # Patterns to extract from logs
        self.patterns = {
            'timestamp': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            'signal': r'Signal for (\w+): (BUY|SELL)',
            'entry': r'Entry: ([\d.]+)',
            'sl': r'SL: ([\d.]+)',
            'tp': r'TP: ([\d.]+)',
            'lots': r'Total Lots: ([\d.]+)',
            'position_opened': r'Position opened: (\w+) (BUY|SELL) at ([\d.]+)',
            'position_closed': r'Position (\d+) closed.*at ([\d.]+)',
            'profit': r'Profit: ([-\d.]+)',
            'ml_confidence': r'Combined Confidence: ([\d.]+)',
            'ml_approved': r'(✅ ML APPROVED|❌ ML REJECTED)',
            'rsi': r'RSI: ([\d.]+)',
            'macd': r'MACD Histogram: ([-\d.]+)',
            'adx': r'ADX: ([\d.]+)',
            'atr': r'ATR: ([\d.]+)',
            'technical_signal': r'Technical Analysis: (BUY|SELL) \(([\d.]+)%\)',
            'ml_signal': r'ML Analysis: (BUY|SELL) \(([\d.]+)%\)',
            'pattern_signal': r'Pattern: (