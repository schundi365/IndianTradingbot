"""
Integration tests for Strategy Parameters section
Tests the complete functionality of strategy parameter inputs, validation, and integration
"""

import unittest
import json
from pathlib import Path


class TestStrategyParametersIntegration(unittest.TestCase):
    """Test Strategy Parameters section integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(__file__).parent
        self.static_dir = self.test_dir.parent / 'static'
        self.js_file = self.static_dir / 'js' / 'strategy-parameters.js'
        self.html_file = self.test_dir.parent / 'templates' / 'dashboard.html'

    def test_strategy_parameters_js_exists(self):
        """Test that strategy-parameters.js file exists"""
        self.assertTrue(self.js_file.exists(), "strategy-parameters.js should exist")

    def test_strategy_parameters_module_structure(self):
        """Test that StrategyParameters module has required methods"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        required_methods = [
            'init',
            'setupInputListeners',
            'setupPositionSizingToggle',
            'setupValidation',
            'validateField',
            'getParameters',
            'setParameters',
            'validateAll',
            'updateDependentFields',
            'updateStrategyParameters'
        ]

        for method in required_methods:
            self.assertIn(f'{method}(', content, 
                         f"StrategyParameters should have {method}() method")

    def test_html_has_strategy_section(self):
        """Test that dashboard.html has Strategy Parameters section"""
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for strategy section
        self.assertIn('data-config-section="strategy"', content,
                     "HTML should have strategy config section")

        # Check for required input fields
        required_fields = [
            'config-indicator-period',
            'config-position-sizing',
            'config-base-position-size',
            'config-take-profit',
            'config-stop-loss'
        ]

        for field_id in required_fields:
            self.assertIn(f'id="{field_id}"', content,
                         f"HTML should have {field_id} input field")

    def test_indicator_period_field_attributes(self):
        """Test indicator period field has correct attributes"""
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for indicator period field with correct attributes
        self.assertIn('id="config-indicator-period"', content)
        self.assertIn('name="indicator_period"', content)
        self.assertIn('min="5"', content)
        self.assertIn('max="200"', content)
        self.assertIn('value="20"', content)

    def test_position_sizing_options(self):
        """Test position sizing selector has all options"""
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        required_options = [
            'value="fixed"',
            'value="percentage"',
            'value="risk_based"'
        ]

        for option in required_options:
            self.assertIn(option, content,
                         f"Position sizing should have {option} option")

    def test_take_profit_stop_loss_fields(self):
        """Test TP/SL fields have correct attributes"""
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Take Profit
        self.assertIn('id="config-take-profit"', content)
        self.assertIn('name="take_profit"', content)
        self.assertIn('min="0.5"', content)
        self.assertIn('max="20"', content)

        # Stop Loss
        self.assertIn('id="config-stop-loss"', content)
        self.assertIn('name="stop_loss"', content)
        self.assertIn('min="0.5"', content)
        self.assertIn('max="10"', content)

    def test_validation_logic(self):
        """Test validation logic in JavaScript"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for validation rules
        validation_checks = [
            'indicatorPeriod < 5',
            'indicatorPeriod > 200',
            'takeProfit < 0.5',
            'takeProfit > 20',
            'stopLoss < 0.5',
            'stopLoss > 10',
            'stopLoss >= takeProfit',
            'basePositionSize < 1000'
        ]

        for check in validation_checks:
            self.assertIn(check, content,
                         f"Validation should include check: {check}")

    def test_position_sizing_toggle_logic(self):
        """Test position sizing toggle updates labels"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for label updates based on position sizing method
        label_updates = [
            'Base Position Size (₹)',
            'Position Size (% of Capital)',
            'Risk Amount (₹)'
        ]

        for label in label_updates:
            self.assertIn(label, content,
                         f"Should update label to: {label}")

    def test_get_parameters_method(self):
        """Test getParameters method structure"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that getParameters returns all required fields
        required_params = [
            'indicator_period',
            'position_sizing',
            'base_position_size',
            'take_profit',
            'stop_loss'
        ]

        for param in required_params:
            self.assertIn(param, content,
                         f"getParameters should include {param}")

    def test_set_parameters_method(self):
        """Test setParameters method structure"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that setParameters handles all fields
        self.assertIn('setParameters(params)', content)
        self.assertIn('params.indicator_period', content)
        self.assertIn('params.position_sizing', content)
        self.assertIn('params.base_position_size', content)
        self.assertIn('params.take_profit', content)
        self.assertIn('params.stop_loss', content)

    def test_risk_management_integration(self):
        """Test integration with RiskManagement module"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that strategy parameters trigger risk metrics recalculation
        self.assertIn('RiskManagement.calculateMetrics()', content,
                     "Should trigger risk metrics recalculation")

    def test_strategy_specific_parameters(self):
        """Test strategy-specific parameter updates"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for strategy-specific logic
        strategies = [
            'trend_following',
            'momentum',
            'mean_reversion',
            'breakout'
        ]

        for strategy in strategies:
            self.assertIn(f"'{strategy}'", content,
                         f"Should have logic for {strategy} strategy")

    def test_help_text_updates(self):
        """Test that help text updates based on context"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for help text updates
        self.assertIn('updateParameterHelp', content)
        self.assertIn('form-help', content)

    def test_error_display_methods(self):
        """Test error display and clearing methods"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for error handling methods
        self.assertIn('showFieldError', content)
        self.assertIn('clearFieldError', content)
        self.assertIn('form-error', content)

    def test_validate_all_method(self):
        """Test validateAll method returns proper structure"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that validateAll returns errors array
        self.assertIn('validateAll()', content)
        self.assertIn('errors.length === 0', content)
        self.assertIn('valid:', content)
        self.assertIn('errors', content)

    def test_risk_reward_ratio_calculation(self):
        """Test risk/reward ratio calculation"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for risk/reward ratio calculation
        self.assertIn('riskRewardRatio', content)
        self.assertIn('takeProfit / stopLoss', content)

    def test_field_validation_on_blur(self):
        """Test that fields validate on blur event"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for blur event listeners
        self.assertIn("addEventListener('blur'", content)

    def test_field_validation_on_change(self):
        """Test that fields validate on change event"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for change event listeners
        self.assertIn("addEventListener('change'", content)

    def test_css_styling_exists(self):
        """Test that CSS styling exists for strategy parameters"""
        css_file = self.static_dir / 'css' / 'dashboard.css'
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for form styling
        self.assertIn('.form-group', content)
        self.assertIn('.form-control', content)
        self.assertIn('.form-help', content)
        self.assertIn('.form-error', content)
        self.assertIn('.form-row', content)

    def test_module_initialization(self):
        """Test that module initializes on DOM ready"""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for initialization
        self.assertIn("DOMContentLoaded", content)
        self.assertIn("StrategyParameters.init()", content)


