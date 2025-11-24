# Hostinger Deployment Guide

Complete guide for deploying the OCR API with SSL/HTTPS to Hostinger.

## Prerequisites

1. **Hostinger Account** with one of the following:
   - **VPS Hosting** (recommended for Docker)
   - **Cloud Hosting** (if Docker support is available)
   - **Business/Pro Shared Hosting** (limited Docker support)

2. **Domain Name** pointing to your Hostinger server

3. **SSH Access** to your Hostinger server

4. **Docker and Docker Compose** installed on the server

## Step 1: Prepare Your Application

### Option A: Deploy via Git (Recommended)

1. **Push your code to a Git repository** (GitHub, GitLab, Bitbucket):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Note your repository URL** for cloning on the server

### Option B: Deploy via File Transfer

1. **Create a deployment package**:
   ```powershell
   # Create a zip file excluding unnecessary files
   Compress-Archive -Path * -DestinationPath ocr-api-deploy.zip -Exclude @('__pycache__', '*.pyc', '.git', 'output', '*.log')
   ```

2. **Upload via Hostinger File Manager** or **FTP/SFTP**

## Step 2: Connect to Your Hostinger Server

### Via SSH

```bash
ssh username@your-server-ip
# or
ssh username@your-domain.com
```

**Note**: Your SSH credentials are in your Hostinger control panel under "SSH Access"

## Step 3: Install Docker and Docker Compose

If not already installed on your Hostinger server:

```bash
# Update system
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Add your user to docker group (optional, to avoid sudo)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

## Step 4: Clone/Upload Your Application

### If using Git:

```bash
# Navigate to your web directory (usually /home/username/public_html or /var/www)
cd /home/your-username/public_html
# or create a dedicated directory
mkdir -p ~/ocr-api
cd ~/ocr-api

# Clone your repository
git clone https://github.com/your-username/ocr-doc.git .
# or
git clone https://github.com/your-username/ocr-doc.git ocr-api
cd ocr-api
```

### If using File Transfer:

1. Upload your files via **Hostinger File Manager** or **SFTP**
2. Extract the archive:
   ```bash
   unzip ocr-api-deploy.zip -d ~/ocr-api
   cd ~/ocr-api
   ```

## Step 5: Set Up Environment Variables

Create a `.env` file on the server:

```bash
cd ~/ocr-api
nano .env
```

Add your environment variables:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# PaddleOCR Configuration
USE_GPU=False
OCR_LANG=en

# API Configuration
API_HOST=0.0.0.0
API_PORT=8050
PORT=8050

# CORS Configuration (update with your frontend domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Upload Configuration
MAX_FILE_SIZE=10485760
```

**Important**: 
- Replace `your_supabase_project_url` and `your_supabase_anon_key` with your actual Supabase credentials
- Update `CORS_ORIGINS` with your frontend domain(s)

Save and exit (Ctrl+X, then Y, then Enter for nano)

## Step 6: Set Up SSL Certificates

### Option A: Let's Encrypt (Recommended for Production)

1. **Install Certbot**:
   ```bash
   sudo apt-get update
   sudo apt-get install certbot
   ```

2. **Stop nginx temporarily** (if running):
   ```bash
   docker-compose stop nginx
   ```

3. **Obtain SSL certificate**:
   ```bash
   sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
   ```

4. **Copy certificates to nginx/ssl directory**:
   ```bash
   mkdir -p ~/ocr-api/nginx/ssl
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ~/ocr-api/nginx/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ~/ocr-api/nginx/ssl/key.pem
   sudo chown $USER:$USER ~/ocr-api/nginx/ssl/*.pem
   ```

5. **Update nginx configuration** (if needed):
   The default configuration should work, but verify the paths in `nginx/default.conf`

### Option B: Use Hostinger's SSL (If Available)

1. **Enable SSL in Hostinger Control Panel**:
   - Go to your domain settings
   - Enable "Free SSL" or "Let's Encrypt SSL"
   - Wait for activation

