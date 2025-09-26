# 🚀 AI Recipes Backend - Deployment Guide (FIXED)

## ✅ Issue Resolution Summary

The deployment error you encountered:
```
error: failed to solve: failed to read dockerfile: read /home/user/.local/tmp/buildkit-mount825796518/src: is a directory
```

**Was caused by:** A nested directory structure with duplicate files that confused Render's build system.

**Solution Applied:**
1. ✅ Removed nested `ai-recipes-backend/ai-recipes-backend/` directory
2. ✅ Updated Dockerfile to use dynamic PORT from Render
3. ✅ Added explicit Docker configuration to render.yaml
4. ✅ Pushed changes to GitHub

## 📋 Current Project Structure (CORRECT)
```
ai-recipes-backend/
├── Dockerfile              # Docker configuration
├── render.yaml            # Render deployment config
├── requirements.txt       # Python dependencies
├── main.py               # FastAPI application
├── config.py             # Configuration management
├── models.py             # Data models
├── gemini_service.py     # Gemini API service
├── .env                  # Local environment variables
├── .env.example          # Environment template
└── .gitignore           # Git ignore rules
```

## 🔧 Key Configuration Files

### 1. Dockerfile (UPDATED)
- Uses Python 3.11-slim base image
- Properly handles Render's dynamic PORT environment variable
- Includes health check for monitoring
- Runs as non-root user for security

### 2. render.yaml (UPDATED)
```yaml
services:
  - type: web
    name: ai-recipes-backend
    runtime: docker
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
```

## 📝 Deployment Steps for Render

### Method 1: Using Render Dashboard (Recommended)

1. **Go to Render Dashboard**
   - Navigate to: https://dashboard.render.com
   - Sign in with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect to GitHub if not already connected
   - Select repository: `nikhil0100kumar/ai-recipes-backend`

3. **Configure Service Settings**
   - **Name:** ai-recipes-backend
   - **Region:** Choose closest to you (Oregon, Frankfurt, Singapore)
   - **Branch:** main
   - **Root Directory:** Leave empty (repository root)
   - **Runtime:** Docker (should auto-detect from Dockerfile)

4. **Environment Variables** (CRITICAL)
   Add these in the dashboard:
   - `GEMINI_API_KEY` = `AIzaSyDbdmxvF8ZRaKih0M22bPgImdc35D7-ccA`
   - `DEBUG` = `false`
   - `ALLOWED_ORIGINS` = `*`

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build and deployment

### Method 2: Using Render Blueprint

1. **Use render.yaml directly**
   - Go to: https://dashboard.render.com/blueprints
   - Click "New Blueprint Instance"
   - Select your repository
   - Render will use the render.yaml configuration

2. **Add Secret Environment Variable**
   - In the dashboard, add `GEMINI_API_KEY` as a secret

## 🧪 Testing Your Deployment

### Local Docker Test (Optional but Recommended)
```powershell
# Run the test script
.\test_docker_locally.ps1
```

### After Render Deployment
1. **Check deployment logs** in Render dashboard
2. **Test health endpoint:**
   ```
   https://your-service-name.onrender.com/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "AI Recipes Backend",
     "version": "1.0.0"
   }
   ```

3. **Test with cURL:**
   ```bash
   curl https://your-service-name.onrender.com/health
   ```

## 🔗 Connecting Flutter Frontend

Once deployed, update your Flutter app:

1. Open `ai_recipes/lib/services/backend_service.dart`
2. Update the base URL:
   ```dart
   final String baseUrl = 'https://ai-recipes-backend.onrender.com';
   ```

## ⚠️ Important Notes

### Free Tier Limitations
- **Spin-down:** Service sleeps after 15 minutes of inactivity
- **Cold start:** First request after sleep takes 30-60 seconds
- **Monthly limit:** 750 free hours (enough for one 24/7 service)
- **Solution:** Consider implementing a keep-alive mechanism or upgrading to paid tier

### Security Considerations
- **API Key:** Never commit API keys to Git
- **CORS:** Currently set to `*` for development; restrict in production
- **Rate Limiting:** Currently using in-memory; implement Redis for production

### Performance Optimization
- Docker image is optimized with multi-stage build considerations
- Health checks ensure service availability
- Proper error handling and logging implemented

## 📊 Monitoring

### Render Dashboard Metrics
- CPU usage
- Memory consumption
- Request count
- Response times
- Error logs

### Application Logs
Check logs in Render dashboard or use:
```bash
# View recent logs
https://dashboard.render.com/web/[your-service-id]/logs
```

## 🐛 Troubleshooting

### If deployment fails:
1. Check Render build logs for specific errors
2. Ensure GitHub repository is public or Render has access
3. Verify all environment variables are set
4. Check Dockerfile syntax is correct
5. Ensure no nested directories exist

### Common Issues:
- **Port binding:** Ensure using `${PORT:-8000}` in CMD
- **Module not found:** Check requirements.txt is complete
- **API key error:** Verify GEMINI_API_KEY is set in environment

## 🎉 Success Indicators

Your backend is successfully deployed when:
- ✅ Build completes without errors in Render
- ✅ Service shows "Live" status
- ✅ Health endpoint returns 200 OK
- ✅ No errors in deployment logs
- ✅ Can analyze images through the API

## 📧 Support

If you encounter issues:
1. Check Render documentation: https://render.com/docs
2. Review application logs in Render dashboard
3. Verify all configuration files match this guide
4. Test locally with Docker first

---

**Last Updated:** December 2024
**Repository:** https://github.com/nikhil0100kumar/ai-recipes-backend
**Expected Live URL:** https://ai-recipes-backend.onrender.com