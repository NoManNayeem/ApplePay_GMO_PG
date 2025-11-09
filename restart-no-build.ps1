# PowerShell script to restart Docker containers without rebuild
# Faster restart for when you only changed code (not dependencies)
# Usage: .\restart-no-build.ps1 [service_name]

param(
    [string]$Service = ""
)

Write-Host "🔄 Restarting Docker containers (no rebuild)..." -ForegroundColor Cyan

if ($Service) {
    Write-Host "Restarting service: $Service" -ForegroundColor Yellow
    docker compose restart $Service
} else {
    Write-Host "Restarting all services..." -ForegroundColor Yellow
    docker compose restart
}

Write-Host "✅ Done! Containers restarted." -ForegroundColor Green
Write-Host ""
Write-Host "Note: Use .\restart.ps1 if you changed dependencies (package.json, requirements.txt, etc.)" -ForegroundColor Yellow

