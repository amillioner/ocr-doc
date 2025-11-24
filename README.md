# OCR Document Processing API

A FastAPI-based service for processing documents using PaddleOCR and storing results in Supabase.

## Features

- 📄 Document OCR processing using PaddleOCR
- 💾 Automatic storage to Supabase database
- 🔍 Document retrieval and management
- 📊 Confidence scoring for extracted text
- 🚀 Fast and efficient processing

## Prerequisites

- Python 3.8 or higher
- Supabase account and project
- (Optional) CUDA-enabled GPU for faster processing

## Installation

1. **Clone the repository** (or ensure you're in the project directory)

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
USE_GPU=False
OCR_LANG=en
```

4. **Set up Supabase database**

Create a table in your Supabase project with the following SQL:

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    extracted_text TEXT,
    confidence FLOAT,
    file_type TEXT,
    file_size INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index for faster queries
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
```

## Running the Application

### Development Mode

```bash
# Using virtual environment (recommended)
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or using system Python
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Endpoints

### OCR Document Processing

```bash
POST /ocr
Content-Type: multipart/form-data
```

Upload a document for OCR processing with optional parameters.

**Query Parameters:**
- `lang` (optional): Language code (e.g., 'en', 'ch', 'fr')
- `ocr_version` (optional): OCR version ('PP-OCRv3', 'PP-OCRv4', 'PP-OCRv5')
- `use_doc_orientation_classify` (default: false): Enable document orientation classification
- `use_doc_unwarping` (default: false): Enable document unwarping
- `use_textline_orientation` (default: false): Enable text line orientation classification

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/ocr?use_doc_orientation_classify=false&use_doc_unwarping=false&use_textline_orientation=false" \
  -F "file=@/path/to/your/document.png"
```

**Example using Python:**

```python
import requests

url = "http://localhost:8000/ocr"
files = {"file": open("document.png", "rb")}
params = {
    "use_doc_orientation_classify": False,
    "use_doc_unwarping": False,
    "use_textline_orientation": False
}
response = requests.post(url, files=files, params=params)
print(response.json())
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Supported File Formats

- PNG (.png)
- JPEG/JPG (.jpg, .jpeg)
- PDF (.pdf)
- BMP (.bmp)
- TIFF (.tiff)

## Configuration

### PaddleOCR Languages

Set the `OCR_LANG` environment variable to change the OCR language:

- `en` - English (default)
- `ch` - Chinese
- `fr` - French
- `german` - German
- `japan` - Japanese
- `korean` - Korean
- And more... (see PaddleOCR documentation)

### GPU Support

To use GPU acceleration, set `USE_GPU=True` in your `.env` file. Make sure you have CUDA installed and PaddlePaddle GPU version.

## Project Structure

```
ocr-doc/
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your environment variables (not in git)
└── README.md           # This file
```

## Example Response

```json
{
  "success": true,
  "message": "Document processed and saved successfully",
  "data": {
    "document_id": "123e4567-e89b-12d3-a456-426614174000",
    "filename": "document.png",
    "extracted_text": "This is the extracted text from the document...",
    "confidence": 0.95,
    "created_at": "2024-01-01T12:00:00"
  }
}
```

## Troubleshooting

### Supabase Connection Error

- Verify your `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check that your Supabase project is active
- Ensure the `documents` table exists in your database

### PaddleOCR Installation Issues

- Make sure you have Python 3.8-3.12
- For GPU support, install PaddlePaddle GPU version first
- See [PaddleOCR Installation Guide](https://github.com/PaddlePaddle/PaddleOCR/blob/main/README.md)

### Memory Issues

- Reduce image size before upload
- Use CPU mode if GPU memory is limited
- Consider processing documents in batches

## Docker Deployment

### Quick Start with HTTPS/SSL

1. **Create `.env` file** with your configuration:
   ```bash
   # Copy from example (if you have .env.example)
   # Or create manually with required variables:
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   USE_GPU=False
   OCR_LANG=en
   PORT=8000
   WORKERS=2
   CORS_ORIGINS=*
   MAX_FILE_SIZE=10485760
   ```

2. **Generate SSL certificates** (for development):
   
   **Windows (PowerShell):**
   ```powershell
   .\nginx\generate-ssl-cert.ps1
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x nginx/generate-ssl-cert.sh
   ./nginx/generate-ssl-cert.sh
   ```
   
   **For production**, see [nginx/README-SSL.md](nginx/README-SSL.md) for Let's Encrypt setup.

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d --build
   ```

4. **Access the API**:
   - **HTTPS**: https://localhost (or https://yourdomain.com)
   - **HTTP**: http://localhost (redirects to HTTPS)
   - **API Docs**: https://localhost/docs
   
   **Note**: With self-signed certificates, browsers will show a security warning. Click "Advanced" → "Proceed" for development.

### Building the Docker Image

```bash
docker build -t ocr-doc-api .
```

### Running with Docker

#### Using Docker Compose (Recommended)

```bash
# Ensure .env file exists with your configuration
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f ocr-api

# Stop the service
docker-compose down
```

#### Using Docker directly

```bash
docker run -d \
  --name ocr-doc-api \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  ocr-doc-api
```

Or with environment variables:

```bash
docker run -d \
  --name ocr-api \
  -p 8000:8000 \
  -e SUPABASE_URL=your_supabase_project_url \
  -e SUPABASE_KEY=your_supabase_anon_key \
  -e OCR_LANG=en \
  -e USE_GPU=False \
  ocr-doc-api
```

**View logs**:
```bash
docker logs -f ocr-doc-api
```

**Stop the container**:
```bash
docker stop ocr-doc-api
docker rm ocr-doc-api
```

### PowerShell (Windows)

For Windows users, use the provided PowerShell script:

```powershell
# Build and start services
.\docker-build.ps1 up

# View logs
.\docker-build.ps1 logs

# Stop services
.\docker-build.ps1 down
```

Or use Docker Compose directly (works in PowerShell):
```powershell
docker-compose up -d --build
```

See [README_DOCKER_POWERSHELL.md](README_DOCKER_POWERSHELL.md) for detailed PowerShell instructions and troubleshooting.

### SSL/HTTPS Configuration

The application now includes NGINX as a reverse proxy with SSL/HTTPS support.

**Features:**
- ✅ Automatic HTTP to HTTPS redirect
- ✅ SSL/TLS encryption
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ Support for self-signed certificates (development)
- ✅ Support for Let's Encrypt certificates (production)

**Quick Setup:**
1. Generate SSL certificates (see step 2 in Quick Start above)
2. NGINX will automatically proxy requests to the FastAPI app
3. Access via HTTPS on port 443

**For Production:**
- Use Let's Encrypt for trusted certificates
- See [nginx/README-SSL.md](nginx/README-SSL.md) for detailed instructions

### Deploying to Hostinger

**📖 Complete Guide**: See [HOSTINGER-DEPLOYMENT.md](HOSTINGER-DEPLOYMENT.md) for detailed step-by-step instructions.

**Quick Steps**:
1. **Connect to your Hostinger VPS/Cloud server via SSH**
2. **Install Docker and Docker Compose** (if not already installed)
3. **Clone your repository** or upload files to the server
4. **Create `.env` file** with your environment variables
5. **Set up SSL certificates** (Let's Encrypt recommended for production)
6. **Build and start services**: `docker-compose up -d --build`
7. **Configure firewall** to allow ports 80 and 443
8. **Point your domain** to the server IP address

**Requirements**:
- Hostinger VPS or Cloud Hosting (Docker support required)
- Domain name pointing to your server
- SSH access to your server

**For detailed instructions**, including SSL setup, troubleshooting, and maintenance, see [HOSTINGER-DEPLOYMENT.md](HOSTINGER-DEPLOYMENT.md).

### Docker Image Details

- **Base Image**: Python 3.11-slim
- **Working Directory**: `/app`
- **User**: Non-root user (`appuser`) for security
- **Port**: 8000 (configurable via `PORT` env var)
- **Workers**: 2 (configurable via `WORKERS` env var)
- **Health Check**: Built-in endpoint check every 30 seconds
- **Environment**: Uses `.env` file via `--env-file` or docker-compose

## License

This project is open source and available under the MIT License.

## References

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Supabase](https://supabase.com/)

