# Archive Directory

This directory contains historical files that were moved from the main repository to keep it clean and organized.

## Purpose

The archive preserves all development history, debugging scripts, test files, and documentation that are no longer actively used but may be valuable for reference.

## Structure

```
archive/
├── analysis_scripts/      # Scripts for analyzing trades, signals, and bot behavior
├── build_scripts/         # Build, deployment, and setup scripts
├── config_backups/        # Old configuration backups and templates
├── debug_scripts/         # Debugging and troubleshooting scripts
├── documentation/         # Historical documentation, guides, and status reports
├── fix_scripts/           # Bug fixes, updates, and maintenance scripts
├── logs/                  # Old log files
├── mt5_bot/               # MT5 trading bot files (26 files)
├── old_configs/           # Deprecated configuration templates (7 files)
├── test_scripts/          # Test scripts moved from root
├── verification_scripts/  # Verification and validation scripts
├── Bugs/                  # Bug tracking directory
├── config_backups/        # Configuration backup directory
├── ml_training/           # ML training scripts and data
├── RSI_IMPLEMENTATION_GUIDE/  # Implementation guides
├── static/                # Old static web files
└── templates/             # Old HTML templates
```

## Categories

### Analysis Scripts (~50 files)
Scripts for analyzing trading performance, signals, and bot behavior:
- Trade analysis
- Signal monitoring
- Performance diagnostics
- Symbol processing checks

### Build Scripts (~30 files)
Scripts for building executables and deploying the bot:
- PyInstaller build scripts
- Deployment automation
- Setup and installation
- Cross-platform builds

### Debug Scripts (~50 files)
Scripts for debugging issues and emergency fixes:
- Error diagnostics
- Emergency repairs
- Force updates
- Surgical fixes

### Fix Scripts (~100 files)
Historical bug fixes and feature implementations:
- ADX calculation fixes
- MACD precision fixes
- TP/SL calculation fixes
- Configuration synchronization
- Logging enhancements

### Test Scripts (~150 files)
Test files moved from root directory:
- Unit tests
- Integration tests
- Property-based tests
- Dashboard tests
- HTML test files

### Verification Scripts (~50 files)
Scripts for verifying functionality:
- Configuration validation
- Feature verification
- Integration checks
- Cross-platform testing

### Documentation (~100 files)
Historical documentation and status reports:
- Implementation guides
- Status summaries
- Analysis reports
- Quick start guides
- Troubleshooting docs

### MT5 Bot Files (26 files)
All MetaTrader 5 trading bot files and backups:
- Main MT5 bot implementation
- Multiple backup versions
- Corrupted file versions
- Working pre-fix versions
- All MT5-specific code

### Old Configs (7 files)
Deprecated configuration files from src/:
- Config backups with timestamps
- Experimental configurations
- Migration temporary files
- Optimized config versions
- Profitable balanced configs

## Usage

### Finding Files

All files are organized by category. To find a specific file:

1. Identify the category (analysis, debug, fix, test, etc.)
2. Navigate to the appropriate subdirectory
3. Files retain their original names

### Restoring Files

If you need to restore an archived file:

```bash
# Copy to root
cp archive/[category]/[filename] .

# Or move back
mv archive/[category]/[filename] .
```

### Searching

To search for a file across all archive directories:

```bash
# Linux/Mac
find archive/ -name "filename"

# Windows PowerShell
Get-ChildItem -Path archive -Recurse -Filter "filename"
```

## Important Notes

1. **No Deletion**: No files were deleted, only moved to archive
2. **Preservation**: All development history is preserved
3. **Reference**: Files can be referenced for historical context
4. **Restoration**: Any file can be restored if needed
5. **Git History**: Git history remains intact

## When to Use Archive

Use archived files when you need to:
- Reference old implementations
- Understand historical decisions
- Restore previous functionality
- Debug similar issues
- Review test coverage

## Maintenance

The archive should be:
- Kept for reference but not actively maintained
- Excluded from active development
- Reviewed periodically for cleanup
- Documented for future reference

## Archive Date

**Created**: February 18, 2026
**Files Archived**: 534+
**Last Updated**: February 18, 2026 (MT5 cleanup)
**Organization**: By category and type

### Recent Updates

**February 18, 2026 - MT5 Cleanup**:
- Moved 26 MT5 trading bot files from src/ to archive/mt5_bot/
- Moved 7 config backup files from src/ to archive/old_configs/
- Moved 1 backup file (adaptive_risk_manager) to archive/
- Total: 34 additional files archived
- **Reason**: Repository now focuses exclusively on Indian market trading (Kite Connect)

---

For the current, active codebase, see the main repository root directory.
