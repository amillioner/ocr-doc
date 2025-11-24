"""
Configuration settings for the OCR Document Processing API
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("VITE_GEMINI_API_KEY")

# PaddleOCR Configuration (Fallback)
USE_GPU = os.getenv("USE_GPU", "False").lower() == "true"
OCR_LANG = os.getenv("OCR_LANG", "en")  # Default to English, can be 'ch', 'en', 'fr', etc.

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8050"))

# File Upload Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf', '.bmp', '.tiff'}

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in environment variables or .env file"
    )

