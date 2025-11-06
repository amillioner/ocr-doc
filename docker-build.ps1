# PowerShell script for building and running the OCR Docker container
# Usage: .\docker-build.ps1 [build|run|up|down|logs|check]

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "run", "up", "down", "logs", "stop", "restart", "check")]
    [string]$Action = "up"
)

# Function to check if Docker Desktop is running
function Test-DockerDesktop {
    try {
        docker ps 2>&1 | Out-Null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

# Check Docker Desktop before any Docker operations
if ($Action -ne "check") {
    Write-Host "Checking Docker Desktop status..." -ForegroundColor Cyan
    if (-not (Test-DockerDesktop)) {
        Write-Host ""
        Write-Host "ERROR: Docker Desktop is not running!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please start Docker Desktop and wait for it to fully initialize." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Options:" -ForegroundColor Cyan
        Write-Host "  1. Open Docker Desktop from Start Menu" -ForegroundColor White
        Write-Host "  2. Or run: Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'" -ForegroundColor White
        Write-Host ""
        Write-Host "After Docker Desktop starts, wait for the whale icon in the system tray to be steady," -ForegroundColor Yellow
        Write-Host "then run this script again." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "You can check status with: .\docker-build.ps1 check" -ForegroundColor Cyan
        exit 1
    }
    Write-Host "Docker Desktop is running ✓" -ForegroundColor Green
    Write-Host ""
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env file from .env.example. Please edit it with your credentials." -ForegroundColor Yellow
    } else {
        Write-Host "Error: .env.example not found. Please create .env file manually." -ForegroundColor Red
        exit 1
    }
}

switch ($Action) {
    "check" {
        Write-Host "Checking Docker Desktop status..." -ForegroundColor Cyan
        if (Test-DockerDesktop) {
            Write-Host "✓ Docker Desktop is running" -ForegroundColor Green
            Write-Host ""
            Write-Host "Docker version:" -ForegroundColor Cyan
            docker --version
            Write-Host ""
            Write-Host "Docker Compose version:" -ForegroundColor Cyan
            docker-compose --version
            Write-Host ""
            Write-Host "Running containers:" -ForegroundColor Cyan
            docker ps
        } else {
            Write-Host "✗ Docker Desktop is not running" -ForegroundColor Red
            Write-Host ""
            Write-Host "Please start Docker Desktop and wait for it to fully initialize." -ForegroundColor Yellow
        }
    }
    "build" {
        Write-Host "Building Docker image..." -ForegroundColor Green
        docker build -t ocr-doc-api:latest .
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Build successful!" -ForegroundColor Green
        } else {
            Write-Host "Build failed!" -ForegroundColor Red
            exit 1
        }
    }
    "run" {
        Write-Host "Running Docker container..." -ForegroundColor Green
        docker run -d --name ocr-doc-api --restart unless-stopped -p 8000:8000 --env-file .env ocr-doc-api:latest
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Container started successfully!" -ForegroundColor Green
            Write-Host "API available at: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "Docs available at: http://localhost:8000/docs" -ForegroundColor Cyan
        }
    }
    "up" {
        Write-Host "Starting services with Docker Compose..." -ForegroundColor Green
        docker-compose up -d --build
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Services started successfully!" -ForegroundColor Green
            Write-Host "API available at: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "Docs available at: http://localhost:8000/docs" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "To view logs: .\docker-build.ps1 logs" -ForegroundColor Yellow
        } else {
            Write-Host "Failed to start services!" -ForegroundColor Red
            exit 1
        }
    }
    "down" {
        Write-Host "Stopping services..." -ForegroundColor Yellow
        docker-compose down
    }
    "stop" {
        Write-Host "Stopping container..." -ForegroundColor Yellow
        docker stop ocr-doc-api
        if ($LASTEXITCODE -ne 0) {
            docker-compose stop
        }
    }
    "restart" {
        Write-Host "Restarting services..." -ForegroundColor Yellow
        docker-compose restart
        if ($LASTEXITCODE -ne 0) {
            docker restart ocr-doc-api
        }
    }
    "logs" {
        Write-Host "Showing logs (Ctrl+C to exit)..." -ForegroundColor Green
        docker-compose logs -f
        if ($LASTEXITCODE -ne 0) {
            docker logs -f ocr-doc-api
        }
    }
}
