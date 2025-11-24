from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Tuple
import os
from dotenv import load_dotenv
from paddleocr import PaddleOCR
import tempfile
from datetime import datetime, timezone
import uuid
from supabase import create_client, Client
from pydantic import BaseModel
import logging
import numpy as np
import base64
import google.generativeai as genai
from PIL import Image

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OCR Document Processing API",
    description="FastAPI service for OCR document processing with Google Gemini (primary) and PaddleOCR (fallback) and Supabase storage",
    version="2.0.0"
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

# Initialize Google Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("VITE_GEMINI_API_KEY")
gemini_model = None

if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Google Gemini initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini: {str(e)}")
        gemini_model = None
else:
    logger.warning("GEMINI_API_KEY not found. Gemini OCR will not be available.")

# Initialize PaddleOCR instance (lazy initialization) - Fallback
ocr = None

def get_ocr():
    """Lazy initialization of PaddleOCR for fallback OCR"""
    global ocr
    if ocr is None:
        logger.info("Initializing PaddleOCR (fallback)...")
        ocr_lang = os.getenv("OCR_LANG", "en")
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            lang=ocr_lang
        )
        logger.info(f"PaddleOCR initialized successfully with language: {ocr_lang}")
    return ocr

def extract_text_with_gemini(image_path: str) -> Tuple[str, float, List[Dict]]:
    """
    Extract text from image using Google Gemini Vision API.
    Returns: (extracted_text, confidence, text_lines)
    """
    try:
        if not gemini_model:
            raise Exception("Gemini model not initialized")
        
        logger.info("[GEMINI] Starting OCR with Google Gemini...")
        
        # Load image
        image = Image.open(image_path)
        
        # Use Gemini to extract text
        prompt = """Extract all text from this image. Return the text exactly as it appears, preserving line breaks and formatting. 
        If there are multiple sections, separate them with line breaks. 
        Be accurate and include all visible text."""
        
        response = gemini_model.generate_content([prompt, image])
        
        extracted_text = response.text.strip() if response.text else ""
        
        # Gemini doesn't provide confidence scores, so we'll use a default high confidence
        confidence = 0.95  # High confidence for Gemini results
        
        # Create text lines from extracted text
        text_lines = []
        if extracted_text:
            lines = extracted_text.split('\n')
            for i, line in enumerate(lines):
                if line.strip():  # Only add non-empty lines
                    text_lines.append({
                        'text': line.strip(),
                        'confidence': confidence,
                        'line_number': i + 1
                    })
        
        logger.info(f"[GEMINI] Successfully extracted {len(extracted_text)} characters, {len(text_lines)} lines")
        
        return extracted_text, confidence, text_lines
        
    except Exception as e:
        logger.error(f"[GEMINI] Error extracting text with Gemini: {str(e)}")
        raise Exception(f"Gemini OCR failed: {str(e)}")

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
        logger.info(f"Supabase client initialized (table: 'documents')")
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

class UploadResponse(BaseModel):
    success: bool
    message: str
    total_files: int
    successful: int
    failed: int
    documents: List[OCRResult]
    errors: Optional[List[Dict[str, str]]] = None

