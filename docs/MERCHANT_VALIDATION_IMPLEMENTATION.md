# Apple Pay Merchant Validation Implementation Guide

## Current Status

⚠️ **The current implementation uses MOCK merchant sessions, which will be REJECTED by Apple Pay.**

This is expected behavior. Apple Pay requires properly signed merchant sessions from Apple's validation servers.

## Why Mock Sessions Don't Work

Apple Pay validates merchant sessions cryptographically. When you create a mock session:
- The signature is fake/invalid
- Apple Pay's servers verify the signature
- The session is immediately rejected
- The payment is automatically cancelled

## How to Implement Proper Merchant Validation

### Step 1: Obtain Merchant Identity Certificate

1. **Generate a Certificate Signing Request (CSR):**
   ```bash
   openssl genrsa -out merchant_identity_key.pem 2048
   openssl req -new -key merchant_identity_key.pem -out merchant_identity.csr
   ```

2. **Upload CSR to Apple Developer Portal:**
   - Go to https://developer.apple.com/account/
   - Navigate to Certificates, Identifiers & Profiles
   - Select your Merchant ID
   - Click "Create Certificate" → "Merchant Identity Certificate"
   - Upload your CSR file
   - Download the certificate (.cer file)

3. **Convert Certificate to PEM Format:**
   ```bash
   openssl x509 -inform DER -in merchant_identity.cer -out merchant_identity.crt
   ```

4. **Store Securely:**
   - Place certificate and private key in a secure location
   - Set proper permissions: `chmod 600 merchant_identity_key.pem`
   - **NEVER commit to version control**
   - Use environment variables or secrets manager

### Step 2: Update Backend Configuration

Add to your `.env` file:
```env
APPLE_MERCHANT_IDENTITY_CERT_PATH=/path/to/merchant_identity.crt
APPLE_MERCHANT_IDENTITY_KEY_PATH=/path/to/merchant_identity_key.pem
```

### Step 3: Implement Merchant Validation

Replace the mock validation in `backend/payments/views.py` with real validation:

```python
import requests
import json
from django.conf import settings
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
import ssl
import certifi

def validate_merchant_with_apple(validation_url):
    """
    Validate merchant session with Apple's servers.
    
    Args:
        validation_url: The validation URL provided by Apple Pay
        
    Returns:
        dict: Validated merchant session from Apple
    """
    # Load Merchant Identity Certificate and Key
    cert_path = settings.APPLE_MERCHANT_IDENTITY_CERT_PATH
    key_path = settings.APPLE_MERCHANT_IDENTITY_KEY_PATH
    
    if not cert_path or not key_path:
        raise ValueError("Merchant Identity Certificate not configured")
    
    # Read certificate and key
    with open(cert_path, 'rb') as f:
        cert_data = f.read()
    
    with open(key_path, 'rb') as f:
        key_data = f.read()
    
    # Create SSL context with client certificate
    context = ssl.create_default_context(cafile=certifi.where())
    context.load_cert_chain(cert_path, key_path)
    
    # Send validation request to Apple
    response = requests.post(
        validation_url,
        cert=(cert_path, key_path),
        verify=True,
        timeout=10
    )
    
    if response.status_code != 200:
        raise Exception(f"Apple validation failed: {response.status_code} - {response.text}")
    
    # Return the merchant session
    return response.json()
```

### Step 4: Update ValidateMerchantView

Replace the mock session code in `ValidateMerchantView.post()`:

```python
def post(self, request):
    validation_url = request.data.get('validation_url')
    
    if not validation_url:
        return Response(
            {'error': 'validation_url is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate configuration
    apple_config = ConfigValidator.validate_apple_pay_config()
    if not apple_config['valid']:
        return Response(
            {
                'error': 'Apple Pay not configured',
                'errors': apple_config['errors'],
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        # Validate with Apple's servers
        merchant_session = validate_merchant_with_apple(validation_url)
        
        return Response({
            'merchantSession': merchant_session,
            'merchant_id': settings.APPLE_MERCHANT_ID,
        })
    except Exception as e:
        logger.error(f'Merchant validation error: {str(e)}')
        return Response(
            {
                'error': 'Merchant validation failed',
                'message': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

### Step 5: Install Required Dependencies

Add to `backend/requirements.txt`:
```
requests>=2.31.0
cryptography>=41.0.0
certifi>=2023.0.0
```

### Step 6: Domain Verification

Apple Pay requires domain verification:

1. **Download Domain Association File:**
   - From Apple Developer Portal → Your Merchant ID
   - Download `apple-developer-merchantid-domain-association` file

2. **Host the File:**
   - Place at: `https://yourdomain.com/.well-known/apple-developer-merchantid-domain-association`
   - Must be accessible via HTTPS
   - Must return correct Content-Type: `text/plain`

3. **Verify in Apple Developer Portal:**
   - Add your domain
   - Apple will verify the file is accessible
   - Status will show as "Verified" when complete

### Testing

Once implemented:
1. The merchant session will be properly signed by Apple
2. Apple Pay will accept the session
3. The payment sheet will remain open
4. Users can complete the payment

## Alternative: Using a Library

Consider using a library that handles merchant validation:

### Python: `applepay-merchant-validation`

```bash
pip install applepay-merchant-validation
```

```python
from applepay_merchant_validation import validate_merchant

merchant_session = validate_merchant(
    validation_url=validation_url,
    merchant_id=settings.APPLE_MERCHANT_ID,
    cert_path=settings.APPLE_MERCHANT_IDENTITY_CERT_PATH,
    key_path=settings.APPLE_MERCHANT_IDENTITY_KEY_PATH
)
```

## Troubleshooting

### Certificate Errors
- Ensure certificate and key are in correct format (PEM)
- Check file permissions (should be readable by server)
- Verify certificate hasn't expired

### Domain Verification Fails
- Ensure file is accessible via HTTPS
- Check Content-Type header
- Verify file content matches exactly (no extra whitespace)
- Check CORS headers if needed

### Validation Request Fails
- Check network connectivity to Apple's servers
- Verify certificate is valid and not expired
- Ensure Merchant ID matches certificate
- Check SSL/TLS configuration

## References

- [Apple Pay on the Web - Setting Up Your Server](https://developer.apple.com/documentation/apple_pay_on_the_web/setting_up_your_server)
- [Apple Pay JS API Documentation](https://developer.apple.com/documentation/apple_pay_on_the_web/apple_pay_js_api)
- [Merchant Identity Certificate Guide](https://developer.apple.com/documentation/apple_pay_on_the_web/setting_up_your_server#2953987)

