# Docker Commands for PowerShell (Windows)

This guide provides PowerShell-friendly commands for running the OCR Docker container on Windows.

## Prerequisites

Ensure Docker Desktop is installed and running on Windows.

## Quick Start

### Option 1: Using the PowerShell Script (Recommended)

```powershell
# Build and start services
.\docker-build.ps1 up

# View logs
.\docker-build.ps1 logs

# Stop services
.\docker-build.ps1 down

# Restart services
.\docker-build.ps1 restart
```

### Option 2: Using Docker Compose Directly

```powershell
# Start services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 3: Using Docker Run

```powershell
# Build the image
docker build -t ocr-doc-api .

# Run the container
docker run -d `
    --name ocr-doc-api `
    --restart unless-stopped `
    -p 8000:8000 `
    --env-file .env `
    ocr-doc-api
```

## Common PowerShell Issues and Solutions

### Issue 0: Docker Desktop Not Running

**Problem**: 
```
ERROR: error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**Solution**: Docker Desktop must be running before using Docker commands.

```powershell
# Check if Docker Desktop is running
.\docker-build.ps1 check

# Start Docker Desktop manually
Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'

# Or search for "Docker Desktop" in Start Menu and launch it

# Wait for Docker Desktop to fully start (check system tray icon)
# Then verify it's running
docker ps
```

**Prevention**: The `docker-build.ps1` script now automatically checks if Docker Desktop is running before executing Docker commands.

### Issue 1: Environment Variables Not Working

**Problem**: PowerShell doesn't interpret bash-style variable substitution like `${VAR:-default}`.

**Solution**: Docker Compose handles this automatically. The syntax in `docker-compose.yml` is correct for Docker Compose, not PowerShell.

If you need to set variables in PowerShell before running:

```powershell
$env:SUPABASE_URL = "your_url"
$env:SUPABASE_KEY = "your_key"
docker-compose up -d
```

Or use the `.env` file (recommended):

```powershell
# Create .env file with your variables
@"
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
PORT=8000
WORKERS=2
"@ | Out-File -FilePath .env -Encoding utf8
```

### Issue 2: Line Continuation in PowerShell

**Problem**: PowerShell uses backticks (`` ` ``) for line continuation, not backslashes.

**Solution**: When writing multi-line commands in PowerShell:

```powershell
# Correct PowerShell syntax
docker run -d `
    --name ocr-doc-api `
    -p 8000:8000 `
    --env-file .env `
    ocr-doc-api
```

### Issue 3: Port Already in Use

**Problem**: Port 8000 is already in use.

**Solution**: Change the port in your `.env` file:

```powershell
# Edit .env file
$env:PORT = "8001"
docker-compose up -d
```

Or stop the conflicting service:

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Stop the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Issue 4: Docker Build Fails

**Problem**: Build fails with permission or path issues.

**Solution**: Ensure Docker Desktop is running and you have proper permissions:

```powershell
# Check Docker is running
docker ps

# If not running, start Docker Desktop
# Then try building again
docker build -t ocr-doc-api .
```

### Issue 5: Environment Variables Not Loading from .env

**Problem**: `.env` file variables aren't being read.

**Solution**: Ensure the `.env` file is in the same directory as `docker-compose.yml`:

```powershell
# Check file exists
Test-Path .env

# Verify file encoding (should be UTF-8 without BOM)
Get-Content .env -Encoding UTF8

# Create .env if missing
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    # Edit .env with your credentials
}
```

## Useful PowerShell Commands

### Check Container Status

```powershell
docker ps -a
```

### View Container Logs

```powershell
# All logs
docker logs ocr-doc-api

# Follow logs
docker logs -f ocr-doc-api

# Last 100 lines
docker logs --tail 100 ocr-doc-api
```

### Execute Commands in Container

```powershell
# Open shell in container
docker exec -it ocr-doc-api /bin/bash

# Run Python command
docker exec ocr-doc-api python -c "print('Hello')"

# Check environment variables
docker exec ocr-doc-api env | Select-String SUPABASE
```

### Clean Up

```powershell
# Stop and remove container
docker stop ocr-doc-api
docker rm ocr-doc-api

# Remove image
docker rmi ocr-doc-api

# Remove all unused containers, networks, images
docker system prune -a
```

### Test API

```powershell
# Test health endpoint
Invoke-WebRequest -Uri http://localhost:8000/docs

# Using curl (if available)
curl http://localhost:8000/docs
```

## Troubleshooting

### Container Exits Immediately

```powershell
# Check logs for errors
docker logs ocr-doc-api

# Run container interactively to see errors
docker run -it --rm --env-file .env ocr-doc-api
```

### Cannot Connect to Supabase

```powershell
# Verify environment variables are set correctly
docker exec ocr-doc-api env | Select-String SUPABASE

# Test connection from container
docker exec ocr-doc-api python -c "from supabase import create_client; import os; client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); print('Connected!')"
```

### Memory Issues

```powershell
# Check container resource usage
docker stats ocr-doc-api

# Limit memory if needed (in docker-compose.yml)
# Add under ocr-api service:
# deploy:
#   resources:
#     limits:
#       memory: 2G
```

## Environment File Template

Create a `.env` file with this content:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
PORT=8000
WORKERS=2
OCR_LANG=en
USE_GPU=False
CORS_ORIGINS=*
MAX_FILE_SIZE=10485760
```

## Next Steps

After successful deployment:
1. Visit http://localhost:8000/docs to see API documentation
2. Test the `/ocr` endpoint with a sample document
3. Check Supabase to verify documents are being saved

For detailed deployment instructions, see [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md).
