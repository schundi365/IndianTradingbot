"""
Explore the tgadise directory and identify useful components
"""
import os
from pathlib import Path

def explore_directory(path):
    """Explore a directory and categorize files"""
    
    target_path = Path(path)
    
    if not target_path.exists():
        print(f"❌ Directory not found: {path}")
        return
    
    print("=" * 80)
    print(f"EXPLORING: {path}")
    print("=" * 80)
    
    # Categories to look for
    categories = {
        'Trading Bots': [],
        'Strategies': [],
        'Indicators': [],
        'Risk Management': [],
        'Dashboards': [],
        'Configuration': [],
        'Utilities': [],
        'Documentation': [],
        'Tests': [],
        'Other': []
    }
    
    # Keywords for categorization
    keywords = {
        'Trading Bots': ['bot', 'trader', 'trading', 'mt5', 'metatrader'],
        'Strategies': ['strategy', 'signal', 'entry', 'exit'],
        'Indicators': ['indicator', 'rsi', 'macd', 'ema', 'sma', 'atr', 'adx'],
        'Risk Management': ['risk', 'position', 'sizing', 'stop', 'loss', 'profit'],
        'Dashboards': ['dashboard', 'web', 'flask', 'html', 'ui'],
        'Configuration': ['config', 'settings', 'params'],
        'Utilities': ['util', 'helper', 'tool'],
        'Documentation': ['readme', 'doc', 'guide', 'md'],
        'Tests': ['test', 'spec']
    }
    
    # Scan directory
    for root, dirs, files in os.walk(target_path):
        # Skip common ignore directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
        
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(target_path)
            
            # Categorize file
            categorized = False
            file_lower = file.lower()
            
            for category, kws in keywords.items():
                if any(kw in file_lower for kw in kws):
                    categories[category].append(str(relative_path))
                    categorized = True
                    break
            
            if not categorized:
                categories['Other'].append(str(relative_path))
    
    # Display results
    print("\n📊 FILE CATEGORIZATION:")
    print("=" * 80)
    
    for category, files in categories.items():
        if files:
            print(f"\n{category} ({len(files)} files):")
            print("-" * 40)
            for file in sorted(files)[:10]:  # Show first 10
                print(f"  • {file}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")
    
    # Identify interesting files
    print("\n\n🎯 POTENTIALLY USEFUL FILES:")
    print("=" * 80)
    
    interesting_patterns = [
        ('*.py', 'Python scripts'),
        ('*bot*.py', 'Bot implementations'),
        ('*strategy*.py', 'Trading strategies'),
        ('*indicator*.py', 'Custom indicators'),
        ('*risk*.py', 'Risk management'),
        ('*dashboard*.py', 'Dashboard code'),
        ('*config*.py', 'Configuration'),
        ('*.html', 'HTML templates'),
        ('*.json', 'JSON configs'),
        ('*.md', 'Documentation')
    ]
    
    for pattern, description in interesting_patterns:
        matches = list(target_path.rglob(pattern))
        if matches:
            print(f"\n{description} ({pattern}):")
            for match in matches[:5]:
                rel_path = match.relative_to(target_path)
                size = match.stat().st_size
                print(f"  • {rel_path} ({size:,} bytes)")
            if len(matches) > 5:
                print(f"  ... and {len(matches) - 5} more")
    
    # Summary
    print("\n\n📋 SUMMARY:")
    print("=" * 80)
    total_files = sum(len(files) for files in categories.values())
    print(f"Total files found: {total_files}")
    print(f"\nTop categories:")
    sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
    for cat, files in sorted_cats[:5]:
        if files:
            print(f"  • {cat}: {len(files)} files")
    
    print("\n\n💡 RECOMMENDATIONS:")
    print("=" * 80)
    print("To incorporate useful code from this directory:")
    print("1. Review the files listed above")
    print("2. Copy interesting files to your current workspace")
    print("3. I can then analyze and integrate them")
    print("\nSuggested files to review:")
    print("  • Trading bot implementations")
    print("  • Custom indicators or strategies")
    print("  • Risk management modules")
    print("  • Dashboard enhancements")
    print("  • Configuration systems")


if __name__ == "__main__":
    # Target directory
    target_dir = r"C:\Users\srika\Labs\AgenticAI\Bots\tgadise"
    
    try:
        explore_directory(target_dir)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease ensure the directory exists and you have read permissions.")
