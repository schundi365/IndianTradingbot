"""
Mock MetaTrader5 module for macOS/Linux builds
This allows PyInstaller to build the executable on non-Windows platforms
The actual MT5 functionality will work when run on Windows or via Wine
"""

# Mock constants
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 16385
TIMEFRAME_H4 = 16388
TIMEFRAME_D1 = 16408

ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1
ORDER_TYPE_BUY_LIMIT = 2
ORDER_TYPE_SELL_LIMIT = 3
ORDER_TYPE_BUY_STOP = 4
ORDER_TYPE_SELL_STOP = 5

TRADE_ACTION_DEAL = 1
TRADE_ACTION_PENDING = 5
TRADE_ACTION_SLTP = 2
TRADE_ACTION_MODIFY = 3
TRADE_ACTION_REMOVE = 4
TRADE_ACTION_CLOSE_BY = 10

ORDER_FILLING_FOK = 0
ORDER_FILLING_IOC = 1
ORDER_FILLING_RETURN = 2

ORDER_TIME_GTC = 0
ORDER_TIME_DAY = 1
ORDER_TIME_SPECIFIED = 2
ORDER_TIME_SPECIFIED_DAY = 3

DEAL_ENTRY_IN = 0
DEAL_ENTRY_OUT = 1
DEAL_ENTRY_INOUT = 2
DEAL_ENTRY_OUT_BY = 3

TRADE_RETCODE_DONE = 10009
TRADE_RETCODE_REQUOTE = 10004
TRADE_RETCODE_REJECT = 10006
TRADE_RETCODE_CANCEL = 10007
TRADE_RETCODE_PLACED = 10008
TRADE_RETCODE_TIMEOUT = 10012
TRADE_RETCODE_INVALID = 10013
TRADE_RETCODE_INVALID_VOLUME = 10014
TRADE_RETCODE_INVALID_PRICE = 10015
TRADE_RETCODE_INVALID_STOPS = 10016
TRADE_RETCODE_TRADE_DISABLED = 10017
TRADE_RETCODE_MARKET_CLOSED = 10018
TRADE_RETCODE_NO_MONEY = 10019
TRADE_RETCODE_PRICE_CHANGED = 10020
TRADE_RETCODE_PRICE_OFF = 10021
TRADE_RETCODE_INVALID_EXPIRATION = 10022
TRADE_RETCODE_ORDER_CHANGED = 10023
TRADE_RETCODE_TOO_MANY_REQUESTS = 10024
TRADE_RETCODE_NO_CHANGES = 10025
TRADE_RETCODE_SERVER_DISABLES_AT = 10026
TRADE_RETCODE_CLIENT_DISABLES_AT = 10027
TRADE_RETCODE_LOCKED = 10028
TRADE_RETCODE_FROZEN = 10029
TRADE_RETCODE_INVALID_FILL = 10030
TRADE_RETCODE_CONNECTION = 10031
TRADE_RETCODE_ONLY_REAL = 10032
TRADE_RETCODE_LIMIT_ORDERS = 10033
TRADE_RETCODE_LIMIT_VOLUME = 10034
TRADE_RETCODE_INVALID_ORDER = 10035
TRADE_RETCODE_POSITION_CLOSED = 10036

# Mock classes
class AccountInfo:
    def __init__(self):
        self.balance = 0
        self.equity = 0
        self.profit = 0
        self.margin = 0
        self.margin_free = 0
        self.margin_level = 0
        self.currency = "USD"
        self.leverage = 100
        self.login = 0
        self.name = "Mock Account"
        self.server = "Mock Server"

class SymbolInfo:
    def __init__(self):
        self.visible = True
        self.digits = 5
        self.point = 0.00001
        self.trade_tick_value = 1.0
        self.trade_contract_size = 100000
        self.volume_min = 0.01
        self.volume_max = 100.0
        self.volume_step = 0.01
        self.filling_mode = 3

class TickInfo:
    def __init__(self):
        self.ask = 0.0
        self.bid = 0.0
        self.last = 0.0
        self.time = 0

class OrderSendResult:
    def __init__(self):
        self.retcode = TRADE_RETCODE_DONE
        self.order = 0
        self.volume = 0.0
        self.price = 0.0
        self.comment = ""

# Mock functions
def initialize(*args, **kwargs):
    """Mock MT5 initialization"""
    return False  # Return False to indicate MT5 not available

def shutdown():
    """Mock MT5 shutdown"""
    pass

def version():
    """Mock MT5 version"""
    return (5, 0, 47)

def last_error():
    """Mock last error"""
    return (0, "Mock MT5 - Not available on this platform")

def account_info():
    """Mock account info"""
    return None

def symbol_info(symbol):
    """Mock symbol info"""
    return None

