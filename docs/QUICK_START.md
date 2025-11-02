# Quick Start Guide

## Start Both Frontend and Backend

```bash
docker compose up --build
```

This command will:
1. Build both frontend and backend Docker images
2. Generate SSL certificates automatically
3. Start both services with HTTPS enabled
4. Run database migrations

## Access the Application

### Frontend (React/Next.js)
- **HTTPS (for Apple Pay)**: https://localhost:3443
- **HTTP (testing only)**: http://localhost:3000
- **Note**: You'll need to accept the self-signed certificate warning in your browser

### Backend API (Django REST Framework)
- **HTTPS**: https://localhost:8443
- **HTTP**: http://localhost:8000
- **Admin Panel**: https://localhost:8443/admin/

## Browser Security Warning

When accessing HTTPS URLs, your browser will show a security warning because we're using self-signed certificates for development.

**To proceed:**
- **Chrome/Edge**: Click "Advanced" → "Proceed to localhost (unsafe)"
- **Firefox**: Click "Advanced" → "Accept the Risk and Continue"
- **Safari**: Click "Show Details" → "visit this website"

## Verify Everything is Working

### Check Container Status
```bash
docker compose ps
```

Both containers should show "healthy" status.

### Test Frontend
1. Open https://localhost:3443 in your browser
2. You should see the home page with navigation to payment pages

### Test Backend API
```bash
# Test API endpoint (in PowerShell)
Invoke-WebRequest -Uri https://localhost:8443/api/payments/merchant-session/ -UseBasicParsing
```

## Troubleshooting

### Frontend not loading?
1. Check if port 3443 is accessible: `Test-NetConnection -ComputerName localhost -Port 3443`
2. Try HTTP fallback: http://localhost:3000
3. Check logs: `docker compose logs frontend`

### Backend not responding?
1. Check if port 8443 is accessible: `Test-NetConnection -ComputerName localhost -Port 8443`
2. Check logs: `docker compose logs backend`

### CORS errors?
- Ensure the frontend URL is in `CORS_ALLOWED_ORIGINS` environment variable
- Check backend logs for CORS-related errors

### Cannot connect between FE and BE?
- Verify both are on the same Docker network (`applepay_network`)
- Check that `NEXT_PUBLIC_API_URL` is set correctly (should be `https://localhost:8443`)
- Accept the certificate warning for both frontend AND backend URLs in your browser

## Stop Services

```bash
docker compose down
```

## Restart Services

```bash
docker compose restart
```

## View Logs

```bash
# All services
docker compose logs

# Frontend only
docker compose logs frontend

# Backend only
docker compose logs backend

# Follow logs in real-time
docker compose logs -f
```

## Environment Variables

Create a `.env` file in the root directory with:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS (frontend URLs)
CORS_ALLOWED_ORIGINS=https://localhost:3443,http://localhost:3000

# Frontend API URL
NEXT_PUBLIC_API_URL=https://localhost:8443

# GMO Payment Gateway (required for actual payments)
GMO_SHOP_ID=your-shop-id
GMO_SHOP_PASS=your-shop-pass
GMO_API_ENDPOINT=https://pt01.mul-pay.jp

# Apple Pay (required for merchant validation)
APPLE_MERCHANT_ID=your-merchant-id
```

