"""
Indian Market Web Dashboard
Flask application for multi-broker trading dashboard
"""

from flask import Flask, render_template, request, jsonify, session, g
from flask_cors import CORS
import logging
import os
import sys
from pathlib import Path
from datetime import timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import logging utils
from src.utils.logging_utils import setup_db_logging
from src.managers.database_manager import LogDatabaseManager

# Import config
from config import DASHBOARD_CONFIG, PRESET_CONFIGS

# Import services
from services.broker_manager import BrokerManager
from services.instrument_service import InstrumentService
from services.bot_controller import BotController
from services.credential_manager import CredentialManager
from services.analytics_service import AnalyticsService
from services.chart_data_service import ChartDataService
from services.backtest_service import BacktestService

# Import session manager
from session_manager import SessionManager

# Import API blueprint initializers
from api.broker import init_broker_api
from api.instruments import init_instruments_api
from api.config import init_config_api
from api.bot import init_bot_api
from api.session import init_session_api
from api.analytics import init_analytics_api
from api.charts import init_charts_api
from api.logs import init_logs_api
from api.backtest import init_backtest_api

# Import error handler
from dashboard_error_handler import init_error_handlers, log_request, log_response

# Import rate limiter
from rate_limiter import init_rate_limiter

# Create Flask app
app = Flask(__name__)
app.secret_key = DASHBOARD_CONFIG.get('secret_key', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=DASHBOARD_CONFIG.get('session_timeout', 3600))

# Disable template caching for development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.jinja_env.auto_reload = True

# Enable CORS for development
CORS(app)

# Setup logging
log_level = getattr(logging, DASHBOARD_CONFIG.get('log_level', 'INFO'))
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DASHBOARD_CONFIG['log_dir'] / DASHBOARD_CONFIG['log_file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup database logging
db_manager = LogDatabaseManager(str(DASHBOARD_CONFIG['log_dir'] / "logs.db"))
setup_db_logging(str(DASHBOARD_CONFIG['log_dir'] / "logs.db"))

# Initialize session manager
session_manager = SessionManager(
    app=app,
    session_timeout=DASHBOARD_CONFIG.get('session_timeout', 3600)
)

# Initialize services
broker_manager = BrokerManager()
instrument_service = InstrumentService(
    DASHBOARD_CONFIG['cache_dir'],
    DASHBOARD_CONFIG['instrument_cache_ttl']
)
bot_controller = BotController()
credential_manager = CredentialManager(
    DASHBOARD_CONFIG['credentials_dir'],
    DASHBOARD_CONFIG.get('encryption_key')
)
analytics_service = AnalyticsService()
chart_data_service = ChartDataService(broker_manager)

# Initialize backtest DB and service
try:
    from src.managers.backtest_db_manager import BacktestDatabaseManager
    backtest_db = BacktestDatabaseManager(str(DASHBOARD_CONFIG['log_dir'].parent / 'data' / 'backtests.db'))
    backtest_service = BacktestService(db_manager=backtest_db, broker_manager=broker_manager)
except Exception as _bt_err:
    logger.warning(f'Backtest service init failed: {_bt_err}')
    backtest_service = None

# Store services in app config for access in routes
app.config['DB_MANAGER'] = db_manager
app.config['BROKER_MANAGER'] = broker_manager
app.config['INSTRUMENT_SERVICE'] = instrument_service
app.config['BOT_CONTROLLER'] = bot_controller
app.config['CREDENTIAL_MANAGER'] = credential_manager
app.config['SESSION_MANAGER'] = session_manager
app.config['ANALYTICS_SERVICE'] = analytics_service
app.config['CHART_DATA_SERVICE'] = chart_data_service

# Initialize and register API blueprints
broker_bp = init_broker_api(broker_manager, credential_manager)
instruments_bp = init_instruments_api(broker_manager, instrument_service)
config_bp = init_config_api(DASHBOARD_CONFIG['config_dir'], PRESET_CONFIGS)
bot_bp = init_bot_api(bot_controller, broker_manager)
session_bp = init_session_api(session_manager)
analytics_bp = init_analytics_api(bot_controller, analytics_service)
charts_bp = init_charts_api(bot_controller, chart_data_service)
logs_bp = init_logs_api(db_manager)
if backtest_service:
    backtest_api_bp = init_backtest_api(backtest_service)

app.register_blueprint(broker_bp)
app.register_blueprint(instruments_bp)
app.register_blueprint(config_bp)
app.register_blueprint(bot_bp)
app.register_blueprint(session_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(charts_bp)
app.register_blueprint(logs_bp)
if backtest_service:
    app.register_blueprint(backtest_api_bp)

# Initialize global error handlers
init_error_handlers(app)

# Initialize rate limiter
limiter = init_rate_limiter(app)
app.config['LIMITER'] = limiter

# Apply rate limits to API endpoints
from api.broker import apply_rate_limits as apply_broker_rate_limits
from api.instruments import apply_rate_limits as apply_instruments_rate_limits
from api.config import apply_rate_limits as apply_config_rate_limits
from api.bot import apply_rate_limits as apply_bot_rate_limits
from api.session import apply_rate_limits as apply_session_rate_limits
from api.analytics import apply_rate_limits as apply_analytics_rate_limits
from api.charts import apply_rate_limits as apply_charts_rate_limits
from api.logs import apply_rate_limits as apply_logs_rate_limits

apply_broker_rate_limits(limiter)
apply_instruments_rate_limits(limiter)
apply_config_rate_limits(limiter)
apply_bot_rate_limits(limiter)
apply_session_rate_limits(limiter, session_bp)
apply_analytics_rate_limits(limiter)
apply_charts_rate_limits(limiter)
apply_logs_rate_limits(limiter)

# Add request/response logging
@app.before_request
def before_request():
    """Log request before processing and make session manager available"""
    # Make session manager available in request context
    g.session_manager = session_manager
    
    # Log request
    log_request()

@app.after_request
def after_request(response):
    """Log response after processing and add cache control headers"""
    # Add cache control headers for static files in development
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return log_response(response)


@app.route('/')
def index():
    """Main dashboard page"""
    # Create session if it doesn't exist
    if 'session_id' not in session:
        session_manager.create_session()
    
    return render_template('dashboard.html')


@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    from flask import Response
    return Response(status=204)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Indian Market Web Dashboard')
    parser.add_argument('--host', default=DASHBOARD_CONFIG['host'], help='Host to bind to')
    parser.add_argument('--port', type=int, default=DASHBOARD_CONFIG['port'], help='Port to bind to')
    parser.add_argument('--debug', action='store_true', default=DASHBOARD_CONFIG['debug'], help='Enable debug mode')
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("Starting Indian Market Web Dashboard")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Debug: {args.debug}")
    logger.info("=" * 80)
    
    app.run(host=args.host, port=args.port, debug=args.debug)
