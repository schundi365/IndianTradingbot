# Windows Build Guide - GitHub Actions

## 🚀 Quick Start

Build your Windows executable automatically using GitHub's free Windows runners.

---

## ⚡ 3-Step Process

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Windows build workflow"
git push origin main
```

### Step 2: Trigger Build

**Option A: Automatic (on every push)**
- Build starts automatically when you push to `main` branch
- Go to Actions tab to monitor progress

**Option B: Manual Trigger**
1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
2. Click "Build Windows Executable"
3. Click "Run workflow"
4. Enter version: `2.0.0`
5. Click "Run workflow"

**Option C: Create Release**
```bash
git tag v2.0.0
git push origin v2.0.0
```
This creates a GitHub Release with the executable attached.

### Step 3: Download
- Wait 3-5 minutes for build to complete
- Download from Artifacts section
- Or download from Releases tab (if using tags)

---

## 📋 What Gets Built

### Build Output
```
GEM_Trading_Bot_Windows/
├── GEM_Trading_Bot.exe          # Main executable (~150-200 MB)
├── USER_GUIDE.md                # Complete user manual
├── QUICK_START_CARD.md          # Quick reference
├── INSTALLATION_GUIDE_FOR_USERS.md
├── TROUBLESHOOTING.md
└── README.txt                   # Quick start instructions
```

### Packaged As
- `GEM_Trading_Bot_v2.0.0_Windows.zip` (~150-200 MB)

---

## 🔧 Workflow Features

### Triggers
✅ **Push to main** - Automatic build on every push
✅ **Version tags** - Build releases (v1.0, v2.0, etc.)
✅ **Manual** - Run anytime from Actions tab

### Build Process
1. ✅ Checkout code
2. ✅ Setup Python 3.11
3. ✅ Install dependencies
4. ✅ Run build_windows.bat
5. ✅ Create ZIP archive
6. ✅ Upload artifact (90 days retention)
7. ✅ Create release (if tag)

### Output
✅ **Artifacts** - Downloadable for 90 days
✅ **Releases** - Permanent downloads
✅ **Build logs** - Detailed logs for debugging
✅ **Summary** - Quick overview in Actions tab

---

## 💰 Cost: FREE

### GitHub Actions Free Tier
- **Windows minutes:** 2,000/month
- **Build time:** ~3-5 minutes
- **Builds per month:** ~400-600
- **Storage:** 500 MB
- **Retention:** 90 days

**More than enough for development and releases!**

---

## 📝 Usage Examples

### Example 1: Development Build
```bash
# Make changes
git add .
git commit -m "Update trading logic"
git push origin main

# Build starts automatically
# Download from Actions → Artifacts
```

### Example 2: Release Build
```bash
# Create release
git tag v2.0.0
git push origin v2.0.0

# Build starts automatically
# Creates GitHub Release
# Download from Releases tab
```

### Example 3: Manual Build
1. Go to Actions tab
2. Select "Build Windows Executable"
3. Click "Run workflow"
4. Select branch: `main`
5. Enter version: `2.0.1`
6. Click "Run workflow"
7. Wait 3-5 minutes
8. Download from Artifacts

---

## 🐛 Troubleshooting

### Build Fails

**Check build logs:**
1. Go to Actions tab
2. Click on failed workflow run
3. Click on "build-windows" job
4. Expand failed step
5. Read error message

**Common issues:**

1. **Missing dependency**
   ```
   ModuleNotFoundError: No module named 'flask'
   ```
   **Fix:** Add to `requirements.txt`

2. **Build script error**
   ```
   'build_windows.bat' is not recognized
   ```
   **Fix:** Ensure file is committed and in root directory

3. **PyInstaller error**
   ```
   Failed to execute script
   ```
   **Fix:** Check build_windows.bat for syntax errors

### No Artifact

**Verify:**
1. Build completed successfully (green checkmark)
2. "Upload artifact" step succeeded
3. Scroll to bottom for Artifacts section

**If missing:**
- Check build logs for errors
- Verify `dist/GEM_Trading_Bot_Windows/` was created
- Ensure ZIP creation succeeded

### Executable Doesn't Run

**Common causes:**
1. **Antivirus blocking** - Add exception
2. **Missing DLLs** - Reinstall Visual C++ Redistributable
3. **Corrupted download** - Re-download and extract

**Solutions:**
- Right-click → Properties → Unblock
- Run as Administrator
- Check Windows Event Viewer for errors

---

## 🎯 Best Practices

### 1. Version Tagging
Use semantic versioning:
```bash
git tag v2.0.0    # Major release
git tag v2.1.0    # New features
git tag v2.1.1    # Bug fixes
```

### 2. Build on Tags Only
Save minutes by building only releases:
```yaml
on:
  push:
    tags:
      - 'v*'
