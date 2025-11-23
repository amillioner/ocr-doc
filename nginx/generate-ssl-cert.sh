#!/bin/bash
# Script to generate self-signed SSL certificates for development/testing
# For production, use Let's Encrypt certificates instead

set -e

SSL_DIR="./nginx/ssl"
DOMAIN="${DOMAIN:-localhost}"

echo "Generating self-signed SSL certificate for ${DOMAIN}..."

# Create SSL directory if it doesn't exist
mkdir -p "${SSL_DIR}"

# Generate private key
openssl genrsa -out "${SSL_DIR}/key.pem" 2048

# Generate certificate signing request
openssl req -new -key "${SSL_DIR}/key.pem" -out "${SSL_DIR}/csr.pem" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in "${SSL_DIR}/csr.pem" -signkey "${SSL_DIR}/key.pem" \
    -out "${SSL_DIR}/cert.pem" \
    -extensions v3_req \
    -extfile <(echo "[v3_req]"; echo "subjectAltName=DNS:${DOMAIN},DNS:*.${DOMAIN},IP:127.0.0.1,IP:::1")

# Set proper permissions
chmod 600 "${SSL_DIR}/key.pem"
chmod 644 "${SSL_DIR}/cert.pem"

# Clean up CSR file
rm -f "${SSL_DIR}/csr.pem"

echo "✓ SSL certificate generated successfully!"
echo "  Certificate: ${SSL_DIR}/cert.pem"
echo "  Private Key: ${SSL_DIR}/key.pem"
echo ""
echo "⚠️  WARNING: This is a self-signed certificate for development only."
echo "   Browsers will show a security warning. For production, use Let's Encrypt."

