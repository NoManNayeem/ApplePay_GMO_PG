# 🔧 Troubleshooting Guide - Apple Pay POC

**Common issues and how to fix them**

---

## 🌐 Connection Issues

### Error: "Cannot connect to backend API"

**Symptoms**:
- WebSocket errors in browser console
- "Payment cancelled" message
- No requests showing in backend logs

**Causes**:
1. Frontend and backend on different URLs
2. Self-signed SSL certificate not accepted in browser
3. CORS blocking requests

**Fix**:

#### Step 1: Accept Backend SSL Certificate

Before Apple Pay can work, you must accept the self-signed certificate in your browser:

```bash
# Open backend URL directly in your browser:
# 1. Visit: https://localhost:8443/admin/
# 2. Browser will show "Not Secure" warning
# 3. Click "Advanced" → "Proceed to localhost (unsafe)"
# 4. You should see Django admin login page
```

**Important**: Do this BEFORE testing Apple Pay!

#### Step 2: Verify Frontend Can Reach Backend

Open browser console on `https://localhost:3443` and run:

```javascript
fetch('https://localhost:8443/api/payments/config/status/')
  .then(r => r.json())
  .then(data => console.log(data))
```

Expected output: `{all_valid: true, ...}`

If you get an error, the SSL certificate wasn't accepted.

#### Step 3: Check Environment Variables

Make sure `.env` has matching URLs:

```bash
# Frontend should use localhost (not IP address)
NEXT_PUBLIC_API_URL=https://localhost:8443

# CORS should allow frontend origin
CORS_ALLOWED_ORIGINS=https://localhost:3443,https://localhost:3000

# Backend should allow localhost
ALLOWED_HOSTS=localhost,127.0.0.1,backend,0.0.0.0
```

#### Step 4: Restart Containers

```bash
docker-compose down
docker-compose up --build
```

---

## 🍎 Apple Pay Button Not Showing

**Symptoms**:
- Apple Pay button doesn't appear
- Message: "Apple Pay Not Available"

**Causes**:

### Cause 1: Not Using Safari
Apple Pay JS API **only works in Safari**. Chrome, Firefox, Edge won't work.

**Fix**: Use Safari browser

### Cause 2: Not on Apple Device
Apple Pay on the web requires:
- iPhone/iPad with iOS, OR
- Mac with macOS and Touch ID

**Fix**: Test on real Apple device. iOS Simulator and Android don't work.

### Cause 3: No Cards in Wallet
Device must have at least one card added to Apple Wallet.

**Fix**: Add a card to Wallet app (can be test card)

### Cause 4: Not HTTPS
Apple Pay requires HTTPS (not HTTP).

**Fix**: Use `https://localhost:3443` not `http://localhost:3000`

---

## ⚠️ "Payment Cancelled" Error

### Error Message: "The merchant session was rejected by Apple Pay"

This happens when Apple Pay cancels the session quickly (< 3 seconds). Common causes:

#### Cause 1: Backend Not Reachable

**Check**:
```bash
# In browser console (while on https://localhost:3443):
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
```

Should show: `https://localhost:8443`

**Fix**:
1. Accept backend SSL certificate (see Step 1 above)
2. Verify `.env` has `NEXT_PUBLIC_API_URL=https://localhost:8443`
3. Restart: `docker-compose restart frontend`

#### Cause 2: Domain Verification File Not Accessible

**Check**:
```bash
curl -k https://localhost:8443/.well-known/apple-developer-merchantid-domain-association
```

Should return file content (not 404).

