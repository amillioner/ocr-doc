# Deploy with IP Address: 93.127.216.78

Complete step-by-step guide for deploying your OCR API using IP address with self-signed SSL certificates.

## Prerequisites

- [x] Repository cloned on your Hostinger VPS
- [x] Docker and Docker Compose installed
- [x] You're in the project directory: `cd ~/ocr-doc` (or wherever you cloned it)

## Step 1: Generate SSL Certificate for Your IP

```bash
# Generate self-signed certificate for your IP address
python3 nginx/generate-ssl-cert.py 93.127.216.78
```

**Expected output:**
```
Generating self-signed SSL certificate for 93.127.216.78...
Generating private key...
Generating certificate...

[SUCCESS] SSL certificate generated successfully!
  Certificate: nginx/ssl/cert.pem
  Private Key: nginx/ssl/key.pem
```

**Verify certificates were created:**
```bash
ls -la nginx/ssl/
# Should show: cert.pem and key.pem
```

## Step 2: Create .env File

```bash
# Copy the template
cp env.hostinger.template .env

# Edit with your values
nano .env
```

**Add these values (use your actual Supabase key):**
```env
# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://owpylhrddksbsrnatokc.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im93cHlsaHJkZGtzYnNybmF0b2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyMTg0NDQsImV4cCI6MjA3Mzc5NDQ0NH0.baE9RQfNiXj71kN_X8JOKt-B6Ei9tYgLLy-Om8NqQxw

# OCR API Configuration
USE_GPU=False
OCR_LANG=en

# API Configuration
API_HOST=0.0.0.0
API_PORT=8050
PORT=8050

# CORS Configuration
# Use * for development, or specify your frontend domain(s)
CORS_ORIGINS=*

# File Upload Configuration
MAX_FILE_SIZE=10485760
```

**Save and exit:**
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

## Step 3: Build Docker Images

```bash
# Build both API and NGINX images
docker-compose build
```

**This will take a few minutes** (especially the first time). You'll see:
- Building OCR API image (Python + PaddleOCR dependencies)
- Building NGINX image (with SSL certificates)

**Expected output:**
```
Building ocr-api...
Building nginx...
Successfully built...
```

## Step 4: Start the Services

```bash
# Start all services in detached mode
docker-compose up -d
```

**Expected output:**
```
Creating network ocr-doc_ocr-network
Creating container ocr-doc-api
Creating container ocr-nginx
Starting ocr-doc-api
Starting ocr-nginx
```

## Step 5: Verify Services Are Running

```bash
# Check container status
docker-compose ps
```

**Should show:**
```
NAME          STATUS
ocr-doc-api   Up (healthy)
ocr-nginx     Up
```

**If containers aren't running:**
```bash
# Check logs for errors
docker-compose logs

# Check specific service
docker-compose logs nginx
docker-compose logs ocr-api
```

## Step 6: Configure Firewall

```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Reload firewall
sudo ufw reload

# Verify ports are open
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

## Step 7: Test Your Deployment

### Test HTTP (should redirect to HTTPS)

```bash
curl -I http://93.127.216.78
```

**Expected:** `301 Moved Permanently` (redirect to HTTPS)

### Test HTTPS

```bash
curl -k -I https://93.127.216.78/docs
```

**Expected:** `200 OK`

**Note:** The `-k` flag ignores SSL certificate warnings (needed for self-signed certs)

### Test in Browser

1. Open your browser
2. Go to: `https://93.127.216.78/docs`
3. You'll see a security warning (this is normal for self-signed certificates)
4. Click **"Advanced"** → **"Proceed to 93.127.216.78"** (or similar)
5. You should see the FastAPI documentation page

## Step 8: Test Your API Endpoints

### Test OCR Endpoint

```bash
# Test with a sample image (if you have one)
curl -k -X POST https://93.127.216.78/ocr \
  -F "file=@/path/to/image.png"
```

### Access API Documentation

Open in browser: `https://93.127.216.78/docs`

You can test all endpoints directly from the Swagger UI.

## Troubleshooting

### Containers Won't Start

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose down
docker-compose build
docker-compose up -d
```

### SSL Certificate Issues

```bash
# Verify certificates exist
ls -la nginx/ssl/

# Rebuild NGINX if certificates changed
docker-compose build nginx
docker-compose up -d nginx
```

### Port Already in Use

```bash
# Check what's using ports 80/443
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Stop conflicting services
sudo systemctl stop apache2 2>/dev/null
sudo systemctl stop nginx 2>/dev/null
```

### Can't Access from Browser

1. **Check firewall**: Ensure ports 80 and 443 are open
2. **Check container status**: `docker-compose ps`
3. **Check logs**: `docker-compose logs nginx`
4. **Test locally first**: `curl -k https://localhost/docs`

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

# Rebuild after code changes
docker-compose down
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
```

## Your API URLs

- **HTTPS API**: `https://93.127.216.78`
- **API Docs**: `https://93.127.216.78/docs`
- **OCR Endpoint**: `https://93.127.216.78/ocr`
- **Upload Endpoint**: `https://93.127.216.78/upload`

## For Your Frontend

Update your frontend to call:
```javascript
const API_URL = 'https://93.127.216.78';

// Example: OCR request
fetch(`${API_URL}/ocr`, {
  method: 'POST',
  body: formData
});
```

**Important:** Make sure `CORS_ORIGINS` in your `.env` includes your frontend domain, or use `*` for development.

## Next Steps

1. ✅ Test all endpoints from `/docs` page
2. ✅ Update your frontend to use `https://93.127.216.78`
3. ✅ Monitor logs: `docker-compose logs -f`
4. ✅ (Optional) Get a domain name later for production (no browser warnings)

## Summary

You're all set! Your OCR API is now running at:
- **https://93.127.216.78/docs**

The browser warning is normal for self-signed certificates. Your API works perfectly - just click through the warning.

🎉 **Deployment Complete!**

