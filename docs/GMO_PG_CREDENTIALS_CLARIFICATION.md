# GMO Payment Gateway Credentials Clarification

## Shop ID and Shop Password Requirements

**Yes, Shop ID and Shop Pass ARE REQUIRED** for GMO Payment Gateway API authentication.

Based on GMO PG documentation and API specifications:

1. **Shop ID (Site ID)**: Unique identifier for your merchant account
   - Provided by GMO PG when you register
   - Required for all API requests
   - Different for test and production environments

2. **Shop Pass (Site Pass)**: Authentication password
   - Set during account setup
   - Must be included in all API requests
   - Must comply with GMO PG password requirements
   - Note: Some special characters may be accepted by dashboard but rejected by API

3. **Why Required**:
   - Authenticates your identity to GMO PG
   - Prevents unauthorized API access
   - Required for all payment operations (one-time, recurring, Apple Pay)
   - GMO PG validates these credentials on every API call

## Base URL Configuration

**Correct Base URLs:**

- **Test Environment**: `https://pt01.mul-pay.jp`
- **Production Environment**: `https://p01.mul-pay.jp`

**API Endpoint Format:**

GMO PG uses a base URL with endpoint names appended:
- Base URL: `https://pt01.mul-pay.jp`
- API Endpoint: `EntryTranBrandtoken.idPass`
- Full URL: `https://pt01.mul-pay.jp/EntryTranBrandtoken.idPass`

**Our Implementation:**

The `GMOClient` class automatically constructs the full URL:
```python
url = f"{self.api_endpoint}/{endpoint}"
# Example: https://pt01.mul-pay.jp/EntryTranBrandtoken.idPass
```

## Configuration in .env

```env
# Required: Shop ID for API authentication
GMO_SHOP_ID=your-test-shop-id

# Required: Shop Password for API authentication  
GMO_SHOP_PASS=your-test-shop-password

# Base URL (endpoints are appended automatically)
GMO_API_ENDPOINT=https://pt01.mul-pay.jp
```

## Summary

✅ **Shop ID and Shop Pass ARE REQUIRED**
- Without them, API calls will fail
- Configured in `.env` file
- Provided by GMO PG when you register

✅ **Correct Base URL**: `https://pt01.mul-pay.jp` (not `.com`, no `/payment/` path)
- API endpoints are appended automatically
- Test environment: `pt01.mul-pay.jp`
- Production environment: `p01.mul-pay.jp`

## References

- [GMO Payment Gateway Official Site](https://www.gmo-pg.com/en/service/mulpay-applepay/)
- Test Environment: https://pt01.mul-pay.jp

