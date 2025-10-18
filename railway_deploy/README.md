# Railway Deployment for Docker Network Diagnostics

Web-based interface for the Docker Network Diagnostic Tool, deployable to Railway.

## Quick Deploy to Railway

### Option 1: Deploy with Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize and deploy
railway init
railway up
```

### Option 2: Deploy via GitHub

1. Push this directory to a GitHub repository
2. Go to [Railway](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect the configuration
6. Your app will be live in ~2 minutes!

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000

## Environment Variables

No environment variables required! The app works out of the box.

Optional:
- `PORT` - Port to run on (default: 8000, Railway sets this automatically)

## Features

- ✅ Mobile-responsive web terminal interface
- ✅ Real-time WebSocket communication
- ✅ Beautiful dark theme optimized for code
- ✅ Interactive buttons for all diagnostic modes
- ✅ ANSI color code rendering
- ✅ Auto-reconnection on disconnect
- ✅ Works on phones, tablets, and desktops

## Testing After Deployment

Once deployed, share the Railway URL with your friend. They can:

1. Open the URL on any device (including phone)
2. Click any diagnostic mode button
3. See real-time diagnostic output
4. Type custom commands
5. Share the URL during the interview

## Customization

### Change Theme Colors

Edit the CSS in `main.py` (lines ~60-200) to customize:
- Background colors
- Accent colors
- Button styles
- Terminal appearance

### Add Real Docker Integration

If deploying to a server with Docker installed:

1. Uncomment the Docker detection logic
2. Set `use_real_docker = True` in the demo functions
3. Add Docker socket mounting if using Railway containers

## Troubleshooting

### WebSocket Connection Fails

Railway provides both HTTP and WebSocket support. If WS fails:
- Check that your Railway service is running
- Verify the domain is correctly set
- Check browser console for errors

### Port Already in Use (Local)

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn main:app --port 8001
```

## Architecture

```
┌─────────────┐
│   Browser   │ ← User accesses via phone/laptop
└──────┬──────┘
       │ WebSocket
       ▼
┌─────────────┐
│  FastAPI    │ ← Railway hosts this
│  + Uvicorn  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Diagnostic  │ ← Demo mode (mock data)
│   Engine    │
└─────────────┘
```

## Cost

Railway offers:
- $5/month for hobby plan
- Free tier with 500 hours/month
- Perfect for demos and interviews

## Production Considerations

For a real production deployment:

1. Add authentication (basic auth, OAuth, etc.)
2. Rate limiting on WebSocket connections
3. Session management for multiple users
4. Database for storing diagnostic history
5. Metrics and monitoring
6. Docker daemon access (if using real containers)

## Interview Tips

When demonstrating this during the interview:

1. Open the URL on your phone to show it works anywhere
2. Walk through each diagnostic mode
3. Explain how this solves the pain points in the assignment
4. Discuss how you'd integrate this into Docker Desktop GUI
5. Talk about the MLP scope and what you'd build first

## Support

Questions? Check the main README.md in the parent directory.
