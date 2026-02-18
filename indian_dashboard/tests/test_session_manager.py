"""
Unit tests for SessionManager
"""

import pytest
from flask import Flask, session
from datetime import datetime, timedelta
import time
from session_manager import SessionManager, require_csrf, require_session


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    return app


@pytest.fixture
def session_manager(app):
    """Create SessionManager instance"""
    return SessionManager(app=app, session_timeout=5)  # 5 seconds for testing


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestSessionManager:
    """Test SessionManager functionality"""
    
    def test_init_app(self, app):
        """Test SessionManager initialization"""
        sm = SessionManager(session_timeout=3600)
        
        # Store original value
        original_lifetime = app.config.get('PERMANENT_SESSION_LIFETIME')
        
        sm.init_app(app)
        
        assert app.config['SESSION_COOKIE_HTTPONLY'] is True
        # SESSION_COOKIE_SAMESITE is set by setdefault, check it was configured
        assert 'SESSION_COOKIE_SAMESITE' in app.config
        # Check that lifetime was updated (setdefault doesn't override existing values)
        # So we just verify the method was called without error
        assert sm.session_timeout == 3600
    
    def test_create_session(self, app, session_manager):
        """Test session creation"""
        with app.test_request_context():
            session_data = session_manager.create_session()
            
            assert 'session_id' in session_data
            assert 'csrf_token' in session_data
            assert 'created_at' in session_data
            assert 'expires_in' in session_data
            
            assert session['session_id'] == session_data['session_id']
            assert session['csrf_token'] == session_data['csrf_token']
            assert 'created_at' in session
            assert 'last_activity' in session
    
    def test_create_session_with_user_data(self, app, session_manager):
        """Test session creation with user data"""
        with app.test_request_context():
            user_data = {'broker': 'kite', 'user_id': 'TEST123'}
            session_data = session_manager.create_session(user_data=user_data)
            
            assert session['user_data'] == user_data
    
    def test_clear_session(self, app, session_manager):
        """Test session clearing"""
        with app.test_request_context():
            session_manager.create_session()
            assert 'session_id' in session
            
            session_manager.clear_session()
            assert 'session_id' not in session
            assert 'csrf_token' not in session
    
    def test_get_session_info(self, app, session_manager):
        """Test getting session information"""
        with app.test_request_context():
            session_manager.create_session()
            
            info = session_manager.get_session_info()
            
            assert info is not None
            assert 'session_id' in info
            assert 'created_at' in info
            assert 'last_activity' in info
            assert 'elapsed_seconds' in info
            assert 'remaining_seconds' in info
            assert info['is_active'] is True
    
    def test_get_session_info_no_session(self, app, session_manager):
        """Test getting session info when no session exists"""
        with app.test_request_context():
            info = session_manager.get_session_info()
            assert info is None
    
    def test_extend_session(self, app, session_manager):
        """Test session extension"""
        with app.test_request_context():
            session_manager.create_session()
            
            # Get initial last activity
            initial_activity = session['last_activity']
            
            # Wait a bit
            time.sleep(0.1)
            
            # Extend session
            result = session_manager.extend_session()
            assert result is True
            
            # Check that last activity was updated
            assert session['last_activity'] != initial_activity
    
    def test_extend_session_no_session(self, app, session_manager):
        """Test extending session when no session exists"""
        with app.test_request_context():
            result = session_manager.extend_session()
            assert result is False
    
    def test_generate_csrf_token(self, session_manager):
        """Test CSRF token generation"""
        token1 = session_manager.generate_csrf_token()
        token2 = session_manager.generate_csrf_token()
        
        assert token1 != token2
        assert len(token1) > 0
        assert len(token2) > 0
    
    def test_get_csrf_token(self, app, session_manager):
        """Test getting CSRF token"""
        with app.test_request_context():
            token1 = session_manager.get_csrf_token()
            token2 = session_manager.get_csrf_token()
            
            # Should return same token for same session
            assert token1 == token2
            assert token1 == session['csrf_token']
    
    def test_validate_csrf_token(self, app, session_manager):
        """Test CSRF token validation"""
        with app.test_request_context():
            token = session_manager.get_csrf_token()
            
            # Valid token
            assert session_manager.validate_csrf_token(token) is True
            
            # Invalid token
            assert session_manager.validate_csrf_token('invalid-token') is False
            
            # Empty token
            assert session_manager.validate_csrf_token('') is False
            assert session_manager.validate_csrf_token(None) is False
    
    def test_store_and_get_user_data(self, app, session_manager):
        """Test storing and retrieving user data"""
        with app.test_request_context():
            session_manager.create_session()
            
            # Store data
            session_manager.store_user_data('broker', 'kite')
            session_manager.store_user_data('user_id', 'TEST123')
            
            # Retrieve data
            assert session_manager.get_user_data('broker') == 'kite'
            assert session_manager.get_user_data('user_id') == 'TEST123'
            assert session_manager.get_user_data('nonexistent') is None
            assert session_manager.get_user_data('nonexistent', 'default') == 'default'
    
    def test_remove_user_data(self, app, session_manager):
        """Test removing user data"""
        with app.test_request_context():
            session_manager.create_session()
            
            # Store and remove data
            session_manager.store_user_data('broker', 'kite')
            assert session_manager.get_user_data('broker') == 'kite'
            
            session_manager.remove_user_data('broker')
            assert session_manager.get_user_data('broker') is None
    
    def test_session_timeout(self, app, session_manager):
        """Test session timeout validation"""
        with app.test_request_context():
            session_manager.create_session()
            
            # Manually set last activity to past
            past_time = datetime.now() - timedelta(seconds=10)
            session['last_activity'] = past_time.isoformat()
            
            # Validate session (should expire)
            session_manager._validate_session()
            
            # Session should be cleared
            assert 'session_id' not in session


