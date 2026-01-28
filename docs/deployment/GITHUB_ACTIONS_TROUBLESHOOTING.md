# GitHub Actions Build Troubleshooting

## Common Issues and Solutions

### ❌ Issue: MetaTrader5 Not Available on macOS

**Error:**
```
ERROR: Could not find a version that satisfies the requirement MetaTrader5>=5.0.47
ERROR: No matching distribution found for MetaTrader5>=5.0.47
```

**Cause:**
MetaTrader5 Python package is **Windows-only**. It's not available on macOS or Linux through pip.

**Solution:** ✅ FIXED
We've created a mock MetaTrader5 module that allows the build to complete on macOS. The workflows now:
1. Create a mock MT5 package
2. Install it during the build
3. Build the executable successfully

**How it works:**
- The `mock_mt5.py` file provides all MT5 constants and functions
- Returns appropriate "not available" messages
- Allows PyInstaller to bundle the code
- The actual MT5 functionality works when run on Windows or via Wine

**Files involved:**
- `mock_mt5.py` - Mock MetaTrader5 module
- `.github/workflows/build-macos.yml` - Updated to use mock
- `.github/workflows/build-all-platforms.yml` - Updated to use mock

---

## Other Common Issues

### ❌ Build Fails: Permission Denied

**Error:**
```
Permission denied: build_mac.sh
```

**Solution:**
The workflow now includes `chmod +x build_mac.sh` before running it.

If you still see this error, ensure the script is committed with execute permissions:
```bash
git update-index --chmod=+x build_mac.sh
git commit -m "Make build script executable"
git push
```

---

### ❌ Build Fails: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
Add the missing module to `requirements.txt`:
```bash
echo "flask>=2.0.0" >> requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push
```

---

### ❌ Build Succeeds but No Artifact

**Symptoms:**
- Build shows green checkmark
- No "Artifacts" section at bottom

**Solution:**
Check the build logs:
1. Click on the workflow run
2. Click on the job (e.g., "build-macos")
3. Expand "Build macOS executable" step
4. Look for errors in the output

Common causes:
- Build script didn't create `dist/` directory
- ZIP creation failed
- Artifact upload step failed

---

### ❌ Executable Doesn't Run on Mac

**Error:**
```
"GEM_Trading_Bot" can't be opened because it is from an unidentified developer
```

**Solution:**
This is normal macOS security. Users need to:
1. Right-click the app
2. Select "Open"
3. Click "Open" in the dialog

Or:
1. System Preferences > Security & Privacy
2. Click "Open Anyway"

**For distribution:**
Consider code signing (requires Apple Developer account $99/year):
```yaml
- name: Code sign
  env:
    CERTIFICATE: ${{ secrets.MACOS_CERTIFICATE }}
  run: |
    # Import certificate
    # Sign the app
    codesign --deep --force --sign "Developer ID" GEM_Trading_Bot.app
```

---

### ❌ Out of GitHub Actions Minutes

**Error:**
```
You have exceeded your GitHub Actions minutes
```

**Solution:**
1. Check usage: Settings → Billing → Plans and usage
2. Wait for monthly reset
3. Optimize builds (use caching)
4. Build less frequently (only on tags)
5. Use self-hosted runner (free, unlimited)

