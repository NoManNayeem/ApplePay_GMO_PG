# PowerShell script to build and start Docker Compose services
# This workaround avoids the "file already closed" error on Windows

Write-Host "Building Docker images separately to avoid Compose bake issue..." -ForegroundColor Cyan

# Build backend
Write-Host "`nBuilding backend..." -ForegroundColor Yellow
docker build -t applepay_poc-backend -f backend/Dockerfile backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend build failed!" -ForegroundColor Red
    exit 1
}

# Build frontend
Write-Host "`nBuilding frontend..." -ForegroundColor Yellow
docker build -t applepay_poc-frontend -f frontend/Dockerfile.dev frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`nAll images built successfully!" -ForegroundColor Green
Write-Host "Starting services..." -ForegroundColor Cyan

# Start services (without --build since images are already built)
docker compose up