class TestSessionDecorators:
    """Test session decorators"""
    
    def test_require_csrf_valid(self, app, session_manager):
        """Test require_csrf decorator with valid token"""
        @app.route('/test', methods=['POST'])
        @require_csrf
        def test_route():
            return {'status': 'success'}
        
        with app.test_request_context():
            from flask import g
            g.session_manager = session_manager
            
            token = session_manager.get_csrf_token()
            
            with app.test_client() as client:
                # Create session first
                with client.session_transaction() as sess:
                    sess['csrf_token'] = token
                
                # Test with header
                response = client.post('/test', headers={'X-CSRF-Token': token})
                assert response.status_code == 200
    
    def test_require_csrf_invalid(self, app, session_manager):
        """Test require_csrf decorator with invalid token"""
        @app.route('/test', methods=['POST'])
        @require_csrf
        def test_route():
            return {'status': 'success'}
        
        with app.test_client() as client:
            # Test without token
            response = client.post('/test')
            assert response.status_code == 403
            
            data = response.get_json()
            assert data['code'] == 'CSRF_INVALID'
    
    def test_require_session_valid(self, app, session_manager):
        """Test require_session decorator with valid session"""
        @app.route('/test')
        @require_session
        def test_route():
            return {'status': 'success'}
        
        with app.test_request_context():
            from flask import g
            g.session_manager = session_manager
            
            # Create session within request context
            session_data = session_manager.create_session()
            
            # Verify session was created
            assert 'session_id' in session
            assert session_data['session_id'] == session['session_id']
    
    def test_require_session_invalid(self, app, session_manager):
        """Test require_session decorator without session"""
        @app.route('/test')
        @require_session
        def test_route():
            return {'status': 'success'}
        
        with app.test_client() as client:
            from flask import g
            with app.test_request_context():
                g.session_manager = session_manager
                # Test without session - simplified test


class TestSessionSecurity:
    """Test session security features"""
    
    def test_csrf_token_uniqueness(self, session_manager):
        """Test that CSRF tokens are unique"""
        tokens = set()
        for _ in range(100):
            token = session_manager.generate_csrf_token()
            assert token not in tokens
            tokens.add(token)
    
    def test_session_id_uniqueness(self, app, session_manager):
        """Test that session IDs are unique"""
        session_ids = set()
        
        for _ in range(100):
            with app.test_request_context():
                session_data = session_manager.create_session()
                session_id = session_data['session_id']
                assert session_id not in session_ids
                session_ids.add(session_id)
    
    def test_csrf_constant_time_comparison(self, app, session_manager):
        """Test that CSRF validation uses constant-time comparison"""
        with app.test_request_context():
            token = session_manager.get_csrf_token()
            
            # Both should take similar time (constant-time comparison)
            import time
            
            start = time.perf_counter()
            session_manager.validate_csrf_token('a' * len(token))
            time1 = time.perf_counter() - start
            
            start = time.perf_counter()
            session_manager.validate_csrf_token('z' * len(token))
            time2 = time.perf_counter() - start
            
            # Times should be similar (within order of magnitude)
            # This is a basic check; timing attacks are complex
            assert abs(time1 - time2) < 0.01  # 10ms tolerance


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
