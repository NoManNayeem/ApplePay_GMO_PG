#!/bin/bash
# Certificate Verification Script for Apple Pay POC
# This script verifies that all required certificates are present and valid

set -e

echo "🔍 Apple Pay Certificate Verification"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CERT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$CERT_DIR"

# Track overall status
ALL_VALID=true

echo "📁 Certificate Directory: $CERT_DIR"
echo ""

# Function to check file exists
check_file() {
    local file=$1
    local desc=$2

    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $desc: $file"
        return 0
    else
        echo -e "${RED}❌${NC} $desc: $file (NOT FOUND)"
        ALL_VALID=false
        return 1
    fi
}

# Function to check certificate expiry
check_cert_expiry() {
    local file=$1
    local desc=$2

    if [ ! -f "$file" ]; then
        return 1
    fi

    # Get expiry date
    expiry=$(openssl x509 -in "$file" -noout -enddate 2>/dev/null | cut -d= -f2)

    if [ -z "$expiry" ]; then
        echo -e "${YELLOW}⚠️${NC}  $desc: Could not parse expiry date"
        return 1
    fi

    # Convert to epoch for comparison
    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$expiry" +%s 2>/dev/null)
    now_epoch=$(date +%s)
    days_until_expiry=$(( ($expiry_epoch - $now_epoch) / 86400 ))

    if [ $days_until_expiry -lt 0 ]; then
        echo -e "${RED}❌${NC} $desc: EXPIRED on $expiry"
        ALL_VALID=false
    elif [ $days_until_expiry -lt 30 ]; then
        echo -e "${YELLOW}⚠️${NC}  $desc: Expires SOON on $expiry ($days_until_expiry days)"
    else
        echo -e "${GREEN}✅${NC} $desc: Valid until $expiry ($days_until_expiry days)"
    fi
}

# Function to verify cert and key match
verify_cert_key_match() {
    local cert=$1
    local key=$2
    local desc=$3

    if [ ! -f "$cert" ] || [ ! -f "$key" ]; then
        return 1
    fi

    cert_mod=$(openssl x509 -noout -modulus -in "$cert" 2>/dev/null | openssl md5)
    key_mod=$(openssl rsa -noout -modulus -in "$key" 2>/dev/null | openssl md5)

    if [ "$cert_mod" = "$key_mod" ]; then
        echo -e "${GREEN}✅${NC} $desc: Certificate and key MATCH"
    else
        echo -e "${RED}❌${NC} $desc: Certificate and key DO NOT MATCH!"
        ALL_VALID=false
    fi
}

echo "1️⃣  Merchant Identity Certificate (for Apple merchant validation)"
echo "----------------------------------------------------------------"
check_file "merchant-identity-cert.pem" "Certificate file"
check_file "merchant-identity-key.pem" "Private key file"
check_file "applepay-merchant-identity.p12" "P12 bundle (backup)"

if [ -f "merchant-identity-cert.pem" ]; then
    check_cert_expiry "merchant-identity-cert.pem" "Certificate expiry"

    # Check subject
    subject=$(openssl x509 -in merchant-identity-cert.pem -noout -subject 2>/dev/null)
    echo "   Subject: $subject"
fi

if [ -f "merchant-identity-cert.pem" ] && [ -f "merchant-identity-key.pem" ]; then
    verify_cert_key_match "merchant-identity-cert.pem" "merchant-identity-key.pem" "Cert/Key matching"
fi

echo ""

echo "2️⃣  Payment Processing Certificate (for GMO Payment Gateway)"
echo "------------------------------------------------------------"
check_file "applepay-payment-processing-gmo.p12" "P12 for GMO upload"
check_file "payment-processing.pem" "PEM certificate (backup)"

if [ -f "payment-processing.pem" ]; then
    check_cert_expiry "payment-processing.pem" "Certificate expiry"

    # Check subject
    subject=$(openssl x509 -in payment-processing.pem -noout -subject 2>/dev/null)
    echo "   Subject: $subject"
fi

echo ""

echo "3️⃣  File Permissions"
echo "-------------------"
# Check permissions on private keys
for keyfile in merchant-identity-key.pem payment-processing.key; do
    if [ -f "$keyfile" ]; then
        perms=$(stat -c "%a" "$keyfile" 2>/dev/null || stat -f "%Lp" "$keyfile" 2>/dev/null)
        if [ "$perms" = "600" ] || [ "$perms" = "400" ]; then
            echo -e "${GREEN}✅${NC} $keyfile: Secure permissions ($perms)"
        else
            echo -e "${YELLOW}⚠️${NC}  $keyfile: Permissions too open ($perms) - should be 600"
            echo "   Run: chmod 600 $keyfile"
        fi
    fi
done

echo ""

echo "4️⃣  Environment Configuration Check"
echo "----------------------------------"
if [ -f "../.env" ]; then
    cert_path=$(grep "APPLE_MERCHANT_IDENTITY_CERT_PATH" ../.env | cut -d= -f2)
    key_path=$(grep "APPLE_MERCHANT_IDENTITY_KEY_PATH" ../.env | cut -d= -f2)
    merchant_id=$(grep "APPLE_MERCHANT_ID" ../.env | cut -d= -f2)

    echo "   Merchant ID: $merchant_id"
    echo "   Cert Path: $cert_path"
    echo "   Key Path: $key_path"

    if [[ "$cert_path" == *"merchant-identity-cert.pem"* ]]; then
        echo -e "${GREEN}✅${NC} Certificate path configured correctly"
    else
        echo -e "${RED}❌${NC} Certificate path may be incorrect"
        ALL_VALID=false
    fi
else
    echo -e "${YELLOW}⚠️${NC}  .env file not found in parent directory"
fi

echo ""

echo "5️⃣  Action Items"
echo "--------------"
echo "📤 Upload to GMO Payment Gateway:"
echo "   File: applepay-payment-processing-gmo.p12"
echo "   Location: GMO PG Dashboard → Payment Settings → Apple Pay"
echo ""
echo "🌐 Domain Verification:"
echo "   Ensure /.well-known/apple-developer-merchantid-domain-association is accessible"
echo "   Test: curl https://yourdomain.com/.well-known/apple-developer-merchantid-domain-association"
echo ""

echo "======================================"
if [ "$ALL_VALID" = true ]; then
    echo -e "${GREEN}✅ All certificate checks PASSED!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some certificate checks FAILED!${NC}"
    echo "   Review errors above and fix before proceeding."
    exit 1
fi