class SimpleDocumentResult(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size: int
    created_at: str

class SimpleDocumentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[SimpleDocumentResult] = None

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
        file_size = len(file_content)
        
        logger.info(f"[OCR] Processing document: {file.filename} (ID: {document_id}, {file_size / 1024:.2f} KB, {file_extension})")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
            logger.debug(f"[OCR] Temporary file: {temp_file_path}")
        
        try:
            # Try Gemini first, fallback to PaddleOCR
            extracted_text = ""
            all_confidences = []
            text_lines = []
            ocr_method = None
            
            # Attempt Gemini OCR first
            if gemini_model:
                try:
                    logger.info("[OCR] Attempting OCR with Google Gemini...")
                    extracted_text, confidence, text_lines = extract_text_with_gemini(temp_file_path)
                    all_confidences = [confidence] * len(text_lines) if text_lines else [confidence]
                    avg_confidence = confidence
                    ocr_method = "gemini"
                    logger.info("[OCR] Successfully extracted text using Google Gemini")
                except Exception as gemini_error:
                    logger.warning(f"[OCR] Gemini OCR failed: {str(gemini_error)}")
                    logger.info("[OCR] Falling back to PaddleOCR...")
                    # Fall through to PaddleOCR
            
            # Fallback to PaddleOCR if Gemini failed or not available
            if not extracted_text or ocr_method != "gemini":
                logger.info("[OCR] Using PaddleOCR (fallback)...")
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
                ocr_method = "paddleocr"
                logger.info("[OCR] Successfully extracted text using PaddleOCR")
            
            # If both methods failed
            if not extracted_text:
                raise Exception("Both Gemini and PaddleOCR failed to extract text")
            
            # Prepare data for Supabase
            document_data = {
                "id": document_id,
                "filename": file.filename,
                "extracted_text": extracted_text.strip(),
                "confidence": avg_confidence,
                "file_type": file_extension,
                "file_size": file_size,
                "ocr_method": ocr_method,  # Track which OCR method was used
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            confidence_str = f"{avg_confidence:.4f}" if avg_confidence else "N/A"
            logger.info(f"[OCR] Extracted {len(extracted_text.strip())} chars, {len(text_lines) if text_lines else 0} lines, confidence: {confidence_str}, method: {ocr_method}")
            
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
            
            logger.info(f"[OCR] Successfully processed document: {document_id}")
            
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
                logger.debug(f"[CLEANUP] Deleted temporary file")
            else:
                logger.debug(f"[CLEANUP] Temporary file not found")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/upload", response_model=UploadResponse)
async def upload_documents(
    files: List[UploadFile] = File(...),
    use_doc_orientation_classify: bool = Query(False, description="Enable document orientation classification"),
    use_doc_unwarping: bool = Query(False, description="Enable document unwarping"),
    use_textline_orientation: bool = Query(False, description="Enable text line orientation classification")
):
    """
    Upload one or multiple documents for OCR processing and database storage.
    Supports batch upload of multiple files at once.
    """
    table_name = "documents"
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf', '.bmp', '.tiff'}
    
    logger.info(f"[UPLOAD] Starting batch upload: {len(files)} file(s)")
    if not supabase:
        logger.warning(f"[UPLOAD] Supabase not configured - files will NOT be saved to database")
    
    successful_docs = []
    errors = []
    temp_files = []  # Track temp files for cleanup
    
    for idx, file in enumerate(files, 1):
        document_id = str(uuid.uuid4())
        temp_file_path = None
        
        try:
            # Validate file extension
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                error_msg = f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"
                logger.warning(f"[UPLOAD] File {idx}/{len(files)} rejected: {file.filename} - {error_msg}")
                errors.append({
                    "filename": file.filename,
                    "error": error_msg
                })
                continue
            
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            logger.info(f"[UPLOAD] Processing file {idx}/{len(files)}: {file.filename} ({file_size / 1024:.2f} KB, {file_extension})")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
                temp_files.append(temp_file_path)
                logger.debug(f"[UPLOAD] File {idx} - Temp file: {temp_file_path}")
            # Try Gemini first, fallback to PaddleOCR
            extracted_text = ""
            all_confidences = []
            text_lines = []
            ocr_method = None
            
            # Attempt Gemini OCR first
            if gemini_model:
                try:
                    logger.info(f"[UPLOAD] File {idx} - Attempting OCR with Google Gemini...")
                    extracted_text, confidence, text_lines = extract_text_with_gemini(temp_file_path)
                    all_confidences = [confidence] * len(text_lines) if text_lines else [confidence]
                    avg_confidence = confidence
                    ocr_method = "gemini"
                    logger.info(f"[UPLOAD] File {idx} - Successfully extracted text using Google Gemini")
                except Exception as gemini_error:
                    logger.warning(f"[UPLOAD] File {idx} - Gemini OCR failed: {str(gemini_error)}")
                    logger.info(f"[UPLOAD] File {idx} - Falling back to PaddleOCR...")
            
            # Fallback to PaddleOCR if Gemini failed or not available
            if not extracted_text or ocr_method != "gemini":
                logger.info(f"[UPLOAD] File {idx} - Using PaddleOCR (fallback)...")
                ocr_instance = get_ocr()
                
                ocr_result_raw = ocr_instance.predict(
                    temp_file_path,
                    use_doc_orientation_classify=use_doc_orientation_classify,
                    use_doc_unwarping=use_doc_unwarping,
                    use_textline_orientation=use_textline_orientation
                )
                
                # Convert and extract text
                ocr_result = convert_to_json_serializable(ocr_result_raw)
                extracted_text, all_confidences, text_lines = extract_text_from_ocr_result(ocr_result)
                avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else None
                ocr_method = "paddleocr"
                logger.info(f"[UPLOAD] File {idx} - Successfully extracted text using PaddleOCR")
            
            # If both methods failed
            if not extracted_text:
                raise Exception("Both Gemini and PaddleOCR failed to extract text")
            
            confidence_str = f"{avg_confidence:.4f}" if avg_confidence else "N/A"
            logger.debug(f"[UPLOAD] File {idx} - Extracted {len(extracted_text.strip())} chars, confidence: {confidence_str}")
            
            # Prepare data for database
            document_data = {
                "id": document_id,
                "filename": file.filename,
                "extracted_text": extracted_text.strip(),
                "confidence": avg_confidence,
                "file_type": file_extension,
                "file_size": file_size,
                "ocr_method": ocr_method,  # Track which OCR method was used
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Save to database
            if supabase:
                try:
                    result = supabase.table(table_name).insert(document_data).execute()
                    if result.data:
                        logger.debug(f"[UPLOAD] File {idx} - Saved to database")
                    else:
                        raise Exception("No data returned from insert")
                except Exception as db_error:
                    error_msg = f"Database error: {str(db_error)}"
                    logger.error(f"[UPLOAD] File {idx} - Database error: {error_msg}")
                    errors.append({
                        "filename": file.filename,
                        "error": error_msg
                    })
                    continue
            
            # Create response object
            serializable_text_lines = None
            if text_lines:
                serializable_text_lines = [convert_to_json_serializable(line) for line in text_lines]
            
            successful_docs.append(OCRResult(
                document_id=document_id,
                filename=file.filename,
                extracted_text=extracted_text.strip(),
                confidence=float(avg_confidence) if avg_confidence is not None else None,
                text_lines=serializable_text_lines,
                created_at=document_data["created_at"]
            ))
            
            logger.debug(f"[UPLOAD] File {idx} - Successfully processed")
            
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            logger.error(f"[UPLOAD] File {idx} - Error: {error_msg}")
            errors.append({
                "filename": file.filename,
                "error": error_msg
            })
        finally:
            # Cleanup temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.debug(f"[UPLOAD] File {idx} - Cleaned up temp file")
                except Exception as cleanup_error:
                    logger.warning(f"[UPLOAD] File {idx} - Failed to cleanup: {cleanup_error}")
    
    # Final summary
    total_files = len(files)
    successful = len(successful_docs)
    failed = len(errors)
    
    logger.info(f"[UPLOAD] Batch complete: {successful}/{total_files} successful, {failed} failed")
    
    return UploadResponse(
        success=successful > 0,
        message=f"Processed {successful} of {total_files} file(s) successfully",
        total_files=total_files,
        successful=successful,
        failed=failed,
        documents=successful_docs,
        errors=errors if errors else None
    )

@app.post("/upload-doc", response_model=SimpleDocumentResponse)
async def upload_document_simple(
    file: UploadFile = File(...)
):
    """
    Upload a document without OCR processing.
    Saves document metadata directly to Supabase database.
    No OCR processing is performed - just file storage.
    """
    table_name = "documents"
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf', '.bmp', '.tiff', '.doc', '.docx', '.txt', '.csv', '.xlsx', '.xls'}
    
    try:
        logger.info(f"[UPLOAD-DOC] Starting simple document upload")
        logger.info(f"[UPLOAD-DOC] Filename: {file.filename}")
        
        # Validate file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Read file content as binary
        file_content = await file.read()
        file_size = len(file_content)
        
        document_id = str(uuid.uuid4())
        
        logger.info(f"[UPLOAD-DOC] Document ID: {document_id}")
        logger.info(f"[UPLOAD-DOC] File size: {file_size} bytes ({file_size / 1024:.2f} KB)")
        logger.info(f"[UPLOAD-DOC] File extension: {file_extension}")
        
        # Convert binary to base64 for storage
        # PostgreSQL BYTEA can store binary, but base64 is safer for JSON/API transport
        file_binary_base64 = base64.b64encode(file_content).decode('utf-8')
        
        logger.info(f"[UPLOAD-DOC] File binary encoded to base64: {len(file_binary_base64)} characters")
        
        # Prepare data for database (no OCR, no extracted text, includes binary file)
        document_data = {
            "id": document_id,
            "filename": file.filename,
            "extracted_text": None,  # No OCR processing
            "confidence": None,  # No OCR processing
            "file_type": file_extension,
            "file_size": file_size,
            "file_data": file_binary_base64,  # Binary file data as base64
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to Supabase database
        if supabase:
            logger.info(f"[UPLOAD-DOC] Saving to database table '{table_name}'")
            logger.info(f"[UPLOAD-DOC] Supabase URL: {supabase_url}")
            
            try:
                result = supabase.table(table_name).insert(document_data).execute()
                if result.data:
                    logger.info(f"[UPLOAD-DOC] Successfully saved document to table '{table_name}'")
                    logger.info(f"[UPLOAD-DOC] Inserted document ID: {result.data[0].get('id', document_id)}")
                    logger.info(f"[UPLOAD-DOC] Document saved with timestamp: {result.data[0].get('created_at', 'N/A')}")
                else:
                    logger.error(f"[UPLOAD-DOC] ✗ Failed to save document - no data returned from insert")
                    raise HTTPException(status_code=500, detail="Failed to save document to database")
            except Exception as db_error:
                logger.error(f"[UPLOAD-DOC] ✗ Database error: {str(db_error)}")
                logger.error(f"[UPLOAD-DOC] Failed to insert into table '{table_name}'")
                raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        else:
            logger.warning(f"[UPLOAD-DOC] Supabase not configured - document NOT saved to database")
            logger.warning(f"[UPLOAD-DOC] Document would be saved to table: '{table_name}'")
            raise HTTPException(status_code=503, detail="Database not configured")
        
        logger.info(f"[UPLOAD-DOC] Successfully uploaded document: {document_id}")
        
        return SimpleDocumentResponse(
            success=True,
            message="Document uploaded and saved to database successfully",
            data=SimpleDocumentResult(
                document_id=document_id,
                filename=file.filename,
                file_type=file_extension,
                file_size=file_size,
                created_at=document_data["created_at"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[UPLOAD-DOC] Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8050))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Set to False for production
    )