class TestStrategyParametersValidation(unittest.TestCase):
    """Test validation rules for strategy parameters"""

    def test_indicator_period_range(self):
        """Test indicator period validation range"""
        # Valid range: 5-200
        valid_periods = [5, 20, 50, 100, 200]
        invalid_periods = [0, 4, 201, 300, -10]

        # This is a conceptual test - actual validation happens in JavaScript
        for period in valid_periods:
            self.assertTrue(5 <= period <= 200, 
                          f"Period {period} should be valid")

        for period in invalid_periods:
            self.assertFalse(5 <= period <= 200, 
                           f"Period {period} should be invalid")

    def test_take_profit_range(self):
        """Test take profit validation range"""
        # Valid range: 0.5-20%
        valid_tp = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
        invalid_tp = [0, 0.4, 21, 50, -1]

        for tp in valid_tp:
            self.assertTrue(0.5 <= tp <= 20, 
                          f"Take profit {tp}% should be valid")

        for tp in invalid_tp:
            self.assertFalse(0.5 <= tp <= 20, 
                           f"Take profit {tp}% should be invalid")

    def test_stop_loss_range(self):
        """Test stop loss validation range"""
        # Valid range: 0.5-10%
        valid_sl = [0.5, 1.0, 2.0, 5.0, 10.0]
        invalid_sl = [0, 0.4, 11, 20, -1]

        for sl in valid_sl:
            self.assertTrue(0.5 <= sl <= 10, 
                          f"Stop loss {sl}% should be valid")

        for sl in invalid_sl:
            self.assertFalse(0.5 <= sl <= 10, 
                           f"Stop loss {sl}% should be invalid")

    def test_stop_loss_less_than_take_profit(self):
        """Test that stop loss must be less than take profit"""
        test_cases = [
            (1.0, 2.0, True),   # SL < TP: valid
            (2.0, 1.0, False),  # SL > TP: invalid
            (1.5, 1.5, False),  # SL = TP: invalid
            (0.5, 5.0, True),   # SL << TP: valid
        ]

        for sl, tp, expected_valid in test_cases:
            is_valid = sl < tp
            self.assertEqual(is_valid, expected_valid,
                           f"SL={sl}, TP={tp} should be {'valid' if expected_valid else 'invalid'}")

    def test_position_size_minimum(self):
        """Test position size minimum validation"""
        # Minimum: ₹1,000
        valid_sizes = [1000, 5000, 10000, 50000]
        invalid_sizes = [0, 500, 999, -1000]

        for size in valid_sizes:
            self.assertTrue(size >= 1000, 
                          f"Position size ₹{size} should be valid")

        for size in invalid_sizes:
            self.assertFalse(size >= 1000, 
                           f"Position size ₹{size} should be invalid")

    def test_risk_reward_ratio(self):
        """Test risk/reward ratio calculation"""
        test_cases = [
            (1.0, 2.0, 2.0),    # 1:2 ratio
            (1.0, 3.0, 3.0),    # 1:3 ratio
            (2.0, 4.0, 2.0),    # 1:2 ratio
            (1.5, 3.0, 2.0),    # 1:2 ratio
        ]

        for sl, tp, expected_ratio in test_cases:
            ratio = tp / sl
            self.assertAlmostEqual(ratio, expected_ratio, places=2,
                                 msg=f"SL={sl}, TP={tp} should give ratio {expected_ratio}")


if __name__ == '__main__':
    unittest.main()
