# How to Restart and See New Changes

## Quick Restart (Do This Now!)

```bash
# 1. Stop any running server
pkill -f "uvicorn main:app"

# 2. Go to railway_deploy directory
cd /Users/petermoore/Desktop/Code/docker_play/railway_deploy

# 3. Activate virtual environment
source venv/bin/activate

# 4. Start server with latest code
uvicorn main:app --reload --port 8000

# 5. Open browser
# Visit: http://localhost:8000
```

## Why You Need to Restart

The code changes are on disk but the server is running the old code in memory.

**What happens when you restart:**
- Server reads new code
- New animations will work
- Enhanced topology will display
- Spinners will rotate
- Progress bars will fill

## Browser Cache (If Still Not Working)

If you restart but still see old output:

**Option 1: Hard Refresh**
- Chrome/Firefox: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Safari: `Cmd+Option+R`

**Option 2: Clear Cache**
- Open DevTools (F12)
- Right-click refresh button
- Select "Empty Cache and Hard Reload"

**Option 3: Incognito/Private Window**
- Open new incognito window
- Go to http://localhost:8000
- Should see new code

## Verify Latest Code

Check you're running latest:

```bash
cd /Users/petermoore/Desktop/Code/docker_play
git log --oneline -1
```

Should show:
```
b413403 Fix animations to actually display in terminal
```

## Common Issues

### "Address already in use"
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Then restart
uvicorn main:app --reload
```

### "Module not found"
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall if needed
pip install -r requirements.txt
```

### Changes Still Not Showing
```bash
# Check you're in right directory
pwd
# Should be: /Users/petermoore/Desktop/Code/docker_play/railway_deploy

# Check file has latest changes
grep "type.*animate" main.py
# Should find matches if code is updated
```

## Testing Animations

After restart, in browser:

**Test 1: Full Diagnostic**
- Type `1` and press Enter
- Should see spinner: ◐ ◓ ◑ ◒ rotating
- Then progress bar filling: 0% → 100%

**Test 2: Live Monitor**
- Type `3` and press Enter
- Should see bars changing every 500ms

**Test 3: Topology**
- Type `5` and press Enter
- Should see centered, emoji-enhanced topology

## What You'll See (After Restart)

```
> 1

═══════════════════════════════════════════════
        Docker Network Diagnostics
═══════════════════════════════════════════════

▼ System Check

◐ Detecting Docker daemon...         ← THIS WILL SPIN!

(then changes to)

✓ Docker is installed and running

▼ Container Discovery

[████░░░░░░░░] 20% Scanning...       ← THIS FILLS UP!
[████████░░░░] 40% Scanning...
[████████████] 60% Scanning...

✓ Scan complete

Discovered 5 containers:
  ● web-app            172.18.0.2      Ports: 8080:80
  ...
```

## One-Line Restart Command

```bash
cd /Users/petermoore/Desktop/Code/docker_play/railway_deploy && source venv/bin/activate && uvicorn main:app --reload
```

Copy and paste this ⬆️ to restart quickly!