def symbol_info_tick(symbol):
    """Mock tick info"""
    return None

def symbol_select(symbol, enable):
    """Mock symbol select"""
    return False

def copy_rates_from_pos(symbol, timeframe, start_pos, count):
    """Mock copy rates"""
    return None

def positions_get(*args, **kwargs):
    """Mock positions get"""
    return None

def orders_get(*args, **kwargs):
    """Mock orders get"""
    return None

def history_deals_get(*args, **kwargs):
    """Mock history deals get"""
    return None

def history_orders_get(*args, **kwargs):
    """Mock history orders get"""
    return None

def order_send(request):
    """Mock order send"""
    result = OrderSendResult()
    result.retcode = TRADE_RETCODE_INVALID
    result.comment = "Mock MT5 - Not available on this platform"
    return result

def order_check(request):
    """Mock order check"""
    result = OrderSendResult()
    result.retcode = TRADE_RETCODE_INVALID
    return result

def order_calc_margin(action, symbol, volume, price):
    """Mock margin calculation"""
    return None

def order_calc_profit(action, symbol, volume, price_open, price_close):
    """Mock profit calculation"""
    return None

# Export all
__all__ = [
    'initialize', 'shutdown', 'version', 'last_error',
    'account_info', 'symbol_info', 'symbol_info_tick', 'symbol_select',
    'copy_rates_from_pos', 'positions_get', 'orders_get',
    'history_deals_get', 'history_orders_get',
    'order_send', 'order_check', 'order_calc_margin', 'order_calc_profit',
    'AccountInfo', 'SymbolInfo', 'TickInfo', 'OrderSendResult',
    'TIMEFRAME_M1', 'TIMEFRAME_M5', 'TIMEFRAME_M15', 'TIMEFRAME_M30',
    'TIMEFRAME_H1', 'TIMEFRAME_H4', 'TIMEFRAME_D1',
    'ORDER_TYPE_BUY', 'ORDER_TYPE_SELL', 'ORDER_TYPE_BUY_LIMIT',
    'ORDER_TYPE_SELL_LIMIT', 'ORDER_TYPE_BUY_STOP', 'ORDER_TYPE_SELL_STOP',
    'TRADE_ACTION_DEAL', 'TRADE_ACTION_PENDING', 'TRADE_ACTION_SLTP',
    'TRADE_ACTION_MODIFY', 'TRADE_ACTION_REMOVE', 'TRADE_ACTION_CLOSE_BY',
    'ORDER_FILLING_FOK', 'ORDER_FILLING_IOC', 'ORDER_FILLING_RETURN',
    'ORDER_TIME_GTC', 'ORDER_TIME_DAY', 'ORDER_TIME_SPECIFIED',
    'ORDER_TIME_SPECIFIED_DAY',
    'DEAL_ENTRY_IN', 'DEAL_ENTRY_OUT', 'DEAL_ENTRY_INOUT', 'DEAL_ENTRY_OUT_BY',
    'TRADE_RETCODE_DONE', 'TRADE_RETCODE_REQUOTE', 'TRADE_RETCODE_REJECT',
    'TRADE_RETCODE_CANCEL', 'TRADE_RETCODE_PLACED', 'TRADE_RETCODE_TIMEOUT',
    'TRADE_RETCODE_INVALID', 'TRADE_RETCODE_INVALID_VOLUME',
    'TRADE_RETCODE_INVALID_PRICE', 'TRADE_RETCODE_INVALID_STOPS',
    'TRADE_RETCODE_TRADE_DISABLED', 'TRADE_RETCODE_MARKET_CLOSED',
    'TRADE_RETCODE_NO_MONEY', 'TRADE_RETCODE_PRICE_CHANGED',
    'TRADE_RETCODE_PRICE_OFF', 'TRADE_RETCODE_INVALID_EXPIRATION',
    'TRADE_RETCODE_ORDER_CHANGED', 'TRADE_RETCODE_TOO_MANY_REQUESTS',
    'TRADE_RETCODE_NO_CHANGES', 'TRADE_RETCODE_SERVER_DISABLES_AT',
    'TRADE_RETCODE_CLIENT_DISABLES_AT', 'TRADE_RETCODE_LOCKED',
    'TRADE_RETCODE_FROZEN', 'TRADE_RETCODE_INVALID_FILL',
    'TRADE_RETCODE_CONNECTION', 'TRADE_RETCODE_ONLY_REAL',
    'TRADE_RETCODE_LIMIT_ORDERS', 'TRADE_RETCODE_LIMIT_VOLUME',
    'TRADE_RETCODE_INVALID_ORDER', 'TRADE_RETCODE_POSITION_CLOSED',
]
