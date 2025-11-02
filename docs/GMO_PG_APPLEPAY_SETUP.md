# GMO Payment Gateway - Apple Pay Setup Guide (2025)

This guide explains how to set up Apple Pay integration with GMO Payment Gateway, including test mode configuration, obtaining credentials, and required certificates.

## Table of Contents

1. [Test Mode vs Live Mode](#test-mode-vs-live-mode)
2. [Obtaining GMO PG Credentials](#obtaining-gmo-pg-credentials)
3. [Obtaining Apple Pay Merchant ID](#obtaining-apple-pay-merchant-id)
4. [Required Certificates and Secrets](#required-certificates-and-secrets)
5. [Domain Verification](#domain-verification)
6. [Configuration Steps](#configuration-steps)

---

## Test Mode vs Live Mode

### Test Mode (Development Environment)

**Purpose:** Simulate transactions without processing real payments.

**GMO PG Test Endpoints:**
- **Test Base URL:** `https://pt01.mul-pay.jp`
- **API Endpoints:** Append endpoint names to base URL (e.g., `EntryTranBrandtoken.idPass`)
- **Test Shop ID:** Provided when you register for a test account
- **Test Shop Password:** Set during test account creation

**Characteristics:**
- No real money is processed
- Transactions are simulated
- Test cards can be used
- Essential for integration verification
- Results don't affect production data

**How to Access Test Mode:**
1. Register for a GMO PG test account at: https://www.gmo-pg.com/
2. Complete merchant registration process
3. GMO PG will provide test Shop ID and credentials
4. Use test endpoint: `https://pt01.mul-pay.jp`

### Live Mode (Production Environment)

**Purpose:** Process actual transactions with real customer payments.

**GMO PG Production Endpoints:**
- **Production Base URL:** `https://p01.mul-pay.jp`
- **API Endpoints:** Append endpoint names to base URL
- **Live Shop ID:** Provided after account approval
- **Live Shop Password:** Set during production account setup

**Requirements:**
- All certificates must be production-grade
- Domain must be verified with Apple
- SSL/TLS with valid certificates
- Full compliance with PCI DSS standards
- Complete merchant verification

**Switching to Live Mode:**
- Contact GMO PG support to activate production account
- Update API endpoint in your application
- Replace test credentials with production credentials
- Ensure all Apple Pay certificates are production versions

---

## Obtaining GMO PG Credentials

### 1. Shop ID

**What it is:** Unique identifier for your merchant account with GMO PG.

**How to Get:**
1. Register with GMO Payment Gateway: https://www.gmo-pg.com/
2. Complete merchant registration and verification
3. Shop ID is provided in your account dashboard
4. Separate Shop IDs for test and production environments

**Where to Find:**
- GMO PG Merchant Dashboard → Account Settings
- Contact GMO PG support if not visible

### 2. Shop Password

**What it is:** API authentication password for secure API access.

**How to Get:**
1. Set during account registration
2. Can be changed in GMO PG dashboard → Security Settings
3. Must comply with GMO PG password requirements

**Important Notes:**
- Password requirements may differ between management interface and API
- Some special characters accepted by dashboard may be rejected by API
- Use alphanumeric characters and safe special characters (e.g., `@`, `_`, `-`)
- Store securely - never commit to version control

### 3. API Endpoint

**Test Environment:**
```
https://pt01.mul-pay.jp
```

**Production Environment:**
```
https://p01.mul-pay.jp
```

**Where to Configure:**
- Set in your `.env` file as `GMO_API_ENDPOINT`
- For this POC (test mode), use base URL: `https://pt01.mul-pay.jp`
- API endpoints (like `EntryTranBrandtoken.idPass`) are automatically appended

---

## Obtaining Apple Pay Merchant ID

### Step 1: Apple Developer Account

**Requirement:** Active Apple Developer Program membership ($99/year)

**Sign Up:** https://developer.apple.com/programs/

### Step 2: Create Merchant ID

1. **Log in to Apple Developer Account:**
   - Go to https://developer.apple.com/account
   - Sign in with your Apple ID

2. **Navigate to Merchant IDs:**
   - Go to "Certificates, Identifiers & Profiles"
   - Click "Identifiers" in the sidebar
   - Select "Merchant IDs" from the dropdown

3. **Create New Merchant ID:**
   - Click the "+" button
   - Select "Merchant IDs"
   - Click "Continue"

4. **Register Merchant ID:**
   - **Description:** Enter a human-readable name (e.g., "My Company Apple Pay")
   - **Identifier:** Enter your Merchant ID (e.g., `merchant.com.yourcompanyname`)
     - Must be reverse domain format
     - Unique across all Apple developers
     - Cannot be changed after creation
   - Click "Continue" → "Register"

5. **Important Notes:**
   - Merchant IDs **cannot be deleted** once created
   - Choose identifier carefully
   - One Merchant ID can be used for multiple domains/apps
   - Format: `merchant.com.domain` or `merchant.com.subdomain`

### Step 3: Configure Merchant ID

1. **Enable Capabilities:**
   - Select your Merchant ID
   - Enable "Apple Pay" capability
   - Configure payment processing certificate (see below)

2. **Add Domain:**
   - Click "Add Domain"
   - Enter your domain (e.g., `yourdomain.com`)
   - Apple will provide a verification file to host

---

## Required Certificates and Secrets

### 1. Payment Processing Certificate

**Purpose:** Encrypts payment token data received from Apple Pay.

**How to Generate:**

1. **Generate Certificate Signing Request (CSR):**
   
   **On macOS (using Keychain Access):**
   - Open Keychain Access
   - Go to Certificate Assistant → Request a Certificate from a Certificate Authority
   - Enter your email and name
   - Select "Saved to disk"
   - Save CSR file

   **On Linux/Windows (using OpenSSL):**
   ```bash
   openssl genrsa -out merchant_private_key.key 2048
   openssl req -new -key merchant_private_key.key -out merchant.csr
   ```

2. **Upload CSR to Apple Developer Portal:**
   - Go to Apple Developer → Certificates, Identifiers & Profiles
   - Select your Merchant ID
   - Click "Create Certificate" → "Payment Processing Certificate"
   - Upload your CSR file
   - Download the certificate (.cer file)

3. **Convert to .p12 (for GMO PG upload):**
   - On macOS: Import to Keychain, export as .p12
   - On Linux: Use OpenSSL to create .p12:
   ```bash
   openssl x509 -inform DER -in merchant.cer -out merchant.crt
   openssl pkcs12 -export -out merchant.p12 -inkey merchant_private_key.key -in merchant.crt
   ```

4. **Upload to GMO PG:**
   - Log in to GMO PG Merchant Dashboard
   - Navigate to Payment Methods → Apple Pay
   - Upload the .p12 file
   - Enter the password used when creating .p12

**Validity:** 25 months (must be renewed before expiration)

### 2. Merchant Identity Certificate

**Purpose:** Authenticates merchant session validation requests to Apple Pay servers.

**How to Generate:**

1. **Generate CSR (similar to Payment Processing Certificate)**

2. **Upload to Apple Developer Portal:**
   - Select your Merchant ID
   - Click "Create Certificate" → "Merchant Identity Certificate"
   - Upload CSR
   - Download certificate

3. **Install on Your Server:**
   - Used for merchant session validation
   - Must be accessible to your backend server
   - Store securely with private key

**Note:** Some implementations may not require this for basic integration, but recommended for production.

### 3. Private Keys

**Purpose:** Used to decrypt payment tokens and authenticate requests.

**Security:**
- **NEVER** commit private keys to version control
- Store in secure location (environment variables, secrets manager)
- Use file permissions: `chmod 600` (Linux/Mac)
- Back up securely
- Rotate periodically

**Location:**
- Generated alongside CSR
- Usually `.key` or `.pem` format
- Associated with certificates

---

## Domain Verification

### Why Domain Verification?

Apple requires domain verification to ensure secure communication between your server and Apple Pay services.

### Step 1: Download Verification File

1. Go to Apple Developer → Merchant ID configuration
2. Add your domain (e.g., `yourdomain.com`)
3. Download verification file: `apple-developer-merchantid-domain-association`

### Step 2: Host Verification File

**Required Location:**
```
https://yourdomain.com/.well-known/apple-developer-merchantid-domain-association
```

**Requirements:**
- Must be served over HTTPS
- Must have valid SSL certificate
- File must be accessible without authentication
- Content-Type should be `application/pkcs7-mime` or `text/plain`
- Must return 200 status code

### Step 3: Verify in Apple Developer Portal

1. Return to Apple Developer Portal
2. Click "Verify" next to your domain
3. Apple will check if file is accessible
4. Verification may take a few minutes

### Step 4: For Local Development (POC)

For local testing with self-signed certificates:
- Domain verification may not work with `localhost`
- Use a real domain with HTTPS for full testing
- Or use Apple Pay test mode which may be more lenient

---

## Configuration Steps

### 1. Environment Variables Setup

Create `.env` file from `env.txt` template:

```env
# GMO Payment Gateway (Test Mode)
GMO_SHOP_ID=your-test-shop-id
GMO_SHOP_PASS=your-test-shop-password
GMO_API_ENDPOINT=https://pt01.mul-pay.jp

# Apple Pay
APPLE_MERCHANT_ID=merchant.com.yourcompanyname

# Frontend-Backend Connection
NEXT_PUBLIC_API_URL=https://localhost:8443
CORS_ALLOWED_ORIGINS=https://localhost:3443,https://localhost:3000,http://localhost:3000
```

### 2. GMO PG Dashboard Configuration

1. **Enable Apple Pay:**
   - Log in to GMO PG Merchant Dashboard
   - Navigate to Payment Methods
   - Enable Apple Pay

2. **Upload Payment Processing Certificate:**
   - Go to Apple Pay settings
   - Upload `.p12` certificate file
   - Enter certificate password
   - Save configuration

3. **Configure Callback URLs (if needed):**
   - Set notification URLs for payment status updates
   - Configure webhook endpoints

### 3. Backend Configuration

Ensure your backend can:
- Accept payment tokens from frontend
- Decrypt tokens using Payment Processing Certificate
- Make API calls to GMO PG endpoints
- Handle GMO PG responses

### 4. Frontend Configuration

Ensure your frontend:
- Uses HTTPS (required for Apple Pay)
- Can detect Apple Pay availability
- Properly validates merchant session
- Sends payment tokens to backend securely

---

## Testing Checklist

### Prerequisites

- [ ] GMO PG test account created
- [ ] Test Shop ID and password obtained
- [ ] Apple Developer account active
- [ ] Merchant ID created and configured
- [ ] Payment Processing Certificate generated and uploaded to GMO PG
- [ ] Domain verified with Apple (for production)
- [ ] HTTPS enabled on frontend and backend
- [ ] All environment variables configured

### Test Scenarios

1. **Merchant Session Validation:**
   - Frontend requests merchant session
   - Backend validates with Apple
   - Session token returned

2. **Payment Processing:**
   - User authorizes payment
   - Token sent to backend
   - Backend processes with GMO PG
   - Transaction completed

3. **Error Handling:**
   - Test with invalid credentials
   - Test with expired certificates
   - Test network failures

---

## Common Issues and Solutions

### Issue: "Merchant session validation failed"

**Possible Causes:**
- Merchant ID not configured correctly
- Merchant Identity Certificate missing or invalid
- Domain not verified

**Solution:**
- Verify Merchant ID in environment variables
- Check certificate validity
- Ensure domain verification completed

### Issue: "Payment processing failed"

**Possible Causes:**
- Payment Processing Certificate not uploaded to GMO PG
- Certificate password incorrect
- GMO PG credentials invalid

**Solution:**
- Verify certificate uploaded correctly in GMO PG dashboard
- Check Shop ID and password
- Test API connection independently

### Issue: "Apple Pay not available"

**Possible Causes:**
- Not using HTTPS
- Not on supported browser/device
- Apple Pay not set up on device

**Solution:**
- Ensure HTTPS is enabled
- Test on Safari (macOS/iOS) or supported browser
- Check device has Apple Pay configured

---

## Security Best Practices

1. **Never commit secrets to version control**
   - Use `.env` files (gitignored)
   - Use secrets management services in production

2. **Rotate credentials regularly**
   - Change passwords periodically
   - Renew certificates before expiration

3. **Use environment-specific credentials**
   - Separate test and production credentials
   - Never use production credentials in test environment

4. **Secure certificate storage**
   - Encrypt private keys
   - Use secure file permissions
   - Limit access to authorized personnel

5. **Monitor and log**
   - Log all payment transactions
   - Monitor for suspicious activity
   - Set up alerts for failures

---

## Resources

- **GMO Payment Gateway Documentation:** https://www.gmo-pg.com/en/service/mulpay-applepay/
- **Apple Pay Developer Documentation:** https://developer.apple.com/apple-pay/
- **Apple Developer Account:** https://developer.apple.com/account/
- **GMO PG Support:** Contact through merchant dashboard

---

## Summary

**For Test Mode (This POC):**

1. ✅ Register for GMO PG test account → Get test Shop ID
2. ✅ Create Apple Developer account → Create Merchant ID
3. ✅ Generate Payment Processing Certificate → Upload to GMO PG
4. ✅ Configure `.env` with test credentials
5. ✅ Use test endpoint: `https://pt01.mul-pay.jp`

**For Production:**

1. Switch to GMO PG production account
2. Use production Shop ID and endpoint
3. Ensure all certificates are production-grade
4. Complete domain verification with Apple
5. Update all environment variables

---

**Note:** This guide is based on 2025 documentation and best practices. Always refer to the latest official documentation from GMO PG and Apple for the most current requirements.

