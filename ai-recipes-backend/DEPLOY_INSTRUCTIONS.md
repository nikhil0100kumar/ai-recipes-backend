# 🚀 Deploy to Render.com (FREE) - Step by Step Guide

## Prerequisites
✅ Your Gemini API Key (which you already have)
✅ A GitHub account (free if you don't have one)

## Step 1: Upload Your Code to GitHub

### Option A: Using GitHub Website (Easiest)
1. Go to https://github.com and sign in
2. Click the "+" icon in top right → "New repository"
3. Name it: `ai-recipes-backend`
4. Make it PUBLIC (important for free hosting)
5. Click "Create repository"
6. Click "uploading an existing file"
7. Drag and drop ALL files from `ai-recipes-backend` folder:
   - main.py
   - config.py
   - gemini_service.py
   - models.py
   - requirements.txt
   - render.yaml
   - runtime.txt
   - start.py
   - Dockerfile (optional)
8. Click "Commit changes"

### Option B: Using Git Commands
```bash
cd C:\Users\nikhil\Desktop\ai-recipes\ai-recipes-backend
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-recipes-backend.git
git push -u origin main
```

## Step 2: Deploy on Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up using your GitHub account (easiest)
4. Click "New +" → "Web Service"
5. Connect your GitHub repository:
   - Click "Connect GitHub"
   - Authorize Render
   - Select your `ai-recipes-backend` repository
6. Fill in the details:
   - **Name**: `ai-recipes-backend` (or any name you like)
   - **Region**: Choose closest to you
   - **Branch**: main
   - **Root Directory**: leave empty
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: FREE

7. Add Environment Variables (IMPORTANT!):
   - Click "Advanced" 
   - Add Environment Variable:
     - Key: `GEMINI_API_KEY`
     - Value: `AIzaSyDbdmxvF8ZRaKih0M22bPgImdc35D7-ccA` (your actual key)

8. Click "Create Web Service"

## Step 3: Wait for Deployment
- Render will build and deploy your app (takes 5-10 minutes)
- You'll see logs showing the progress
- When done, you'll get a URL like: `https://ai-recipes-backend.onrender.com`

## Step 4: Update Your Flutter App

Once deployed, update your Flutter app to use the new backend URL:

1. Open `lib/services/backend_service.dart` in your Flutter app
2. Change the baseUrl from `http://localhost:8001` to your Render URL
3. Example: `https://ai-recipes-backend.onrender.com`

## 🎉 That's it! Your backend is now live and FREE!

## Important Notes:
- Free tier spins down after 15 minutes of inactivity (first request will be slow)
- 750 free hours per month (enough for 24/7 if it's your only app)
- Your API key is secure (only visible to you in Render dashboard)

## Test Your Deployed Backend:
Visit: `https://YOUR-APP-NAME.onrender.com/health`
You should see: `{"status":"healthy","service":"AI Recipes Backend","version":"1.0.0"}`