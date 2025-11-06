# Dev Container Setup

This directory contains the configuration files for developing this project in a containerized environment using VS Code Dev Containers or GitHub Codespaces.

## What is a Dev Container?

A dev container is a Docker container configured as a fully-featured development environment. It ensures that:

- ✅ All developers have the same environment
- ✅ Dependencies are isolated from your system
- ✅ Easy onboarding for new contributors
- ✅ Consistent development experience across platforms

## Prerequisites

- **VS Code** with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)

## Quick Start

### 1. Open in VS Code

1. Open VS Code in this project directory
2. Press `F1` (or `Cmd+Shift+P` on Mac / `Ctrl+Shift+P` on Windows/Linux)
3. Type: `Dev Containers: Reopen in Container`
4. Select it and wait for the container to build

### 2. Configure Environment Variables

After the container starts, create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` with your actual Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_actual_anon_key
USE_GPU=False
OCR_LANG=en
```

### 3. Start the Development Server

Once inside the container, run:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

## What's Included

### Python Environment
- Python 3.11
- All dependencies from `requirements.txt` installed automatically
- Virtual environment management ready

### VS Code Extensions
The following extensions are automatically installed:
- **Python** - Full Python language support
- **Pylance** - Fast Python language server
- **Black** - Code formatter
- **Flake8** - Linter
- **isort** - Import sorter
- **Ruff** - Fast Python linter and formatter
- **GitLens** - Git supercharged
- **Docker** - Docker support
- **YAML** - YAML support

### System Dependencies
All required system libraries for PaddleOCR are pre-installed:
- OpenGL libraries (`libgl1-mesa-glx`)
- Image processing libraries
- Git and development tools

## Features

### Automatic Port Forwarding
Port 8000 is automatically forwarded from the container to your host machine.

### File Watching
The workspace folder is mounted, so changes are immediately reflected in the container.

### Git Integration
Git is fully configured and ready to use.

### Terminal Access
Use the integrated terminal in VS Code - it runs inside the container.

## Development Workflow

1. **Edit files** - Files are synced between host and container
2. **Run commands** - All commands run in the container environment
3. **Debug** - Use VS Code's debugger (configured for Python)
4. **Test** - Run tests with pytest (configured automatically)

## Troubleshooting

### Container Won't Build

**Issue**: Docker build fails
**Solution**: 
- Ensure Docker Desktop is running
- Check Docker has enough resources (CPU/Memory)
- Try: `docker system prune` to free up space

### Port Already in Use

**Issue**: Port 8000 is already in use
**Solution**:
- Change the port in `devcontainer.json`: `"forwardPorts": [8001]`
- Or stop the conflicting service: `docker ps` and `docker stop <container-id>`

### Environment Variables Not Loading

**Issue**: Application can't find Supabase credentials
**Solution**:
- Ensure `.env` file exists in the project root (not in `.devcontainer/`)
- Check file permissions: `ls -la .env`
- Restart the container after creating `.env`

### Dependencies Not Installing

**Issue**: `pip install` fails during container creation
**Solution**:
- Check `requirements.txt` syntax
- Review build logs in VS Code output panel
- Try rebuilding: `Dev Containers: Rebuild Container`

### PaddleOCR Installation Issues

**Issue**: PaddleOCR fails to import
**Solution**:
- System dependencies are already installed in the container
- If issues persist, check the container logs
- Try: `pip install --upgrade paddleocr`

## Manual Container Commands

If you need to work with the container manually:

```bash
# Build the container
docker build -f .devcontainer/Dockerfile -t ocr-doc-dev .

# Run interactively
docker run -it --rm -v $(pwd):/workspace ocr-doc-dev bash

# Check container status
docker ps
```

## Using Docker Compose (Alternative)

You can also use the included `docker-compose.yml`:

```bash
cd .devcontainer
docker-compose up -d
docker-compose exec app bash
```

## Customization

### Add More VS Code Extensions

Edit `.devcontainer/devcontainer.json` and add to the `extensions` array:

```json
"extensions": [
    "ms-python.python",
    "your-extension-id"
]
```

### Change Python Version

Edit `.devcontainer/Dockerfile`:

```dockerfile
FROM python:3.12-slim  # Change version here
```

### Add Environment Variables

Edit `.devcontainer/devcontainer.json`:

```json
"containerEnv": {
    "MY_VAR": "value"
}
```

## GitHub Codespaces

This dev container configuration also works with GitHub Codespaces:

1. Go to your repository on GitHub
2. Click "Code" → "Codespaces" → "Create codespace on main"
3. Wait for the environment to build
4. Start coding!

## Next Steps

- ✅ Create your `.env` file with Supabase credentials
- ✅ Start the dev server: `uvicorn main:app --reload`
- ✅ Visit http://localhost:8000/docs to see the API
- ✅ Start developing!

For more information, see:
- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)

