# 🔐 Certificate Status Report

**Generated**: 2025-11-09
**Status**: ✅ ALL CERTIFICATES VALID

---

## ✅ Certificate Verification Summary

All required Apple Pay certificates are present, valid, and properly configured.

### 1️⃣ Merchant Identity Certificate

**Purpose**: Authenticate with Apple's servers during merchant validation
**Status**: ✅ **VALID**

| Component | File | Status |
|-----------|------|--------|
| Certificate | `merchant-identity-cert.pem` | ✅ Valid until Nov 6, 2027 (727 days) |
| Private Key | `merchant-identity-key.pem` | ✅ Matches certificate |
| P12 Bundle | `applepay-merchant-identity.p12` | ✅ Available for backup |

**Details**:
- **Merchant ID**: `merchant.alpha.throwinglow`
- **Issuer**: Apple Worldwide Developer Relations CA (G3)
- **Subject**: `merchant.alpha.throwinglow`
- **Validity**: Oct 7, 2025 - Nov 6, 2027
- **Certificate/Key Match**: ✅ Verified (MD5 hashes match)

**Configuration** (in `.env`):
```bash
APPLE_MERCHANT_ID=merchant.alpha.throwinglow
APPLE_MERCHANT_IDENTITY_CERT_PATH=/certs/merchant-identity-cert.pem
APPLE_MERCHANT_IDENTITY_KEY_PATH=/certs/merchant-identity-key.pem
```

### 2️⃣ Payment Processing Certificate

**Purpose**: GMO Payment Gateway uses this to decrypt Apple Pay payment tokens
**Status**: ✅ **VALID**

| Component | File | Status |
|-----------|------|--------|
| P12 for GMO | `applepay-payment-processing-gmo.p12` | ✅ Valid until Nov 4, 2027 (725 days) |
| PEM Certificate | `payment-processing.pem` | ✅ Backup available |
| Private Key | `payment-processing.key` | ✅ Backup available |

**Details**:
- **Merchant ID**: `merchant.alpha.throwinglow`
- **Issuer**: Apple Worldwide Developer Relations CA
- **Purpose**: Apple Pay Payment Processing
- **Validity**: Oct 5, 2025 - Nov 4, 2027

**⚠️ ACTION REQUIRED**:
```
📤 Upload applepay-payment-processing-gmo.p12 to GMO Payment Gateway

Steps:
1. Log in to GMO PG merchant dashboard
2. Navigate to: Payment Settings → Apple Pay
3. Upload: applepay-payment-processing-gmo.p12
4. Enter P12 password (if set during certificate creation)
5. Save and verify the upload
```

### 3️⃣ File Permissions

**Status**: ✅ **SECURED**

All private keys have been set to secure permissions (600):
- ✅ `merchant-identity-key.pem` - Permission: 600
- ✅ `payment-processing.key` - Permission: 600

### 4️⃣ Environment Configuration

**Status**: ✅ **CONFIGURED**

All environment variables are properly set:
- ✅ Merchant ID configured: `merchant.alpha.throwinglow`
- ✅ Certificate path correct: `/certs/merchant-identity-cert.pem`
- ✅ Key path correct: `/certs/merchant-identity-key.pem`
- ✅ Paths match actual file locations

---

## 🎯 Setup Completion Checklist

### ✅ Completed

- [x] Merchant Identity Certificate installed
- [x] Merchant Identity Private Key installed
- [x] Payment Processing Certificate available
- [x] Certificate/Key pair verified (MD5 match)
- [x] File permissions secured (600 for private keys)
- [x] Environment variables configured
- [x] Certificates validated (not expired)
- [x] Domain verification file served via Django route

### ⚠️ Pending Actions

- [ ] **Upload Payment Processing Certificate to GMO PG** (CRITICAL)
  - File: `certs/applepay-payment-processing-gmo.p12`
  - Location: GMO PG Dashboard → Payment Settings → Apple Pay
  - See: [SETUP_GUIDE.md](SETUP_GUIDE.md) Part 2, Step 2

- [ ] **Verify Domain with Apple** (Required for production)
  - Test: `curl https://yourdomain.com/.well-known/apple-developer-merchantid-domain-association`
  - Should return verification file content (not 404)
  - Add domain in Apple Developer portal

- [ ] **Test on Real Device** (Apple Pay only works on real devices)
  - Use iPhone/iPad with Safari
  - Add test card to Apple Wallet
  - Test payment flow end-to-end

---

## 📅 Certificate Renewal Schedule

### Set Calendar Reminders:

| Certificate | Expires | Renewal Due | Days Remaining |
|-------------|---------|-------------|----------------|
| Merchant Identity | Nov 6, 2027 | Oct 1, 2027 | 727 days |
| Payment Processing | Nov 4, 2027 | Sep 1, 2027 | 725 days |