```

### 3. Test Before Release
1. Build manually first
2. Download and test
3. If good, create release tag

### 4. Add Build Badge
Show build status in README:
```markdown
![Windows Build](https://github.com/USERNAME/REPO/workflows/Build%20Windows%20Executable/badge.svg)
```

---

## 📊 Build Times

| Task | Time |
|------|------|
| Checkout | ~10 seconds |
| Setup Python | ~30 seconds |
| Install deps | ~1-2 minutes |
| Build executable | ~2-3 minutes |
| Create ZIP | ~10 seconds |
| Upload | ~30 seconds |
| **Total** | **~3-5 minutes** |

---

## 🔍 Monitoring Builds

### View Build Status
```bash
# In browser
https://github.com/YOUR_USERNAME/YOUR_REPO/actions

# Or use GitHub CLI
gh run list
gh run view
gh run watch
```

### Download via CLI
```bash
# Install GitHub CLI
winget install GitHub.cli

# Download artifact
gh run download <run-id>

# Or download release
gh release download v2.0.0
```

---

## 📦 Distribution

### Option 1: GitHub Releases (Recommended)
```bash
# Create release
git tag v2.0.0
git push origin v2.0.0

# Share download link
https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest
```

**Pros:**
- ✅ Permanent storage
- ✅ Version tracking
- ✅ Professional presentation
- ✅ Easy to share

### Option 2: Artifacts
- Download from Actions tab
- Share ZIP file directly
- Expires after 90 days

### Option 3: External Hosting
- Upload to Google Drive, Dropbox, etc.
- Share download link
- No GitHub account needed for users

---

## 🔐 Security

### Code Signing (Optional)

For production releases, consider code signing:

1. **Get certificate** ($100-300/year)
2. **Add to GitHub Secrets**
3. **Update workflow:**

```yaml
- name: Sign executable
  env:
    CERTIFICATE: ${{ secrets.WINDOWS_CERTIFICATE }}
    PASSWORD: ${{ secrets.CERTIFICATE_PASSWORD }}
  run: |
    # Import certificate
    # Sign executable
    signtool sign /f cert.pfx /p $PASSWORD GEM_Trading_Bot.exe
```

**Benefits:**
- ✅ No Windows SmartScreen warning
- ✅ Professional appearance
- ✅ User trust

---

## 📚 Related Documentation

- **GitHub Actions Guide:** `GITHUB_ACTIONS_BUILD_GUIDE.md`
- **Quick Start:** `GITHUB_ACTIONS_QUICK_START.md`
- **Troubleshooting:** `GITHUB_ACTIONS_TROUBLESHOOTING.md`
- **Build Script:** `build_windows.bat`

---

## ✅ Checklist

Before first build:
- [ ] `build_windows.bat` exists
- [ ] `requirements.txt` is complete
- [ ] Workflow file in `.github/workflows/`
- [ ] Code pushed to GitHub
- [ ] GitHub Actions enabled

After build:
- [ ] Build completed successfully
- [ ] Artifact uploaded
- [ ] Downloaded and tested
- [ ] Executable runs correctly
- [ ] Dashboard opens

---

## 🎉 Quick Commands

### First Time Setup
```bash
# Add workflow
git add .github/workflows/build-windows.yml

# Commit
git commit -m "Add Windows build workflow"

# Push
git push origin main
```

### Create Release
```bash
# Tag version
git tag v2.0.0

# Push tag
git push origin v2.0.0

# GitHub Actions will:
# 1. Build Windows executable
# 2. Create GitHub Release
# 3. Upload ZIP file
```

### Manual Build
1. Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
2. Click "Build Windows Executable"
3. Click "Run workflow"
4. Enter version and run
5. Download from Artifacts

---

## 📊 Summary

✅ **Free Windows builds** - 2,000 minutes/month
✅ **Fast builds** - 3-5 minutes
✅ **Automatic** - On push or tags
✅ **Professional** - GitHub Releases
✅ **Easy** - 3-step process

**Your Windows executable is just a push away!** 🚀

---

## 🆘 Need Help?

1. Check `GITHUB_ACTIONS_TROUBLESHOOTING.md`
2. View build logs on GitHub
3. Search GitHub Actions documentation
4. Open an issue on GitHub

---

**Ready to build? Push to GitHub and go to the Actions tab!** 🎯
