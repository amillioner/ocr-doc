#!/usr/bin/env python3
"""
Generate self-signed SSL certificates for development/testing
Uses Python's cryptography library instead of OpenSSL
"""

import os
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, timezone
import ipaddress
import sys

def generate_ssl_certificates():
    """Generate self-signed SSL certificate and private key"""
    
    ssl_dir = Path("nginx/ssl")
    domain = os.getenv("DOMAIN", "localhost")
    
    print(f"Generating self-signed SSL certificate for {domain}...")
    
    # Create SSL directory if it doesn't exist
    ssl_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate private key
    print("Generating private key...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate
    print("Generating certificate...")
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])
    
    # Create Subject Alternative Names
    san_list = [
        x509.DNSName(domain),
        x509.DNSName(f"*.{domain}"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        x509.IPAddress(ipaddress.IPv6Address("::1")),
    ]
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now(timezone.utc)
    ).not_valid_after(
        datetime.now(timezone.utc) + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName(san_list),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Write private key
    key_path = ssl_dir / "key.pem"
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Write certificate
    cert_path = ssl_dir / "cert.pem"
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # Use ASCII-safe characters for Windows console
    print("\n[SUCCESS] SSL certificate generated successfully!")
    print(f"  Certificate: {cert_path}")
    print(f"  Private Key: {key_path}")
    print("")
    print("[WARNING] This is a self-signed certificate for development only.")
    print("          Browsers will show a security warning. For production, use Let's Encrypt.")

if __name__ == "__main__":
    generate_ssl_certificates()

