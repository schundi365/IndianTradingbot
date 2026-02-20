"""
Timezone utilities for handling broker-specific timezones
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger(__name__)

# Broker timezone mappings
BROKER_TIMEZONES = {
    'kite': 'Asia/Kolkata',  # IST (UTC+5:30)
    'alice_blue': 'Asia/Kolkata',  # IST
    'angel_one': 'Asia/Kolkata',  # IST
    'upstox': 'Asia/Kolkata',  # IST
    'paper': 'Asia/Kolkata',  # Default to IST for paper trading
}

# Market hours for each broker (in broker's local timezone)
MARKET_HOURS = {
    'kite': {
        'open': time(9, 15),  # 9:15 AM IST
        'close': time(15, 30),  # 3:30 PM IST
        'pre_open_start': time(9, 0),  # 9:00 AM IST
        'pre_open_end': time(9, 15),  # 9:15 AM IST
    },
    'alice_blue': {
        'open': time(9, 15),
        'close': time(15, 30),
    },
    'angel_one': {
        'open': time(9, 15),
        'close': time(15, 30),
    },
    'upstox': {
        'open': time(9, 15),
        'close': time(15, 30),
    },
    'paper': {
        'open': time(9, 15),
        'close': time(15, 30),
    },
}


def get_broker_timezone(broker: str) -> ZoneInfo:
    """
    Get timezone for a specific broker
    
    Args:
        broker: Broker ID (e.g., 'kite', 'alice_blue')
        
    Returns:
        ZoneInfo object for the broker's timezone
    """
    tz_name = BROKER_TIMEZONES.get(broker, 'Asia/Kolkata')
    return ZoneInfo(tz_name)


def get_broker_time(broker: str, dt: datetime = None) -> datetime:
    """
    Get current time in broker's timezone
    
    Args:
        broker: Broker ID
        dt: Optional datetime to convert (defaults to now)
        
    Returns:
        datetime in broker's timezone
    """
    if dt is None:
        dt = datetime.now(ZoneInfo('UTC'))
    
    broker_tz = get_broker_timezone(broker)
    return dt.astimezone(broker_tz)


def is_market_open(broker: str, dt: datetime = None) -> bool:
    """
    Check if market is currently open for the broker
    
    Args:
        broker: Broker ID
        dt: Optional datetime to check (defaults to now)
        
    Returns:
        True if market is open, False otherwise
    """
    broker_time = get_broker_time(broker, dt)
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    if broker_time.weekday() >= 5:  # Saturday or Sunday
        return False
    
    market_hours = MARKET_HOURS.get(broker, MARKET_HOURS['kite'])
    current_time = broker_time.time()
    
    return market_hours['open'] <= current_time <= market_hours['close']


def get_market_open_time(broker: str, dt: datetime = None) -> datetime:
    """
    Get market open time for the broker on a given date
    
    Args:
        broker: Broker ID
        dt: Optional date (defaults to today)
        
    Returns:
        datetime of market open in broker's timezone
    """
    broker_time = get_broker_time(broker, dt)
    market_hours = MARKET_HOURS.get(broker, MARKET_HOURS['kite'])
    
    return broker_time.replace(
        hour=market_hours['open'].hour,
        minute=market_hours['open'].minute,
        second=0,
        microsecond=0
    )


def get_market_close_time(broker: str, dt: datetime = None) -> datetime:
    """
    Get market close time for the broker on a given date
    
    Args:
        broker: Broker ID
        dt: Optional date (defaults to today)
        
    Returns:
        datetime of market close in broker's timezone
    """
    broker_time = get_broker_time(broker, dt)
    market_hours = MARKET_HOURS.get(broker, MARKET_HOURS['kite'])
    
    return broker_time.replace(
        hour=market_hours['close'].hour,
        minute=market_hours['close'].minute,
        second=0,
        microsecond=0
    )


def parse_trading_hours(trading_hours: dict, broker: str) -> tuple:
    """
    Parse trading hours configuration and convert to broker timezone
    
    Args:
        trading_hours: Dict with 'start' and 'end' times (HH:MM format)
        broker: Broker ID
        
    Returns:
        Tuple of (start_time, end_time) as time objects
    """
    try:
        start_str = trading_hours.get('start', '09:15')
        end_str = trading_hours.get('end', '15:30')
        
        start_hour, start_min = map(int, start_str.split(':'))
        end_hour, end_min = map(int, end_str.split(':'))
        
        start_time = time(start_hour, start_min)
        end_time = time(end_hour, end_min)
        
        return start_time, end_time
        
    except Exception as e:
        logger.error(f"Error parsing trading hours: {e}")
        # Return default market hours
        market_hours = MARKET_HOURS.get(broker, MARKET_HOURS['kite'])
        return market_hours['open'], market_hours['close']


def format_broker_time(dt: datetime, broker: str, fmt: str = '%Y-%m-%d %H:%M:%S %Z') -> str:
    """
    Format datetime in broker's timezone
    
    Args:
        dt: datetime to format
        broker: Broker ID
        fmt: Format string
        
    Returns:
        Formatted datetime string
    """
    broker_time = get_broker_time(broker, dt)
    return broker_time.strftime(fmt)


def convert_to_utc(dt: datetime, broker: str) -> datetime:
    """
    Convert broker local time to UTC
    
    Args:
        dt: datetime in broker's timezone (naive or aware)
        broker: Broker ID
        
    Returns:
        datetime in UTC
    """
    broker_tz = get_broker_timezone(broker)
    
    # If datetime is naive, assume it's in broker's timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=broker_tz)
    
    return dt.astimezone(ZoneInfo('UTC'))


def convert_from_utc(dt: datetime, broker: str) -> datetime:
    """
    Convert UTC time to broker's local time
    
    Args:
        dt: datetime in UTC
        broker: Broker ID
        
    Returns:
        datetime in broker's timezone
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo('UTC'))
    
    broker_tz = get_broker_timezone(broker)
    return dt.astimezone(broker_tz)


def get_next_market_open(broker: str, dt: datetime = None) -> datetime:
    """
    Get the next market open time
    
    Args:
        broker: Broker ID
        dt: Optional datetime to start from (defaults to now)
        
    Returns:
        datetime of next market open in broker's timezone
    """
    from datetime import timedelta
    
    broker_time = get_broker_time(broker, dt)
    market_hours = MARKET_HOURS.get(broker, MARKET_HOURS['kite'])
    
    # Start with today's market open
    next_open = broker_time.replace(
        hour=market_hours['open'].hour,
        minute=market_hours['open'].minute,
        second=0,
        microsecond=0
    )
    
    # If market already opened today, move to next day
    if broker_time.time() >= market_hours['open']:
        next_open += timedelta(days=1)
    
    # Skip weekends
    while next_open.weekday() >= 5:  # Saturday or Sunday
        next_open += timedelta(days=1)
    
    return next_open


def get_timezone_info(broker: str) -> dict:
    """
    Get timezone information for a broker
    
    Args:
        broker: Broker ID
        
    Returns:
        Dict with timezone info
    """
    broker_tz = get_broker_timezone(broker)
    broker_time = get_broker_time(broker)
    market_hours = MARKET_HOURS.get(broker, MARKET_HOURS['kite'])
    
    return {
        'timezone': str(broker_tz),
        'current_time': broker_time.isoformat(),
        'utc_offset': broker_time.strftime('%z'),
        'market_open': market_hours['open'].strftime('%H:%M'),
        'market_close': market_hours['close'].strftime('%H:%M'),
        'is_market_open': is_market_open(broker),
    }
