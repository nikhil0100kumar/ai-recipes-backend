# PowerShell script to deploy to Render via GitHub

Write-Host "=== AI Recipes Backend Deployment Script ===" -ForegroundColor Green
Write-Host ""

# Step 1: Check if repository exists
Write-Host "Step 1: Checking GitHub repository..." -ForegroundColor Yellow
$repoName = Read-Host "Enter your GitHub repository name (e.g., ai-recipes-backend)"
$githubUsername = "nikhil0100kumar"

# Step 2: Add remote if not exists
Write-Host "Step 2: Setting up Git remote..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin "https://github.com/$githubUsername/$repoName.git"
Write-Host "Remote added: https://github.com/$githubUsername/$repoName.git" -ForegroundColor Green

# Step 3: Push to GitHub
Write-Host "Step 3: Pushing code to GitHub..." -ForegroundColor Yellow
git add .
git commit -m "Update for deployment" 2>$null
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Code pushed successfully!" -ForegroundColor Green
} else {
    Write-Host "Note: You may need to authenticate with GitHub" -ForegroundColor Yellow
    Write-Host "A browser window might open for authentication" -ForegroundColor Yellow
    git push -u origin main --force
}

Write-Host ""
Write-Host "=== Next Steps for Render Deployment ===" -ForegroundColor Cyan
Write-Host "1. Go to: https://render.com" -ForegroundColor White
Write-Host "2. Sign in with GitHub" -ForegroundColor White
Write-Host "3. Click 'New +' -> 'Web Service'" -ForegroundColor White
Write-Host "4. Select your repository: $repoName" -ForegroundColor White
Write-Host "5. Use these settings:" -ForegroundColor White
Write-Host "   - Runtime: Python 3" -ForegroundColor Gray
Write-Host "   - Build: pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "   - Start: uvicorn main:app --host 0.0.0.0 --port `$PORT" -ForegroundColor Gray
Write-Host "   - Add env variable: GEMINI_API_KEY = AIzaSyDbdmxvF8ZRaKih0M22bPgImdc35D7-ccA" -ForegroundColor Gray
Write-Host "6. Choose FREE tier and deploy!" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open Render.com in your browser..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
Start-Process 'https://render.com'
