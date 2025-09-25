@echo off
cls
echo =============================================
echo    AI RECIPES BACKEND - DEPLOYMENT SCRIPT
echo =============================================
echo.
echo What is your GitHub repository name?
echo (The exact name you created on GitHub)
echo.
set /p repo_name="Enter repository name: "
echo.
echo Adding GitHub remote for: %repo_name%
git remote remove origin 2>nul
git remote add origin https://github.com/nikhil0100kumar/%repo_name%.git
echo.
echo Pushing code to GitHub...
git push -u origin main
echo.
if %ERRORLEVEL% NEQ 0 (
    echo Authentication required. Trying with force push...
    git push -u origin main --force
)
echo.
echo =============================================
echo    CODE PUSHED! Now deploy on Render.com
echo =============================================
echo.
echo NEXT STEPS:
echo 1. Open https://render.com in your browser
echo 2. Sign in with GitHub
echo 3. Click "New +" then "Web Service"
echo 4. Select your repository: %repo_name%
echo 5. Configure:
echo    - Runtime: Python 3
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
echo    - Environment Variable:
echo      GEMINI_API_KEY = AIzaSyDbdmxvF8ZRaKih0M22bPgImdc35D7-ccA
echo 6. Select FREE tier
echo 7. Click "Create Web Service"
echo.
echo Press any key to open Render.com...
pause >nul
start https://render.com