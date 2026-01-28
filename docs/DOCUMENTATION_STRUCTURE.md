# Documentation Structure Guide

This document explains how the GEM Trading Bot documentation is organized.

## 📁 Directory Structure

```
root/
├── README.md                    # Main project documentation
├── QUICK_START.md              # 5-minute getting started guide
├── USER_GUIDE.md               # Complete user manual
├── TROUBLESHOOTING.md          # Common issues and solutions
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
│
└── docs/                       # All detailed documentation
    ├── README.md               # Documentation index
    │
    ├── User Guides (11 files)
    │   ├── INSTALLATION_GUIDE_FOR_USERS.md
    │   ├── DASHBOARD_CONFIGURATION_GUIDE.md
    │   ├── PROFITABLE_STRATEGY_GUIDE.md
    │   ├── DYNAMIC_SL_GUIDE.md
    │   ├── DYNAMIC_TP_GUIDE.md
    │   ├── SCALPING_MODE_GUIDE.md
    │   ├── SPLIT_ORDERS_GUIDE.md
    │   ├── TRAILING_STRATEGIES_GUIDE.md
    │   ├── ADAPTIVE_RISK_GUIDE.md
    │   └── ... (and more)
    │
    ├── deployment/             # Build & deployment guides
    │   ├── README.md
    │   ├── WINDOWS_BUILD_GUIDE.md
    │   ├── GITHUB_ACTIONS_BUILD_GUIDE.md
    │   ├── MACOS_MT5_SOLUTIONS.md
    │   └── ... (10 files total)
    │
    ├── fixes/                  # Bug fixes & enhancements
    │   ├── README.md
    │   ├── BOT_STATUS_DETECTION_FIX.md
    │   ├── PIP_CALCULATION_FIX.md
    │   └── ... (15 files total)
    │
    ├── analysis/               # Trade analysis & optimization
    │   ├── README.md
    │   ├── TRADE_ANALYSIS.md
    │   ├── MISSED_TRADE_ANALYSIS.md
    │   └── OPTIMIZATION_SUMMARY.md
    │
    ├── reference/              # Technical reference
    │   ├── README.md
    │   ├── DYNAMIC_RISK_SYSTEM.md
    │   ├── CONFIGURATION_PROFILES.md
    │   └── ... (8 files total)
    │
    └── archive/                # Historical documentation
        ├── README.md
        ├── SESSION_3_COMPLETE.md
        ├── SESSION_4_COMPLETE.md
        └── ... (31 files total)
```

## 🎯 Finding Documentation

### For New Users
Start here:
1. [README.md](../README.md) - Project overview
2. [QUICK_START.md](../QUICK_START.md) - Get started quickly
3. [docs/INSTALLATION_GUIDE_FOR_USERS.md](INSTALLATION_GUIDE_FOR_USERS.md) - Detailed setup

### For Configuration
1. [docs/DASHBOARD_CONFIGURATION_GUIDE.md](DASHBOARD_CONFIGURATION_GUIDE.md) - Web interface
2. [docs/CONFIGURATION_QUICK_REFERENCE.md](CONFIGURATION_QUICK_REFERENCE.md) - Quick reference
3. [docs/PROFITABLE_STRATEGY_GUIDE.md](PROFITABLE_STRATEGY_GUIDE.md) - Strategy details

### For Troubleshooting
1. [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Common issues
2. [docs/fixes/](fixes/README.md) - Specific bug fixes
3. [docs/TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing procedures

### For Deployment
1. [docs/deployment/](deployment/README.md) - All deployment guides
2. [docs/deployment/WINDOWS_BUILD_GUIDE.md](deployment/WINDOWS_BUILD_GUIDE.md) - Windows
3. [docs/deployment/24_7_DEPLOYMENT_GUIDE.md](deployment/24_7_DEPLOYMENT_GUIDE.md) - 24/7 trading

### For Developers
1. [docs/reference/](reference/README.md) - Technical reference
2. [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
3. [docs/reference/DYNAMIC_RISK_SYSTEM.md](reference/DYNAMIC_RISK_SYSTEM.md) - Core systems

## 📊 Documentation Categories

### User Guides (docs/)
**Purpose**: Help users understand and use features  
**Audience**: All users  
**Examples**: Installation, configuration, strategy guides

### Deployment (docs/deployment/)
**Purpose**: Build and deployment instructions  
**Audience**: Users deploying the bot  
**Examples**: Build guides, GitHub Actions, 24/7 deployment

### Fixes (docs/fixes/)
**Purpose**: Document bug fixes and enhancements  
**Audience**: Users experiencing issues, developers  
**Examples**: Bug fixes, patches, improvements

### Analysis (docs/analysis/)
**Purpose**: Trade analysis and optimization  
**Audience**: Users optimizing strategy  
**Examples**: Performance analysis, optimization results

### Reference (docs/reference/)
**Purpose**: Technical documentation  
**Audience**: Developers, advanced users  
**Examples**: System architecture, algorithms, technical specs

### Archive (docs/archive/)
**Purpose**: Historical documentation  
**Audience**: Developers, project historians  
**Examples**: Session notes, old guides, status files

## 🔍 Search Tips

### By Topic
- **Installation**: Check docs/INSTALLATION_GUIDE_FOR_USERS.md
- **Configuration**: Check docs/DASHBOARD_CONFIGURATION_GUIDE.md
- **Errors**: Check TROUBLESHOOTING.md and docs/fixes/
- **Strategy**: Check docs/PROFITABLE_STRATEGY_GUIDE.md
- **Building**: Check docs/deployment/

### By File Type
- **Guides**: docs/*.md (user guides)
- **Technical**: docs/reference/*.md
- **Historical**: docs/archive/*.md
- **Fixes**: docs/fixes/*.md

## 📝 Adding New Documentation

### User Guide
Place in: `docs/`  
Update: `docs/README.md`

### Deployment Guide
Place in: `docs/deployment/`  
Update: `docs/deployment/README.md`

### Bug Fix Documentation
Place in: `docs/fixes/`  
Update: `docs/fixes/README.md`

### Analysis Report
Place in: `docs/analysis/`  
Update: `docs/analysis/README.md`

### Technical Reference
Place in: `docs/reference/`  
Update: `docs/reference/README.md`

### Historical Document
Place in: `docs/archive/`  
Update: `docs/archive/README.md`

## ✅ Benefits of This Structure

1. **Clean Root Directory**
   - Only 7 essential files
   - Easy to find main docs
   - Professional appearance

2. **Logical Organization**
   - Grouped by purpose
   - Easy to navigate
   - Clear hierarchy

3. **Easy Maintenance**
   - Know where to add new docs
   - Easy to update related docs
   - Clear what's current vs historical

4. **Better Discoverability**
   - Index files in each folder
   - Clear naming conventions
   - Linked navigation

## 🔗 Navigation

All documentation includes:
- Links to related documents
- Back links to index files
- Clear section headers
- Table of contents (for long docs)

---

**Need help finding something?** Check [docs/README.md](README.md) for the complete index.

[← Back to Documentation Index](README.md)
