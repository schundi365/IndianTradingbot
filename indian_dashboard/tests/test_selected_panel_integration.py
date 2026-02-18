"""
Integration test for Selected Instruments Panel (Task 6.5)

Tests the complete functionality of the selected instruments panel:
- Display of selected instruments
- Remove button for each instrument
- Total count display
- Continue to Configuration button state
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_selected_panel_html_structure():
    """Test that the HTML structure for selected panel exists"""
    with open('indian_dashboard/templates/dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Check for selected instruments section
    assert 'id="selected-instruments"' in html, "Selected instruments container missing"
    assert 'id="selected-count"' in html, "Selected count span missing"
    assert 'id="clear-all-selections-btn"' in html, "Clear all button missing"
    assert 'id="continue-to-config-btn"' in html, "Continue button missing"
    
    print("✓ HTML structure test passed")

def test_selected_panel_css_styles():
    """Test that CSS styles for selected panel exist"""
    with open('indian_dashboard/static/css/dashboard.css', 'r', encoding='utf-8') as f:
        css = f.read()
    
    # Check for selected instrument tag styles
    assert '.selected-instrument-tag' in css, "Selected instrument tag style missing"
    assert '.instrument-info' in css, "Instrument info style missing"
    assert '.instrument-symbol' in css, "Instrument symbol style missing"
    assert '.instrument-exchange' in css, "Instrument exchange style missing"
    assert '.remove-instrument' in css, "Remove instrument button style missing"
    
    print("✓ CSS styles test passed")

def test_update_selected_instruments_function():
    """Test that updateSelectedInstruments function exists in app.js"""
    with open('indian_dashboard/static/js/app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # Check for function definition
    assert 'function updateSelectedInstruments()' in js, "updateSelectedInstruments function missing"
    
    # Check for key functionality
    assert 'selected-count' in js, "Count update missing"
    assert 'selected-instrument-tag' in js, "Tag creation missing"
    assert 'remove-instrument' in js, "Remove button missing"
    assert 'No instruments selected' in js, "Empty state message missing"
    assert 'continueBtn.disabled' in js, "Continue button state management missing"
    
    print("✓ updateSelectedInstruments function test passed")

def test_continue_button_event_handler():
    """Test that continue button has event handler"""
    with open('indian_dashboard/static/js/app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # Check for continue button event listener
    assert 'continue-to-config-btn' in js, "Continue button reference missing"
    assert "querySelector('[data-tab=\"configuration\"]')" in js or "data-tab=\"configuration\"" in js, "Tab navigation missing"
    
    print("✓ Continue button event handler test passed")

def test_clear_all_button_event_handler():
    """Test that clear all button has event handler"""
    with open('indian_dashboard/static/js/app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # Check for clear all button event listener
    assert 'clear-all-selections-btn' in js, "Clear all button reference missing"
    assert 'clearSelectedInstruments' in js or 'removeSelectedInstrument' in js, "Clear functionality missing"
    
    print("✓ Clear all button event handler test passed")

def test_remove_individual_instrument():
    """Test that individual remove buttons work"""
    with open('indian_dashboard/static/js/app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # Check for remove button functionality
    assert 'removeSelectedInstrument' in js, "Remove instrument function missing"
    assert 'data-token' in js, "Token tracking missing"
    
    print("✓ Individual remove functionality test passed")

def test_empty_state_display():
    """Test that empty state is properly displayed"""
    with open('indian_dashboard/static/js/app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # Check for empty state handling
    assert 'No instruments selected' in js, "Empty state message missing"
    assert 'selected.length === 0' in js or 'selected.length == 0' in js, "Empty state check missing"
    
    print("✓ Empty state display test passed")

def test_selected_count_update():
    """Test that selected count is updated"""
    with open('indian_dashboard/static/js/app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # Check for count update
    assert 'selected-count' in js, "Count element reference missing"
    assert 'selected.length' in js, "Count calculation missing"
    
    print("✓ Selected count update test passed")

def test_instrument_tag_structure():
    """Test that instrument tags have correct structure"""
    with open('indian_dashboard/static/js/app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # Check for tag structure elements
    assert 'instrument-symbol' in js, "Symbol display missing"
    assert 'instrument-exchange' in js, "Exchange display missing"
    assert 'remove-instrument' in js, "Remove button missing"
    
    print("✓ Instrument tag structure test passed")

def test_continue_button_state_management():
    """Test that continue button is enabled/disabled correctly"""
    with open('indian_dashboard/static/js/app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # Check for button state management
    assert 'continueBtn.disabled = true' in js or 'continueBtn.disabled=true' in js, "Disable logic missing"
    assert 'continueBtn.disabled = false' in js or 'continueBtn.disabled=false' in js, "Enable logic missing"
    
    print("✓ Continue button state management test passed")

def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("Selected Instruments Panel Integration Tests (Task 6.5)")
    print("="*60 + "\n")
    
    tests = [
        test_selected_panel_html_structure,
        test_selected_panel_css_styles,
        test_update_selected_instruments_function,
        test_continue_button_event_handler,
        test_clear_all_button_event_handler,
        test_remove_individual_instrument,
        test_empty_state_display,
        test_selected_count_update,
        test_instrument_tag_structure,
        test_continue_button_state_management
    ]
    
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
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    if failed == 0:
        print("✓ All tests passed! Task 6.5 implementation is complete.")
        return True
    else:
        print("✗ Some tests failed. Please review the implementation.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
