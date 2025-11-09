# 🚀 START HERE - Apple Pay POC Quick Start

**Having the "Payment Cancelled" error? Follow this guide step-by-step.**

---

## ⚡ IMPORTANT: Which URL Are You Using?

### Option A: Testing on THIS computer (localhost)

✅ **Use**: `https://localhost:3443`
✅ **Best for**: Testing on your development machine
✅ **Steps**: Follow "Quick Start - Localhost" below

### Option B: Testing on iPhone/iPad (same WiFi network)

✅ **Use**: `https://YOUR_IP:3443` (e.g., `https://192.168.1.100:3443`)
✅ **Best for**: Real Apple Pay testing on iOS device
✅ **Steps**: Follow "Quick Start - Network Device" below

---

## 🏃 Quick Start - Localhost (Testing on Same Computer)

### Step 1: Close ALL Browser Tabs

Close any tabs with `10.10.10.127` or any other IP addresses. We need fresh start.

### Step 2: Accept Backend Certificate

1. Open **NEW** tab in Safari
2. Visit exactly: **`https://localhost:8443/admin/`** (copy-paste this!)
3. You'll see: "Your connection is not private" warning
4. Click **"Show Details"** → **"visit this website"**
5. Click **"Visit Website"** again
6. You should see Django admin login page (don't need to log in)
7. ✅ Keep this tab open

### Step 3: Accept Frontend Certificate

1. Open **ANOTHER NEW** tab
2. Visit exactly: **`https://localhost:3443`** (copy-paste this!)
3. Accept certificate warning again (same as step 2)
4. You should see the Apple Pay demo page
5. ✅ This is your testing tab

### Step 4: Open Browser Console

1. While on `https://localhost:3443`, press **F12** (or Right-click → Inspect)
2. Click **Console** tab
3. Clear any old messages (click 🚫 button)

### Step 5: Test Backend Connection

In the console, paste this EXACT command:

```javascript
fetch('https://localhost:8443/api/payments/config/status/')
  .then(r => r.json())
  .then(data => console.log('✅ Backend connected:', data.all_valid))
  .catch(e => console.error('❌ Backend ERROR:', e.message))
```

**Expected result**: `✅ Backend connected: true`

**If you see error**: Go back to Step 2 - the certificate wasn't accepted properly.

### Step 6: Test Apple Pay

1. Look at the page - do you see the Apple Pay button?
   - **YES**: Go to step 7
   - **NO**: This is normal if you're not using Safari on Mac/iPhone

2. If on Safari with Apple Pay available, click the Apple Pay button

3. Watch the Console - you should see:
   ```
   [API Request] POST https://localhost:8443/api/payments/validate-merchant/
   [Apple Pay] ✅ Real merchant session received from Apple
   ```

4. Check backend logs in terminal:
   ```bash
   docker-compose logs -f backend | grep -i merchant
   ```

   Should see:
   ```
   INFO ✅ Using REAL merchant validation with Apple servers
   INFO ✅✅✅ Merchant validation SUCCESSFUL with Apple
   ```

✅ **If you see these logs, it's working!** Apple Pay sheet should appear.

❌ **Still not working?** See Troubleshooting section below.

---

## 🏃 Quick Start - Network Device (iPhone/iPad Testing)

### Step 0: Get Your Computer's IP Address

Run this command on your computer:

**macOS/Linux**:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}'
```

**Windows (PowerShell)**:
```powershell
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}).IPAddress
```

**Windows (Command Prompt)**:
```cmd
ipconfig | findstr IPv4
```

Example result: `192.168.1.100`

**⚠️ IMPORTANT**: Use the IP address on your LOCAL network (usually starts with 192.168.x.x or 10.x.x.x)

### Step 1: Update Configuration

1. Edit `.env` file and change these lines:

```bash
# IMPORTANT: Replace 192.168.1.100 with YOUR actual IP from Step 0!

# Frontend should connect to backend via IP
NEXT_PUBLIC_API_URL=https://192.168.1.100:8443

# Backend should allow this IP
ALLOWED_HOSTS=localhost,127.0.0.1,backend,0.0.0.0,192.168.1.100

# CORS should allow frontend from this IP
CORS_ALLOWED_ORIGINS=https://localhost:3443,https://localhost:3000,https://192.168.1.100:3443
```

2. **CRITICAL**: Replace `192.168.1.100` with YOUR actual IP address from Step 0!

### Step 2: Restart Services

```bash
docker-compose down
docker-compose up -d
```

Wait 30 seconds for services to start.

### Step 3: Accept Certificates on Your Computer

1. Open browser on your computer
2. Visit: `https://192.168.1.100:8443/admin/` (use YOUR IP)
3. Accept certificate
4. Visit: `https://192.168.1.100:3443` (use YOUR IP)
5. Accept certificate
6. Verify you see the page

### Step 4: Accept Certificates on iPhone/iPad

1. Make sure iPhone/iPad is on **same WiFi** as your computer
2. Open **Safari** on the device (must be Safari!)
3. Visit: `https://192.168.1.100:8443/admin/` (use YOUR IP)
4. Tap **"Show Details"** → **"visit this website"**
5. Tap **"Visit Website"**
6. You should see Django admin page

7. Open new tab in Safari
8. Visit: `https://192.168.1.100:3443` (use YOUR IP)
9. Accept certificate again
10. You should see Apple Pay demo page

### Step 5: Test Apple Pay on Device

1. On the `https://192.168.1.100:3443` page
2. Click Apple Pay button
3. Apple Pay sheet should appear!

---

## 🔧 Troubleshooting

### Error: "Backend ERROR" when testing fetch

