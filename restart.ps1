# PowerShell script to restart Docker containers with rebuild
# Usage: .\restart.ps1 [service_name]
#   - If service_name is provided, only that service will be restarted
#   - If no service_name, all services will be restarted

param(
    [string]$Service = ""
)

Write-Host "🔄 Restarting Docker containers..." -ForegroundColor Cyan

if ($Service) {
    Write-Host "Rebuilding and restarting service: $Service" -ForegroundColor Yellow
    docker compose up -d --build $Service
} else {
    Write-Host "Rebuilding and restarting all services..." -ForegroundColor Yellow
    docker compose up -d --build
}

Write-Host "✅ Done! Containers are restarting..." -ForegroundColor Green
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Cyan
if ($Service) {
    Write-Host "  docker compose logs -f $Service" -ForegroundColor Gray
} else {
    Write-Host "  docker compose logs -f" -ForegroundColor Gray
}

