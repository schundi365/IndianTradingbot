# GitHub Release Guide - Windows Executable

## Overview

This guide explains how to create a Windows executable release using GitHub Actions.

---

## 🚀 Automated Build Process

### What Happens Automatically

When you push a version tag (e.g., `v2.1.0`), GitHub Actions will:

1. **Build Windows Executable**
   - Uses PyInstaller to create standalone .exe
   - Includes all dependencies
   - Embeds Python runtime
   - Packages web dashboard

2. **Package Documentation**
   - Copies all essential guides
   - Includes START_HERE.txt
   - Adds configuration guides
   - Packages in docs/ folder

3. **Create ZIP Archive**
   - Names: `GEM_Trading_Bot_v2.1.0_Windows.zip`
   - Size: ~150-200 MB
   - Ready for distribution

4. **Create GitHub Release**
   - Uploads ZIP file
   - Generates release notes
   - Makes publicly available
   - Includes comprehensive documentation

---

## 📋 Files Included in Release

### Executable
- `GEM_Trading_Bot.exe` - Main application

### Root Documentation
- `START_HERE.txt` - Quick start guide
- `WINDOWS_INSTALLATION_GUIDE.md` - Complete installation
- `USER_GUIDE.md` - Complete user manual
- `FEATURES_GUIDE.md` - All features explained
- `QUICK_START.md` - 5-minute guide
- `TROUBLESHOOTING.md` - Problem solving
- `README.md` - Project overview
- `CHANGELOG.md` - Version history

### docs/ Folder
- `INSTALLATION_GUIDE_FOR_USERS.md` - Detailed setup
- `DASHBOARD_CONFIGURATION_GUIDE.md` - All settings
- `PROFITABLE_STRATEGY_GUIDE.md` - Strategy details
- `WEB_DASHBOARD_GUIDE.md` - Dashboard features
- `CONFIGURATION_QUICK_REFERENCE.md` - Quick reference

---

## 🏷️ Creating a Release

### Method 1: Push a Tag (Recommended)

```bash
# Create and push a version tag
git tag -a v2.1.0 -m "Release version 2.1.0"
git push origin v2.1.0
```

**What happens:**
1. GitHub Actions detects the tag
2. Builds Windows executable automatically
3. Creates release with comprehensive notes
4. Uploads ZIP file
5. Makes available for download

### Method 2: Manual Trigger

1. Go to GitHub Actions tab
2. Select "Build Windows Executable" workflow
3. Click "Run workflow"
4. Enter version number (e.g., 2.1.0)
5. Click "Run workflow" button

**What happens:**
1. Builds executable
2. Creates artifact (downloadable for 90 days)
3. Does NOT create release (manual trigger only)

---

## 📦 Build Configuration

### Build Script: `build_windows.bat`

**What it does:**
1. Checks Python version
2. Installs PyInstaller
3. Cleans previous builds
4. Builds executable with PyInstaller
5. Creates distribution folder
6. Copies all documentation
7. Creates START_HERE.txt
8. Verifies build

**PyInstaller Options:**
- `--onefile` - Single executable
- `--windowed` - No console window
- `--add-data` - Include templates and src
- `--hidden-import` - Include all dependencies
- `--collect-all` - Collect Flask, Werkzeug, Jinja2

### GitHub Actions Workflow: `.github/workflows/build-windows.yml`

**Triggers:**
- Push to main/master branch
- Push version tags (v*)
- Manual workflow dispatch

**Steps:**
1. Checkout code
2. Setup Python 3.11
3. Install dependencies
4. Run build script
5. Package documentation
6. Verify build
7. Create ZIP archive
8. Upload artifact
9. Create release (if tag)
10. Generate build summary

---

## 📝 Release Notes

### Automatically Generated

The workflow creates comprehensive release notes including:

**Sections:**
- Download & Install instructions
- System Requirements
- What's Included
- Quick Start (3 steps)
- Key Features
- Performance metrics
- Important Notes & Warnings
- Documentation Guide
- Troubleshooting tips
- Updates information
- Support channels
- Getting Started Checklist
- Build Information

**Benefits:**
- Users know exactly what they're getting
- Clear installation instructions
- All features highlighted
- Safety warnings included
- Support information provided

---

## 🔍 Verification

### After Build Completes

**Check these:**
1. ✅ Artifact uploaded successfully
2. ✅ ZIP file created (150-200 MB)
3. ✅ Release created (if tag)
4. ✅ Release notes generated
5. ✅ Download link works

### Test the Release

