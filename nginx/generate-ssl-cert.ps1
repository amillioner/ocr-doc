# PowerShell script to generate self-signed SSL certificates for development/testing
# For production, use Let's Encrypt certificates instead

$SSL_DIR = ".\nginx\ssl"
$DOMAIN = if ($env:DOMAIN) { $env:DOMAIN } else { "localhost" }

Write-Host "Generating self-signed SSL certificate for $DOMAIN..." -ForegroundColor Cyan

# Create SSL directory if it doesn't exist
if (-not (Test-Path $SSL_DIR)) {
    New-Item -ItemType Directory -Path $SSL_DIR -Force | Out-Null
}

# Check if OpenSSL is available
$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if (-not $openssl) {
    Write-Host "ERROR: OpenSSL is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install OpenSSL:" -ForegroundColor Yellow
    Write-Host "  - Windows: Download from https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor Yellow
    Write-Host "  - Or use: choco install openssl" -ForegroundColor Yellow
    Write-Host "  - Or use: winget install ShiningLight.OpenSSL" -ForegroundColor Yellow
    exit 1
}

# Generate private key
Write-Host "Generating private key..." -ForegroundColor Gray
& openssl genrsa -out "$SSL_DIR\key.pem" 2048

# Generate certificate signing request
Write-Host "Generating certificate signing request..." -ForegroundColor Gray
& openssl req -new -key "$SSL_DIR\key.pem" -out "$SSL_DIR\csr.pem" `
    -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"

# Create config file for SAN (Subject Alternative Names)
$configContent = @"
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = *.$DOMAIN
IP.1 = 127.0.0.1
IP.2 = ::1
"@
$configFile = "$SSL_DIR\openssl.conf"
$configContent | Out-File -FilePath $configFile -Encoding ASCII

# Generate self-signed certificate (valid for 365 days)
Write-Host "Generating self-signed certificate..." -ForegroundColor Gray
& openssl x509 -req -days 365 -in "$SSL_DIR\csr.pem" -signkey "$SSL_DIR\key.pem" `
    -out "$SSL_DIR\cert.pem" -extensions v3_req -extfile "$configFile"

# Set proper permissions (Windows)
$acl = Get-Acl "$SSL_DIR\key.pem"
$permission = "BUILTIN\Administrators","FullControl","Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl "$SSL_DIR\key.pem" $acl

# Clean up temporary files
Remove-Item "$SSL_DIR\csr.pem" -ErrorAction SilentlyContinue
Remove-Item "$configFile" -ErrorAction SilentlyContinue

Write-Host "`n✓ SSL certificate generated successfully!" -ForegroundColor Green
Write-Host "  Certificate: $SSL_DIR\cert.pem" -ForegroundColor Gray
Write-Host "  Private Key: $SSL_DIR\key.pem" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  WARNING: This is a self-signed certificate for development only." -ForegroundColor Yellow
Write-Host "   Browsers will show a security warning. For production, use Let's Encrypt." -ForegroundColor Yellow

