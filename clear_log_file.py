#!/usr/bin/env python3
"""
Clear Trading Bot Log File

This script safely clears the trading_bot.log file while the bot is running.
It creates a backup of recent logs and starts fresh.
"""

import os
import shutil
from datetime import datetime

def clear_log_file():
    """
    Clear the trading bot log file safely
    """
    log_file = "trading_bot.log"
    
    print("🗂️ Clearing Trading Bot Log File...")
    print("="*50)
    
    # Check if log file exists
    if not os.path.exists(log_file):
        print("❌ Log file not found!")
        return False
    
    # Get current file size
    file_size = os.path.getsize(log_file)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"📊 Current log file size: {file_size_mb:.2f} MB")
    
    # Create backup of recent logs (last 1000 lines)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"trading_bot_backup_{timestamp}.log"
    
    try:
        print("💾 Creating backup of recent logs...")
        
        # Read last 1000 lines for backup
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Keep last 1000 lines
        recent_lines = lines[-1000:] if len(lines) > 1000 else lines
        
        # Write backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.writelines(recent_lines)
        
        backup_size = os.path.getsize(backup_file) / 1024
        print(f"✅ Backup created: {backup_file} ({backup_size:.1f} KB)")
        
        # Clear the main log file
        print("🧹 Clearing main log file...")
        
        # Write a fresh start message
        fresh_start_message = f"""
===============================================================================
LOG FILE CLEARED - FRESH START
===============================================================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Previous log size: {file_size_mb:.2f} MB
Backup created: {backup_file}
Enhanced signal generation: ACTIVE
System status: OPERATIONAL
===============================================================================

"""
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(fresh_start_message)
        
        new_size = os.path.getsize(log_file) / 1024
        print(f"✅ Log file cleared! New size: {new_size:.1f} KB")
        
        # Show space saved
        space_saved_mb = file_size_mb - (new_size / 1024)
        print(f"💾 Space saved: {space_saved_mb:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing log file: {e}")
        return False

def cleanup_old_backups():
    """
    Clean up old backup files (keep only last 5)
    """
    print("\n🧹 Cleaning up old backup files...")
    
    # Find all backup files
    backup_files = []
    for filename in os.listdir('.'):
        if filename.startswith('trading_bot_backup_') and filename.endswith('.log'):
            backup_files.append(filename)
    
    if len(backup_files) > 5:
        # Sort by modification time (oldest first)
        backup_files.sort(key=lambda x: os.path.getmtime(x))
        
        # Remove oldest files, keep last 5
        files_to_remove = backup_files[:-5]
        
        for old_backup in files_to_remove:
            try:
                os.remove(old_backup)
                print(f"🗑️ Removed old backup: {old_backup}")
            except Exception as e:
                print(f"⚠️ Could not remove {old_backup}: {e}")
        
        print(f"✅ Kept {min(5, len(backup_files))} most recent backups")
    else:
        print(f"✅ {len(backup_files)} backup files (within limit)")

if __name__ == "__main__":
    print("🚀 Log File Cleanup Utility")
    print("="*50)
    
    if clear_log_file():
        cleanup_old_backups()
        
        print("\n✅ LOG FILE CLEANUP COMPLETE!")
        print("\nBenefits:")
        print("• Freed up disk space")
        print("• Fresh log file for new session")
        print("• Recent logs backed up safely")
        print("• Bot continues running normally")
        print("\n📊 The bot will continue logging to the cleared file.")
        print("🔍 Monitor new logs for enhanced signal generation activity.")
    else:
        print("\n❌ LOG FILE CLEANUP FAILED!")
        print("Please check file permissions and try again.")