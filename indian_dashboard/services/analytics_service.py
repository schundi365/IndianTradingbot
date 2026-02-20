"""
Analytics Service
Calculates performance metrics and statistics from trade history
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for calculating trading analytics and performance metrics"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 60  # Cache for 60 seconds
    
    def get_performance_metrics(self, trades: List[Dict], from_date: str = None, to_date: str = None) -> Dict:
        """
        Calculate overall performance metrics
        
        Args:
            trades: List of trade dictionaries
            from_date: Start date filter (YYYY-MM-DD)
            to_date: End date filter (YYYY-MM-DD)
            
        Returns:
            Dictionary with performance metrics
        """
        try:
            # Filter trades by date
            filtered_trades = self._filter_trades_by_date(trades, from_date, to_date)
            
            if not filtered_trades:
                return self._empty_metrics()
            
            # Calculate metrics
            total_trades = len(filtered_trades)
            winning_trades = [t for t in filtered_trades if self._get_pnl(t) > 0]
            losing_trades = [t for t in filtered_trades if self._get_pnl(t) < 0]
            
            total_pnl = sum(self._get_pnl(t) for t in filtered_trades)
            total_wins = len(winning_trades)
            total_losses = len(losing_trades)
            
            win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
            
            avg_win = sum(self._get_pnl(t) for t in winning_trades) / total_wins if total_wins > 0 else 0
            avg_loss = sum(self._get_pnl(t) for t in losing_trades) / total_losses if total_losses > 0 else 0
            avg_trade = total_pnl / total_trades if total_trades > 0 else 0
            
            largest_win = max((self._get_pnl(t) for t in winning_trades), default=0)
            largest_loss = min((self._get_pnl(t) for t in losing_trades), default=0)
            
            # Profit factor
            gross_profit = sum(self._get_pnl(t) for t in winning_trades)
            gross_loss = abs(sum(self._get_pnl(t) for t in losing_trades))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': total_wins,
                'losing_trades': total_losses,
                'win_rate': round(win_rate, 2),
                'total_pnl': round(total_pnl, 2),
                'avg_win': round(avg_win, 2),
                'avg_loss': round(avg_loss, 2),
                'avg_trade': round(avg_trade, 2),
                'largest_win': round(largest_win, 2),
                'largest_loss': round(largest_loss, 2),
                'profit_factor': round(profit_factor, 2),
                'gross_profit': round(gross_profit, 2),
                'gross_loss': round(gross_loss, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}", exc_info=True)
            return self._empty_metrics()
    
    def get_profit_by_symbol(self, trades: List[Dict], from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Calculate profit/loss by symbol
        
        Args:
            trades: List of trade dictionaries
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            List of {symbol, pnl, trades_count, win_rate}
        """
        try:
            filtered_trades = self._filter_trades_by_date(trades, from_date, to_date)
            
            symbol_data = defaultdict(lambda: {'pnl': 0, 'trades': [], 'wins': 0})
            
            for trade in filtered_trades:
                symbol = trade.get('symbol', 'UNKNOWN')
                pnl = self._get_pnl(trade)
                
                symbol_data[symbol]['pnl'] += pnl
                symbol_data[symbol]['trades'].append(trade)
                if pnl > 0:
                    symbol_data[symbol]['wins'] += 1
            
            result = []
            for symbol, data in symbol_data.items():
                trades_count = len(data['trades'])
                win_rate = (data['wins'] / trades_count * 100) if trades_count > 0 else 0
                
                result.append({
                    'symbol': symbol,
                    'pnl': round(data['pnl'], 2),
                    'trades_count': trades_count,
                    'win_rate': round(win_rate, 2)
                })
            
            # Sort by PnL descending
            result.sort(key=lambda x: x['pnl'], reverse=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating profit by symbol: {e}", exc_info=True)
            return []
    
    def get_win_loss_by_symbol(self, trades: List[Dict], from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Calculate win/loss count by symbol
        
        Args:
            trades: List of trade dictionaries
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            List of {symbol, wins, losses}
        """
        try:
            filtered_trades = self._filter_trades_by_date(trades, from_date, to_date)
            
            symbol_data = defaultdict(lambda: {'wins': 0, 'losses': 0})
            
            for trade in filtered_trades:
                symbol = trade.get('symbol', 'UNKNOWN')
                pnl = self._get_pnl(trade)
                
                if pnl > 0:
                    symbol_data[symbol]['wins'] += 1
                elif pnl < 0:
                    symbol_data[symbol]['losses'] += 1
            
            result = []
            for symbol, data in symbol_data.items():
                result.append({
                    'symbol': symbol,
                    'wins': data['wins'],
                    'losses': data['losses']
                })
            
            # Sort by total trades descending
            result.sort(key=lambda x: x['wins'] + x['losses'], reverse=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating win/loss by symbol: {e}", exc_info=True)
            return []
    
    def get_daily_profit(self, trades: List[Dict], from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Calculate daily profit/loss trend
        
        Args:
            trades: List of trade dictionaries
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            List of {date, pnl, trades_count}
        """
        try:
            filtered_trades = self._filter_trades_by_date(trades, from_date, to_date)
            
            daily_data = defaultdict(lambda: {'pnl': 0, 'trades_count': 0})
            
            for trade in filtered_trades:
                date = self._get_trade_date(trade)
                pnl = self._get_pnl(trade)
                
                daily_data[date]['pnl'] += pnl
                daily_data[date]['trades_count'] += 1
            
            result = []
            for date, data in sorted(daily_data.items()):
                result.append({
                    'date': date,
                    'pnl': round(data['pnl'], 2),
                    'trades_count': data['trades_count']
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating daily profit: {e}", exc_info=True)
            return []
    
    def get_hourly_performance(self, trades: List[Dict], from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Calculate hourly performance
        
        Args:
            trades: List of trade dictionaries
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            List of {hour, pnl, trades_count}
        """
        try:
            filtered_trades = self._filter_trades_by_date(trades, from_date, to_date)
            
            hourly_data = defaultdict(lambda: {'pnl': 0, 'trades_count': 0})
            
            for trade in filtered_trades:
                hour = self._get_trade_hour(trade)
                pnl = self._get_pnl(trade)
                
                hourly_data[hour]['pnl'] += pnl
                hourly_data[hour]['trades_count'] += 1
            
            result = []
            for hour in range(24):
                hour_str = f"{hour:02d}:00"
                data = hourly_data.get(hour, {'pnl': 0, 'trades_count': 0})
                result.append({
                    'hour': hour_str,
                    'pnl': round(data['pnl'], 2),
                    'trades_count': data['trades_count']
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating hourly performance: {e}", exc_info=True)
            return []
    
    def get_trade_distribution(self, trades: List[Dict], from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Calculate trade distribution by symbol
        
        Args:
            trades: List of trade dictionaries
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            List of {symbol, count, percentage}
        """
        try:
            filtered_trades = self._filter_trades_by_date(trades, from_date, to_date)
            
            if not filtered_trades:
                return []
            
            symbol_counts = defaultdict(int)
            
            for trade in filtered_trades:
                symbol = trade.get('symbol', 'UNKNOWN')
                symbol_counts[symbol] += 1
            
            total_trades = len(filtered_trades)
            
            result = []
            for symbol, count in symbol_counts.items():
                percentage = (count / total_trades * 100) if total_trades > 0 else 0
                result.append({
                    'symbol': symbol,
                    'count': count,
                    'percentage': round(percentage, 2)
                })
            
            # Sort by count descending
            result.sort(key=lambda x: x['count'], reverse=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating trade distribution: {e}", exc_info=True)
            return []
    
    def get_drawdown_data(self, trades: List[Dict], from_date: str = None, to_date: str = None) -> Dict:
        """
        Calculate drawdown analysis
        
        Args:
            trades: List of trade dictionaries
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            Dictionary with drawdown data
        """
        try:
            filtered_trades = self._filter_trades_by_date(trades, from_date, to_date)
            
            if not filtered_trades:
                return {'max_drawdown': 0, 'current_drawdown': 0, 'equity_curve': []}
            
            # Sort trades by timestamp
            sorted_trades = sorted(filtered_trades, key=lambda t: self._get_timestamp(t))
            
            equity = 0
            peak_equity = 0
            max_drawdown = 0
            equity_curve = []
            
            for trade in sorted_trades:
                pnl = self._get_pnl(trade)
                equity += pnl
                
                if equity > peak_equity:
                    peak_equity = equity
                
                drawdown = peak_equity - equity
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                
                equity_curve.append({
                    'timestamp': self._get_timestamp(t),
                    'equity': round(equity, 2),
                    'drawdown': round(drawdown, 2)
                })
            
            current_drawdown = peak_equity - equity
            
            return {
                'max_drawdown': round(max_drawdown, 2),
                'current_drawdown': round(current_drawdown, 2),
                'peak_equity': round(peak_equity, 2),
                'current_equity': round(equity, 2),
                'equity_curve': equity_curve
            }
            
        except Exception as e:
            logger.error(f"Error calculating drawdown: {e}", exc_info=True)
            return {'max_drawdown': 0, 'current_drawdown': 0, 'equity_curve': []}
    
    def get_risk_metrics(self, trades: List[Dict], from_date: str = None, to_date: str = None) -> Dict:
        """
        Calculate risk metrics
        
        Args:
            trades: List of trade dictionaries
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            Dictionary with risk metrics
        """
        try:
            filtered_trades = self._filter_trades_by_date(trades, from_date, to_date)
            
            if not filtered_trades:
                return self._empty_risk_metrics()
            
            pnls = [self._get_pnl(t) for t in filtered_trades]
            
            # Calculate standard deviation
            mean_pnl = sum(pnls) / len(pnls)
            variance = sum((x - mean_pnl) ** 2 for x in pnls) / len(pnls)
            std_dev = variance ** 0.5
            
            # Sharpe ratio (simplified, assuming risk-free rate = 0)
            sharpe_ratio = mean_pnl / std_dev if std_dev > 0 else 0
            
            # Max consecutive wins/losses
            max_consecutive_wins = 0
            max_consecutive_losses = 0
            current_wins = 0
            current_losses = 0
            
            for trade in filtered_trades:
                pnl = self._get_pnl(trade)
                if pnl > 0:
                    current_wins += 1
                    current_losses = 0
                    max_consecutive_wins = max(max_consecutive_wins, current_wins)
                elif pnl < 0:
                    current_losses += 1
                    current_wins = 0
                    max_consecutive_losses = max(max_consecutive_losses, current_losses)
            
            return {
                'sharpe_ratio': round(sharpe_ratio, 2),
                'std_deviation': round(std_dev, 2),
                'max_consecutive_wins': max_consecutive_wins,
                'max_consecutive_losses': max_consecutive_losses
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}", exc_info=True)
            return self._empty_risk_metrics()
    
    # Helper methods
    
    def _filter_trades_by_date(self, trades: List[Dict], from_date: str = None, to_date: str = None) -> List[Dict]:
        """Filter trades by date range"""
        if not from_date and not to_date:
            return trades
        
        filtered = []
        for trade in trades:
            trade_date = self._get_trade_date(trade)
            
            if from_date and trade_date < from_date:
                continue
            if to_date and trade_date > to_date:
                continue
            
            filtered.append(trade)
        
        return filtered
    
    def _get_pnl(self, trade: Dict) -> float:
        """Extract P&L from trade"""
        return float(trade.get('pnl', 0) or trade.get('profit', 0) or 0)
    
    def _get_trade_date(self, trade: Dict) -> str:
        """Extract date from trade (YYYY-MM-DD)"""
        timestamp = trade.get('timestamp') or trade.get('order_timestamp') or trade.get('exit_time')
        if timestamp:
            if isinstance(timestamp, str):
                return timestamp[:10]  # Extract YYYY-MM-DD
            elif isinstance(timestamp, datetime):
                return timestamp.strftime('%Y-%m-%d')
        return datetime.now().strftime('%Y-%m-%d')
    
    def _get_trade_hour(self, trade: Dict) -> int:
        """Extract hour from trade (0-23)"""
        timestamp = trade.get('timestamp') or trade.get('order_timestamp') or trade.get('exit_time')
        if timestamp:
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    return dt.hour
                except:
                    pass
            elif isinstance(timestamp, datetime):
                return timestamp.hour
        return 0
    
    def _get_timestamp(self, trade: Dict) -> str:
        """Extract timestamp from trade"""
        return trade.get('timestamp') or trade.get('order_timestamp') or trade.get('exit_time') or ''
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'avg_trade': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'profit_factor': 0,
            'gross_profit': 0,
            'gross_loss': 0
        }
    
    def _empty_risk_metrics(self) -> Dict:
        """Return empty risk metrics structure"""
        return {
            'sharpe_ratio': 0,
            'std_deviation': 0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0
        }
