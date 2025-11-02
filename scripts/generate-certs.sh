#!/bin/bash
# Generate self-signed SSL certificates for development

set -e

CERT_DIR="./certs"
mkdir -p "$CERT_DIR"

echo "Generating self-signed SSL certificates for development..."

# Generate private key
openssl genrsa -out "$CERT_DIR/server.key" 2048

# Generate certificate signing request
openssl req -new -key "$CERT_DIR/server.key" -out "$CERT_DIR/server.csr" \
    -subj "/C=US/ST=Development/L=Local/O=ApplePayPOC/OU=Dev/CN=localhost"

# Generate self-signed certificate valid for 365 days
openssl x509 -req -days 365 -in "$CERT_DIR/server.csr" -signkey "$CERT_DIR/server.key" \
    -out "$CERT_DIR/server.crt" \
    -extensions v3_req \
    -extfile <(
        cat <<EOF
[ v3_req ]
subjectAltName = @alt_names
[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
    )

# Clean up CSR
rm "$CERT_DIR/server.csr"

# Set permissions
chmod 600 "$CERT_DIR/server.key"
chmod 644 "$CERT_DIR/server.crt"

echo "✅ SSL certificates generated successfully!"
echo "   Certificate: $CERT_DIR/server.crt"
echo "   Private Key: $CERT_DIR/server.key"
echo ""
echo "⚠️  Note: This is a self-signed certificate for development only."
echo "   You will need to accept the security warning in your browser."

