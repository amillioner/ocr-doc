# Dev Container Dockerfile for OCR Document Processing API
FROM python:3.11-slim

# Install system dependencies required for PaddleOCR and image processing
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    wget \
    git \
    curl \
    vim \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Create a non-root user for development
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode

# Set working directory
WORKDIR /workspace

# Create directories for temporary files and output
RUN mkdir -p /tmp/ocr /workspace/output && \
    chown -R vscode:vscode /workspace /tmp/ocr

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Switch to non-root user
USER vscode

# Set default command
CMD ["/bin/bash"]

