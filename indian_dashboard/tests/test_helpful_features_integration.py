"""
Integration tests for helpful features
Tests tooltips, contextual help, quick start guide, and example values
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_helpful_features_files_exist():
    """Test that helpful features files exist"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Check JavaScript file
    js_file = os.path.join(base_dir, 'static', 'js', 'helpful-features.js')
    assert os.path.exists(js_file), f"JavaScript file not found: {js_file}"
    
    # Check CSS file
    css_file = os.path.join(base_dir, 'static', 'css', 'helpful-features.css')
    assert os.path.exists(css_file), f"CSS file not found: {css_file}"
    
    print("✓ All helpful features files exist")


def test_helpful_features_js_content():
    """Test that JavaScript file contains required functionality"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    js_file = os.path.join(base_dir, 'static', 'js', 'helpful-features.js')
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for main object
    assert 'const HelpfulFeatures' in content, "HelpfulFeatures object not found"
    
    # Check for parameter help data
    assert 'parameterHelp:' in content, "Parameter help data not found"
    
    # Check for quick start steps
    assert 'quickStartSteps:' in content, "Quick start steps not found"
    
    # Check for key methods
    required_methods = [
        'addTooltipsToParameters',
        'addExampleValues',
        'createQuickStartGuide',
        'addContextualHelp',
        'showQuickStartGuide',
        'closeQuickStartGuide'
    ]
    
    for method in required_methods:
        assert method in content, f"Method {method} not found in JavaScript"
    
    # Check for parameter help entries
    required_params = [
        'timeframe',
        'strategy',
        'risk_per_trade',
        'max_positions',
        'take_profit',
        'stop_loss'
    ]
    
    for param in required_params:
        assert f"'{param}'" in content, f"Parameter help for {param} not found"
    
    print("✓ JavaScript file contains all required functionality")


def test_helpful_features_css_content():
    """Test that CSS file contains required styles"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    css_file = os.path.join(base_dir, 'static', 'css', 'helpful-features.css')
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for tooltip styles
    assert '.tooltip-wrapper' in content, "Tooltip wrapper styles not found"
    assert '.tooltip-icon' in content, "Tooltip icon styles not found"
    assert '.tooltip-content' in content, "Tooltip content styles not found"
    
    # Check for quick start guide styles
    assert '.quick-start-overlay' in content, "Quick start overlay styles not found"
    assert '.quick-start-modal' in content, "Quick start modal styles not found"
    assert '.quick-start-step' in content, "Quick start step styles not found"
    
    # Check for contextual help styles
    assert '.contextual-help-panel' in content, "Contextual help panel styles not found"
    assert '.help-panel-header' in content, "Help panel header styles not found"
    assert '.help-panel-content' in content, "Help panel content styles not found"
    
    # Check for tab help banner styles
    assert '.tab-help-panel' in content, "Tab help panel styles not found"
    assert '.help-banner' in content, "Help banner styles not found"
    
    # Check for parameter help modal styles
    assert '.parameter-help-modal' in content, "Parameter help modal styles not found"
    
    # Check for animations
    assert '@keyframes fadeIn' in content, "fadeIn animation not found"
    assert '@keyframes slideUp' in content, "slideUp animation not found"
    
    # Check for responsive design
    assert '@media (max-width: 768px)' in content, "Responsive styles not found"
    
    print("✓ CSS file contains all required styles")


def test_dashboard_includes_helpful_features():
    """Test that dashboard.html includes helpful features files"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    html_file = os.path.join(base_dir, 'templates', 'dashboard.html')
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for CSS include
    assert 'helpful-features.css' in content, "Helpful features CSS not included in dashboard"
    
    # Check for JS include
    assert 'helpful-features.js' in content, "Helpful features JS not included in dashboard"
    
    print("✓ Dashboard includes helpful features files")


def test_parameter_help_coverage():
    """Test that parameter help covers all important parameters"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    js_file = os.path.join(base_dir, 'static', 'js', 'helpful-features.js')
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Important parameters that should have help
    important_params = [
        'timeframe',
        'strategy',
        'trading_start',
        'trading_end',
        'indicator_period',
        'position_sizing',
        'base_position_size',
        'take_profit',
        'stop_loss',
        'risk_per_trade',
        'max_positions',
        'max_daily_loss',
        'paper_trading',
        'log_level'
    ]
    
    missing_params = []
    for param in important_params:
        if f"'{param}'" not in content:
            missing_params.append(param)
    
    assert len(missing_params) == 0, f"Missing parameter help for: {', '.join(missing_params)}"
    
    print(f"✓ Parameter help covers all {len(important_params)} important parameters")


def test_quick_start_guide_steps():
    """Test that quick start guide has all required steps"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    js_file = os.path.join(base_dir, 'static', 'js', 'helpful-features.js')
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Required steps
    required_steps = [
        'Connect to Broker',
        'Select Instruments',
        'Configure Strategy',
        'Start Trading'
    ]
    
    for step in required_steps:
        assert step in content, f"Quick start step '{step}' not found"
    
    print(f"✓ Quick start guide has all {len(required_steps)} required steps")


def test_contextual_help_sections():
    """Test that contextual help covers all configuration sections"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    js_file = os.path.join(base_dir, 'static', 'js', 'helpful-features.js')
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Required sections
    required_sections = ['basic', 'strategy', 'risk', 'advanced']
    
    for section in required_sections:
        assert f"'{section}'" in content, f"Contextual help for section '{section}' not found"
    
    print(f"✓ Contextual help covers all {len(required_sections)} configuration sections")


def test_tooltip_structure():
    """Test that tooltip HTML structure is correct"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    js_file = os.path.join(base_dir, 'static', 'js', 'helpful-features.js')
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check tooltip creation method
    assert 'createTooltip' in content, "createTooltip method not found"
    assert 'tooltip-wrapper' in content, "tooltip-wrapper class not used"
    assert 'tooltip-icon' in content, "tooltip-icon class not used"
    assert 'tooltip-content' in content, "tooltip-content class not used"
    
    print("✓ Tooltip structure is correct")


def test_example_values_present():
    """Test that example values are provided for parameters"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    js_file = os.path.join(base_dir, 'static', 'js', 'helpful-features.js')
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that examples are provided
    assert 'examples:' in content, "Examples field not found in parameter help"
    
    # Check for specific examples
    example_phrases = [
        'for intraday',
        'for swing trading',
        'for conservative',
        'for aggressive',
        'NIFTY futures'
    ]
    
    found_examples = 0
    for phrase in example_phrases:
        if phrase in content:
            found_examples += 1
    
    assert found_examples >= 3, f"Only {found_examples} example phrases found, expected at least 3"
    
    print(f"✓ Example values are provided ({found_examples} example phrases found)")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_helpful_features_files_exist,
        test_helpful_features_js_content,
        test_helpful_features_css_content,
        test_dashboard_includes_helpful_features,
        test_parameter_help_coverage,
        test_quick_start_guide_steps,
        test_contextual_help_sections,
        test_tooltip_structure,
        test_example_values_present
    ]
    
    print("Running Helpful Features Integration Tests...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ All tests passed!")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
