# GitHub Actions Build Guide

## Overview

Use GitHub's **free macOS runners** to automatically build your Mac executable without needing a physical Mac! GitHub Actions provides free build minutes for public repositories.

---

## ✅ What's Included

### Workflow Files Created

1. **`.github/workflows/build-macos.yml`**
   - Builds macOS executable only
   - Triggers on push to main/master or tags
   - Can be manually triggered
   - Free macOS runner

2. **`.github/workflows/build-all-platforms.yml`**
   - Builds both Windows and macOS executables
   - Creates GitHub releases automatically
   - Triggers on version tags (v1.0, v2.0, etc.)
   - Can be manually triggered

---

## 🚀 How to Use

### Method 1: Manual Trigger (Easiest)

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Add GitHub Actions workflows"
   git push origin main
   ```

2. **Go to GitHub Actions:**
   - Navigate to your repository on GitHub
   - Click the "Actions" tab
   - Select "Build macOS Executable" or "Build All Platforms"

3. **Run workflow manually:**
   - Click "Run workflow" button
   - Select branch (usually `main`)
   - Enter version number (e.g., `2.0.0`)
   - Click "Run workflow"

4. **Download the executable:**
   - Wait 5-10 minutes for build to complete
   - Click on the completed workflow run
   - Scroll to "Artifacts" section
   - Download the ZIP file

### Method 2: Automatic on Push

Every time you push to `main` or `master` branch, the macOS build will automatically run:

```bash
git add .
git commit -m "Update bot"
git push origin main
```

The build will start automatically and you can download the artifact from the Actions tab.

### Method 3: Create a Release (Recommended)

This creates a proper GitHub release with downloadable files:

1. **Create and push a version tag:**
   ```bash
   git tag v2.0.0
   git push origin v2.0.0
   ```

2. **GitHub Actions will automatically:**
   - Build Windows executable
   - Build macOS executable
   - Create a GitHub Release
   - Attach both ZIP files to the release

3. **Download from Releases:**
   - Go to your repository
   - Click "Releases" on the right sidebar
   - Download the files from the latest release

---

## 📊 GitHub Actions Free Tier

### What's Free?

| Feature | Public Repos | Private Repos |
|---------|--------------|---------------|
| macOS minutes | 2,000/month | 2,000/month |
| Windows minutes | 2,000/month | 2,000/month |
| Linux minutes | 2,000/month | 2,000/month |
| Storage | 500 MB | 500 MB |
| Artifact retention | 90 days | 90 days |

### Build Time Estimates

- **macOS build:** ~5-10 minutes
- **Windows build:** ~3-5 minutes
- **Both platforms:** ~10-15 minutes

### Monthly Capacity

With 2,000 free minutes:
- **macOS only:** ~200-400 builds/month
- **Both platforms:** ~130-200 builds/month

**More than enough for development and releases!**

---

## 🔧 Workflow Configuration

### Triggers

Both workflows support multiple trigger methods:

```yaml
on:
  # Automatic on push to main
  push:
    branches: [ main, master ]
  
  # Automatic on version tags
  push:
    tags:
      - 'v*'
  
  # Manual trigger
  workflow_dispatch:
    inputs:
      version:
        description: 'Version number'
        required: true
```

### Customization

#### Change Python Version

Edit the workflow file:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Change to 3.9, 3.10, 3.12, etc.
```

#### Change Artifact Retention

Default is 90 days, can be changed:
```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    retention-days: 30  # Change to 7, 30, 90, etc.
```

#### Add Notifications

Add Slack, Discord, or email notifications:
```yaml
- name: Notify on success
  if: success()
  run: |
    curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Build completed!"}' \
    ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## 📝 Step-by-Step Setup

### 1. Prepare Your Repository

Make sure these files exist:
- ✅ `build_mac.sh` (macOS build script)
- ✅ `build_windows.bat` (Windows build script)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `.github/workflows/build-macos.yml` (GitHub Actions workflow)

### 2. Push to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Add GitHub Actions for macOS builds"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/gem-trading-bot.git

# Push
git push -u origin main
```

### 3. Enable GitHub Actions

GitHub Actions should be enabled by default, but verify:
1. Go to repository Settings
2. Click "Actions" in left sidebar
3. Ensure "Allow all actions and reusable workflows" is selected

### 4. Run Your First Build

**Option A: Manual Trigger**
1. Go to Actions tab
2. Select "Build macOS Executable"
3. Click "Run workflow"
4. Enter version: `2.0.0`
5. Click "Run workflow"

**Option B: Create a Tag**
```bash
git tag v2.0.0
git push origin v2.0.0
```

### 5. Monitor the Build

1. Click on the running workflow
2. Watch the build progress in real-time
3. See logs for each step
4. Wait for completion (~5-10 minutes)

### 6. Download the Executable

**From Artifacts:**
1. Scroll to bottom of workflow run
2. Find "Artifacts" section
3. Click to download ZIP file

**From Releases (if using tags):**
1. Go to "Releases" tab
2. Click on latest release
3. Download the ZIP file

---

## 🐛 Troubleshooting

### Build Fails on macOS

**Error:** `Permission denied: build_mac.sh`
**Solution:** Make sure the script is executable:
```yaml
- name: Make script executable
  run: chmod +x build_mac.sh
```

**Error:** `Module not found`
**Solution:** Add missing dependency to `requirements.txt`

### Build Succeeds but No Artifact

