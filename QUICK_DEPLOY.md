# 🚀 QUICK DEPLOY GUIDE - GET YOUR BACKEND ONLINE IN 10 MINUTES!

## 📍 You Are Here
✅ Your backend code is ready
✅ Git is initialized
✅ All files are committed
🔄 Now you need to push to GitHub and deploy

## 🎯 STEP 1: Create GitHub Repository (2 minutes)

1. **Open your browser** and go to: https://github.com
2. **Sign in** (or create a free account if you don't have one)
3. Click the **green "New" button** or **"+" icon → New repository**
4. Fill in:
   - Repository name: `ai-recipes-backend`
   - Description: "Backend for AI Recipes app"
   - **IMPORTANT**: Choose **PUBLIC** (required for free hosting)
   - ⚠️ **DON'T** check "Initialize with README" (you already have files)
5. Click **"Create repository"**
6. **KEEP THIS PAGE OPEN** - you'll see commands, but use mine below instead

## 🎯 STEP 2: Push Your Code to GitHub (1 minute)

Copy and run these commands ONE BY ONE in your terminal:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ai-recipes-backend.git
git push -u origin main
```

⚠️ **REPLACE** `YOUR_GITHUB_USERNAME` with your actual GitHub username!

Example: If your GitHub username is `nikhil123`, the command would be:
```bash
git remote add origin https://github.com/nikhil123/ai-recipes-backend.git
```

**Note:** You might need to login - a browser window will open for authentication.

## 🎯 STEP 3: Deploy on Render.com (5 minutes)

### 3.1 Sign Up for Render
1. Go to: https://render.com
2. Click **"Get Started for Free"**
3. **IMPORTANT**: Click **"Continue with GitHub"** (easiest option!)
4. Authorize Render to access your GitHub

### 3.2 Create Your Web Service
1. Click **"New +"** button → **"Web Service"**
2. You'll see your repositories - Select **`ai-recipes-backend`**
3. If you don't see it, click **"Configure account"** and grant access

### 3.3 Configure Settings
Fill in these EXACT settings:

- **Name**: `ai-recipes-backend` (or any name you want)
- **Region**: Choose the closest to you
- **Branch**: `main`
- **Root Directory**: (leave empty)
- **Runtime**: **Python 3**
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

### 3.4 Choose FREE Plan
- Scroll down to **"Instance Type"**
- Select **"Free"** ($0.00 / month)

### 3.5 Add Your API Key (CRITICAL!)
1. Click **"Advanced"** button
2. Click **"Add Environment Variable"**
3. Add:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: `AIzaSyDbdmxvF8ZRaKih0M22bPgImdc35D7-ccA`
   (This is your actual API key from the .env file)

### 3.6 Deploy!
Click **"Create Web Service"** button at the bottom

## 🎯 STEP 4: Wait and Watch (5-10 minutes)

1. Render will show you logs as it builds
2. Wait for: **"Your service is live 🎉"**
3. Your URL will be shown at the top, like:
   ```
   https://ai-recipes-backend.onrender.com
   ```

## 🎯 STEP 5: Test Your Backend

1. Copy your Render URL
2. Add `/health` to it
3. Visit in browser: `https://ai-recipes-backend.onrender.com/health`
4. You should see:
   ```json
   {"status":"healthy","service":"AI Recipes Backend","version":"1.0.0"}
   ```

## 🎯 STEP 6: Update Your Flutter App

1. Go back to your Flutter project
2. Open: `lib/services/backend_service.dart`
3. Find this line:
   ```dart
   final String baseUrl = 'http://localhost:8001';
   ```
4. Change it to your Render URL:
   ```dart
   final String baseUrl = 'https://ai-recipes-backend.onrender.com';
   ```
5. Save and run your Flutter app again!

## ✅ DONE! Your AI is now LIVE!

## 🆘 Troubleshooting

### "Permission denied" when pushing to GitHub?
- Make sure you're logged in to GitHub in your browser
- Try: `git push -u origin main --force`

### "Build failed" on Render?
- Check the logs for errors
- Make sure all files are pushed to GitHub
- Verify the GEMINI_API_KEY environment variable is set

### Backend not responding?
- Free tier sleeps after 15 mins - first request takes 30-50 seconds to wake up
- This is normal for free hosting!

## 📝 Important Notes
- **Free = Slow Start**: First request after inactivity will be slow (30-50 seconds)
- **Always On**: Stays awake as long as it gets requests every 15 minutes
- **Secure**: Your API key is encrypted and safe on Render

## 🎉 Congratulations!
Your backend is now:
- ✅ Live on the internet
- ✅ Accessible from anywhere
- ✅ Ready for real AI analysis
- ✅ Completely FREE!

Need help? The error messages are usually helpful - read them carefully!