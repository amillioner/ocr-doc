# Gemini OCR Implementation

## Overview

The OCR API now uses a **two-tier approach**:
1. **Primary**: Google Gemini Vision API (fast, accurate, cloud-based)
2. **Fallback**: PaddleOCR (open-source, local processing)

## How It Works

### Flow Diagram

```
Upload Document
    ↓
Try Google Gemini OCR
    ↓
Success? → Extract text → Save to database ✅
    ↓
Failed?
    ↓
Fallback to PaddleOCR
    ↓
Extract text → Save to database ✅
```

## Implementation Details

### 1. Google Gemini (Primary)

- **Model**: `gemini-1.5-flash` (optimized for speed)
- **API Key**: Uses `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `VITE_GEMINI_API_KEY` from environment
- **Advantages**:
  - Fast processing
  - High accuracy
  - No local dependencies
  - Handles various image formats
- **Confidence**: Default 0.95 (high confidence)

### 2. PaddleOCR (Fallback)

- **When used**: If Gemini fails or is not configured
- **Advantages**:
  - Works offline
  - No API costs
  - Good for simple documents
- **Confidence**: Calculated from OCR results

## Environment Variables

Add to your `.env` file:

```env
# Google Gemini API Key (Primary OCR)
GEMINI_API_KEY=your_gemini_api_key_here
# OR use existing key:
OPENAI_API_KEY=your_gemini_api_key_here
# OR:
VITE_GEMINI_API_KEY=your_gemini_api_key_here

# PaddleOCR (Fallback - optional)
USE_GPU=False
OCR_LANG=en
```

## Database Schema Update

The `documents` table now includes an `ocr_method` field to track which OCR was used:

```sql
ALTER TABLE documents ADD COLUMN IF NOT EXISTS ocr_method TEXT;
```

This allows you to:
- Track which method was used for each document
- Analyze performance differences
- Debug issues

## API Response

The response includes which OCR method was used:

```json
{
  "success": true,
  "message": "Document processed successfully",
  "data": {
    "document_id": "...",
    "filename": "document.png",
    "extracted_text": "...",
    "confidence": 0.95,
    "text_lines": [...],
    "created_at": "2024-01-01T12:00:00"
  }
}
```

The database record includes `ocr_method: "gemini"` or `ocr_method: "paddleocr"`.

## Logging

The logs show which method was used:

```
[OCR] Attempting OCR with Google Gemini...
[OCR] Successfully extracted text using Google Gemini
```

Or if fallback occurs:

```
[OCR] Gemini OCR failed: ...
[OCR] Falling back to PaddleOCR...
[OCR] Successfully extracted text using PaddleOCR
```

## Error Handling

- **Gemini fails**: Automatically falls back to PaddleOCR
- **Both fail**: Returns error to client
- **No Gemini API key**: Uses PaddleOCR directly (no error)

## Performance

- **Gemini**: ~1-3 seconds per document (depends on image size)
- **PaddleOCR**: ~2-5 seconds per document (depends on hardware)

## Cost Considerations

- **Gemini**: Pay-per-use (check Google Cloud pricing)
- **PaddleOCR**: Free (local processing)

## Testing

### Test with Gemini

1. Ensure `GEMINI_API_KEY` is set in `.env`
2. Upload a document
3. Check logs for `[GEMINI]` messages
4. Verify `ocr_method: "gemini"` in database

### Test Fallback

1. Temporarily set invalid `GEMINI_API_KEY`
2. Upload a document
3. Check logs for fallback message
4. Verify `ocr_method: "paddleocr"` in database

## Migration Notes

- Existing code continues to work
- PaddleOCR is still available as fallback
- No breaking changes to API endpoints
- Database schema is backward compatible (ocr_method is optional)

## Next Steps

1. **Update .env** with your Gemini API key
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Test**: Upload a document and check logs
4. **Monitor**: Track which method is used most often

