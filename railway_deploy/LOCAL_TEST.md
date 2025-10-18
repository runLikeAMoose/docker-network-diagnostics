# Test Locally - Step by Step

## Quick Start (2 minutes)

### 1. Create Virtual Environment

```bash
cd railway_deploy

# Create venv
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
# Option A: Using uvicorn directly
uvicorn main:app --reload --port 8000

# Option B: Using Python
python main.py
```

### 4. Open in Browser

Visit: **http://localhost:8000**

You should see:
- 🐳 Beautiful Tailwind CSS interface
- 6 interactive diagnostic mode cards
- Live terminal with WebSocket connection
- Mobile-responsive design

### 5. Test Features

Click any button:
- **Full Diagnostic** - See complete network analysis
- **Guided Wizard** - Step-by-step troubleshooting
- **Live Monitor** - Real-time connection visualization
- **Quick Health Check** - Fast validation
- **Network Topology** - Visual architecture
- **Clear & Restart** - Reset terminal

### 6. Stop Server

Press `Ctrl+C` in terminal

### 7. Deactivate Virtual Environment

```bash
deactivate
```

---

## Complete Commands (Copy-Paste)

```bash
# Setup
cd railway_deploy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
uvicorn main:app --reload

# Open browser to http://localhost:8000

# When done: Ctrl+C to stop, then:
deactivate
```

---

## What You Should See

### In Terminal:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### In Browser:
- Gradient header with Docker logo
- "Connected" status (green)
- 6 colorful diagnostic mode cards
- Terminal window with output
- Input field at bottom
- Beautiful dark theme with Tailwind CSS

---

## Troubleshooting

### "Port 8000 already in use"
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### "WebSocket connection failed"
- Make sure uvicorn is running
- Refresh the page
- Check browser console for errors

### Static files not loading
- Make sure you're in `railway_deploy` directory
- Check that `static/` folder exists
- Restart uvicorn with `--reload`

---

## File Structure

```
railway_deploy/
├── main.py                  # FastAPI server
├── requirements.txt         # Dependencies
├── venv/                    # Virtual environment (created)
└── static/
    ├── index.html          # Main page (Tailwind CSS)
    └── js/
        └── app.js          # WebSocket client
```

---

## Next: Deploy to Railway

Once local testing works, deploy with:

```bash
# Option 1: Railway CLI
railway login
railway init
railway up

# Option 2: Railway Web
# Go to railway.app
# Deploy from GitHub
# Set root directory to: railway_deploy
```

---

## Bonus: Test Both Versions

You can run both the CLI and web version:

**Terminal 1 - CLI version:**
```bash
cd ..  # Go to docker_play root
python3 docker_network_debug.py
```

**Terminal 2 - Web version:**
```bash
cd railway_deploy
source venv/bin/activate
uvicorn main:app --reload
```

Compare the experiences! 🚀
