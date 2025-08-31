# Google Cloud Run Optimized Dockerfile for Visual Product Matcher Backend

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV HF_HOME=/app/models_cache
ENV TRANSFORMERS_CACHE=/app/models_cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads models_cache

# Pre-download CLIP model during build
ENV HF_HOME=/app/models_cache
ENV TRANSFORMERS_CACHE=/app/models_cache
RUN python -c "import os; os.makedirs('/app/models_cache', exist_ok=True); \
    from transformers import CLIPProcessor, CLIPModel; \
    model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32', cache_dir='/app/models_cache'); \
    processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32', cache_dir='/app/models_cache'); \
    print('CLIP model cached successfully to:', '/app/models_cache')"

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Visual Product Matcher Backend..."\n\
echo "PORT: $PORT"\n\
echo "Environment: $FLASK_ENV"\n\
exec gunicorn \\\n\
    --bind 0.0.0.0:$PORT \\\n\
    --workers 1 \\\n\
    --threads 2 \\\n\
    --timeout 900 \\\n\
    --max-requests 1000 \\\n\
    --max-requests-jitter 100 \\\n\
    --preload \\\n\
    --log-level info \\\n\
    --access-logfile - \\\n\
    --error-logfile - \\\n\
    app:app' > /app/start.sh && chmod +x /app/start.sh

# Expose port (Cloud Run will override this)
EXPOSE 8080

# Run the application
CMD ["/app/start.sh"]
