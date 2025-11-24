# Simple Deployment Steps for Your IP: 93.127.216.78

## Quick Answer

**For your IP address `93.127.216.78`**, you have two options:

### Option 1: Use IP Address (Quick Start)

```bash
# 1. Generate self-signed certificate for your IP
python3 nginx/generate-ssl-cert.py 93.127.216.78

# 2. Create .env file
cp env.hostinger.template .env
nano .env  # Add your Supabase credentials

# 3. Build and start
docker-compose build
docker-compose up -d

# 4. Access your API
# https://93.127.216.78/docs
# (Browser will show warning - click "Advanced" → "Proceed")
```

### Option 2: Use Domain Name (Better for Production)

If you have a domain (or want to get one):

1. **Point domain to your IP**: `93.127.216.78`
2. **Get Let's Encrypt certificate**:
   ```bash
   sudo certbot certonly --standalone -d api.yourdomain.com
   sudo cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem nginx/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem nginx/ssl/key.pem
   ```
3. **Build and start**:
   ```bash
   docker-compose build
   docker-compose up -d
   ```
4. **Access**: `https://api.yourdomain.com/docs` (no warnings!)

---

## Complete Steps for IP Address Deployment

### Step 1: Generate SSL Certificate for IP

```bash
# Generate certificate that includes your IP
python3 nginx/generate-ssl-cert.py 93.127.216.78
```

This creates:
- `nginx/ssl/cert.pem`
- `nginx/ssl/key.pem`

### Step 2: Create .env File

```bash
cp env.hostinger.template .env
nano .env
```

**Required values:**
```env
SUPABASE_URL=https://owpylhrddksbsrnatokc.supabase.co
SUPABASE_KEY=your_supabase_key_here
USE_GPU=False
OCR_LANG=en
API_HOST=0.0.0.0
API_PORT=8050
PORT=8050
CORS_ORIGINS=*
MAX_FILE_SIZE=10485760
```

### Step 3: Build Docker Images

```bash
docker-compose build
```

### Step 4: Start Services

```bash
docker-compose up -d
```

### Step 5: Verify

```bash
# Check containers
docker-compose ps

# Test HTTPS (will show warning - that's normal for self-signed)
curl -k https://93.127.216.78/docs

# Or open in browser
# https://93.127.216.78/docs
```

### Step 6: Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

---

## Access Your API

- **HTTPS**: `https://93.127.216.78/docs`
- **HTTP**: `http://93.127.216.78` (redirects to HTTPS)

**Note**: Browser will show "Not Secure" warning for self-signed certificates. This is normal. Click "Advanced" → "Proceed to 93.127.216.78" to continue.

---

## For Your Frontend

Update your frontend to call:
```
https://93.127.216.78/ocr
https://93.127.216.78/upload
```

Make sure `CORS_ORIGINS` in `.env` includes your frontend domain, or use `*` for development.

---

## Summary

**What to put for "yourdomain.com"?**

- **If you have a domain**: Use your domain name (e.g., `api.yourdomain.com`)
- **If you only have IP**: Use `93.127.216.78` and generate self-signed certificate

**The certificate generation script now supports both!**

