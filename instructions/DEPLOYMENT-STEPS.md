# Step-by-Step Docker + NGINX Deployment Guide

Complete instructions for deploying your OCR API with NGINX and SSL/HTTPS.

## Prerequisites Checklist

- [x] Repository cloned and latest code pulled
- [ ] Docker installed on server
- [ ] Docker Compose installed on server
- [ ] Domain name pointing to your server
- [ ] SSH access to your server

## Step 1: Verify Docker Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# If not installed, install Docker:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose:
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Step 2: Navigate to Project Directory

```bash
# Navigate to your cloned repository
cd ~/ocr-doc
# or wherever you cloned it
cd /path/to/ocr-doc

# Verify you're in the right directory
ls -la
# You should see: docker-compose.yml, Dockerfile, main.py, nginx/, etc.
```

## Step 3: Create .env File

```bash
# Copy the template
cp env.hostinger.template .env

# Edit the .env file with your values
nano .env
# or use vi: vi .env
```

**Required values in .env:**
```env
# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://owpylhrddksbsrnatokc.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# OCR API Configuration
USE_GPU=False
OCR_LANG=en

# API Configuration
API_HOST=0.0.0.0
API_PORT=8050
PORT=8050

# CORS Configuration
# For production, replace * with your frontend domain:
# CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ORIGINS=*

# File Upload Configuration
MAX_FILE_SIZE=10485760
```

**Save and exit:**
- Nano: `Ctrl+X`, then `Y`, then `Enter`
- Vi: `Esc`, then `:wq`, then `Enter`

## Step 4: Set Up SSL Certificates

### Option A: Let's Encrypt (Recommended for Production)

```bash
# 1. Install Certbot (if not installed)
sudo apt-get update
sudo apt-get install certbot -y

# 2. Stop any existing web server (if running)
sudo systemctl stop apache2 2>/dev/null
sudo systemctl stop nginx 2>/dev/null

# 3. Obtain SSL certificate
# Replace 'yourdomain.com' with your actual domain
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 4. Create SSL directory
mkdir -p nginx/ssl

# 5. Copy certificates to nginx/ssl directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# 6. Set proper permissions
sudo chown $USER:$USER nginx/ssl/*.pem
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem

# 7. Verify certificates exist
ls -la nginx/ssl/
# You should see: cert.pem and key.pem
```

### Option B: Self-Signed (Development/Testing Only)

```bash
# Generate self-signed certificates using Python
python3 nginx/generate-ssl-cert.py

# Or using the shell script (if OpenSSL is installed)
chmod +x nginx/generate-ssl-cert.sh
./nginx/generate-ssl-cert.sh
```

## Step 5: Build Docker Images

```bash
# Build both the API and NGINX images
docker-compose build

# This will:
# - Build the OCR API image (Python + PaddleOCR)
# - Build the NGINX image (with SSL certificates included)
# - May take several minutes the first time
```

**Expected output:**
```
Building ocr-api...
Building nginx...
Successfully built...
```

## Step 6: Start the Services

```bash
# Start all services in detached mode
docker-compose up -d

# This will start:
# - ocr-doc-api (FastAPI application on port 8050, internal)
# - ocr-nginx (NGINX reverse proxy on ports 80 and 443)
```

## Step 7: Verify Services Are Running

```bash
# Check container status
docker-compose ps

# Expected output:
# NAME          STATUS
# ocr-doc-api   Up (healthy)
# ocr-nginx     Up
```

**If containers aren't running:**
```bash
# Check logs for errors
docker-compose logs

# Check specific service logs
docker-compose logs nginx
docker-compose logs ocr-api
```

## Step 8: Configure Firewall (If Needed)

```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# If using firewalld (CentOS/RHEL):
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Verify ports are open
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

## Step 9: Test Your Deployment

### Test HTTP (should redirect to HTTPS)

```bash
curl -I http://yourdomain.com
# or
curl -I http://localhost
```

**Expected:** `301 Moved Permanently` redirect to HTTPS

### Test HTTPS

```bash
curl -I https://yourdomain.com/docs
# or
curl -I https://localhost/docs
```

**Expected:** `200 OK` response

### Test in Browser

1. Open your browser
2. Navigate to: `https://yourdomain.com/docs`
3. You should see the FastAPI documentation page

**Note:** If using self-signed certificates, you'll see a security warning. Click "Advanced" → "Proceed to site" (for development only).

## Step 10: Set Up Auto-Renewal for SSL (Let's Encrypt)

```bash
# Edit crontab
crontab -e

# Add this line (runs twice daily at midnight and noon)
0 0,12 * * * certbot renew --quiet && docker-compose restart nginx

# Save and exit
```

## Step 11: Set Up Auto-Start on Reboot (Optional)

```bash
# Create systemd service file
sudo nano /etc/systemd/system/ocr-api.service
```

**Add this content:**
```ini
[Unit]
Description=OCR API Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/your-username/ocr-doc
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=your-username

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
# Replace 'your-username' with your actual username
sudo systemctl daemon-reload
sudo systemctl enable ocr-api.service
sudo systemctl start ocr-api.service
```

## Troubleshooting

### Containers Won't Start

```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs nginx
docker-compose logs ocr-api

# Restart services
docker-compose restart
```

### SSL Certificate Errors

```bash
# Verify certificates exist
ls -la nginx/ssl/

# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Rebuild NGINX image if certificates changed
docker-compose build nginx
docker-compose up -d nginx
```

### Port Already in Use

```bash
# Check what's using port 80/443
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Stop conflicting services
sudo systemctl stop apache2
sudo systemctl stop nginx
```

### Can't Access from Browser

1. **Check firewall:** Ensure ports 80 and 443 are open
2. **Check DNS:** Verify domain points to correct IP
3. **Check container status:** `docker-compose ps`
4. **Check logs:** `docker-compose logs nginx`

### Update After Code Changes

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
```

## Quick Reference Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild after changes
docker-compose build
docker-compose up -d

# Check status
docker-compose ps

# Access container shell
docker exec -it ocr-doc-api bash
docker exec -it ocr-nginx sh
```

## Summary

Your deployment is complete when:
- ✅ Both containers are running (`docker-compose ps`)
- ✅ HTTPS is accessible (`https://yourdomain.com/docs`)
- ✅ HTTP redirects to HTTPS
- ✅ No errors in logs (`docker-compose logs`)

## Next Steps

1. **Update CORS_ORIGINS** in `.env` with your frontend domain for production
2. **Test your API endpoints** using the `/docs` interface
3. **Monitor logs** regularly: `docker-compose logs -f`
4. **Set up monitoring** (optional) for production

Your OCR API is now live with HTTPS! 🚀

