# 🚨 QUICK FIX: "Payment Cancelled" Error

**You're seeing this error because the frontend can't reach the backend API.**

---

## ⚡ 3-Step Fix (Takes 2 minutes)

### Step 1: Accept Backend SSL Certificate

**Before Apple Pay can work, you MUST accept the self-signed SSL certificate:**

1. Open a new browser tab
2. Visit: **https://localhost:8443/admin/**
3. You'll see: "Your connection is not private" warning
4. Click **"Advanced"** → **"Proceed to localhost (unsafe)"**
5. You should see Django admin login page
6. ✅ Done! Leave this tab open

**Why?** Your browser blocks API calls to HTTPS endpoints with untrusted certificates. By visiting the URL directly and accepting, the browser will allow API calls.

### Step 2: Verify Backend Connection

Open browser console (F12) on your frontend page and run:

```javascript
fetch('https://localhost:8443/api/payments/config/status/')
  .then(r => r.json())
  .then(data => console.log('Backend OK:', data.all_valid))
  .catch(e => console.error('Backend ERROR:', e))
```

Expected: `Backend OK: true`

If you see an error, go back to Step 1.

### Step 3: Test Apple Pay Again

1. Refresh your frontend page (https://localhost:3443)
2. Click the Apple Pay button
3. Check browser console for new logs

You should see:
```
[API Request] POST https://localhost:8443/api/payments/validate-merchant/
```

---

## 🔍 What Was Wrong?

**Your Error**:
```
[Warning] [Apple Pay] Payment session cancelled
Payment Failed: The merchant session was rejected by Apple Pay...
```

**The Real Problem**:
- Frontend at `https://localhost:3443` or `https://localhost:3443`
- Trying to call backend at `https://localhost:8443`
- Browser blocked the API call because SSL certificate not accepted
- No merchant validation request reached backend
- Apple Pay session cancelled due to timeout/no response

**The Fix**:
- Accept SSL certificate by visiting backend URL directly
- Browser now allows API calls
- Merchant validation can reach backend
- Apple Pay works!

---

## ✅ Verification Checklist

After fixing, you should see in browser console:

- [x] `[API Request] POST https://localhost:8443/api/payments/validate-merchant/`
- [x] `[Apple Pay] Validating merchant with URL:...`
- [x] `[Apple Pay] ✅ Real merchant session received from Apple`
- [x] `[Apple Pay] Merchant validation completed successfully`

In backend logs (`docker-compose logs -f backend`):

- [x] `INFO Merchant validation request from domain: localhost`
- [x] `INFO ✅ Using REAL merchant validation with Apple servers`
- [x] `INFO ✅✅✅ Merchant validation SUCCESSFUL with Apple`

---

## 🚨 Still Not Working?

### Error: "Cannot connect to backend API"

**Check `.env` file**:
```bash
# Should have:
NEXT_PUBLIC_API_URL=https://localhost:8443
# NOT an IP address
```

If it has an IP address like `https://localhost:8443`, change it to `https://localhost:8443`

**Restart frontend**:
```bash
docker-compose restart frontend
```

### Error: "CORS policy error"

**Check `.env` file**:
```bash
# Should have:
CORS_ALLOWED_ORIGINS=https://localhost:3443,https://localhost:3000
```

**Restart backend**:
```bash
docker-compose restart backend
```

### Error: "Apple Pay is not available"

**Requirements**:
- ✅ Must use Safari browser (not Chrome/Firefox/Edge)
- ✅ Must be on iPhone/iPad/Mac (not Android/Windows)
- ✅ Must have card in Apple Wallet
- ✅ Must use HTTPS (https://localhost:3443, not http://localhost:3000)

---

## 📱 Testing on iPhone/iPad

If testing on real device on same WiFi:

1. **Get your computer's IP address**:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1

   # Windows
   ipconfig | findstr IPv4
   ```
   Example: `192.168.1.100`

2. **Accept backend cert on device**:
   - On iPhone/iPad, open Safari
   - Visit: `https://192.168.1.100:8443/admin/`
   - Accept certificate warning

3. **Accept frontend cert on device**:
   - Visit: `https://192.168.1.100:3443`
   - Accept certificate warning

4. **Now test Apple Pay** on `https://192.168.1.100:3443`

---

## 🎯 Expected Flow

When working correctly, here's what happens:

1. User clicks Apple Pay button
2. Frontend creates ApplePaySession (shows in console)
3. Apple Pay calls `onvalidatemerchant` event
4. Frontend sends validation URL to backend
5. Backend contacts Apple's servers with certificate
6. Backend receives signed merchant session from Apple
7. Backend returns merchant session to frontend
8. Frontend completes validation
9. Apple Pay sheet appears with payment options

**Console logs you should see**:
```
[Apple Pay] Validating merchant with URL: https://apple-pay-gateway.apple.com/...
[API Request] POST https://localhost:8443/api/payments/validate-merchant/
[Apple Pay] Validation response: {merchantSession: {...}, merchant_id: "..."}
[Apple Pay] ✅ Real merchant session received from Apple
[Apple Pay] Completing merchant validation with session
[Apple Pay] Merchant validation completed successfully
```

**Backend logs you should see**:
```
INFO Merchant validation request from domain: localhost
INFO Validation URL: https://apple-pay-gateway.apple.com/...
INFO ✅ Using REAL merchant validation with Apple servers
INFO Certificate file: /certs/merchant-identity-cert.pem
INFO ✅✅✅ Merchant validation SUCCESSFUL with Apple
POST /api/payments/validate-merchant/ HTTP/1.1" 200
```

---

## 📞 Need More Help?

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for comprehensive debugging guide.

**Quick Commands**:

```bash
# Check if backend is accessible
curl -k https://localhost:8443/api/payments/config/status/

# View backend logs
docker-compose logs -f backend | grep -i "merchant\|validation"

# View frontend logs
docker-compose logs -f frontend

# Restart everything
docker-compose restart
```

---

**TL;DR**: Visit **https://localhost:8443/admin/** in your browser and accept the SSL certificate. Then try Apple Pay again. 🎉
