"""
Activity Logger for Bot Operations
Tracks and stores bot activities for display in dashboard
"""

from datetime import datetime
from collections import deque
from typing import Dict, List
import threading


class ActivityLogger:
    """
    Thread-safe activity logger for bot operations
    Stores recent activities in memory for dashboard display
    """
    
    def __init__(self, max_activities: int = 500):
        """
        Initialize activity logger
        
        Args:
            max_activities: Maximum number of activities to store
        """
        self.activities = deque(maxlen=max_activities)
        self.lock = threading.Lock()
    
    def log(self, activity_type: str, message: str, symbol: str = None, 
            data: Dict = None, level: str = 'info'):
        """
        Log an activity
        
        Args:
            activity_type: Type of activity (analysis, signal, order, position, error)
            message: Activity message
            symbol: Trading symbol (optional)
            data: Additional data (optional)
            level: Log level (info, success, warning, error)
        """
        activity = {
            'timestamp': datetime.now().isoformat(),
            'type': activity_type,
            'message': message,
            'symbol': symbol,
            'data': data or {},
            'level': level
        }
        
        with self.lock:
            self.activities.append(activity)
    
    def get_recent(self, limit: int = 100, activity_type: str = None) -> List[Dict]:
        """
        Get recent activities
        
        Args:
            limit: Maximum number of activities to return
            activity_type: Filter by activity type (optional)
            
        Returns:
            List of recent activities
        """
        with self.lock:
            activities = list(self.activities)
        
        # Filter by type if specified
        if activity_type:
            activities = [a for a in activities if a['type'] == activity_type]
        
        # Return most recent first, limited
        return list(reversed(activities))[:limit]
    
    def clear(self):
        """Clear all activities"""
        with self.lock:
            self.activities.clear()
    
    # Convenience methods for common activity types
    
    def log_analysis(self, symbol: str, message: str, data: Dict = None):
        """Log market analysis activity"""
        self.log('analysis', message, symbol=symbol, data=data, level='info')
    
    def log_signal(self, symbol: str, signal_type: str, message: str, data: Dict = None):
        """Log trading signal"""
        level = 'success' if signal_type in ['BUY', 'SELL'] else 'info'
        self.log('signal', message, symbol=symbol, data=data, level=level)
    
    def log_order(self, symbol: str, order_type: str, message: str, data: Dict = None):
        """Log order placement"""
        self.log('order', message, symbol=symbol, data=data, level='success')
    
    def log_position(self, symbol: str, message: str, data: Dict = None):
        """Log position update"""
        self.log('position', message, symbol=symbol, data=data, level='info')
    
    def log_error(self, message: str, symbol: str = None, data: Dict = None):
        """Log error"""
        self.log('error', message, symbol=symbol, data=data, level='error')
    
    def log_warning(self, message: str, symbol: str = None, data: Dict = None):
        """Log warning"""
        self.log('warning', message, symbol=symbol, data=data, level='warning')
    
    # Detailed logging methods for bot tracking
    
    def log_bot_start(self, config: Dict):
        """Log bot startup with configuration details"""
        symbols_str = ', '.join(config.get('symbols', [])[:5])
        if len(config.get('symbols', [])) > 5:
            symbols_str += f" ... ({len(config['symbols'])} total)"
        
        self.log('system', '=' * 80, level='info')
        self.log('system', 'STARTING BOT WITH CONFIGURATION:', level='info')
        self.log('system', f"Symbols: {symbols_str}", level='info')
        self.log('system', f"Timeframe: {config.get('timeframe', 'N/A')}", level='info')
        self.log('system', f"Risk per trade: {config.get('risk_per_trade', 0)}%", level='info')
        self.log('system', f"Max positions: {config.get('max_positions', 0)}", level='info')
        self.log('system', f"Strategy: {config.get('strategy', 'N/A')}", level='info')
        self.log('system', f"Paper trading: {config.get('paper_trading', False)}", level='info')
        self.log('system', '=' * 80, level='info')
    
    def log_symbol_analysis_start(self, symbol: str):
        """Log start of symbol analysis"""
        self.log('analysis', '╔' + '=' * 78 + '╗', symbol=symbol, level='info')
        self.log('analysis', f'║ ANALYZING {symbol:^66} ║', symbol=symbol, level='info')
        self.log('analysis', '╚' + '=' * 78 + '╝', symbol=symbol, level='info')
    
    def log_data_fetch(self, symbol: str, bars_requested: int, bars_received: int):
        """Log data fetching"""
        status = '✅' if bars_received >= bars_requested else '⚠️'
        self.log('analysis', 
                f"{status} Fetched {bars_received} bars (requested: {bars_requested})",
                symbol=symbol, level='info')
    
    def log_indicator_calculation(self, symbol: str, indicators: Dict):
        """Log indicator calculation results"""
        self.log('analysis', '📊 Indicators calculated:', symbol=symbol, level='info')
        for name, value in indicators.items():
            if isinstance(value, (int, float)):
                self.log('analysis', f"  {name}: {value:.2f}", symbol=symbol, level='info')
    
    def log_signal_check(self, symbol: str, method: str, result: str, details: Dict = None):
        """Log signal detection method check"""
        icon = '✅' if 'passed' in result.lower() or 'detected' in result.lower() else '❌'
        self.log('signal', f"{icon} {method}: {result}", symbol=symbol, data=details, level='info')
    
    def log_filter_check(self, symbol: str, filter_name: str, passed: bool, details: str):
        """Log filter check result"""
        icon = '✅' if passed else '❌'
        level = 'success' if passed else 'warning'
        self.log('signal', f"{icon} {filter_name}: {details}", symbol=symbol, level=level)
    
    def log_trade_decision(self, symbol: str, decision: str, reason: str, data: Dict = None):
        """Log final trade decision"""
        self.log('signal', '-' * 80, symbol=symbol, level='info')
        if 'rejected' in decision.lower() or 'no signal' in decision.lower():
            self.log('signal', f"❌ {decision}: {reason}", symbol=symbol, data=data, level='warning')
        else:
            self.log('signal', f"✅ {decision}: {reason}", symbol=symbol, data=data, level='success')
        self.log('signal', '-' * 80, symbol=symbol, level='info')
    
    def log_position_check(self, symbol: str, current: int, max_allowed: int):
        """Log position check"""
        self.log('position', 
                f"📊 Position check: {current}/{max_allowed} positions for {symbol}",
                symbol=symbol, level='info')
    
    def log_risk_calculation(self, symbol: str, risk_data: Dict):
        """Log risk calculation details"""
        self.log('position', '💰 Risk calculation:', symbol=symbol, level='info')
        for key, value in risk_data.items():
            self.log('position', f"  {key}: {value}", symbol=symbol, level='info')
    
    def log_order_details(self, symbol: str, order_data: Dict):
        """Log detailed order information"""
        self.log('order', '📝 Order details:', symbol=symbol, level='info')
        for key, value in order_data.items():
            self.log('order', f"  {key}: {value}", symbol=symbol, level='info')
    
    def log_separator(self):
        """Log a separator line"""
        self.log('system', '=' * 80, level='info')
