# Create .env File on Server

The template file isn't on your server. Here's how to create the .env file directly:

## Option 1: Create .env File Directly (Easiest)

Run this command on your server:

```bash
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
CORS_ORIGINS=*

# File Upload Configuration
MAX_FILE_SIZE=10485760
EOF
```

This will create the `.env` file with all the required values.

## Option 2: Create with nano (Manual)

```bash
# Create empty .env file
touch .env

# Edit it
nano .env
```

Then paste this content:

```env
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
CORS_ORIGINS=*

# File Upload Configuration
MAX_FILE_SIZE=10485760
```

Save: `Ctrl+X`, then `Y`, then `Enter`

## Verify .env File

```bash
# Check if file exists
ls -la .env

# View contents (first few lines)
head .env
```

## Continue with Deployment

After creating .env, continue with:

```bash
# Generate SSL certificate
python3 nginx/generate-ssl-cert.py 93.127.216.78

# Build and start
docker-compose build
docker-compose up -d
```