2. **If Hostinger provides certificates**, download them and place in `nginx/ssl/`:
   ```bash
   # Download certificates from Hostinger
   # Place cert.pem and key.pem in nginx/ssl/
   ```

## Step 7: Build and Start Services

```bash
cd ~/ocr-api

# Build the Docker images
docker-compose build

# Start the services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Step 8: Configure Firewall (If Applicable)

If your Hostinger server has a firewall, open ports 80 and 443:

```bash
# For UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# For firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## Step 9: Configure Domain DNS (If Needed)

1. **Point your domain to Hostinger**:
   - In your domain registrar, set A record to your Hostinger server IP
   - Or use Hostinger's nameservers

2. **Verify DNS propagation**:
   ```bash
   dig yourdomain.com
   # or
   nslookup yourdomain.com
   ```

## Step 10: Test Your Deployment

1. **Test HTTP (should redirect to HTTPS)**:
   ```bash
   curl -I http://yourdomain.com
   ```

2. **Test HTTPS**:
   ```bash
   curl -I https://yourdomain.com/docs
   ```

3. **Access in browser**:
   - Visit: `https://yourdomain.com`
   - API Docs: `https://yourdomain.com/docs`

## Step 11: Set Up Auto-Renewal for SSL (Let's Encrypt)

Create a cron job to automatically renew certificates:

```bash
# Edit crontab
crontab -e

# Add this line (runs twice daily at midnight and noon)
0 0,12 * * * certbot renew --quiet && docker-compose restart nginx
```

## Step 12: Set Up Auto-Start on Server Reboot

Create a systemd service (optional but recommended):

```bash
sudo nano /etc/systemd/system/ocr-api.service
```

Add this content:

```ini
[Unit]
Description=OCR API Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/your-username/ocr-api
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=your-username

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ocr-api.service
sudo systemctl start ocr-api.service
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs nginx
docker-compose logs ocr-api

# Restart services
docker-compose restart
```

### SSL Certificate Issues

```bash
# Verify certificates exist
ls -la ~/ocr-api/nginx/ssl/

# Check nginx configuration
docker exec ocr-nginx nginx -t

# View nginx error logs
docker-compose logs nginx | grep error
```

### Port Already in Use

```bash
# Check what's using port 80/443
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Stop conflicting services
sudo systemctl stop apache2  # if Apache is running
sudo systemctl stop nginx     # if system nginx is running
```

### Can't Access from Browser

1. **Check firewall**: Ensure ports 80 and 443 are open
2. **Check DNS**: Verify domain points to correct IP
3. **Check container status**: `docker-compose ps`
4. **Check logs**: `docker-compose logs`

### Out of Memory Issues

If your server has limited RAM:

```bash
# Check memory usage
free -h
docker stats

# Consider upgrading your Hostinger plan
# Or optimize the Docker images
```

## Maintenance

### Update Your Application

```bash
cd ~/ocr-api

# Pull latest changes (if using Git)
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup SSL Certificates

```bash
# Backup certificates
tar -czf ssl-backup-$(date +%Y%m%d).tar.gz nginx/ssl/
```

### Monitor Logs

```bash
# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

## Hostinger-Specific Notes

### Shared Hosting Limitations

If you're on **Shared Hosting**:
- Docker may not be available
- Consider upgrading to **VPS** or **Cloud Hosting**
- Alternative: Deploy without Docker (see below)

### VPS Hosting

- Full root access
- Can install Docker
- Recommended for this setup

### Cloud Hosting

- May have Docker support
- Check Hostinger documentation for Docker availability
- May have built-in container management

## Alternative: Deploy Without Docker (Shared Hosting)

If Docker is not available, you can deploy directly:

1. **Install Python 3.11** on the server
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run with Gunicorn or Uvicorn**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. **Use Hostinger's built-in SSL** for HTTPS
5. **Configure reverse proxy** in Hostinger control panel

## Support

- **Hostinger Support**: Check your Hostinger control panel for support options
- **Docker Documentation**: https://docs.docker.com/
- **Let's Encrypt**: https://letsencrypt.org/docs/

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