**Check:**
1. Look at build logs for errors
2. Verify `dist/` directory was created
3. Check artifact upload step didn't fail

### Workflow Doesn't Trigger

**Check:**
1. Workflow file is in `.github/workflows/` directory
2. File has `.yml` or `.yaml` extension
3. YAML syntax is valid (use YAML validator)
4. Branch name matches trigger (main vs master)

### Out of Minutes

**Solutions:**
1. Check usage: Settings → Billing → Plans and usage
2. Optimize builds (cache dependencies)
3. Build less frequently
4. Use self-hosted runners (free, unlimited)

---

## 🎯 Best Practices

### 1. Use Caching

Speed up builds by caching dependencies:
```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

### 2. Build on Tags Only

For production releases, only build on version tags:
```yaml
on:
  push:
    tags:
      - 'v*'
```

### 3. Test Before Building

Add a test job that runs before building:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: python -m pytest tests/
  
  build:
    needs: test  # Only build if tests pass
    runs-on: macos-latest
    # ... build steps
```

### 4. Use Matrix Builds

Build multiple Python versions:
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```

### 5. Add Build Badges

Show build status in README:
```markdown
![Build Status](https://github.com/yourusername/gem-trading-bot/workflows/Build%20macOS%20Executable/badge.svg)
```

---

## 📦 Advanced: Self-Hosted Runners

For unlimited free builds, use your own Mac:

### Setup

1. **Go to Settings → Actions → Runners**
2. **Click "New self-hosted runner"**
3. **Select macOS**
4. **Follow installation instructions**

### Benefits
- ✅ Unlimited build minutes
- ✅ Faster builds (no queue)
- ✅ Access to local resources
- ✅ Custom software pre-installed

### Drawbacks
- ❌ Requires maintaining a Mac
- ❌ Must keep runner online
- ❌ Security considerations

---

## 🔐 Security Notes

### Secrets

Store sensitive data as GitHub Secrets:
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name and value
4. Use in workflow: `${{ secrets.SECRET_NAME }}`

### Example: Code Signing

For macOS code signing:
```yaml
- name: Import certificate
  env:
    CERTIFICATE_BASE64: ${{ secrets.MACOS_CERTIFICATE }}
    CERTIFICATE_PASSWORD: ${{ secrets.CERTIFICATE_PASSWORD }}
  run: |
    echo $CERTIFICATE_BASE64 | base64 --decode > certificate.p12
    security import certificate.p12 -P $CERTIFICATE_PASSWORD
```

---

## 📊 Monitoring Builds

### View Build History

1. Go to Actions tab
2. See all workflow runs
3. Filter by status, branch, or workflow
4. Click any run to see details

### Build Notifications

Get notified when builds complete:
1. Watch your repository (top right)
2. Settings → Notifications
3. Enable "Actions" notifications

### Build Insights

See usage and trends:
1. Settings → Actions → General
2. View workflow usage
3. See success/failure rates
4. Monitor build times

---

## 🎉 Quick Start Commands

### First Time Setup
```bash
# Add workflows
git add .github/workflows/

# Commit
git commit -m "Add GitHub Actions for automated builds"

# Push
git push origin main
```

### Create a Release
```bash
# Tag the release
git tag v2.0.0

# Push tag
git push origin v2.0.0

# GitHub Actions will automatically:
# 1. Build Windows executable
# 2. Build macOS executable  
# 3. Create GitHub Release
# 4. Upload both files
```

### Manual Build
1. Go to https://github.com/yourusername/gem-trading-bot/actions
2. Click "Build macOS Executable"
3. Click "Run workflow"
4. Enter version and run
5. Download from Artifacts

---

## ✅ Checklist

Before pushing to GitHub:

- [ ] `build_mac.sh` is executable (`chmod +x build_mac.sh`)
- [ ] `requirements.txt` includes all dependencies
- [ ] Workflow files are in `.github/workflows/`
- [ ] YAML syntax is valid
- [ ] Repository is pushed to GitHub
- [ ] GitHub Actions is enabled

After first build:

- [ ] Build completed successfully
- [ ] Artifact was uploaded
- [ ] Downloaded and tested executable
- [ ] Executable runs on macOS
- [ ] Dashboard opens correctly

---

## 📚 Resources

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Workflow Syntax:** https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
- **PyInstaller Docs:** https://pyinstaller.org/
- **macOS Runners:** https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners

---

## 🆘 Support

### Common Issues

1. **Build fails:** Check logs in Actions tab
2. **No artifact:** Verify build completed successfully
3. **Executable doesn't run:** Check macOS version compatibility
4. **Out of minutes:** Use tags to build less frequently

### Getting Help

1. Check workflow logs for errors
2. Review this guide
3. Search GitHub Actions documentation
4. Open an issue on GitHub

---

## 🎯 Summary

✅ **Free macOS builds** with GitHub Actions
✅ **No Mac required** - runs in the cloud
✅ **Automatic builds** on push or tags
✅ **Easy downloads** from Artifacts or Releases
✅ **2,000 free minutes/month** - plenty for development
✅ **Professional releases** with automatic versioning

**You can now build Mac executables without owning a Mac!** 🎉

---

## Next Steps

1. ✅ Push workflows to GitHub
2. ✅ Run your first build
3. ✅ Download and test the executable
4. ✅ Create a release tag for v2.0.0
5. ✅ Share the download link with users

**Your GEM Trading Bot can now be built for macOS automatically!**
