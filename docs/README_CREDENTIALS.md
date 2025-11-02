# Credentials and Secrets Setup Guide

This is a quick reference guide for setting up credentials. For detailed instructions, see [GMO_PG_APPLEPAY_SETUP.md](./GMO_PG_APPLEPAY_SETUP.md).

## Quick Setup Checklist

### 1. Create `.env` File

```bash
# Windows
copy env.txt .env

# Linux/Mac
cp env.txt .env
```

### 2. Required Credentials

#### GMO Payment Gateway (Test Mode)

**Get from GMO PG Dashboard:**
1. Register at https://www.gmo-pg.com/
2. Log in to merchant dashboard
3. Go to Account Settings
4. Copy your **Shop ID** and set **Shop Password**

**Set in `.env`:**
```env
GMO_SHOP_ID=your-test-shop-id
GMO_SHOP_PASS=your-test-shop-password
GMO_API_ENDPOINT=https://pt01.mul-pay.jp
```

#### Apple Pay Merchant ID

**Get from Apple Developer Account:**
1. Sign up for Apple Developer Program ($99/year): https://developer.apple.com/programs/
2. Log in: https://developer.apple.com/account
3. Go to "Certificates, Identifiers & Profiles" → "Identifiers"
4. Click "+" → Select "Merchant IDs"
5. Register: Format `merchant.com.yourdomain`
6. Enable "Apple Pay" capability

**Set in `.env`:**
```env
APPLE_MERCHANT_ID=merchant.com.yourdomain
```

### 3. Verify Configuration

After starting the application:

1. **Frontend**: Visit https://localhost:3443
2. Check the **Configuration Status** banner at the top
3. **Green**: All configured ✓
4. **Yellow**: Missing credentials - follow the instructions shown

### 4. Test Configuration Endpoint

Check backend configuration directly:

```bash
# In browser or curl
GET https://localhost:8443/api/payments/config/status/
```

Returns:
- `all_valid`: true/false
- List of errors if configuration incomplete
- Setup guide links

## Common Issues

### "GMO_SHOP_ID is not configured"
- Copy `.env` from `env.txt`
- Add your GMO PG Shop ID
- Restart Docker containers

### "APPLE_MERCHANT_ID is not configured"
- Create Merchant ID in Apple Developer portal
- Add to `.env` file
- Restart Docker containers

### "Payment gateway connection failed"
- Check GMO PG credentials are correct
- Verify Shop Password (some special chars may not work with API)
- Ensure using test base URL: `https://pt01.mul-pay.jp`

## Next Steps

1. ✅ Configure `.env` with all credentials
2. ✅ Check configuration status on frontend
3. ✅ Test one-time payment
4. ✅ Test recurring payment setup

For detailed setup instructions, see [GMO_PG_APPLEPAY_SETUP.md](./GMO_PG_APPLEPAY_SETUP.md).

