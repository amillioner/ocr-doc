# Docker Deployment Guide for Hostinger

This guide provides step-by-step instructions for deploying the OCR Document Processing API to Hostinger using Docker.

## Problem: GitHub Authentication Error

If you're seeing this error:
```
fatal: could not read Username for 'https://github.com': terminal prompts disabled
Failed to clone repository
```

This means Hostinger is trying to automatically clone your repository but doesn't have authentication configured. Use one of the solutions below.

## Solution 1: Push to Docker Hub (Recommended)

This is the easiest and most reliable method for Hostinger deployment.

### Step 1: Build the Docker Image Locally

```bash
# Build the image
docker build -t ocr-doc-api:latest .

# Tag it for Docker Hub (replace 'yourusername' with your Docker Hub username)
docker tag ocr-doc-api:latest yourusername/ocr-doc-api:latest
```

### Step 2: Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Push the image
docker push yourusername/ocr-doc-api:latest
```

### Step 3: Configure Hostinger

1. Log in to your Hostinger control panel
2. Navigate to **Docker** or **Container** section
3. Click **Create Container** or **New Container**
4. Instead of building from source, select **Pull from Registry**
5. Enter your image: `yourusername/ocr-doc-api:latest`
6. Configure the container settings:
   - **Port Mapping**: Map Hostinger port (e.g., 8000) → Container port 8000
   - **Environment Variables**: Add all required variables:
     ```
     SUPABASE_URL=your_supabase_project_url
     SUPABASE_KEY=your_supabase_anon_key
     USE_GPU=False
     OCR_LANG=en
     PORT=8000
     CORS_ORIGINS=*
     MAX_FILE_SIZE=10485760
     ```
   - **Restart Policy**: `unless-stopped`
7. Start the container

## Solution 2: Configure GitHub Authentication in Hostinger

If you prefer to build from source on Hostinger:

### Option A: Use SSH Keys

1. Generate an SSH key pair (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Add the public key to your GitHub account:
   - Go to GitHub → Settings → SSH and GPG keys
   - Click "New SSH key"
   - Paste your public key (`~/.ssh/id_ed25519.pub`)

3. In Hostinger control panel:
   - Navigate to Docker/Container settings
   - Find "SSH Keys" or "Repository Access" section
   - Add your private SSH key
   - Update the repository URL to use SSH: `git@github.com:amillioner/ocr-doc.git`

### Option B: Use GitHub Personal Access Token

1. Create a GitHub Personal Access Token:
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token"
   - Select scopes: `repo` (Full control of private repositories)
   - Copy the token

2. In Hostinger:
   - Use HTTPS URL: `https://github.com/amillioner/ocr-doc.git`
   - When prompted for credentials:
     - Username: your GitHub username
     - Password: your Personal Access Token (not your GitHub password)

### Option C: Make Repository Public

If your repository doesn't contain sensitive information:

1. Make the repository public:
   - Go to GitHub repository settings
   - Scroll to "Danger Zone"
   - Click "Change visibility" → "Make public"

2. Hostinger should now be able to clone without authentication

## Solution 3: Upload Docker Image File

If the above methods don't work:

### Step 1: Save Docker Image as Tar File

```bash
# Build the image
docker build -t ocr-doc-api:latest .

# Save to tar file
docker save ocr-doc-api:latest -o ocr-doc-api.tar

# Compress it (optional but recommended)
gzip ocr-doc-api.tar
```

### Step 2: Upload to Hostinger

1. Upload `ocr-doc-api.tar.gz` to Hostinger via:
   - File Manager
   - FTP/SFTP
   - Hostinger's file upload interface

2. Load the image in Hostinger:
   ```bash
   # SSH into Hostinger or use their Docker interface
   docker load -i ocr-doc-api.tar.gz
   ```

3. Run the container with the same configuration as Solution 1, Step 3

## Verification

After deployment, verify the container is running:

```bash
# Check container status
docker ps

# Check logs
docker logs ocr-doc-api

# Test the API
curl http://your-hostinger-domain:8000/docs
```

## Environment Variables Checklist

Ensure these environment variables are set in Hostinger:

- ✅ `SUPABASE_URL` - Your Supabase project URL
- ✅ `SUPABASE_KEY` - Your Supabase anon/service key
- ✅ `USE_GPU` - Set to `False` for Hostinger (no GPU support)
- ✅ `OCR_LANG` - Language code (e.g., `en`, `ch`, `fr`)
- ✅ `PORT` - Container port (usually `8000`)
- ✅ `CORS_ORIGINS` - Allowed CORS origins (use `*` for development)
- ✅ `MAX_FILE_SIZE` - Maximum file size in bytes (default: `10485760` = 10MB)

## Troubleshooting

### Container Exits Immediately

Check the logs:
```bash
docker logs ocr-doc-api
```

Common issues:
- Missing environment variables (especially `SUPABASE_URL` and `SUPABASE_KEY`)
- Port conflicts
- Insufficient memory

### Cannot Connect to Supabase

Verify environment variables:
```bash
docker exec ocr-doc-api env | grep SUPABASE
```

Test connection:
```bash
docker exec ocr-doc-api python -c "from supabase import create_client; import os; client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); print('Connected!')"
```

### Memory Issues

Hostinger containers may have memory limits. If you see memory errors:

1. Reduce concurrent requests
2. Process smaller files
3. Consider upgrading your Hostinger plan

### Port Not Accessible

1. Ensure port mapping is correct in Hostinger settings
2. Check firewall rules
3. Verify the container is actually running: `docker ps`

## Automated Deployment Script

You can create a script to automate the Docker Hub push:

```bash
#!/bin/bash
# deploy.sh

VERSION=${1:-latest}
DOCKER_USERNAME="yourusername"

echo "Building Docker image..."
docker build -t ocr-doc-api:$VERSION .

echo "Tagging image..."
docker tag ocr-doc-api:$VERSION $DOCKER_USERNAME/ocr-doc-api:$VERSION
docker tag ocr-doc-api:$VERSION $DOCKER_USERNAME/ocr-doc-api:latest

echo "Pushing to Docker Hub..."
docker push $DOCKER_USERNAME/ocr-doc-api:$VERSION
docker push $DOCKER_USERNAME/ocr-doc-api:latest

echo "Deployment complete!"
echo "Image: $DOCKER_USERNAME/ocr-doc-api:$VERSION"
```

Usage:
```bash
chmod +x deploy.sh
./deploy.sh v1.0.0
```

## Continuous Deployment

For automated deployments, consider:

1. **GitHub Actions**: Build and push on every push to main
2. **Docker Hub Automated Builds**: Connect GitHub repo to Docker Hub
3. **CI/CD Pipeline**: Use GitHub Actions to build, test, and deploy

Example GitHub Actions workflow (`.github/workflows/docker.yml`):

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            yourusername/ocr-doc-api:latest
            yourusername/ocr-doc-api:${{ github.sha }}
```

## Next Steps

After successful deployment:

1. ✅ Test the API at `http://your-domain:8000/docs`
2. ✅ Verify documents are being saved to Supabase
3. ✅ Monitor logs for any errors
4. ✅ Set up monitoring and alerts (optional)

## Support

If you encounter issues:

1. Check Hostinger Docker documentation
2. Review container logs: `docker logs ocr-doc-api`
3. Verify all environment variables are set correctly
4. Ensure Supabase credentials are valid

