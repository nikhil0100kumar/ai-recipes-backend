# Test Docker deployment locally
Write-Host "=== Testing Docker Deployment Locally ===" -ForegroundColor Green
Write-Host ""

# Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t ai-recipes-backend .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker image built successfully!" -ForegroundColor Green
Write-Host ""

# Run Docker container
Write-Host "Starting Docker container..." -ForegroundColor Yellow
docker run -d `
    --name ai-recipes-test `
    -p 8000:8000 `
    -e GEMINI_API_KEY="AIzaSyDbdmxvF8ZRaKih0M22bPgImdc35D7-ccA" `
    -e PORT=8000 `
    ai-recipes-backend

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start container!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Container started!" -ForegroundColor Green
Write-Host ""

# Wait for service to be ready
Write-Host "Waiting for service to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test health endpoint
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✓ Health check passed!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "Health check failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Container Logs ===" -ForegroundColor Yellow
docker logs ai-recipes-test --tail 20

Write-Host ""
Write-Host "To stop and remove the test container, run:" -ForegroundColor Cyan
Write-Host "docker stop ai-recipes-test && docker rm ai-recipes-test" -ForegroundColor White