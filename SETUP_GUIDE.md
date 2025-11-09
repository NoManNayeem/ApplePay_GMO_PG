# Apple Pay + GMO Payment Gateway Setup Guide

This guide walks you through setting up Apple Pay with GMO Payment Gateway integration.

## Prerequisites

- Apple Developer Account ($99/year) - https://developer.apple.com/programs/
- GMO Payment Gateway test or production account - https://www.gmo-pg.com/en/
- Domain with HTTPS support (Let's Encrypt recommended for production)
- Docker and Docker Compose installed

## Part 1: Apple Developer Setup

### Step 1: Create Apple Merchant ID

1. Log in to [Apple Developer Account](https://developer.apple.com/account)
2. Navigate to **Certificates, Identifiers & Profiles**
3. Click **Identifiers** → **+** (Add button)
4. Select **Merchant IDs** → Click **Continue**
5. Enter:
   - **Description**: Your app name (e.g., "My E-commerce Store")
   - **Identifier**: `merchant.com.yourdomain.yourapp` (e.g., `merchant.com.example.store`)
6. Click **Continue** → **Register**

### Step 2: Enable Apple Pay Capability

1. In **Identifiers**, find your Merchant ID
2. Click to edit
3. Click **Create Certificate** under **Apple Pay Payment Processing Certificate**
4. Follow the prompts to create a Certificate Signing Request (CSR)

### Step 3: Generate Payment Processing Certificate

#### Create CSR (Certificate Signing Request)

```bash
# On your local machine or server
openssl genrsa -out payment-processing.key 2048
openssl req -new -key payment-processing.key -out payment-processing.csr -subj "/C=JP/O=YourCompany/CN=YourDomain"
```

#### Upload CSR to Apple Developer

1. Return to Apple Developer → Your Merchant ID → **Create Certificate**
2. Upload the `payment-processing.csr` file
3. Click **Continue**
4. Download the generated certificate (e.g., `apple_pay_payment_processing.cer`)

#### Convert Certificate to PEM/P12 Format

```bash
# Convert .cer to .pem
openssl x509 -inform DER -in apple_pay_payment_processing.cer -out payment-processing-cert.pem

# Create .p12 bundle (needed for GMO PG)
openssl pkcs12 -export -out applepay-payment-processing-gmo.p12 \
  -inkey payment-processing.key \
  -in payment-processing-cert.pem \
  -name "Apple Pay Payment Processing"

# Enter a password when prompted (you'll need this for GMO PG)
```

### Step 4: Generate Merchant Identity Certificate

This certificate is used for merchant session validation (communicating with Apple's servers during checkout).

#### Create CSR for Merchant Identity

```bash
openssl genrsa -out merchant-identity-key.pem 2048
openssl req -new -key merchant-identity-key.pem -out merchant-identity.csr \
  -subj "/C=JP/O=YourCompany/CN=merchant.com.yourdomain.yourapp"
```

#### Upload to Apple Developer

1. Go to **Certificates, Identifiers & Profiles** → **Certificates** → **+**
2. Select **Apple Pay Merchant Identity Certificate** → **Continue**
3. Select your Merchant ID → **Continue**
4. Upload `merchant-identity.csr` → **Continue**
5. Download the certificate (e.g., `merchant_id.cer`)

#### Convert Merchant Identity Certificate

```bash
# Convert .cer to .pem
openssl x509 -inform DER -in merchant_id.cer -out merchant-identity-cert.pem

# Verify you have both files:
# - merchant-identity-cert.pem (certificate)
# - merchant-identity-key.pem (private key from earlier)
```

### Step 5: Domain Verification

1. In Apple Developer, go to your Merchant ID
2. Click **Add Domain** under **Merchant Domains**
3. Enter your domain (e.g., `yourdomain.com`)
4. Download the verification file: `apple-developer-merchantid-domain-association`
5. Place it in your project's `.well-known/` directory (already done in this POC)
6. Ensure it's accessible at: `https://yourdomain.com/.well-known/apple-developer-merchantid-domain-association`
7. Click **Verify** in Apple Developer portal

**Note**: This POC already serves this file via Django - see `backend/applepay_poc/urls.py`

## Part 2: GMO Payment Gateway Setup

### Step 1: Register for GMO PG Account

**Test Environment**:
1. Visit https://www.gmo-pg.com/en/
2. Request a test account
3. You'll receive:
   - Shop ID (e.g., `tshop00070718`)
   - Shop Password
   - Test API endpoint: `https://pt01.mul-pay.jp`

**Production Environment**:
- Contact GMO PG sales for production account
- Production API endpoint: `https://p01.mul-pay.jp`

### Step 2: Upload Payment Processing Certificate to GMO

1. Log in to GMO PG merchant dashboard
2. Navigate to **Payment Settings** → **Apple Pay**
3. Click **Upload Certificate**
4. Upload the `applepay-payment-processing-gmo.p12` file (created in Part 1, Step 3)
5. Enter the password you used when creating the .p12 file
6. Click **Save**

**IMPORTANT**: GMO PG needs this certificate to decrypt Apple Pay payment tokens.

### Step 3: Configure API Credentials

Update your `.env` file:

```bash
# GMO Payment Gateway
GMO_SHOP_ID=your_shop_id_here
GMO_SHOP_PASS=your_shop_password_here
GMO_API_ENDPOINT=https://pt01.mul-pay.jp  # Test environment

# For production, use:
# GMO_API_ENDPOINT=https://p01.mul-pay.jp
```

## Part 3: Configure This Project

### Step 1: Place Certificate Files

Copy your certificates to the `certs/` directory:

```bash
cd certs/

# Merchant Identity Certificate (for Apple validation)
cp /path/to/merchant-identity-cert.pem .
cp /path/to/merchant-identity-key.pem .

# Payment Processing Certificate (already uploaded to GMO)
cp /path/to/applepay-payment-processing-gmo.p12 .
```

### Step 2: Update Environment Variables

Edit `.env` file:

```bash
# Apple Pay Configuration
APPLE_MERCHANT_ID=merchant.com.yourdomain.yourapp

# Certificate paths (default paths in Docker)
APPLE_MERCHANT_IDENTITY_CERT_PATH=/certs/merchant-identity-cert.pem
APPLE_MERCHANT_IDENTITY_KEY_PATH=/certs/merchant-identity-key.pem

# GMO Payment Gateway
GMO_SHOP_ID=your_shop_id
GMO_SHOP_PASS=your_shop_password
GMO_API_ENDPOINT=https://pt01.mul-pay.jp

# Django Security
SECRET_KEY=your_secure_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=https://localhost:8443  # For local dev
# For production: https://api.yourdomain.com
```

### Step 3: Secure Your Certificates

**IMPORTANT**: Never commit private keys to version control!

The `.gitignore` is already configured to exclude:
- `certs/*.pem`
- `certs/*.p12`
- `certs/*.key`

Verify with:
```bash
git status certs/
# Should show: "nothing to commit" or only README files
```

## Part 4: Testing

### Local Development Testing

```bash
# Start the services
docker-compose up --build

# Backend will be available at:
# - HTTPS: https://localhost:8443
# - HTTP: http://localhost:8000

# Frontend will be available at:
# - HTTPS: https://localhost:3443
# - HTTP: http://localhost:3000
```

### Test Merchant Validation

```bash
# Check configuration status
curl -k https://localhost:8443/api/payments/config/status/ | jq

# Should return:
# {
#   "all_valid": true,
#   "gmo_pg": { "valid": true, ... },
#   "apple_pay": { "valid": true, ... }
# }
```

### Test Domain Verification File

```bash
# Check that Apple domain verification file is accessible
curl -k https://localhost:8443/.well-known/apple-developer-merchantid-domain-association

# Should return the Apple verification file content
```

### Test Apple Pay on Real Device

**IMPORTANT**: Apple Pay only works on:
- Real iOS devices (iPhone, iPad) with Apple Pay set up
- Real Mac with Touch ID
- Safari browser (required for Apple Pay JS)

**Cannot test on**:
- iOS Simulator
- Android devices
- Chrome/Firefox browsers

**Test Steps**:

1. Access frontend on your device: `https://localhost:3443` (or your domain)
2. Accept the self-signed certificate warning (for local dev)
3. Add a test card to Apple Wallet
4. Try to make a payment
5. Check browser console and backend logs for any errors

### Production Deployment Checklist

- [ ] Domain registered and DNS configured
- [ ] SSL certificate from trusted CA (Let's Encrypt recommended)
- [ ] Domain verified in Apple Developer portal
- [ ] Merchant Identity Certificate created with production domain
- [ ] Payment Processing Certificate uploaded to GMO PG
- [ ] GMO PG production credentials configured
- [ ] `DEBUG=False` in `.env`
- [ ] `SECRET_KEY` generated and secure
- [ ] `ALLOWED_HOSTS` set to your domain only
- [ ] Database migrated to PostgreSQL/MySQL (not SQLite)
- [ ] Static files collected and served
- [ ] HTTPS enforced (no HTTP access)
- [ ] Monitoring and error tracking enabled

## Troubleshooting

### Issue: "Apple Pay certificates not configured"

**Solution**:
1. Check that certificate files exist in `certs/` directory
2. Verify paths in `.env` match actual file locations
3. Check file permissions (certificates should be readable)

### Issue: "Merchant validation failed"

**Possible causes**:
1. Domain not verified in Apple Developer portal
2. Domain verification file not accessible at `/.well-known/apple-developer-merchantid-domain-association`
3. Merchant Identity Certificate expired or invalid
4. Domain mismatch (certificate domain != request domain)

**Debug**:
```bash
# Check backend logs
docker-compose logs -f backend

# Test domain verification
curl https://yourdomain.com/.well-known/apple-developer-merchantid-domain-association
```

### Issue: "Payment execution failed"

**Possible causes**:
1. Payment Processing Certificate not uploaded to GMO PG
2. GMO PG credentials incorrect
3. Token format incompatible
4. GMO PG account not configured for Apple Pay

**Debug**:
```bash
# Check GMO API response in backend logs
docker-compose logs -f backend | grep "GMO"
```

### Issue: "Apple Pay button not showing"

**Requirements**:
1. Must use HTTPS (not HTTP)
2. Must use Safari browser
3. Must be on real device with Apple Pay configured
4. Device must have cards added to Wallet

### Issue: "Certificate expired"

**Solution**:
1. Merchant Identity Certificates expire after 1 year
2. Payment Processing Certificates expire after 25 months
3. Generate new CSR and create new certificate in Apple Developer portal
4. Replace old certificate files
5. Restart services

## Security Best Practices

1. **Never commit private keys** - Already configured in `.gitignore`
2. **Use environment variables** - All secrets in `.env` (gitignored)
3. **Rotate certificates** - Set calendar reminders before expiry
4. **Use production DB** - PostgreSQL/MySQL, not SQLite
5. **Enable monitoring** - Sentry, DataDog, or similar
6. **Rate limiting** - Prevent API abuse
7. **HTTPS only** - No mixed content, enforce HTTPS
8. **Regular updates** - Keep dependencies updated

## Support

- **Apple Pay Documentation**: https://developer.apple.com/apple-pay/
- **GMO PG Documentation**: https://www.gmo-pg.com/en/docs/
- **This Project Issues**: Check README.md for contact info

## Certificate Renewal Checklist

### Annually (Merchant Identity Certificate)

- [ ] Create new CSR: `openssl req -new -key merchant-identity-key.pem -out merchant-identity-renewal.csr`
- [ ] Upload to Apple Developer portal
- [ ] Download new certificate
- [ ] Convert to PEM: `openssl x509 -inform DER -in new_cert.cer -out merchant-identity-cert.pem`
- [ ] Replace old certificate
- [ ] Restart services
- [ ] Test merchant validation

### Every 25 Months (Payment Processing Certificate)

- [ ] Create new CSR: `openssl req -new -key payment-processing.key -out payment-processing-renewal.csr`
- [ ] Upload to Apple Developer portal
- [ ] Download new certificate
- [ ] Convert to P12
- [ ] Upload to GMO PG dashboard
- [ ] Test payment flow

## Next Steps

1. Complete this setup guide
2. Test on staging environment
3. Verify all payments work correctly
4. Deploy to production
5. Monitor for errors
6. Set up certificate expiry alerts

For any issues, check the backend logs: `docker-compose logs -f backend`
