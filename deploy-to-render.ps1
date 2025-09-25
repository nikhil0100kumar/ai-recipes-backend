# Render Deployment Script for AI Recipes Backend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AI Recipes Backend - Render Deploy   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "render.yaml")) {
    Write-Host "Error: render.yaml not found in current directory!" -ForegroundColor Red
    Write-Host "Please run this script from the ai-recipes-backend directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Checking Git status..." -ForegroundColor Green
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "Warning: You have uncommitted changes:" -ForegroundColor Yellow
    Write-Host $gitStatus
    $commit = Read-Host "Do you want to commit and push these changes? (y/n)"
    if ($commit -eq 'y') {
        $message = Read-Host "Enter commit message"
        git add -A
        git commit -m $message
        git push origin main
        Write-Host "Changes pushed to GitHub!" -ForegroundColor Green
    }
} else {
    Write-Host "Git repository is clean." -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Deployment Instructions" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Since your code is already on GitHub with render.yaml, you can deploy using one of these methods:" -ForegroundColor White
Write-Host ""
Write-Host "METHOD 1: Automatic Deployment (Recommended)" -ForegroundColor Yellow
Write-Host "--------------------------------------------" -ForegroundColor Gray
Write-Host "1. Go to: https://dashboard.render.com/blueprints" -ForegroundColor White
Write-Host "2. Click 'New Blueprint Instance'" -ForegroundColor White
Write-Host "3. Connect your GitHub account if not already connected" -ForegroundColor White
Write-Host "4. Select repository: nikhil0100kumar/ai-recipes-backend" -ForegroundColor White
Write-Host "5. Render will automatically detect your render.yaml file" -ForegroundColor White
Write-Host "6. Click 'Apply' to deploy" -ForegroundColor White
Write-Host ""
Write-Host "METHOD 2: Manual Service Creation" -ForegroundColor Yellow
Write-Host "---------------------------------" -ForegroundColor Gray
Write-Host "1. Go to: https://dashboard.render.com/create?type=web" -ForegroundColor White
Write-Host "2. Connect your GitHub repository: nikhil0100kumar/ai-recipes-backend" -ForegroundColor White
Write-Host "3. Use these settings:" -ForegroundColor White
Write-Host "   - Name: ai-recipes-backend" -ForegroundColor Gray
Write-Host "   - Runtime: Docker" -ForegroundColor Gray
Write-Host "   - Branch: main" -ForegroundColor Gray
Write-Host "   - Plan: Free" -ForegroundColor Gray
Write-Host "4. Add environment variables:" -ForegroundColor White
Write-Host "   - GEMINI_API_KEY: (your API key)" -ForegroundColor Gray
Write-Host "   - DEBUG: false" -ForegroundColor Gray
Write-Host "   - ALLOWED_ORIGINS: *" -ForegroundColor Gray
Write-Host "5. Click 'Create Web Service'" -ForegroundColor White
Write-Host ""
Write-Host "METHOD 3: Using Render API (Advanced)" -ForegroundColor Yellow
Write-Host "-------------------------------------" -ForegroundColor Gray
Write-Host "If you have a Render API key, press Enter to continue with API deployment" -ForegroundColor White
Write-Host "Otherwise, press Ctrl+C to exit and use one of the methods above" -ForegroundColor White
Write-Host ""
$continue = Read-Host "Press Enter to continue with API deployment or Ctrl+C to exit"

# API Deployment
Write-Host ""
Write-Host "Step 3: API Deployment" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Cyan
$apiKey = Read-Host "Enter your Render API key (or press Enter to skip)" -AsSecureString

if ($apiKey.Length -gt 0) {
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
    $apiKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    
    Write-Host "Creating service via Render API..." -ForegroundColor Yellow
    
    $headers = @{
        "Authorization" = "Bearer $apiKeyPlain"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        "type" = "web"
        "name" = "ai-recipes-backend"
        "runtime" = "docker"
        "repo" = "https://github.com/nikhil0100kumar/ai-recipes-backend"
        "autoDeploy" = "yes"
        "branch" = "main"
        "envVars" = @(
            @{
                "key" = "DEBUG"
                "value" = "false"
            },
            @{
                "key" = "ALLOWED_ORIGINS"
                "value" = "*"
            }
        )
        "plan" = "free"
    } | ConvertTo-Json -Depth 10
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.render.com/v1/services" -Method Post -Headers $headers -Body $body
        Write-Host "Service created successfully!" -ForegroundColor Green
        Write-Host "Service ID: $($response.service.id)" -ForegroundColor Cyan
        Write-Host "Service URL: https://$($response.service.name).onrender.com" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Note: Don't forget to add your GEMINI_API_KEY in the Render dashboard!" -ForegroundColor Yellow
    } catch {
        Write-Host "Error creating service: $_" -ForegroundColor Red
        Write-Host "Please use one of the manual methods above." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "No API key provided. Please use one of the manual methods above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "         Deployment Complete!           " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your repository is ready for deployment!" -ForegroundColor Green
Write-Host "GitHub: https://github.com/nikhil0100kumar/ai-recipes-backend" -ForegroundColor Cyan
Write-Host ""
Write-Host "After deployment, your backend will be available at:" -ForegroundColor White
Write-Host "https://ai-recipes-backend.onrender.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "Remember to:" -ForegroundColor Yellow
Write-Host "1. Add your GEMINI_API_KEY in Render dashboard environment variables" -ForegroundColor White
Write-Host "2. Wait 2-5 minutes for the initial deployment to complete" -ForegroundColor White
Write-Host "3. The free tier may take 30-50 seconds to wake up after inactivity" -ForegroundColor White