**Fix**: Already implemented in [backend/applepay_poc/urls.py](backend/applepay_poc/urls.py#L36-L38)

#### Cause 3: Certificate Issues

**Check**:
```bash
cd certs
./verify-certificates.sh
```

Should show all green checkmarks.

**Fix**: See [CERTIFICATES_STATUS.md](CERTIFICATES_STATUS.md)

#### Cause 4: Merchant ID Mismatch

**Check backend logs**:
```bash
docker-compose logs -f backend | grep -i "merchant\|validation"
```

Look for error messages about merchant ID.

**Fix**: Verify `.env` has correct merchant ID matching your certificates

---

## 📱 Testing on Different Networks

If testing on iPhone/iPad on same WiFi as your dev machine:

### Step 1: Get Your Computer's IP

```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr IPv4
```

Example: `192.168.1.100`

### Step 2: Update .env

```bash
# Replace with your actual IP
NEXT_PUBLIC_API_URL=https://192.168.1.100:8443
ALLOWED_HOSTS=localhost,127.0.0.1,backend,0.0.0.0,192.168.1.100
CORS_ALLOWED_ORIGINS=https://localhost:3443,https://192.168.1.100:3443
```

### Step 3: Restart

```bash
docker-compose restart
```

### Step 4: Accept Certificates on Device

On your iPhone/iPad:

1. Visit `https://192.168.1.100:8443/admin/` in Safari
2. Accept certificate warning
3. Visit `https://192.168.1.100:3443`
4. Accept certificate warning
5. Now try Apple Pay

---

## 🔍 Debugging Tools

### View Backend Logs

```bash
# All logs
docker-compose logs -f backend

# Only errors
docker-compose logs -f backend | grep -i error

# Merchant validation logs
docker-compose logs -f backend | grep -i "merchant\|validation\|apple"

# GMO PG logs
docker-compose logs -f backend | grep -i "gmo"
```

### View Frontend Logs

```bash
docker-compose logs -f frontend
```

### Check Configuration

```bash
# Backend config status
curl -k https://localhost:8443/api/payments/config/status/ | jq

# Should return:
# {
#   "all_valid": true,
#   "gmo_pg": {"valid": true},
#   "apple_pay": {"valid": true}
# }
```

### Test Merchant Validation Manually

```bash
# Check if endpoint exists
curl -k -X POST https://localhost:8443/api/payments/validate-merchant/ \
  -H "Content-Type: application/json" \
  -d '{"validation_url": "https://apple-pay-gateway.apple.com/paymentservices/startSession"}' \
  | jq

# Should return merchant session or clear error message
```

---

## 🚨 Common Error Messages

### "Apple Pay is not available"

**Cause**: Not using Safari on Apple device
**Fix**: Use Safari on iPhone/iPad/Mac

### "Cannot connect to backend API at https://localhost:8443"

**Cause**: SSL certificate not accepted or backend not running
**Fix**:
1. Visit https://localhost:8443/admin/ and accept certificate
2. Check backend is running: `docker-compose ps`

### "CORS policy error"

**Cause**: Frontend origin not in CORS_ALLOWED_ORIGINS
**Fix**: Add your frontend URL to CORS_ALLOWED_ORIGINS in `.env`

### "Apple Pay certificates not configured"

**Cause**: Certificate files missing or paths wrong
**Fix**:
```bash
cd certs && ./verify-certificates.sh
```

### "Merchant validation failed"

**Cause**: Multiple possible issues
**Fix**: Check backend logs for specific error:
```bash
docker-compose logs -f backend | grep -i "merchant\|validation"
```

### "Payment Processing Certificate not uploaded to GMO"

**Cause**: GMO PG doesn't have your payment processing certificate
**Fix**: See [SETUP_GUIDE.md](SETUP_GUIDE.md) Part 2, Step 2

---

## 📋 Pre-Flight Checklist

Before testing Apple Pay, verify:

- [ ] Using Safari browser (not Chrome/Firefox)
- [ ] On real Apple device (not simulator/Android)
- [ ] HTTPS URLs (not HTTP)
- [ ] Backend SSL certificate accepted in browser
- [ ] Frontend SSL certificate accepted in browser
- [ ] At least one card in Apple Wallet
- [ ] Backend running: `docker-compose ps` shows "healthy"
- [ ] Configuration valid: `curl -k https://localhost:8443/api/payments/config/status/` returns `all_valid: true`
- [ ] Domain verification file accessible
- [ ] Environment variables correct in `.env`

**Quick Test**:
```bash
# Run all checks
cd certs && ./verify-certificates.sh
curl -k https://localhost:8443/api/payments/config/status/ | jq '.all_valid'
curl -k https://localhost:8443/.well-known/apple-developer-merchantid-domain-association | head -5
```

All should return success/data.

---

## 🔧 Reset and Start Fresh

If nothing works, try a complete reset:

```bash
# Stop everything
docker-compose down -v

# Clean caches
rm -rf frontend/.next
rm -rf frontend/node_modules/.cache

# Rebuild and start
docker-compose up --build

# Accept certificates
# 1. Visit https://localhost:8443/admin/ - accept certificate
# 2. Visit https://localhost:3443 - accept certificate
# 3. Try Apple Pay
```

---

## 📞 Still Having Issues?

### Check Documentation

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete setup instructions
- [FIXES_APPLIED.md](FIXES_APPLIED.md) - All fixes applied
- [CERTIFICATES_STATUS.md](CERTIFICATES_STATUS.md) - Certificate status

### Verify System Status

```bash
# 1. Containers running
docker-compose ps
# Both should show "Up" and "healthy"

# 2. Backend accessible
curl -k https://localhost:8443/api/payments/config/status/
# Should return JSON with all_valid: true

# 3. Certificates valid
cd certs && ./verify-certificates.sh
# Should show all green checkmarks

# 4. No errors in logs
docker-compose logs --tail=50 | grep -i error
# Should be minimal/no errors
```

### Enable Debug Logging

Add to backend logs:

1. Edit `.env`: `DEBUG=True`
2. Restart: `docker-compose restart backend`
3. Watch logs: `docker-compose logs -f backend`

---

## 💡 Pro Tips

### Tip 1: Browser Console is Your Friend

Always have browser console open (F12) when testing Apple Pay. It shows:
- API requests
- Apple Pay events
- Error messages
- Certificate issues

### Tip 2: Test Backend First

Before testing full Apple Pay flow:
```bash
# Test config
curl -k https://localhost:8443/api/payments/config/status/ | jq

# Test domain verification
curl -k https://localhost:8443/.well-known/apple-developer-merchantid-domain-association
```

### Tip 3: One Issue at a Time

Fix in this order:
1. Get containers running (docker-compose up)
2. Accept SSL certificates in browser
3. Verify backend API accessible
4. Check certificate files exist
5. Test Apple Pay button appears
6. Test merchant validation
7. Test payment processing

### Tip 4: Check Apple System Status

Sometimes Apple Pay services have issues:
https://developer.apple.com/system-status/

---

**Last Updated**: 2025-11-09
**Need More Help?** Check the logs: `docker-compose logs -f backend frontend`
