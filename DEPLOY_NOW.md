# Deploy to Railway - Quick Commands

## Option 1: Railway CLI (Run These Commands)

```bash
cd railway_deploy

# Login (opens browser)
railway login

# Create new project
railway init

# Deploy
railway up

# Get the URL
railway domain
```

That's it! You'll have a live URL in ~2 minutes.

---

## Option 2: Railway Web UI (Even Easier!)

1. Go to: https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select: `runLikeAMoose/docker-network-diagnostics`
4. **Important:** Set "Root Directory" to: `railway_deploy`
5. Click "Deploy"
6. Wait ~2 minutes
7. Click "Generate Domain" to get public URL

**That's the easiest method!** ⬆️

---

## Option 3: One-Click Deploy Button

Add this to your GitHub README to let anyone deploy with one click:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/docker-diagnostics?referralCode=docker)

---

## After Deployment

Once deployed, you'll get a URL like:
```
https://docker-diagnostics-production.up.railway.app
```

**Test it:**
1. Open URL on your laptop ✅
2. Open URL on your phone ✅
3. Click the diagnostic buttons ✅
4. See it work in real-time ✅

**Share with your friend:**
- Send them the Railway URL
- They can demo it during the interview from their phone
- Perfect for showing product thinking!

---

## Cost

Railway free tier includes:
- $5 free credit per month
- 500 hours of usage
- Perfect for demos and interviews
- Can delete after interview if needed

---

## Troubleshooting

**"Root directory not set"**
- In Railway dashboard, go to Settings
- Set "Root Directory" to `railway_deploy`
- Redeploy

**"Build failed"**
- Check Railway logs in dashboard
- Make sure Python 3.11+ is available
- Verify requirements.txt is correct

**"WebSocket connection failed"**
- Make sure deployment is active (not sleeping)
- Check that HTTPS is working
- Railway provides both HTTP and WS automatically

---

## Next: Test Your Deployment

After deploying, test these features:
- [ ] Click "Full Network Diagnostic" button
- [ ] Click "Guided Wizard" button
- [ ] Click "Quick Health Check" button
- [ ] Test on mobile phone
- [ ] Share URL with friend

You're ready! 🚀
