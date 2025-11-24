# Hostinger Deployment Checklist

Quick checklist for deploying your OCR API to Hostinger.

## Pre-Deployment

- [ ] Hostinger VPS or Cloud Hosting account (with Docker support)
- [ ] Domain name registered and pointing to Hostinger
- [ ] SSH access credentials from Hostinger control panel
- [ ] Supabase credentials ready (URL and API key)
- [ ] Code pushed to Git repository (or ready to upload)

## Server Setup

- [ ] Connected to server via SSH
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Firewall configured (ports 80 and 443 open)

## Application Deployment

- [ ] Application files on server (via Git clone or file upload)
- [ ] `.env` file created with all environment variables
- [ ] SSL certificates set up (Let's Encrypt or Hostinger SSL)
- [ ] Certificates placed in `nginx/ssl/` directory

## Build & Start

- [ ] Docker images built: `docker-compose build`
- [ ] Services started: `docker-compose up -d`
- [ ] Services running: `docker-compose ps` (both containers up)
- [ ] No errors in logs: `docker-compose logs`

## SSL/HTTPS

- [ ] SSL certificates valid and not expired
- [ ] HTTPS accessible: `curl -I https://yourdomain.com`
- [ ] HTTP redirects to HTTPS: `curl -I http://yourdomain.com`
- [ ] Browser shows valid SSL (no warnings for Let's Encrypt)

## Testing

- [ ] API accessible: `https://yourdomain.com/docs`
- [ ] API endpoints working (test `/ocr` endpoint)
- [ ] CORS configured correctly for your frontend domain
- [ ] File uploads working (test with a sample document)

## Production Setup

- [ ] Auto-renewal configured for SSL certificates (cron job)
- [ ] Auto-start on reboot configured (systemd service)
- [ ] Monitoring/logging set up (optional)
- [ ] Backups configured (optional)

## Post-Deployment

- [ ] Update frontend to use new HTTPS API URL
- [ ] Test end-to-end workflow
- [ ] Monitor for errors: `docker-compose logs -f`
- [ ] Document any custom configurations

## Troubleshooting Commands

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild after changes
docker-compose build && docker-compose up -d

# Check SSL certificate
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test HTTPS
curl -I https://yourdomain.com/docs
```

## Quick Reference

- **Full Guide**: [HOSTINGER-DEPLOYMENT.md](HOSTINGER-DEPLOYMENT.md)
- **SSL Setup**: [nginx/README-SSL.md](nginx/README-SSL.md)
- **Main README**: [README.md](README.md)