**Renewal Process**:
1. Create new CSR (Certificate Signing Request)
2. Upload to Apple Developer portal
3. Download new certificate
4. Convert to required format (.pem for Merchant Identity, .p12 for Payment Processing)
5. Replace old certificates
6. Restart services
7. For Payment Processing: Upload new .p12 to GMO PG

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed renewal instructions.

---

## 🔍 Verification Commands

### Quick Status Check
```bash
# Run verification script
cd certs
./verify-certificates.sh
```

### Manual Verification
```bash
# Check certificate expiry
openssl x509 -in certs/merchant-identity-cert.pem -noout -dates

# Verify cert and key match
openssl x509 -noout -modulus -in certs/merchant-identity-cert.pem | openssl md5
openssl rsa -noout -modulus -in certs/merchant-identity-key.pem | openssl md5
# MD5 hashes should match

# Check certificate details
openssl x509 -in certs/merchant-identity-cert.pem -noout -text

# Test configuration endpoint
curl -k https://localhost:8443/api/payments/config/status/ | jq
```

---

## 🚀 Next Steps

### 1. Test Configuration
```bash
# Start services
docker-compose up --build

# Check configuration status
curl -k https://localhost:8443/api/payments/config/status/ | jq

# Expected output:
# {
#   "all_valid": true,
#   "apple_pay": {
#     "valid": true,
#     "configured": {
#       "cert_file_exists": true,
#       "key_file_exists": true
#     }
#   }
# }
```

### 2. Upload to GMO PG
Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) Part 2, Step 2 to upload `applepay-payment-processing-gmo.p12`

### 3. Test Merchant Validation
- Open `https://localhost:3443` in Safari
- Check browser console for errors
- Backend logs should show: "✅ Using REAL merchant validation with Apple servers"

### 4. Test on Real Device
- Connect iPhone/iPad to same network
- Update `.env` with your computer's IP
- Access `https://YOUR_IP:3443` in Safari
- Test Apple Pay button

---

## 📞 Troubleshooting

### Issue: Configuration status shows errors

**Check**:
```bash
docker-compose logs -f backend | grep -i "certificate\|apple"
```

**Common causes**:
- Files not accessible in Docker container (check volume mount)
- Incorrect paths in `.env`
- File permissions too restrictive

### Issue: Merchant validation fails

**Check**:
1. Domain verification file accessible
2. Merchant Identity Certificate not expired
3. Certificate matches merchant ID
4. Backend can read certificate files

**Debug**:
```bash
# Check domain verification
curl https://localhost:8443/.well-known/apple-developer-merchantid-domain-association

# Check backend logs
docker-compose logs -f backend
```

### Issue: Payment execution fails

**Check**:
1. Payment Processing Certificate uploaded to GMO PG
2. GMO credentials correct in `.env`
3. Token format correct

**Debug**:
```bash
# Check GMO API responses
docker-compose logs -f backend | grep "GMO"
```

---

## 📚 Documentation

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete setup instructions
- [FIXES_APPLIED.md](FIXES_APPLIED.md) - All fixes and changes
- [QUICK_TEST.md](QUICK_TEST.md) - Quick testing guide
- [certs/CERTIFICATES_INFO.md](certs/CERTIFICATES_INFO.md) - Detailed certificate info

---

## 🔒 Security Notes

### ✅ Security Measures Applied

1. **Private keys protected from version control**
   - All certificate files excluded in `.gitignore`
   - Private keys never committed to git

2. **File permissions secured**
   - Private keys: 600 (owner read/write only)
   - Public certs: 644 (owner read/write, others read)

3. **Environment variables secured**
   - All secrets in `.env` file (gitignored)
   - No hardcoded credentials in code

4. **Certificate validation on startup**
   - Expiry checking implemented
   - File existence verification
   - Certificate/key matching verification

### ⚠️ Important Reminders

1. **Never commit private keys to git**
   - Already protected by `.gitignore`
   - Verify with: `git status certs/`

2. **Backup P12 files securely**
   - Store in password manager or encrypted storage
   - Keep P12 passwords safe

3. **Monitor certificate expiry**
   - Set calendar reminders (see renewal schedule above)
   - Check status regularly: `./certs/verify-certificates.sh`

4. **Production deployment**
   - Use production GMO credentials
   - Use CA-signed SSL certificates (Let's Encrypt)
   - Set `DEBUG=False`
   - Verify domain with Apple

---

**Status**: ✅ **READY FOR TESTING**

All certificates are valid and properly configured. You can now:
1. Upload Payment Processing Certificate to GMO PG
2. Test merchant validation
3. Test payment flow on real device

Run `./certs/verify-certificates.sh` anytime to check certificate status.
