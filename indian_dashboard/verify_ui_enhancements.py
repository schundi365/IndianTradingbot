#!/usr/bin/env python3
"""
Verification script for UI/UX enhancements (Task 14.2)
Checks that all required files are present and properly configured
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and report result"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} MISSING: {filepath}")
        return False

def check_file_content(filepath, search_strings, description):
    """Check if file contains specific strings"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        missing = []
        for search_str in search_strings:
            if search_str not in content:
                missing.append(search_str)
        
        if not missing:
            print(f"✓ {description}: All required content present")
            return True
        else:
            print(f"✗ {description}: Missing content - {', '.join(missing)}")
            return False
    except Exception as e:
        print(f"✗ {description}: Error reading file - {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 70)
    print("UI/UX Enhancements Verification (Task 14.2)")
    print("=" * 70)
    print()
    
    all_passed = True
    
    # Check CSS file
    print("1. Checking CSS Files...")
    css_file = "indian_dashboard/static/css/ui-enhancements.css"
    if check_file_exists(css_file, "UI Enhancements CSS"):
        all_passed &= check_file_content(
            css_file,
            [
                "@keyframes fadeIn",
                "@keyframes slideInUp",
                "@keyframes scaleIn",
                "@keyframes bounce",
                "@media (max-width: 640px)",
                "@media (prefers-reduced-motion: reduce)",
                "@media (prefers-contrast: high)",
                ".keyboard-shortcut-hint",
                ".sr-only"
            ],
            "CSS animations and responsive styles"
        )
    else:
        all_passed = False
    print()
    
    # Check JavaScript file
    print("2. Checking JavaScript Files...")
    js_file = "indian_dashboard/static/js/ui-enhancements.js"
    if check_file_exists(js_file, "UI Enhancements JavaScript"):
        all_passed &= check_file_content(
            js_file,
            [
                "KeyboardShortcuts",
                "AccessibilityEnhancements",
                "MobileEnhancements",
                "AnimationEnhancements",
                "init()",
                "handleKeyPress",
                "addSwipeGestures",
                "addAriaLabels"
            ],
            "JavaScript enhancements modules"
        )
    else:
        all_passed = False
    print()
    
    # Check HTML template
    print("3. Checking HTML Template...")
    html_file = "indian_dashboard/templates/dashboard.html"
    if check_file_exists(html_file, "Dashboard HTML template"):
        all_passed &= check_file_content(
            html_file,
            [
                'href="/static/css/ui-enhancements.css"',
                'src="/static/js/ui-enhancements.js"'
            ],
            "HTML includes UI enhancement files"
        )
    else:
        all_passed = False
    print()
    
    # Check test file
    print("4. Checking Test Files...")
    test_file = "indian_dashboard/tests/test_ui_enhancements.html"
    all_passed &= check_file_exists(test_file, "UI Enhancements test page")
    print()
    
    # Check documentation
    print("5. Checking Documentation...")
    doc_file = "indian_dashboard/UI_UX_ENHANCEMENTS_GUIDE.md"
    all_passed &= check_file_exists(doc_file, "UI/UX Enhancements guide")
    
    summary_file = "indian_dashboard/TASK_14.2_UI_UX_IMPROVEMENTS_SUMMARY.md"
    all_passed &= check_file_exists(summary_file, "Task 14.2 summary")
    print()
    
    # Feature checklist
    print("6. Feature Implementation Checklist...")
    features = [
        ("Animations and transitions", css_file, "@keyframes"),
        ("Mobile responsiveness", css_file, "@media (max-width: 640px)"),
        ("Keyboard shortcuts", js_file, "KeyboardShortcuts"),
        ("Accessibility features", js_file, "AccessibilityEnhancements"),
        ("Touch optimizations", js_file, "MobileEnhancements"),
        ("Reduced motion support", css_file, "prefers-reduced-motion"),
        ("High contrast support", css_file, "prefers-contrast: high"),
        ("Dark mode support", css_file, "prefers-color-scheme: dark")
    ]
    
    for feature_name, file_path, search_str in features:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                if search_str in f.read():
                    print(f"✓ {feature_name}")
                else:
                    print(f"✗ {feature_name} - Not found")
                    all_passed = False
        else:
            print(f"✗ {feature_name} - File missing")
            all_passed = False
    print()
    
    # Final result
    print("=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED - UI/UX enhancements successfully implemented!")
        print()
        print("Next steps:")
        print("1. Start the dashboard: python indian_dashboard.py")
        print("2. Open test page: http://localhost:8080/tests/test_ui_enhancements.html")
        print("3. Test keyboard shortcuts: Press Shift+H")
        print("4. Test mobile: Resize browser or use mobile device")
        print("5. Test accessibility: Use keyboard navigation and screen reader")
        return 0
    else:
        print("✗ SOME CHECKS FAILED - Please review the errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
