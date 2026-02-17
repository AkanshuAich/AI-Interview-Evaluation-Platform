# Deployment Guide - Render (Free Tier)

This guide will help you deploy the AI Interview Platform to Render for free. Render supports both frontend and backend on a single platform.

## Prerequisites

1. GitHub account
2. Render account (sign up at https://render.com)
3. Google Gemini API key (free from https://makersuite.google.com/app/apikey)
4. Your code pushed to a GitHub repository

## Deployment Steps

### Step 1: Push Code to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/ai-interview-platform.git

# Push to GitHub
git push -u origin main
```

### Step 2: Sign Up for Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with your GitHub account
4. Authorize Render to access your repositories

### Step 3: Deploy Using Blueprint (Easiest Method)

Render will automatically detect the `render.yaml` file and deploy everything.

1. **Go to Render Dashboard**
   - Click "New +" button
   - Select "Blueprint"

2. **Connect Repository**
   - Select your GitHub repository
   - Click "Connect"

3. **Configure Blueprint**
   - Render will read `render.yaml` and show:
     - Backend API service
     - Frontend static site
     - PostgreSQL database
   - Click "Apply"

4. **Add Environment Variables**
   - Go to the backend service
   - Click "Environment"
   - Add `LLM_API_KEY` with your Gemini API key
   - Click "Save Changes"

5. **Wait for Deployment**
   - Backend: ~5-10 minutes
   - Frontend: ~3-5 minutes
   - Database: ~2 minutes

### Step 4: Update CORS Settings

After deployment, update the backend CORS settings:

1. Go to backend service in Render
2. Click "Environment"
3. Update `CORS_ORIGINS` to include your frontend URL:
   ```
   ["https://your-frontend-name.onrender.com"]
   ```
4. Save and wait for redeployment

### Step 5: Test Your Application

1. Open your frontend URL: `https://your-frontend-name.onrender.com`
2. Register a new account
3. Create an interview
4. Test the full flow

## Alternative: Manual Deployment

If you prefer to deploy services individually:

### Deploy Database First

1. Click "New +" → "PostgreSQL"
2. Name: `ai-interview-db`
3. Database: `ai_interview`
4. User: `ai_interview_user`
5. Plan: Free
6. Click "Create Database"
7. Copy the "Internal Database URL"

### Deploy Backend

1. Click "New +" → "Web Service"
2. Connect your repository
3. Configure:
   - **Name**: `ai-interview-backend`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. Add Environment Variables:
   ```
   DATABASE_URL=<paste internal database URL>
   SECRET_KEY=<generate with: openssl rand -hex 32>
   LLM_PROVIDER=gemini
   LLM_API_KEY=<your Gemini API key>
   LLM_MODEL=gemini-1.5-flash
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   CORS_ORIGINS=["https://your-frontend-url.onrender.com"]
   ```

5. Click "Create Web Service"

### Deploy Frontend

1. Click "New +" → "Static Site"
2. Connect your repository
3. Configure:
   - **Name**: `ai-interview-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. Add Environment Variable:
   ```
   VITE_API_BASE_URL=https://your-backend-name.onrender.com
   ```

5. Click "Create Static Site"

## Important Notes

### Free Tier Limitations

- **Backend**: Spins down after 15 minutes of inactivity
  - First request after inactivity takes ~30-60 seconds (cold start)
  - Subsequent requests are fast
- **Database**: 90 days of inactivity before deletion
  - 1GB storage limit
  - Shared CPU
- **Frontend**: Always available (no spin down)

### Cold Start Solutions

To keep backend warm:
1. Use a free uptime monitoring service (UptimeRobot, Cron-job.org)
2. Ping your backend every 10 minutes
3. Or accept the cold start delay

### Custom Domains (Optional)

1. Go to your service settings
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records as instructed

## Troubleshooting

### Backend Won't Start

**Check logs:**
1. Go to backend service
2. Click "Logs" tab
3. Look for errors

**Common issues:**
- Missing environment variables
- Database connection failed
- Migration errors

**Solutions:**
```bash
# If migrations fail, check DATABASE_URL format
# Should be: postgresql://user:password@host:port/database

# Manually run migrations (in Render Shell):
alembic upgrade head
```

### Frontend Can't Connect to Backend

**Check:**
1. `VITE_API_BASE_URL` is set correctly
2. Backend CORS includes frontend URL
3. Backend is running (check service status)

**Fix CORS:**
```python
# In backend environment variables:
CORS_ORIGINS=["https://your-frontend.onrender.com"]
```

### Database Connection Issues

**Check:**
1. DATABASE_URL is the "Internal Database URL"
2. Format: `postgresql+asyncpg://user:password@host:port/database`
3. Database service is running

### Build Failures

**Backend:**
```bash
# Check requirements.txt has all dependencies
# Check Python version matches (3.12)
```

**Frontend:**
```bash
# Check package.json is valid
# Check all dependencies are listed
# Try building locally first: npm run build
```

## Monitoring

### View Logs

**Backend:**
1. Go to backend service
2. Click "Logs"
3. See real-time logs

**Frontend:**
1. Static sites don't have runtime logs
2. Check browser console for errors

### Check Service Health

1. Go to service dashboard
2. See status (Running/Failed)
3. Check recent deploys
4. View metrics (requests, CPU, memory)

## Updating Your App

### Automatic Deploys

Render automatically deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Render will automatically:
# 1. Detect the push
# 2. Build your app
# 3. Deploy new version
```

### Manual Deploy

1. Go to service dashboard
2. Click "Manual Deploy"
3. Select branch
4. Click "Deploy"

## Cost Optimization

### Free Tier Includes:
- ✅ 750 hours/month web service (enough for 1 service 24/7)
- ✅ Unlimited static sites
- ✅ 1GB PostgreSQL database
- ✅ Automatic SSL certificates
- ✅ Automatic deploys from GitHub

### Upgrade When Needed:
- More services: $7/month per service
- Faster database: $7/month
- No cold starts: $7/month
- More storage: $7/month per 10GB

## Security Checklist

- ✅ Never commit `.env` file
- ✅ Use environment variables for secrets
- ✅ Enable HTTPS (automatic on Render)
- ✅ Set strong SECRET_KEY
- ✅ Configure CORS properly
- ✅ Keep dependencies updated

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- GitHub Issues: Create issue in your repo

## Next Steps

After successful deployment:

1. **Test thoroughly**
   - Register users
   - Create interviews
   - Submit answers
   - View reports

2. **Monitor performance**
   - Check logs regularly
   - Monitor error rates
   - Track response times

3. **Set up monitoring**
   - Use UptimeRobot for uptime monitoring
   - Set up error tracking (Sentry)
   - Monitor database usage

4. **Share your app**
   - Share frontend URL
   - Add to portfolio
   - Get feedback

Congratulations! Your AI Interview Platform is now live! 🎉
