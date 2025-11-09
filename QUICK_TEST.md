# Quick Testing Guide

This guide helps you quickly verify that all fixes are working.

## Prerequisites

- Docker and Docker Compose installed
- Certificate files in `certs/` directory:
  - `merchant-identity-cert.pem`
  - `merchant-identity-key.pem`

## Quick Start

### 1. Start Services

```bash
# From project root
docker-compose up --build
```

Wait for:
- ✅ Backend: "Starting development server at https://0.0.0.0:8443/"
- ✅ Frontend: "ready - started server on 0.0.0.0:3443"

### 2. Verify Configuration

Open a new terminal:

```bash
# Check configuration status
curl -k https://localhost:8443/api/payments/config/status/ | jq

# Expected output:
# {
#   "all_valid": true,
#   "gmo_pg": { "valid": true, ... },
#   "apple_pay": { "valid": true, ... }
# }
```

If you see errors, check [SETUP_GUIDE.md](SETUP_GUIDE.md).

### 3. Test Domain Verification

```bash
# Test Apple domain verification file
curl -k https://localhost:8443/.well-known/apple-developer-merchantid-domain-association

# Should return file content (not 404)
```

### 4. Test Frontend

Open browser (Safari recommended for Apple Pay):
```
https://localhost:3443
```

1. Accept self-signed certificate warning
2. Check browser console for errors
3. Look for Apple Pay button (may not appear on non-Apple devices)

### 5. Check Backend Logs

```bash
# Follow logs in real-time
docker-compose logs -f backend

# Look for:
# - ✅ "Using REAL merchant validation with Apple servers"
# - ❌ No "MOCK merchant session" warnings
# - ✅ Certificate files loaded successfully
```

## Testing Merchant Validation

### On Real iOS Device or Mac with Safari

1. Connect device to same network as your computer
2. Get your computer's IP address:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "

   # Windows
   ipconfig | findstr IPv4
   ```

3. Update `.env`:
   ```bash
   NEXT_PUBLIC_API_URL=https://YOUR_IP:8443
   ALLOWED_HOSTS=localhost,127.0.0.1,backend,YOUR_IP
   CORS_ALLOWED_ORIGINS=https://localhost:3443,https://YOUR_IP:3443
   ```

4. Restart services:
   ```bash
   docker-compose restart
   ```

5. On device, open Safari and go to `https://YOUR_IP:3443`
6. Accept certificate warning
7. Try Apple Pay button

### Expected Behavior

**With Valid Certificates**:
- Apple Pay button appears
- Clicking triggers merchant validation
- Backend logs show: "✅✅✅ Merchant validation SUCCESSFUL with Apple"
- Payment sheet appears

**With Invalid/Missing Certificates**:
- Clear error message: "Apple Pay certificates not configured"
- Setup instructions provided
- No confusing mock sessions

## Common Test Scenarios

### Scenario 1: Fresh Setup (No Certificates)

```bash
# Temporarily move certificates
mv certs/merchant-identity-cert.pem certs/merchant-identity-cert.pem.backup
mv certs/merchant-identity-key.pem certs/merchant-identity-key.pem.backup

# Restart
docker-compose restart backend

# Test
curl -k https://localhost:8443/api/payments/config/status/ | jq

# Expected:
# "apple_pay": { "valid": false, "errors": ["...not found..."] }
```

Restore:
```bash
mv certs/merchant-identity-cert.pem.backup certs/merchant-identity-cert.pem
mv certs/merchant-identity-key.pem.backup certs/merchant-identity-key.pem
docker-compose restart backend
```

### Scenario 2: Test Transaction Rollback

This requires GMO PG credentials and valid Apple Pay setup.

1. Configure GMO credentials in `.env`
2. Make a payment with intentionally invalid token
3. Check logs for rollback:
   ```
   WARNING: ExecTran failed for transaction ..., attempting rollback
   INFO: Transaction ... successfully rolled back (voided)
   ```

### Scenario 3: Certificate Expiry Warning

Certificates near expiry (< 30 days) will trigger warnings:

```bash
# Check config status
curl -k https://localhost:8443/api/payments/config/status/ | jq

# Look for warnings:
# "warnings": ["Merchant Identity Certificate expires soon (on 2025-XX-XX)"]
```

## Debugging Tools

### View All Environment Variables

```bash
docker-compose exec backend env | grep -E 'APPLE|GMO|SECRET|ALLOWED'
```

### Check Certificate Details

```bash
# Certificate validity period
openssl x509 -in certs/merchant-identity-cert.pem -noout -dates

# Certificate subject
openssl x509 -in certs/merchant-identity-cert.pem -noout -subject

# Certificate issuer
openssl x509 -in certs/merchant-identity-cert.pem -noout -issuer
```

### Test Merchant Validation Directly

```bash
# This will fail without valid Apple validation URL, but tests cert loading
docker-compose exec backend python manage.py shell

>>> from payments.services import validate_merchant_with_apple
>>> validate_merchant_with_apple("https://apple-pay-gateway.apple.com/paymentservices/startSession")
```

### Check Git Status (Security)

```bash
# Verify no private keys are staged
git status certs/

# Should not show .pem, .p12, or .key files
```

## Performance Checks

### Response Times

```bash
# Config endpoint
time curl -k https://localhost:8443/api/payments/config/status/ -o /dev/null

# Should be < 1 second

# Domain verification file
time curl -k https://localhost:8443/.well-known/apple-developer-merchantid-domain-association -o /dev/null

# Should be < 200ms
```

## Cleanup

### Stop Services

```bash
docker-compose down
```

### Remove All Data (Fresh Start)

```bash
docker-compose down -v  # Removes volumes too
docker-compose up --build
```

## Success Criteria

✅ **All fixes working correctly if**:

1. Configuration status returns `"all_valid": true`
2. Domain verification file accessible
3. Backend logs show "Using REAL merchant validation"
4. No "MOCK merchant session" warnings
5. Certificate validation runs on startup
6. Rollback mechanism logs transactions correctly
7. No private keys in git status
8. Frontend can connect to backend API

## Next Steps After Testing

1. ✅ All tests pass → Proceed to [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. ❌ Tests fail → Check [FIXES_APPLIED.md](FIXES_APPLIED.md) Troubleshooting section
3. 🔧 Need changes → Review backend logs: `docker-compose logs -f backend`

## Quick Reference

| Component | URL | Port |
|-----------|-----|------|
| Frontend (HTTPS) | https://localhost:3443 | 3443 |
| Frontend (HTTP) | http://localhost:3000 | 3000 |
| Backend (HTTPS) | https://localhost:8443 | 8443 |
| Backend (HTTP) | http://localhost:8000 | 8000 |
| Config Status API | https://localhost:8443/api/payments/config/status/ | - |
| Domain Verification | https://localhost:8443/.well-known/... | - |

## Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend

# Search for errors
docker-compose logs backend | grep -i error
docker-compose logs backend | grep -i warning
```

---

**Quick Test Complete?** → Go to [SETUP_GUIDE.md](SETUP_GUIDE.md) for production setup
**Issues?** → Check [FIXES_APPLIED.md](FIXES_APPLIED.md) for troubleshooting
