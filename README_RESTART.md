# Docker Compose Restart Guide

## Quick Restart Scripts

Two PowerShell scripts are available for easy container management:

### 1. `restart.ps1` - Full Rebuild and Restart
**Use when:**
- Changed dependencies (package.json, requirements.txt, Dockerfile)
- Changed environment variables
- First time setup
- After pulling new code with dependency changes

**Usage:**
```powershell
# Restart all services with rebuild
.\restart.ps1

# Restart specific service (e.g., backend or frontend)
.\restart.ps1 backend
.\restart.ps1 frontend
```

### 2. `restart-no-build.ps1` - Quick Restart (No Rebuild)
**Use when:**
- Changed code files only (Python, TypeScript, React components)
- Changed configuration files (settings.py, next.config.ts)
- Hot reload didn't pick up changes

**Usage:**
```powershell
# Restart all services (no rebuild)
.\restart-no-build.ps1

# Restart specific service
.\restart-no-build.ps1 backend
.\restart-no-build.ps1 frontend
```

## Hot Reload (Automatic)

The containers are configured with volume mounts, so most code changes are picked up automatically:

- **Backend (Django)**: Automatically reloads on Python file changes
- **Frontend (Next.js)**: Webpack HMR (Hot Module Replacement) watches for changes

You typically **don't need to restart** for code changes - just save your files!

## Manual Docker Compose Commands

If you prefer using docker compose directly:

```powershell
# Restart without rebuild (fast)
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart frontend

# Rebuild and restart (when dependencies change)
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build backend
docker compose up -d --build frontend

# View logs
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
```

## When to Use Each Method

| Change Type | Method | Script |
|------------|--------|-------|
| Python/TypeScript code | Hot reload (automatic) | None needed |
| Configuration files | Quick restart | `restart-no-build.ps1` |
| Dependencies (package.json, requirements.txt) | Full rebuild | `restart.ps1` |
| Dockerfile changes | Full rebuild | `restart.ps1` |
| Environment variables (.env) | Restart | `restart-no-build.ps1` |

## Troubleshooting

If hot reload isn't working:

1. **Check volume mounts**: Ensure `./backend:/app` and `./frontend:/app` are mounted
2. **Check file permissions**: Files should be readable by the container
3. **Restart the service**: Use `restart-no-build.ps1` to force reload
4. **Check logs**: `docker compose logs -f [service]` to see what's happening

## Container Restart Policy

Containers are configured with `restart: unless-stopped`, which means:
- Containers automatically restart if they crash
- Containers restart when Docker daemon restarts
- Containers won't restart if manually stopped

