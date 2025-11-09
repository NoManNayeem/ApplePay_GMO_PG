#!/bin/bash
# Cleanup Duplicate Certificate Files
# This script moves duplicate/legacy certificate files to a backup directory

set -e

CERT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$CERT_DIR"

echo "🗑️  Certificate Cleanup - Removing Duplicates"
echo "==========================================="
echo ""

# Create backup directory
BACKUP_DIR="./backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Creating backup directory: $BACKUP_DIR"
echo ""

# Files to keep (DO NOT MOVE)
KEEP_FILES=(
    "merchant-identity-cert.pem"
    "merchant-identity-key.pem"
    "applepay-merchant-identity.p12"
    "applepay-payment-processing-gmo.p12"
    "payment-processing.pem"
    "payment-processing.key"
    "server.crt"
    "server.key"
    ".gitkeep"
    "README.txt"
    "CERTIFICATES_INFO.md"
    "verify-certificates.sh"
    "cleanup-duplicates.sh"
)

# Files to move (duplicates/legacy)
REMOVE_FILES=(
    "apple_pay.cer"
    "merchant_id.cer"
    "merchantcert.crt"
    "merchantcert (1).crt"
    "merchant-identity.csr"
    "payment-processing.csr"
    "merchant-identity.pem"
    "merchant-identity.key"
    "localhost.crt"
    "localhost.key"
)

echo "📦 Moving duplicate/legacy files to backup..."
echo ""

moved_count=0
for file in "${REMOVE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   Moving: $file"
        mv "$file" "$BACKUP_DIR/"
        moved_count=$((moved_count + 1))
    fi
done

echo ""
if [ $moved_count -gt 0 ]; then
    echo "✅ Moved $moved_count files to $BACKUP_DIR"
    echo ""
    echo "📋 Files kept in certs directory:"
    ls -lh | grep -E "\.(pem|p12|crt|key|md|sh|txt)$" | awk '{print "   " $9, "(" $5 ")"}'
    echo ""
    echo "💡 If you need any moved files, they are in: $BACKUP_DIR"
    echo "   You can safely delete the backup directory after verifying everything works."
else
    echo "✅ No duplicate files found - directory is already clean!"
    rmdir "$BACKUP_DIR"
fi

echo ""
echo "🔍 Run './verify-certificates.sh' to verify certificate setup"