**Cause**: SSL certificate not accepted or wrong URL

**Fix**:
1. Double-check you're using exact URL: `https://localhost:8443/admin/`
2. Make sure you clicked "visit this website" (not just "Go Back")
3. Try in private/incognito window and accept certificate again
4. Check backend is running: `docker-compose ps` (should show "healthy")

### Error: "Mixed Content" or "Blocked by CORS"

**Cause**: Accessing frontend from IP address but .env has `localhost`

**Fix**: Follow "Quick Start - Network Device" section to update `.env`

### Error: "Apple Pay is not available"

**Possible causes**:

1. **Not using Safari**: Apple Pay only works in Safari
   - Chrome/Firefox/Edge won't work
   - Must use Safari

2. **Not on Apple device**:
   - Need iPhone/iPad/Mac with Touch ID
   - Simulators don't work
   - Android doesn't work

3. **No cards in Wallet**:
   - Open Wallet app
   - Add at least one card (can be test card)

4. **Using HTTP instead of HTTPS**:
   - Must use `https://localhost:3443` NOT `http://localhost:3000`

### Error: WebSocket connection failed

**This is normal!** The WebSocket errors are for Next.js hot reloading (development feature).

They don't affect Apple Pay functionality. Ignore these:
```
WebSocket connection to 'wss://...' failed
```

### Error: "Payment Cancelled" but backend shows successful validation

**Possible causes**:

1. **Domain verification file not accessible to Apple**
   - This is expected in localhost testing
   - For production, you need proper domain verification

2. **Payment Processing Certificate not uploaded to GMO**
   - See [SETUP_GUIDE.md](SETUP_GUIDE.md) Part 2, Step 2
   - Upload `certs/applepay-payment-processing-gmo.p12` to GMO dashboard

---

## 📊 Verification Checklist

After following the steps, verify:

### Backend Health
```bash
# Check backend is running
docker-compose ps

# Should show:
# applepay_backend    Up (healthy)
# applepay_frontend   Up (healthy)

# Check configuration
curl -k https://localhost:8443/api/payments/config/status/

# Should return: {"all_valid": true, ...}
```

### Frontend Connection

In browser console on `https://localhost:3443`:
```javascript
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
// Should show: API URL: https://localhost:8443
```

### Certificate Validation
```bash
cd certs
./verify-certificates.sh
# Should show all ✅ green checkmarks
```

---

## 🎯 Common Scenarios

### Scenario 1: "I'm getting the error on localhost:3443"

✅ **Solution**: Follow "Quick Start - Localhost" above

### Scenario 2: "I'm getting the error on 10.10.10.127:3443"

⚠️ **Problem**: Mixing localhost config with IP access

✅ **Solution**:
- Either use `https://localhost:3443` (recommended for development)
- OR follow "Quick Start - Network Device" to properly configure for IP access

### Scenario 3: "I want to test on my iPhone"

✅ **Solution**: Follow "Quick Start - Network Device" above

### Scenario 4: "It worked once but now it's broken"

🔄 **Solution**: Reset everything:
```bash
# Stop containers
docker-compose down

# Clear Next.js cache
rm -rf frontend/.next

# Restart
docker-compose up --build

# Accept certificates again (both backend and frontend)
```

---

## 📞 Still Having Issues?

### 1. Check Container Logs

```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Both logs
docker-compose logs -f
```

### 2. Verify Environment

```bash
# Check what frontend sees
docker-compose exec frontend env | grep NEXT_PUBLIC_API_URL

# Should show: NEXT_PUBLIC_API_URL=https://localhost:8443
# (or your IP if configured for network testing)
```

### 3. Complete Reset

```bash
# Nuclear option - reset everything
docker-compose down -v
rm -rf frontend/.next frontend/node_modules/.cache
docker-compose up --build
```

Then follow the Quick Start steps again.

### 4. Read Full Documentation

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Comprehensive debugging
- [QUICK_FIX.md](QUICK_FIX.md) - Specific error fixes
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete setup guide

---

## ✅ Success Indicators

### You'll know it's working when:

**Browser Console**:
```
[API Request] POST https://localhost:8443/api/payments/validate-merchant/
[Apple Pay] Validating merchant with URL: https://apple-pay-gateway.apple.com/...
[Apple Pay] ✅ Real merchant session received from Apple
[Apple Pay] Merchant validation completed successfully
```

**Backend Logs**:
```
INFO Merchant validation request from domain: localhost
INFO ✅ Using REAL merchant validation with Apple servers
INFO ✅✅✅ Merchant validation SUCCESSFUL with Apple
POST /api/payments/validate-merchant/ 200
```

**Apple Pay Sheet**: Payment sheet appears on device asking you to confirm payment

---

## 🚀 Quick Reference

| Scenario | Frontend URL | Backend URL | .env Setting |
|----------|--------------|-------------|--------------|
| Local testing | https://localhost:3443 | https://localhost:8443 | `NEXT_PUBLIC_API_URL=https://localhost:8443` |
| iPhone on WiFi | https://192.168.1.100:3443 | https://192.168.1.100:8443 | `NEXT_PUBLIC_API_URL=https://192.168.1.100:8443` |

**Remember**:
- Always use **HTTPS** (not HTTP)
- Always use **Safari** (not Chrome)
- Always **accept certificates** for both frontend and backend URLs

---

**TL;DR**:
1. Close all tabs
2. Visit `https://localhost:8443/admin/` and accept certificate
3. Visit `https://localhost:3443` and accept certificate
4. Test Apple Pay

If using IP address (like `10.10.10.127`), update `.env` to use that IP and restart containers.
