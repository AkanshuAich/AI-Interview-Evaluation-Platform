# 🚀 Quick Deploy Guide (5 Minutes)

Deploy your AI Interview Platform to Render for FREE!

## Prerequisites
- ✅ GitHub account
- ✅ Gemini API key (free from https://makersuite.google.com/app/apikey)

## Steps

### 1️⃣ Push to GitHub (2 min)
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2️⃣ Deploy on Render (3 min)

1. **Sign up**: https://render.com (use GitHub login)

2. **Create Blueprint**:
   - Click "New +" → "Blueprint"
   - Select your repository
   - Click "Connect"
   - Click "Apply" (Render reads `render.yaml` automatically)

3. **Add API Key**:
   - Go to backend service
   - Click "Environment"
   - Add: `LLM_API_KEY` = `your-gemini-api-key`
   - Click "Save Changes"

4. **Wait** (~10 minutes for first deploy)

### 3️⃣ Done! 🎉

Your app is live at:
- **Frontend**: `https://ai-interview-frontend.onrender.com`
- **Backend**: `https://ai-interview-backend.onrender.com`

## What You Get (FREE)

✅ Full-stack app deployed
✅ PostgreSQL database
✅ Automatic HTTPS
✅ Auto-deploy on git push
✅ 750 hours/month (enough for 24/7)

## Important Notes

⚠️ **Cold Starts**: Backend sleeps after 15 min inactivity
- First request takes 30-60 seconds
- Solution: Use free uptime monitor (UptimeRobot)

⚠️ **Update CORS**: After deploy, update backend CORS:
```
CORS_ORIGINS=["https://your-actual-frontend-url.onrender.com"]
```

## Troubleshooting

**Backend won't start?**
- Check logs in Render dashboard
- Verify all environment variables are set
- Check DATABASE_URL format

**Frontend can't connect?**
- Verify `VITE_API_BASE_URL` points to backend
- Check backend CORS includes frontend URL
- Ensure backend is running

**Need help?**
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed guide
- Check Render docs: https://render.com/docs

## Next Steps

1. Test your app thoroughly
2. Share the URL
3. Set up uptime monitoring
4. Add custom domain (optional)

Happy deploying! 🚀