**Download and verify:**
1. Download ZIP from release
2. Extract to test folder
3. Verify all files present
4. Run GEM_Trading_Bot.exe
5. Check dashboard opens
6. Verify all documentation included
7. Test basic functionality

---

## 📊 Build Artifacts

### Artifact Retention

**GitHub Actions Artifacts:**
- Retention: 90 days
- Available for all builds
- Downloadable by repository members
- Useful for testing

**GitHub Releases:**
- Permanent (until deleted)
- Publicly available
- Downloadable by anyone
- Recommended for distribution

---

## 🔄 Version Numbering

### Semantic Versioning

Format: `MAJOR.MINOR.PATCH`

**Examples:**
- `v2.0.0` - Major release (breaking changes)
- `v2.1.0` - Minor release (new features)
- `v2.1.1` - Patch release (bug fixes)

**When to increment:**
- **MAJOR:** Breaking changes, major rewrites
- **MINOR:** New features, enhancements
- **PATCH:** Bug fixes, small improvements

---

## 🛠️ Troubleshooting Builds

### Build Fails

**Common Issues:**

**1. PyInstaller Error**
```
Solution: Check dependencies in requirements.txt
Verify all imports are included in --hidden-import
```

**2. Missing Files**
```
Solution: Check --add-data paths
Verify files exist in repository
```

**3. Import Errors**
```
Solution: Add to --hidden-import list
Check --collect-all includes package
```

**4. Size Too Large**
```
Solution: Normal for PyInstaller (150-200 MB)
Includes Python runtime and all dependencies
```

### Release Not Created

**Check:**
1. Did you push a tag? (not just commit)
2. Is tag format correct? (v*.*.*)
3. Check GitHub Actions logs
4. Verify GITHUB_TOKEN permissions

---

## 📈 Distribution

### Sharing the Release

**GitHub Release:**
- Share release page URL
- Users download ZIP directly
- Includes all documentation
- Automatic updates notification

**Alternative Distribution:**
- Download ZIP from release
- Upload to file sharing service
- Share download link
- Include installation instructions

---

## 🔐 Security

### Code Signing (Future)

**Currently:**
- Executable is not code-signed
- Windows SmartScreen may warn
- Users must click "More info" → "Run anyway"

**Future Enhancement:**
- Obtain code signing certificate
- Sign executable during build
- Eliminates SmartScreen warnings
- Increases user trust

---

## 📚 Documentation Updates

### When Releasing

**Update these files:**
1. `CHANGELOG.md` - Add version notes
2. `README.md` - Update version number
3. `WINDOWS_INSTALLATION_GUIDE.md` - Update if needed
4. `USER_GUIDE.md` - Document new features
5. `FEATURES_GUIDE.md` - Add new features

**Commit before tagging:**
```bash
git add .
git commit -m "Update documentation for v2.1.0"
git push
git tag -a v2.1.0 -m "Release version 2.1.0"
git push origin v2.1.0
```

---

## ✅ Release Checklist

### Before Creating Release

- [ ] All features tested
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number decided
- [ ] Build tested locally
- [ ] All tests passing
- [ ] No known critical bugs

### Creating Release

- [ ] Commit all changes
- [ ] Push to main branch
- [ ] Create version tag
- [ ] Push tag to GitHub
- [ ] Wait for build to complete
- [ ] Verify artifact created
- [ ] Check release created
- [ ] Download and test ZIP

### After Release

- [ ] Test downloaded executable
- [ ] Verify all documentation included
- [ ] Check release notes accurate
- [ ] Announce release (if applicable)
- [ ] Monitor for issues
- [ ] Respond to user feedback

---

## 🎯 Best Practices

### Release Frequency

**Recommended:**
- Major releases: Every 3-6 months
- Minor releases: Every 1-2 months
- Patch releases: As needed for bugs

### Testing

**Before Release:**
- Test on clean Windows 10 system
- Test on Windows 11
- Verify with fresh MT5 installation
- Test all documentation links
- Verify all features work

### Communication

**Announce:**
- GitHub release notes
- README.md update
- Social media (if applicable)
- Email users (if applicable)
- Discord/Forum (if applicable)

---

## 📞 Support

### For Build Issues

1. Check GitHub Actions logs
2. Review build script output
3. Test build locally first
4. Check PyInstaller documentation
5. Open GitHub issue if needed

### For Release Issues

1. Verify tag format correct
2. Check workflow file syntax
3. Review GitHub Actions permissions
4. Check release notes template
5. Contact GitHub support if needed

---

**Last Updated:** January 28, 2026  
**Workflow File:** `.github/workflows/build-windows.yml`  
**Build Script:** `build_windows.bat`  

**Happy Releasing! 🚀**
