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
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```bash
GET /health
```

Check if the service is running and Supabase is connected.

### Upload Document

```bash
POST /upload
Content-Type: multipart/form-data
```

Upload a document for OCR processing.

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/document.png"
```

**Example using Python:**

```python
import requests

url = "http://localhost:8000/upload"
files = {"file": open("document.png", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Get All Documents

```bash
GET /documents?limit=10&offset=0
```

Retrieve all processed documents with pagination.

### Get Document by ID

```bash
GET /documents/{document_id}
```

Retrieve a specific document by its ID.

### Delete Document

```bash
DELETE /documents/{document_id}
```

Delete a document from the database.

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

## License

This project is open source and available under the MIT License.

## References

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Supabase](https://supabase.com/)

