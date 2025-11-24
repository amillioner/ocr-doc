#!/bin/bash
# Script to create .env file on server
# Run this on your Hostinger server

cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://owpylhrddksbsrnatokc.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im93cHlsaHJkZGtzYnNybmF0b2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyMTg0NDQsImV4cCI6MjA3Mzc5NDQ0NH0.baE9RQfNiXj71kN_X8JOKt-B6Ei9tYgLLy-Om8NqQxw

# OCR API Configuration
USE_GPU=False
OCR_LANG=en

# API Configuration
API_HOST=0.0.0.0
API_PORT=8050
PORT=8050

# CORS Configuration
# Use * for development, or specify your frontend domain(s)
CORS_ORIGINS=*

# File Upload Configuration (in bytes)
# 10485760 = 10MB
MAX_FILE_SIZE=10485760
EOF

echo ".env file created successfully!"
echo "You can edit it with: nano .env"

