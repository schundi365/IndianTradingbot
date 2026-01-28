# GitHub Actions - Quick Start Guide

## 🎯 Build Mac Executable Without a Mac!

GitHub provides **FREE macOS runners** - you can build Mac executables automatically in the cloud.

---

## ⚡ Quick Start (3 Steps)

### 1. Push to GitHub
```bash
git add .
git commit -m "Add GitHub Actions workflows"
git push origin main
```

### 2. Trigger Build

**Option A: Manual (Easiest)**
1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
2. Click "Build macOS Executable"
3. Click "Run workflow" button
4. Enter version: `2.0.0`
5. Click green "Run workflow" button

**Option B: Automatic Release**
```bash
git tag v2.0.0
git push origin v2.0.0
```

### 3. Download Executable

**From Artifacts (Manual build):**
1. Wait 5-10 minutes for build to complete
2. Click on the completed workflow run
3. Scroll to "Artifacts" section at bottom
4. Click to download ZIP file

**From Releases (Tag build):**
1. Go to "Releases" tab on GitHub
2. Click on latest release
3. Download the ZIP file

---

## 📊 What You Get

✅ **Free macOS builds** - 2,000 minutes/month
✅ **No Mac needed** - runs in GitHub's cloud
✅ **Automatic builds** - on every push or tag
✅ **Professional releases** - with version numbers
✅ **Both platforms** - Windows + macOS together

---

## 🔧 Workflows Included

### 1. Build macOS Only
**File:** `.github/workflows/build-macos.yml`
**Triggers:** Push to main, tags, or manual
**Output:** macOS executable ZIP

### 2. Build All Platforms
**File:** `.github/workflows/build-all-platforms.yml`
**Triggers:** Version tags (v1.0, v2.0) or manual
**Output:** Windows + macOS executables, GitHub Release

---

## 📝 Common Commands

### Create a Release
```bash
# Tag the version
git tag v2.0.0

# Push tag to GitHub
git push origin v2.0.0

# GitHub Actions will automatically:
# - Build Windows executable
# - Build macOS executable
# - Create GitHub Release
# - Upload both files
```

### Update and Rebuild
```bash
# Make changes
git add .
git commit -m "Update bot"

# Push to trigger build
git push origin main

# Or create new version
git tag v2.0.1
git push origin v2.0.1
```

### Check Build Status
```bash
# View in browser
https://github.com/YOUR_USERNAME/YOUR_REPO/actions

# Or use GitHub CLI
gh run list
gh run view
```

---

## ⏱️ Build Times

| Platform | Time | Minutes Used |
|----------|------|--------------|
| macOS | 5-10 min | ~10 minutes |
| Windows | 3-5 min | ~5 minutes |
| Both | 10-15 min | ~15 minutes |

**With 2,000 free minutes/month:**
- ~200 macOS builds
- ~130 multi-platform builds

---

## 🐛 Troubleshooting

### Build Fails
1. Click on failed workflow run
2. Click on failed job
3. Expand failed step
4. Read error message
5. Fix issue and push again

### No Artifact
- Check build completed successfully (green checkmark)
- Look for "Artifacts" section at bottom of workflow run
- Verify build script created `dist/` directory

### Can't Find Actions Tab
- Make sure repository is on GitHub
- Check repository is public (or you have Actions enabled)
- Refresh the page

---

## 💡 Pro Tips

### 1. Build on Tags Only
Save minutes by only building releases:
```yaml
on:
  push:
    tags:
      - 'v*'
```

### 2. Add Build Badge
Show build status in README:
```markdown
![Build](https://github.com/USERNAME/REPO/workflows/Build%20macOS%20Executable/badge.svg)
```

### 3. Download via CLI
```bash
# Install GitHub CLI
gh release download v2.0.0
```

### 4. Auto-increment Version
Use semantic versioning:
- `v2.0.0` - Major release
- `v2.1.0` - New features
- `v2.1.1` - Bug fixes

---

## 📚 Full Documentation

For detailed information, see:
- **`GITHUB_ACTIONS_BUILD_GUIDE.md`** - Complete guide
- **`BUILD_EXECUTABLE_GUIDE.md`** - Build instructions
- **GitHub Actions Docs** - https://docs.github.com/actions

---

## ✅ Verification

Run the setup checker:
```bash
python setup_github_actions.py
```

This verifies:
- ✅ Workflow files exist
- ✅ Build scripts exist
- ✅ Dependencies listed
- ✅ Git configured
- ✅ Ready to push

---

## 🎉 Summary

**You can now build Mac executables without owning a Mac!**

1. ✅ Push code to GitHub
2. ✅ Trigger build (manual or tag)
3. ✅ Wait 5-10 minutes
4. ✅ Download executable
5. ✅ Distribute to users

**It's that simple!** 🚀

---

## 🆘 Need Help?

1. Check `GITHUB_ACTIONS_BUILD_GUIDE.md`
2. View workflow logs on GitHub
3. Search GitHub Actions documentation
4. Open an issue on GitHub

---

**Ready to build? Push to GitHub and go to the Actions tab!** 🎯
