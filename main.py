from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
from paddleocr import PaddleOCR
import tempfile
from datetime import datetime
import uuid
from supabase import create_client, Client
from pydantic import BaseModel
import logging
import numpy as np

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OCR Document Processing API",
    description="FastAPI service for OCR document processing with PaddleOCR and Supabase storage",
    version="1.0.0"
)

# Configure CORS
# Get allowed origins from environment variable or default to all
cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    # If wildcard, can't use credentials
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # If specific origins, can use credentials
    origins_list = [origin.strip() for origin in cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize PaddleOCR instance (lazy initialization)
ocr = None

def get_ocr():
    """Lazy initialization of PaddleOCR for basic OCR"""
    global ocr
    if ocr is None:
        logger.info("Initializing PaddleOCR...")
        ocr_lang = os.getenv("OCR_LANG", "en")
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            lang=ocr_lang
        )
        logger.info(f"PaddleOCR initialized successfully with language: {ocr_lang}")
    return ocr

def convert_to_json_serializable(obj):
    """Convert numpy arrays and other non-serializable types to JSON-serializable formats"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    # Handle numpy integer types (NumPy 2.0 compatible)
    elif isinstance(obj, (np.integer, np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    # Handle numpy float types (NumPy 2.0 compatible - np.float_ removed, use np.float64)
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        return float(obj)
    # Handle numpy bool (NumPy 2.0 compatible)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    # Handle numpy scalar types generically
    elif isinstance(obj, (np.number,)):
        # Generic numpy number - convert to Python type
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return float(obj)  # Fallback to float
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif hasattr(obj, '__array__'):
        # Handle array-like objects (like numpy scalars)
        try:
            arr = np.asarray(obj)
            if arr.ndim == 0:
                # Scalar array - convert to Python type
                return convert_to_json_serializable(arr.item())
            else:
                return convert_to_json_serializable(arr)
        except Exception:
            return str(obj)
    else:
        return obj

def extract_text_from_ocr_result(ocr_result: List[Dict]) -> tuple:
    """
    Extract text and confidence scores from PaddleOCR predict() result.
    Result format: list of dicts with 'dt_polys' and 'rec_texts' keys
    """
    extracted_text = ""
    all_confidences = []
    text_lines = []
    
    if not ocr_result:
        return extracted_text, all_confidences, text_lines
    
    for res in ocr_result:
        if isinstance(res, dict):
            # PaddleOCR returns dict with 'rec_texts' (list of strings) and 'dt_polys' (detection polygons)
            rec_texts = res.get('rec_texts', [])
            rec_scores = res.get('rec_scores', [])
            dt_polys = res.get('dt_polys', [])
            
            for i, text in enumerate(rec_texts):
                if text:
                    extracted_text += text + "\n"
                    
                    # Convert polygon to list if it's a numpy array
                    polygon = None
                    if i < len(dt_polys):
                        polygon_raw = dt_polys[i]
                        polygon = convert_to_json_serializable(polygon_raw)
                    
                    # Convert confidence score
                    confidence = None
                    if i < len(rec_scores):
                        confidence_raw = rec_scores[i]
                        if confidence_raw is not None:
                            confidence = float(confidence_raw)
                            all_confidences.append(confidence)
                    
                    # Create text line dict and ensure it's serializable
                    text_line = {
                        'text': str(text),
                        'confidence': confidence,
                        'polygon': polygon
                    }
                    # Double-check conversion
                    text_line = convert_to_json_serializable(text_line)
                    text_lines.append(text_line)
    
    return extracted_text, all_confidences, text_lines

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Supabase client: {str(e)}")
else:
    logger.warning("Supabase not configured. SUPABASE_URL and SUPABASE_KEY not set in environment variables")

# Pydantic models
class OCRResult(BaseModel):
    document_id: str
    filename: str
    extracted_text: str
    confidence: Optional[float] = None
    text_lines: Optional[List[Dict]] = None
    created_at: str

class DocumentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[OCRResult] = None

@app.post("/ocr", response_model=DocumentResponse)
async def ocr_document(
    file: UploadFile = File(...),
    lang: Optional[str] = Query(None, description="Language code (e.g., 'en', 'ch', 'fr')"),
    ocr_version: Optional[str] = Query(None, description="OCR version: 'PP-OCRv3', 'PP-OCRv4', or 'PP-OCRv5'"),
    use_doc_orientation_classify: bool = Query(False, description="Enable document orientation classification"),
    use_doc_unwarping: bool = Query(False, description="Enable document unwarping"),
    use_textline_orientation: bool = Query(False, description="Enable text line orientation classification")
):
    """
    Basic OCR endpoint using PaddleOCR.
    Extracts text from documents with optional language and version selection.
    """
    try:
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf', '.bmp', '.tiff'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"
            )

        document_id = str(uuid.uuid4())
        file_content = await file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            logger.info(f"Processing document: {file.filename}")
            
            # Initialize OCR with custom parameters if provided
            ocr_instance = get_ocr()
            
            # Use predict() with optional parameters
            ocr_result_raw = ocr_instance.predict(
                temp_file_path,
                use_doc_orientation_classify=use_doc_orientation_classify,
                use_doc_unwarping=use_doc_unwarping,
                use_textline_orientation=use_textline_orientation
            )
            
            # Convert entire result to JSON-serializable format first
            ocr_result = convert_to_json_serializable(ocr_result_raw)
            
            # Extract text from result
            extracted_text, all_confidences, text_lines = extract_text_from_ocr_result(ocr_result)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else None
            
            # Prepare data for Supabase
            document_data = {
                "id": document_id,
                "filename": file.filename,
                "extracted_text": extracted_text.strip(),
                "confidence": avg_confidence,
                "file_type": file_extension,
                "file_size": len(file_content),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Save to Supabase if configured
            if supabase:
                try:
                    logger.info(f"Saving document {document_id} to Supabase")
                    result = supabase.table("documents").insert(document_data).execute()
                    if result.data:
                        logger.info(f"Successfully saved document {document_id} to database")
                    else:
                        logger.error(f"Failed to save document to database - no data returned")
                        raise HTTPException(status_code=500, detail="Failed to save document to database")
                except Exception as db_error:
                    logger.error(f"Database error: {str(db_error)}")
                    raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
            else:
                logger.warning("Supabase not configured - document not saved to database")
            
            logger.info(f"Successfully processed document: {document_id}")
            
            # Ensure text_lines is fully JSON-serializable
            serializable_text_lines = None
            if text_lines:
                serializable_text_lines = [convert_to_json_serializable(line) for line in text_lines]
            
            return DocumentResponse(
                success=True,
                message="Document processed successfully",
                data=OCRResult(
                    document_id=document_id,
                    filename=file.filename,
                    extracted_text=extracted_text.strip(),
                    confidence=float(avg_confidence) if avg_confidence is not None else None,
                    text_lines=serializable_text_lines,
                    created_at=document_data["created_at"]
                )
            )
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Set to False for production
    )
