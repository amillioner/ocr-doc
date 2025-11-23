# Quick start script: Generate SSL certificate and start services
# This script will:
# 1. Generate self-signed SSL certificates
# 2. Start Docker Compose services

Write-Host "=== OCR API SSL Setup and Start ===" -ForegroundColor Cyan
Write-Host ""

# Check if OpenSSL is available
$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if (-not $openssl) {
    Write-Host "ERROR: OpenSSL is not installed or not in PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install OpenSSL using one of these methods:" -ForegroundColor Yellow
    Write-Host "  1. Chocolatey: choco install openssl" -ForegroundColor Gray
    Write-Host "  2. Winget: winget install ShiningLight.OpenSSL" -ForegroundColor Gray
    Write-Host "  3. Download: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor Gray
    Write-Host ""
    Write-Host "After installing, restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

# Check if certificates already exist
$certExists = Test-Path ".\nginx\ssl\cert.pem"
$keyExists = Test-Path ".\nginx\ssl\key.pem"

if ($certExists -and $keyExists) {
    Write-Host "SSL certificates already exist." -ForegroundColor Green
    $regenerate = Read-Host "Regenerate certificates? (y/N)"
    if ($regenerate -eq "y" -or $regenerate -eq "Y") {
        Write-Host "Regenerating SSL certificates..." -ForegroundColor Yellow
        & .\nginx\generate-ssl-cert.ps1
    } else {
        Write-Host "Using existing certificates." -ForegroundColor Green
    }
} else {
    Write-Host "Generating SSL certificates..." -ForegroundColor Yellow
    & .\nginx\generate-ssl-cert.ps1
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to generate SSL certificates. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting Docker Compose services..." -ForegroundColor Cyan
Write-Host ""

# Start Docker Compose
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Services Started Successfully! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your API is now available at:" -ForegroundColor Cyan
    Write-Host "  - HTTPS: https://localhost" -ForegroundColor White
    Write-Host "  - HTTP:  http://localhost (redirects to HTTPS)" -ForegroundColor White
    Write-Host "  - Docs:  https://localhost/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: Browsers will show a security warning for self-signed certificates." -ForegroundColor Yellow
    Write-Host "      This is normal for development. Click 'Advanced' → 'Proceed' to continue." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Gray
    Write-Host "  docker-compose logs -f" -ForegroundColor White
    Write-Host ""
    Write-Host "To stop services:" -ForegroundColor Gray
    Write-Host "  docker-compose down" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "Failed to start services. Check the error messages above." -ForegroundColor Red
    Write-Host "View logs with: docker-compose logs" -ForegroundColor Yellow
    exit 1
}

