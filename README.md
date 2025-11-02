# Apple Pay POC with GMO Payment Gateway (2025)

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/NoManNayeem/ApplePay_GMO_PG)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

This is a minimal proof-of-concept project for integrating Apple Pay with GMO Payment Gateway, supporting both one-time and recurring payments. The implementation follows the latest 2025 documentation and best practices.

## 🌐 Repository

**GitHub:** [https://github.com/NoManNayeem/ApplePay_GMO_PG](https://github.com/NoManNayeem/ApplePay_GMO_PG)

This repository contains both the backend (Django REST Framework) and frontend (Next.js/React) implementation for Apple Pay integration with GMO Payment Gateway.

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Production Checklist](#production-checklist)

## Project Structure

```
ApplePay_POC/
├── backend/                    # Django REST Framework API
│   ├── Dockerfile              # Production Dockerfile
│   ├── manage.py
│   ├── requirements.txt        # Python dependencies
│   ├── .dockerignore
│   ├── applepay_poc/           # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── payments/               # Payments app
│       ├── models.py           # Transaction and Subscription models
│       ├── serializers.py     # DRF serializers
│       ├── views.py            # API endpoints
│       ├── services.py         # GMO PG client
│       ├── exceptions.py      # Custom exceptions
│       ├── config_validator.py # Configuration validation
│       └── urls.py
├── frontend/                   # Next.js application
│   ├── Dockerfile              # Production Dockerfile
│   ├── Dockerfile.dev          # Development Dockerfile
│   ├── package.json
│   ├── next.config.ts
│   ├── server.js               # HTTPS server for development
│   ├── .dockerignore
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx            # Home page
│   │   ├── onetime/            # One-time payment page
│   │   │   └── page.tsx
│   │   └── recurring/          # Recurring payment page
│   │       └── page.tsx
│   ├── components/
│   │   ├── ApplePayButton.tsx  # Apple Pay button component
│   │   └── ConfigStatus.tsx    # Configuration status component
│   └── lib/
│       └── api.ts              # API client
├── docs/                       # Documentation
│   ├── GMO_PG_APPLEPAY_SETUP.md
│   ├── GMO_PG_CREDENTIALS_CLARIFICATION.md
│   ├── QUICK_START.md
│   ├── README_CREDENTIALS.md
│   └── TURBOPACK_FIX.md
├── scripts/                     # Utility scripts
│   ├── generate-certs.sh       # SSL certificate generation (Linux/Mac)
│   ├── generate-certs.ps1      # SSL certificate generation (Windows)
│   └── generate-certs-docker.sh # SSL certificate generation (Docker)
├── certs/                       # SSL certificates (gitignored)
│   └── .gitkeep
├── docker-compose.yml          # Development Docker Compose
├── docker-compose.prod.yml     # Production Docker Compose
├── env.txt                     # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Prerequisites

### 1. Apple Developer Account Setup

#### Create Merchant ID

1. Log in to [Apple Developer Account](https://developer.apple.com/account)
2. Navigate to "Certificates, Identifiers & Profiles" → "Identifiers"
3. Click "+" → Select "Merchant IDs"
4. Create a new Merchant ID (e.g., `merchant.com.yourdomain`)
5. Note: Merchant IDs cannot be deleted once created

#### Generate Certificates

**Payment Processing Certificate:**
- Used to decrypt payment tokens from Apple Pay
- Valid for 25 months
- Generate CSR using Keychain Access (macOS) or OpenSSL
- Upload CSR to Apple Developer portal
- Download and securely store the certificate

**Merchant Identity Certificate:**
- Used to authenticate merchant session validation requests
- Required for proper merchant session generation
- Generate CSR and follow Apple's guidelines
- Store securely with private key

#### Register and Verify Domain (2025 Requirements)

1. Add your domain(s) to the Merchant ID configuration
2. Download the verification file: `apple-developer-merchantid-domain-association`
3. Host the file at: `https://yourdomain.com/.well-known/apple-developer-merchantid-domain-association`
4. Verify domain in Apple Developer portal
5. **Important**: Domain must be served over HTTPS with valid SSL certificate
6. **2025 Update**: Servers must support one of the designated six cipher suites for TLS connections

### 2. GMO Payment Gateway Account

1. **Register for PG Multi-Payment Service:**
   - Sign up at [GMO Payment Gateway](https://www.gmo-pg.com/)
   - Complete merchant registration and verification process
   - Choose appropriate plan (test/production)

2. **Obtain Credentials:**
   - **Shop ID**: Unique identifier for your shop
   - **Shop Password**: API authentication password
     - **Important**: Password must comply with both management interface and API requirements
     - Some symbols may be rejected by API even if accepted by management screen
   - **API Endpoint**: 
     - Test Base URL: `https://pt01.mul-pay.jp`
     - Production Base URL: `https://p01.mul-pay.jp`
     - API endpoints are appended to base URL (e.g., `EntryTranBrandtoken.idPass`)

3. **Configure Apple Pay:**
   - Enable Apple Pay payment method in GMO PG dashboard
   - Upload Apple Pay Payment Processing Certificate
   - Upload Merchant Identity Certificate (if required)
   - Configure notification URLs (for webhook callbacks)

4. **API Access:**
   - GMO PG supports both legacy idPass API and newer OpenAPI
   - This POC uses idPass API format (`EntryTranBrandtoken.idPass`, etc.)
   - For production, consider migrating to OpenAPI for better compliance and features

## Environment Setup

### 1. Create .env File

Copy the template and create your `.env` file:

```bash
# Linux/Mac
cp env.txt .env

# Windows PowerShell
Copy-Item env.txt .env

# Windows CMD
copy env.txt .env
```

### 2. Configure Environment Variables

Edit `.env` and set your values:

```env
# Required: Backend API URL for frontend
NEXT_PUBLIC_API_URL=https://localhost:8443

# Required: CORS allowed origins (frontend URLs)
CORS_ALLOWED_ORIGINS=https://localhost:3443,https://localhost:3000,http://localhost:3000

# Optional: GMO Payment Gateway credentials (for actual payments)
GMO_SHOP_ID=your-shop-id
GMO_SHOP_PASS=your-shop-password
GMO_API_ENDPOINT=https://pt01.mul-pay.jp

# Optional: Apple Pay Merchant ID (for merchant validation)
APPLE_MERCHANT_ID=merchant.com.yourdomain
```

**Important Notes:**
- The `.env` file is gitignored and won't be committed
- `NEXT_PUBLIC_API_URL` must point to your backend HTTPS URL
- `CORS_ALLOWED_ORIGINS` must include your frontend URLs
- Frontend connects to backend using `NEXT_PUBLIC_API_URL`

## Quick Start with Docker

The easiest way to run the entire application is using Docker Compose. This setup uses:
- **Python 3.12** for the backend (matching your system version)
- **Node 23** for the frontend (matching your system version)
- **OpenSSL** for HTTPS support (required for Apple Pay)

### Prerequisites

- Docker Desktop installed (or Docker Engine + Docker Compose)
- Git (to clone the repository)

### Environment Variables

Create a `.env` file in the root directory:

```env
# Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Settings (include HTTPS URLs for Apple Pay)
CORS_ALLOWED_ORIGINS=https://localhost:3443,http://localhost:3000

# GMO Payment Gateway
GMO_SHOP_ID=your-gmo-shop-id
GMO_SHOP_PASS=your-gmo-shop-password
GMO_API_ENDPOINT=https://pt01.mul-pay.jp

# Apple Pay
APPLE_MERCHANT_ID=merchant.com.yourdomain

# Frontend (use HTTPS URL for Apple Pay compatibility)
NEXT_PUBLIC_API_URL=https://localhost:8443
```

### HTTPS/SSL Setup (Automatic)

**Apple Pay requires HTTPS** - even for local development. The Docker setup automatically:

1. Generates self-signed SSL certificates using OpenSSL (on first run)
2. Configures backend to serve HTTPS on port 8443
3. Configures frontend to serve HTTPS on port 3443
4. Stores certificates in `./certs/` directory

**On first run**, certificates are automatically generated. You'll see:
```
Generating SSL certificates...
SSL certificates generated
```

**Important Notes:**
- Certificates are self-signed (for development only)
- Browsers will show a security warning - click "Advanced" → "Proceed to localhost"
- To trust the certificate permanently, import `certs/server.crt` into your system's trusted certificates
- Certificates are valid for 365 days and are reused on subsequent runs

### Running with Docker Compose

1. **Start all services (development mode):**
   ```bash
   docker-compose up
   ```
   
   Or run in detached mode:
   ```bash
   docker-compose up -d
   ```

2. **Access the applications:**
   
   **HTTPS (Recommended for Apple Pay):**
   - Backend API: https://localhost:8443
   - Frontend: https://localhost:3443
   - Admin Panel: https://localhost:8443/admin
   
   **HTTP (Fallback, Apple Pay won't work):**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   
   **First-time SSL warning:**
   - Browsers will show "Your connection is not private" warning
   - Click "Advanced" → "Proceed to localhost (unsafe)"
   - This is normal for self-signed certificates in development
   
   **Create admin user:**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

3. **Stop all services:**
   ```bash
   docker-compose down
   ```

4. **Rebuild containers (after dependency changes):**
   ```bash
   docker-compose up --build
   ```

5. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

6. **Run database migrations:**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

7. **Create superuser:**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

### Production Docker Setup

For production, use the production compose file:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Production differences:**
- Uses production Dockerfile (optimized builds)
- Runs Next.js in production mode
- Collects static files
- `DEBUG=False` by default
- Always restart policy

### Docker Commands Reference

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart a specific service
docker-compose restart backend

# Execute command in container
docker-compose exec backend python manage.py shell
docker-compose exec frontend npm run build

# View container status
docker-compose ps

# Pull latest images
docker-compose pull
```

### Docker Volumes

The following volumes are created for data persistence:

- `backend_static`: Static files for Django
- `backend_media`: Media files (if needed)
- `backend_logs`: Application logs

### Docker Status Check

After starting the services, you should see:

- ✅ Backend running: `Starting development server at http://0.0.0.0:8443/` (HTTPS)
- ✅ Frontend running: `Ready on https://0.0.0.0:3443` (HTTPS)
- ✅ SSL certificates: `SSL certificates generated` (first run only)

Both services are connected via the `applepay_network` Docker network.

**SSL Certificate Location:**
- Certificates are stored in `./certs/` directory
- `server.crt` - Certificate file
- `server.key` - Private key file
- Certificates persist between container restarts

### Troubleshooting Docker

**Port already in use:**
```bash
# Change ports in docker-compose.yml or stop conflicting services
docker-compose down
```

**Permission errors (Linux):**
```bash
# Fix ownership
sudo chown -R $USER:$USER .
```

**Container won't start:**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild without cache
docker-compose build --no-cache
```

**Database issues:**
```bash
# Reset database (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv  # Recommended: use virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory (copy from `.env.example`):

```env
# Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://localhost:3000

# GMO Payment Gateway Settings
GMO_SHOP_ID=your-gmo-shop-id
GMO_SHOP_PASS=your-gmo-shop-password
GMO_API_ENDPOINT=https://pt01.mul-pay.jp

# Apple Pay Settings
APPLE_MERCHANT_ID=merchant.com.yourdomain
```

**Security Notes:**
- Never commit `.env` file to version control
- Use strong, unique values for `SECRET_KEY`
- In production, use environment-specific values
- Rotate credentials regularly

### 3. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Logs Directory

```bash
mkdir logs
# Logs will be automatically created in this directory
```

### 5. Create Superuser (Optional, for Admin Access)

```bash
python manage.py createsuperuser
```

### 6. Start Development Server

```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

**Note**: For Apple Pay testing, you may need HTTPS. See [HTTPS Setup](#https-setup-for-development) section.

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note**: Environment variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### HTTPS Setup for Development

Apple Pay requires HTTPS (except for Safari on localhost in some cases). For local development:

**Option 1: Use Safari on macOS**
- Safari on macOS allows localhost Apple Pay testing without HTTPS

**Option 2: Local HTTPS with mkcert**
```bash
# Install mkcert
npm install -g mkcert

# Create local CA
mkcert -install

# Generate certificates
mkcert localhost 127.0.0.1

# Configure Next.js to use HTTPS (custom server or proxy)
```

**Option 3: Reverse Proxy**
- Use nginx or similar to add HTTPS layer

## API Endpoints

### Backend API Endpoints

All endpoints are under `/api/payments/`:

#### `GET /api/payments/merchant-session/`
Get merchant session information (for validation).

**Response:**
```json
{
  "merchant_id": "merchant.com.yourdomain",
  "message": "Merchant session endpoint"
}
```

#### `POST /api/payments/onetime/session/`
Create payment session for one-time payment.

**Response:**
```json
{
  "merchant_id": "merchant.com.yourdomain",
  "status": "ready"
}
```

#### `POST /api/payments/onetime/process/`
Process one-time Apple Pay payment.

**Request:**
```json
{
  "token": "{\"paymentData\":{...}}",
  "amount": 1000,
  "currency": "JPY"
}
```

**Success Response:**
```json
{
  "transaction_id": "uuid",
  "status": "completed",
  "amount": "1000",
  "currency": "JPY",
  "gmo_order_id": "ORDER_uuid"
}
```

**Error Response:**
```json
{
  "error": true,
  "status_code": 400,
  "message": "Transaction execution failed",
  "error_code": "EXEC_ERROR",
  "error_info": "Detailed error message"
}
```

#### `POST /api/payments/recurring/setup/`
Setup recurring payment subscription.

**Request:**
```json
{
  "token": "{\"paymentData\":{...}}",
  "amount": 1000,
  "currency": "JPY",
  "billing_cycle": "monthly"
}
```

**Success Response:**
```json
{
  "subscription_id": "uuid",
  "status": "active",
  "member_id": "MEMBER_uuid",
  "card_id": "card_id_from_gmo",
  "amount": "1000",
  "currency": "JPY",
  "billing_cycle": "monthly",
  "next_billing_date": "2025-12-02T11:00:00Z"
}
```

#### `POST /api/payments/recurring/charge/`
Process recurring charge for existing subscription.

**Request:**
```json
{
  "subscription_id": "uuid",
  "amount": 1000
}
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": true,
  "status_code": 400,
  "message": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "error_info": "Detailed error information"
}
```

### Common Error Codes

#### GMO Payment Gateway Errors

| Error Code | Description | Resolution |
|-----------|-------------|------------|
| `CONFIG_ERROR` | Payment gateway credentials not configured | Check `.env` file |
| `TIMEOUT` | Request to GMO PG timed out | Retry or check network |
| `CONNECTION_ERROR` | Connection to GMO PG failed | Check network and endpoint |
| `HTTP_4xx` | Client error from GMO PG | Check request parameters |
| `HTTP_5xx` | Server error from GMO PG | Contact GMO PG support |
| `ENTRY_ERROR` | Transaction entry failed | Check amount, order ID format |
| `EXEC_ERROR` | Transaction execution failed | Check payment token validity |
| `INVALID_TOKEN_FORMAT` | Payment token format invalid | Ensure token is valid JSON |

#### Validation Errors

- Amount validation errors
- Currency validation errors
- Token format validation errors
- Subscription validation errors

### Error Handling Best Practices

1. **Always Check Response Status**
   ```javascript
   try {
     const result = await api.processOneTimePayment(data);
     if (result.error) {
       // Handle error
     }
   } catch (error) {
     // Handle network/exception errors
   }
   ```

2. **Log Errors Server-Side**
   - All errors are logged to `backend/logs/django.log`
   - Check logs for detailed error information

3. **User-Friendly Messages**
   - Display user-friendly error messages in frontend
   - Don't expose sensitive information to users

4. **Retry Logic**
   - Implement retry for transient errors (timeouts, connection errors)
   - Use exponential backoff
   - Limit retry attempts

### Exception Types

Backend uses custom exceptions for better error handling:

- `GMOAPIException`: GMO PG API errors
- `PaymentProcessingException`: Payment processing failures
- `InvalidPaymentTokenException`: Invalid payment tokens
- `MerchantValidationException`: Merchant validation failures
- `SubscriptionException`: Subscription-related errors

## Security Considerations

### 2025 Security Requirements

1. **HTTPS/SSL/TLS**
   - All pages serving Apple Pay must use HTTPS
   - SSL certificate must be valid (not self-signed for production)
   - **2025 Update**: Servers must support one of six designated cipher suites:
     - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
     - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
     - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
     - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
     - TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
     - TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256

2. **Environment Variables**
   - Never commit `.env` files
   - Use secret management in production (AWS Secrets Manager, Azure Key Vault, etc.)
   - Rotate credentials regularly

3. **Payment Tokens**
   - Tokens are single-use and time-limited
   - Process tokens immediately upon receipt
   - Never store payment tokens
   - Tokens expire quickly (usually within minutes)

4. **API Security**
   - Implement rate limiting in production
   - Use authentication/authorization (this POC uses AllowAny for simplicity)
   - Validate all input data
   - Sanitize error messages (don't expose sensitive info)

5. **Certificate Management**
   - Store certificates securely
   - Monitor certificate expiration
   - Implement certificate rotation
   - Payment Processing Certificate valid for 25 months
   - Merchant Identity Certificate may have different validity

6. **PCI DSS Compliance**
   - GMO PG handles PCI DSS compliance for card data
   - Don't store card data locally
   - Use tokenization provided by payment gateway

### Browser Support (2025 Update)

As of February 24, 2025, Apple Pay is supported on:
- Safari (all supported versions)
- Chrome (third-party browser support)
- Firefox (third-party browser support)
- Edge (third-party browser support)

However, full feature support may vary by browser.

## Testing

### Prerequisites for Testing

1. **Device/Browser Requirements:**
   - Safari on macOS 10.12+ or iOS 10+
   - Chrome, Firefox, or Edge (2025 update)
   - Apple Pay must be set up with a test card

2. **Apple Pay Test Cards:**
   - Use test cards provided by Apple
   - Add test cards to Wallet app
   - Use test Apple ID in sandbox environment

3. **GMO PG Test Environment:**
   - Use GMO PG test endpoint
   - Test credentials provided by GMO PG
   - Test transactions won't charge real money

### Testing One-Time Payment

1. Navigate to `http://localhost:3000/onetime` (or HTTPS if required)
2. Enter amount and select currency
3. Click the Apple Pay button
4. Authenticate with Face ID, Touch ID, or passcode
5. Verify transaction appears in backend admin or logs
6. Check GMO PG dashboard for transaction status

### Testing Recurring Payment

1. Navigate to `http://localhost:3000/recurring`
2. Enter amount, currency, and billing cycle
3. Click the Apple Pay button
4. Authenticate payment
5. Verify subscription creation
6. Test recurring charge endpoint manually (for scheduled billing)

### Testing Scenarios

**Success Cases:**
- Successful one-time payment
- Successful subscription setup
- Successful recurring charge

**Error Cases:**
- Invalid amount (validation)
- Invalid currency (validation)
- Invalid token format
- Network timeout
- Payment decline
- User cancellation

**Edge Cases:**
- Very large amounts
- Minimum amounts
- Multiple currencies
- Expired tokens
- Concurrent requests

## Troubleshooting

### Apple Pay Button Not Showing

**Possible Causes:**
1. Not using supported browser/device
2. Apple Pay not set up on device
3. Not on HTTPS (except Safari localhost)
4. Merchant ID not configured

**Solutions:**
1. Use Safari on macOS or iOS device
2. Set up Apple Pay in Wallet app
3. Enable HTTPS for development or use Safari
4. Check `APPLE_MERCHANT_ID` in `.env`

### Merchant Validation Errors

**Symptoms:**
- `Merchant validation failed` error
- Apple Pay sheet doesn't open

**Solutions:**
1. Verify Merchant ID is correct
2. Ensure domain is verified in Apple Developer portal
3. Check verification file is accessible at `/.well-known/apple-developer-merchantid-domain-association`
4. Verify SSL certificate is valid
5. Check server supports required cipher suites (2025 requirement)

### GMO PG API Errors

**Common Errors:**

**E01020008**: Password validation error
- Ensure Shop Password meets both management and API requirements
- Some symbols may be rejected by API

**PO01500024**: Credit card authentication error
- User needs to re-enter card details
- Token may be expired or invalid

**Timeout Errors:**
- Check network connectivity
- Verify API endpoint is correct
- Check firewall settings

**Connection Errors:**
- Verify GMO PG endpoint URL
- Check credentials are correct
- Ensure test/production environment matches

### Payment Token Issues

**Expired Tokens:**
- Tokens expire quickly (usually within minutes)
- Process tokens immediately upon receipt
- Don't queue token processing

**Invalid Token Format:**
- Ensure token is valid JSON
- Don't modify token structure
- Pass token as JSON string to backend

### CORS Issues

**Symptoms:**
- `CORS policy` errors in browser console
- API requests blocked

**Solutions:**
1. Check `CORS_ALLOWED_ORIGINS` in backend `.env`
2. Ensure frontend URL matches allowed origins
3. Verify CORS middleware is enabled
4. Check `CORS_ALLOW_CREDENTIALS` setting

### Database Errors

**Migrations:**
```bash
# Reset migrations if needed
python manage.py migrate payments zero
python manage.py makemigrations
python manage.py migrate
```

**Database Lock:**
- Close other connections to SQLite database
- Use PostgreSQL in production

## Production Checklist

### Before Going Live

- [ ] Replace test credentials with production credentials
- [ ] Set `DEBUG=False` in production
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up HTTPS with valid SSL certificate
- [ ] Verify server supports required cipher suites (2025)
- [ ] Set up proper logging and monitoring
- [ ] Implement authentication/authorization
- [ ] Set up rate limiting
- [ ] Configure proper error reporting (Sentry, etc.)
- [ ] Set up database backups
- [ ] Test with real Apple Pay cards (small amounts)
- [ ] Verify webhook handling (if implemented)
- [ ] Set up certificate monitoring and alerts
- [ ] Review and update security headers
- [ ] Conduct security audit
- [ ] Load testing
- [ ] Disaster recovery plan

### Certificate Management

- [ ] Set up certificate expiration monitoring
- [ ] Create certificate rotation procedure
- [ ] Document certificate locations and access
- [ ] Backup certificates securely
- [ ] Test certificate renewal process

### Monitoring

- [ ] Set up transaction monitoring
- [ ] Monitor error rates
- [ ] Set up alerts for critical errors
- [ ] Track API response times
- [ ] Monitor certificate expiration

## 📚 Additional Documentation

For detailed setup instructions and troubleshooting, see the `docs/` directory:

- **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running quickly
- **[GMO PG & Apple Pay Setup](docs/GMO_PG_APPLEPAY_SETUP.md)** - Detailed setup instructions
- **[Credentials Guide](docs/README_CREDENTIALS.md)** - How to obtain and configure credentials
- **[GMO PG Credentials Clarification](docs/GMO_PG_CREDENTIALS_CLARIFICATION.md)** - Common credential questions
- **[Turbopack Fix](docs/TURBOPACK_FIX.md)** - Troubleshooting Next.js bundler issues

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NoManNayeem/ApplePay_GMO_PG.git
   cd ApplePay_GMO_PG
   ```

2. **Create `.env` file:**
   ```bash
   cp env.txt .env
   # Edit .env with your credentials
   ```

3. **Start with Docker:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: https://localhost:3443
   - Backend API: https://localhost:8443
   - Admin Panel: https://localhost:8443/admin

5. **Create admin user:**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

For more detailed instructions, see [Quick Start Guide](docs/QUICK_START.md).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This is a proof-of-concept project for demonstration purposes. Use at your own risk.

## 🙏 Acknowledgments

- [Apple Pay on the Web](https://developer.apple.com/documentation/applepayontheweb) - Official documentation
- [GMO Payment Gateway](https://www.gmo-pg.com/) - Payment gateway provider
- [Django REST Framework](https://www.django-rest-framework.org/) - Backend framework
- [Next.js](https://nextjs.org/) - Frontend framework

## 📞 Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/NoManNayeem/ApplePay_GMO_PG/issues)
- Check the [documentation](docs/) directory
- Review troubleshooting section in this README

## 🔄 Changelog

### 2025 Updates

- ✅ Enhanced error handling with custom exceptions
- ✅ Improved GMO PG API response parsing
- ✅ Added comprehensive input validation
- ✅ Updated for 2025 Apple Pay requirements (cipher suites, browser support)
- ✅ Improved logging and debugging
- ✅ Enhanced security guidelines
- ✅ Docker Compose setup for easy development
- ✅ HTTPS support for local development
- ✅ Configuration validation and status endpoint
- ✅ Proper merchant session validation flow

---

**⚠️ Note**: This POC is for testing purposes only. Ensure proper security measures, testing, and compliance before deploying to production.
