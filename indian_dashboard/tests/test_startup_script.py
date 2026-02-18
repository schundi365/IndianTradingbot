"""
Tests for startup script functionality
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from run_dashboard import DashboardStarter


class TestDashboardStarter(unittest.TestCase):
    """Test cases for DashboardStarter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.starter = DashboardStarter()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_check_python_version(self):
        """Test Python version check"""
        result = self.starter.check_python_version()
        
        # Should pass on Python 3.8+
        if sys.version_info >= (3, 8):
            self.assertTrue(result)
            self.assertEqual(len(self.starter.errors), 0)
        else:
            self.assertFalse(result)
            self.assertGreater(len(self.starter.errors), 0)
    
    def test_check_dependencies(self):
        """Test dependency check"""
        result = self.starter.check_dependencies()
        
        # Should pass if Flask is installed
        try:
            import flask
            self.assertTrue(result)
            self.assertEqual(len(self.starter.errors), 0)
        except ImportError:
            self.assertFalse(result)
            self.assertGreater(len(self.starter.errors), 0)
    
    def test_check_directories(self):
        """Test directory creation"""
        # Override base_dir and parent_dir for testing
        self.starter.base_dir = self.temp_dir
        self.starter.parent_dir = self.temp_dir
        
        result = self.starter.check_directories()
        
        self.assertTrue(result)
        self.assertTrue((self.temp_dir / 'data' / 'cache').exists())
        self.assertTrue((self.temp_dir / 'data' / 'credentials').exists())
        self.assertTrue((self.temp_dir / 'configs').exists())
        self.assertTrue((self.temp_dir / 'logs').exists())
    
    def test_check_env_file_missing(self):
        """Test .env file check when file is missing"""
        # Override base_dir for testing
        self.starter.base_dir = self.temp_dir
        
        result = self.starter.check_env_file()
        
        # Should pass but with warning
        self.assertTrue(result)
        self.assertGreater(len(self.starter.warnings), 0)
    
    def test_check_env_file_exists(self):
        """Test .env file check when file exists"""
        # Override base_dir for testing
        self.starter.base_dir = self.temp_dir
        
        # Create .env file
        env_file = self.temp_dir / '.env'
        env_file.write_text('FLASK_SECRET_KEY=test\n')
        
        result = self.starter.check_env_file()
        
        # Should pass without warning
        self.assertTrue(result)
    
    def test_check_secret_keys_default(self):
        """Test secret key check with default values"""
        with patch.dict(os.environ, {}, clear=True):
            result = self.starter.check_secret_keys()
            
            # Should pass but with warnings
            self.assertTrue(result)
            self.assertGreater(len(self.starter.warnings), 0)
    
    def test_check_secret_keys_configured(self):
        """Test secret key check with proper values"""
        with patch.dict(os.environ, {
            'FLASK_SECRET_KEY': 'secure-key-123',
            'ENCRYPTION_KEY': 'secure-encryption-key'
        }):
            self.starter.warnings = []  # Reset warnings
            result = self.starter.check_secret_keys()
            
            # Should pass without warnings
            self.assertTrue(result)
    
    def test_check_broker_adapters(self):
        """Test broker adapter check"""
        result = self.starter.check_broker_adapters()
        
        # Should always pass (may have warnings)
        self.assertTrue(result)
    
    def test_run_checks_all_pass(self):
        """Test running all checks"""
        # Mock all check methods to return True
        with patch.object(self.starter, 'check_python_version', return_value=True), \
             patch.object(self.starter, 'check_dependencies', return_value=True), \
             patch.object(self.starter, 'check_directories', return_value=True), \
             patch.object(self.starter, 'check_env_file', return_value=True), \
             patch.object(self.starter, 'check_secret_keys', return_value=True), \
             patch.object(self.starter, 'check_broker_adapters', return_value=True):
            
            result = self.starter.run_checks()
            self.assertTrue(result)
    
    def test_run_checks_with_failure(self):
        """Test running checks with a failure"""
        # Mock one check to fail
        with patch.object(self.starter, 'check_python_version', return_value=False), \
             patch.object(self.starter, 'check_dependencies', return_value=True), \
             patch.object(self.starter, 'check_directories', return_value=True), \
             patch.object(self.starter, 'check_env_file', return_value=True), \
             patch.object(self.starter, 'check_secret_keys', return_value=True), \
             patch.object(self.starter, 'check_broker_adapters', return_value=True):
            
            self.starter.errors = ['Python version too old']
            result = self.starter.run_checks()
            self.assertFalse(result)
    
    def test_generate_keys(self):
        """Test key generation"""
        # Should not raise any exceptions
        try:
            with patch('builtins.print'):  # Suppress output
                self.starter.generate_keys()
        except Exception as e:
            self.fail(f"generate_keys raised exception: {e}")


class TestStartupScriptIntegration(unittest.TestCase):
    """Integration tests for startup script"""
    
    def test_import_run_dashboard(self):
        """Test that run_dashboard module can be imported"""
        try:
            import run_dashboard
            self.assertTrue(hasattr(run_dashboard, 'DashboardStarter'))
            self.assertTrue(hasattr(run_dashboard, 'main'))
        except ImportError as e:
            self.fail(f"Failed to import run_dashboard: {e}")
    
    def test_dashboard_starter_instantiation(self):
        """Test that DashboardStarter can be instantiated"""
        try:
            starter = DashboardStarter()
            self.assertIsNotNone(starter)
            self.assertIsInstance(starter.errors, list)
            self.assertIsInstance(starter.warnings, list)
        except Exception as e:
            self.fail(f"Failed to instantiate DashboardStarter: {e}")


if __name__ == '__main__':
    unittest.main()
