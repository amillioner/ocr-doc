# SSL Certificate Setup Guide

This guide explains how to set up SSL certificates for the OCR API with NGINX.

## Quick Start (Self-Signed Certificate for Development)

### Windows (PowerShell)
```powershell
.\nginx\generate-ssl-cert.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x nginx/generate-ssl-cert.sh
./nginx/generate-ssl-cert.sh
```

This will generate self-signed certificates in `nginx/ssl/` directory.

**Note:** Self-signed certificates will trigger browser security warnings. This is fine for development but not suitable for production.

## Production Setup (Let's Encrypt)

For production, use Let's Encrypt to get trusted SSL certificates.

### Prerequisites
1. A domain name pointing to your server
2. Ports 80 and 443 open and accessible
3. Certbot installed

### Option 1: Using Certbot (Recommended)

1. **Install Certbot** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install certbot
   
   # Or use Docker
   docker run -it --rm certbot/certbot --version
   ```

2. **Stop nginx temporarily**:
   ```bash
   docker-compose stop nginx
   ```

3. **Obtain certificate**:
   ```bash
   # Replace yourdomain.com with your actual domain
   docker run -it --rm \
     -v "$(pwd)/nginx/certbot:/var/www/certbot" \
     -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
     certbot/certbot certonly \
     --webroot \
     --webroot-path=/var/www/certbot \
     --email your-email@example.com \
     --agree-tos \
     --no-eff-email \
     -d yourdomain.com \
     -d www.yourdomain.com
   ```

4. **Update nginx configuration** to use Let's Encrypt certificates:
   Edit `nginx/default.conf` and update the SSL paths:
   ```nginx
   ssl_certificate /etc/nginx/ssl/live/yourdomain.com/fullchain.pem;
   ssl_certificate_key /etc/nginx/ssl/live/yourdomain.com/privkey.pem;
   ```

5. **Start nginx**:
   ```bash
   docker-compose up -d nginx
   ```

6. **Set up auto-renewal**:
   Create a cron job or scheduled task to renew certificates:
   ```bash
   # Add to crontab (runs twice daily)
   0 0,12 * * * docker run --rm -v "$(pwd)/nginx/certbot:/var/www/certbot" -v "$(pwd)/nginx/ssl:/etc/letsencrypt" certbot/certbot renew --quiet
   ```

### Option 2: Using Docker Compose with Certbot

You can add a certbot service to your `docker-compose.yml`:

```yaml
  certbot:
    image: certbot/certbot
    volumes:
      - ./nginx/certbot:/var/www/certbot
      - ./nginx/ssl:/etc/letsencrypt
    command: certonly --webroot --webroot-path=/var/www/certbot --email your-email@example.com --agree-tos --no-eff-email -d yourdomain.com
```

## Using Your Own Certificates

If you have your own SSL certificates:

1. Place your certificate file as `nginx/ssl/cert.pem`
2. Place your private key as `nginx/ssl/key.pem`
3. Ensure proper permissions:
   ```bash
   chmod 644 nginx/ssl/cert.pem
   chmod 600 nginx/ssl/key.pem
   ```

## Testing SSL Configuration

After setting up certificates:

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Test HTTPS connection**:
   ```bash
   curl -k https://localhost/docs
   # or
   curl -k https://yourdomain.com/docs
   ```

3. **Check nginx logs**:
   ```bash
   docker-compose logs nginx
   ```

## Troubleshooting

### Certificate not found error
- Ensure certificates are in `nginx/ssl/` directory
- Check file names: `cert.pem` and `key.pem`
- Verify file permissions

### Connection refused
- Check if ports 80 and 443 are open
- Verify firewall settings
- Check docker-compose logs: `docker-compose logs nginx`

### Browser security warning (self-signed)
- This is expected for self-signed certificates
- Click "Advanced" → "Proceed to site" (for development only)
- For production, use Let's Encrypt certificates

### Certificate expired
- Renew Let's Encrypt certificates: `certbot renew`
- Or regenerate self-signed certificate using the scripts

## Security Notes

- **Never commit private keys to version control**
- Add `nginx/ssl/key.pem` to `.gitignore`
- Use strong passwords for private keys in production
- Keep certificates updated and monitor expiration dates
- Use Let's Encrypt for production environments

