#!/bin/bash
# Generate SSL certificates inside Docker container

set -e

CERT_DIR="/certs"
mkdir -p "$CERT_DIR"

echo "Generating self-signed SSL certificates..."

# Generate private key
openssl genrsa -out "$CERT_DIR/server.key" 2048

# Generate self-signed certificate with SAN
openssl req -new -x509 -key "$CERT_DIR/server.key" -out "$CERT_DIR/server.crt" \
    -days 365 \
    -subj "/C=US/ST=Development/L=Local/O=ApplePayPOC/OU=Dev/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:::1"

# Set permissions
chmod 600 "$CERT_DIR/server.key"
chmod 644 "$CERT_DIR/server.crt"

echo "✅ SSL certificates generated in $CERT_DIR"

