# Commands to Explore tgadise Directory

## Quick Directory Listing

Run this in PowerShell to see what's in the tgadise directory:

```powershell
Get-ChildItem -Path "C:\Users\srika\Labs\AgenticAI\Bots\tgadise" -Recurse -File | 
    Where-Object { $_.Extension -in '.py','.html','.json','.md' } | 
    Select-Object FullName, Length | 
    Format-Table -AutoSize
```

## Find Specific File Types

### Python Files
```powershell
Get-ChildItem -Path "C:\Users\srika\Labs\AgenticAI\Bots\tgadise" -Recurse -Filter "*.py" | 
    Select-Object Name, Directory, Length
```

### Configuration Files
```powershell
Get-ChildItem -Path "C:\Users\srika\Labs\AgenticAI\Bots\tgadise" -Recurse -Filter "*.json" | 
    Select-Object Name, Directory, Length
```

### HTML/Dashboard Files
```powershell
Get-ChildItem -Path "C:\Users\srika\Labs\AgenticAI\Bots\tgadise" -Recurse -Filter "*.html" | 
    Select-Object Name, Directory, Length
```

## Find Interesting Files by Name

### Bot Files
```powershell
Get-ChildItem -Path "C:\Users\srika\Labs\AgenticAI\Bots\tgadise" -Recurse | 
    Where-Object { $_.Name -like "*bot*" } | 
    Select-Object Name, Directory
```

### Strategy Files
```powershell
Get-ChildItem -Path "C:\Users\srika\Labs\AgenticAI\Bots\tgadise" -Recurse | 
    Where-Object { $_.Name -like "*strategy*" -or $_.Name -like "*signal*" } | 
    Select-Object Name, Directory
```

### Indicator Files
```powershell
Get-ChildItem -Path "C:\Users\srika\Labs\AgenticAI\Bots\tgadise" -Recurse | 
    Where-Object { $_.Name -like "*indicator*" -or $_.Name -like "*rsi*" -or $_.Name -like "*macd*" } | 
    Select-Object Name, Directory
```

### Risk Management Files
```powershell
Get-ChildItem -Path "C:\Users\srika\Labs\AgenticAI\Bots\tgadise" -Recurse | 
    Where-Object { $_.Name -like "*risk*" -or $_.Name -like "*position*" } | 
    Select-Object Name, Directory
```

## Export File List to Text

```powershell
Get-ChildItem -Path "C:\Users\srika\Labs\AgenticAI\Bots\tgadise" -Recurse -File | 
    Select-Object FullName, Length, LastWriteTime | 
    Out-File -FilePath "tgadise_files.txt"
```

Then you can share the `tgadise_files.txt` file with me!

## Copy Interesting Files

Once you identify useful files, copy them to current workspace:

```powershell
# Example: Copy a specific file
Copy-Item "C:\Users\srika\Labs\AgenticAI\Bots\tgadise\some_file.py" -Destination "."

# Example: Copy all Python files from a specific folder
Copy-Item "C:\Users\srika\Labs\AgenticAI\Bots\tgadise\src\*.py" -Destination ".\tgadise_imports\"
```

## What to Look For

### High Priority Files:
1. **Trading Bot Implementations**
   - Main bot files
   - Strategy implementations
   - Signal generation logic

2. **Custom Indicators**
   - Technical indicator calculations
   - Custom indicator combinations
   - Signal filters

3. **Risk Management**
   - Position sizing algorithms
   - Stop loss/take profit logic
   - Risk calculators

4. **Dashboard Features**
   - Web interface code
   - Real-time updates
   - Chart implementations

5. **Configuration Systems**
   - Config management
   - Parameter optimization
   - Preset configurations

### Files to Copy:
- Any file with "bot" in the name
- Strategy or signal files
- Indicator implementations
- Risk management modules
- Dashboard/web interface files
- Configuration files (*.json, *config.py)
- Documentation (README.md, guides)

## Next Steps

1. **Run one of the commands above** to see what's available
2. **Identify interesting files** based on names and sizes
3. **Copy useful files** to current workspace
4. **Let me know** what you found, and I'll help integrate it!

## Alternative: Manual Exploration

You can also:
1. Open File Explorer
2. Navigate to `C:\Users\srika\Labs\AgenticAI\Bots\tgadise`
3. Look through the folders
4. Copy interesting files to your current workspace
5. Tell me what you found!