**Optimization:**
```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

---

### ❌ Workflow Doesn't Trigger

**Symptoms:**
- Push code but no build starts
- Actions tab shows no runs

**Solution:**
Check these:

1. **Workflow file location:**
   ```
   .github/workflows/build-macos.yml  ✅ Correct
   github/workflows/build-macos.yml   ❌ Wrong
   .github/workflow/build-macos.yml   ❌ Wrong (singular)
   ```

2. **File extension:**
   ```
   build-macos.yml   ✅ Correct
   build-macos.yaml  ✅ Also correct
   build-macos.txt   ❌ Wrong
   ```

3. **YAML syntax:**
   Use a YAML validator: https://www.yamllint.com/

4. **Branch name:**
   ```yaml
   on:
     push:
       branches: [ main ]  # Must match your branch name
   ```

5. **GitHub Actions enabled:**
   - Settings → Actions → General
   - Ensure "Allow all actions" is selected

---

### ❌ Build Takes Too Long

**Symptoms:**
- Build runs for 20+ minutes
- Times out

**Solution:**

1. **Add caching:**
   ```yaml
   - uses: actions/cache@v3
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
   ```

2. **Reduce dependencies:**
   - Remove unused packages from `requirements.txt`
   - Use lighter alternatives

3. **Optimize build script:**
   - Remove unnecessary steps
   - Parallelize where possible

---

### ❌ ZIP File is Too Large

**Symptoms:**
- Artifact is 500+ MB
- Upload fails

**Solution:**

1. **Exclude unnecessary files:**
   ```python
   # In build script
   excludes = [
       '--exclude-module', 'matplotlib',
       '--exclude-module', 'scipy',
       '--exclude-module', 'PIL',
   ]
   ```

2. **Use UPX compression:**
   ```yaml
   - name: Install UPX
     run: brew install upx
   
   - name: Build with compression
     run: |
       pyinstaller --upx-dir=/usr/local/bin ...
   ```

3. **One-file mode:**
   ```bash
   pyinstaller --onefile ...  # Creates single executable
   ```

---

### ❌ Different Behavior on Mac vs Windows

**Symptoms:**
- Works on Windows
- Fails on Mac

**Cause:**
- Path separators (`\` vs `/`)
- Case-sensitive file systems
- Platform-specific code

**Solution:**
Use cross-platform code:
```python
import os

# ✅ Good
path = os.path.join('src', 'config.py')

# ❌ Bad
path = 'src/config.py'  # Unix only
path = 'src\\config.py'  # Windows only
```

---

## Debugging Tips

### View Full Build Logs

1. Go to Actions tab
2. Click on workflow run
3. Click on job name
4. Expand each step to see output

### Download Build Artifacts Locally

```bash
# Install GitHub CLI
brew install gh  # macOS
# or
choco install gh  # Windows

# Download artifact
gh run download <run-id>
```

### Test Build Script Locally

Before pushing, test the build script:
```bash
# On Mac
chmod +x build_mac.sh
./build_mac.sh

# Check output
ls -la dist/
```

### Enable Debug Logging

Add to workflow:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

---

## Prevention Checklist

Before pushing to GitHub:

- [ ] All files committed
- [ ] `requirements.txt` is complete
- [ ] Build script is executable
- [ ] YAML syntax is valid
- [ ] Tested locally (if possible)
- [ ] Mock MT5 module included
- [ ] Documentation updated

---

## Getting Help

### 1. Check Documentation
- `GITHUB_ACTIONS_BUILD_GUIDE.md` - Complete guide
- `GITHUB_ACTIONS_QUICK_START.md` - Quick reference
- This file - Troubleshooting

### 2. Check Build Logs
- Actions tab → Workflow run → Job → Step logs
- Look for error messages
- Check which step failed

### 3. Search GitHub Issues
- https://github.com/actions/runner/issues
- https://github.com/pyinstaller/pyinstaller/issues

### 4. GitHub Actions Documentation
- https://docs.github.com/en/actions
- https://docs.github.com/en/actions/using-workflows

### 5. Ask for Help
- Open an issue on your repository
- Include:
  - Error message
  - Build logs
  - Workflow file
  - What you've tried

---

## Quick Fixes

### Reset Everything
```bash
# Delete workflows
rm -rf .github/workflows/

# Re-add from backup
git checkout HEAD -- .github/workflows/

# Or recreate
# (copy workflow files again)

# Commit and push
git add .github/workflows/
git commit -m "Reset workflows"
git push
```

### Force Rebuild
```bash
# Make a small change
echo "# trigger build" >> README.md

# Commit and push
git add README.md
git commit -m "Trigger rebuild"
git push
```

### Clear Cache
```yaml
# In workflow, change cache key
- uses: actions/cache@v3
  with:
    key: ${{ runner.os }}-pip-v2-${{ hashFiles('requirements.txt') }}
    #                          ^^^ increment version
```

---

## Summary

### Most Common Issues

1. **MetaTrader5 not available** → ✅ Fixed with mock module
2. **Permission denied** → ✅ Fixed with chmod in workflow
3. **Module not found** → Add to requirements.txt
4. **No artifact** → Check build logs
5. **Workflow doesn't trigger** → Check file location and syntax

### Key Points

- ✅ Mock MT5 module allows macOS builds
- ✅ Workflows handle platform differences
- ✅ Build logs show detailed errors
- ✅ Free tier is generous (2,000 min/month)
- ✅ Documentation is comprehensive

**If you encounter an issue not listed here, check the build logs first!**
