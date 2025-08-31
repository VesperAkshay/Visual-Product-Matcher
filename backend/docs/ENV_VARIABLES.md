# Environment Variables Documentation

This document explains all the environment variables used in the Visual Product Matcher backend.

## 🔧 Setup Instructions

1. Copy `.env.example` to `.env` for development:
   ```bash
   cp .env.example .env
   ```

2. For production, copy `.env.production.example` to `.env`:
   ```bash
   cp .env.production.example .env
   ```

3. Edit the `.env` file with your specific values.

## 📋 Environment Variables Reference

### Flask Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `FLASK_ENV` | string | `development` | Environment mode: `development`, `production`, `testing` |
| `FLASK_APP` | string | `app.py` | Entry point for Flask application |
| `SECRET_KEY` | string | ⚠️ **Required in production** | Secret key for Flask sessions and security |
| `MAX_CONTENT_LENGTH` | int | `16777216` | Maximum file upload size in bytes (16MB) |
| `API_VERSION` | string | `v1` | API version identifier |
| `PORT` | int | `5001` | Port number for the application |

### Qdrant Database Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `QDRANT_HOST` | string | `localhost` | Qdrant server hostname |
| `QDRANT_PORT` | int | `6333` | Qdrant server port |
| `QDRANT_COLLECTION` | string | `product_images` | Name of the vector collection |
| `USE_DOCKER_QDRANT` | bool | `true` | Whether to use Docker-based Qdrant |
| `QDRANT_TIMEOUT` | int | `30` | Connection timeout in seconds |
| `VECTOR_DIMENSION` | int | `512` | Dimension of embedding vectors |

### CLIP Model Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CLIP_MODEL_NAME` | string | `openai/clip-vit-base-patch32` | HuggingFace model identifier |
| `MODEL_CACHE_DIR` | string | `./models_cache` | Directory to cache downloaded models |

### File Upload Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ALLOWED_EXTENSIONS` | string | `png,jpg,jpeg,gif,webp` | Comma-separated list of allowed file extensions |
| `UPLOAD_FOLDER` | string | `./uploads` | Directory for temporary uploaded files |
| `DATA_FOLDER` | string | `./data` | Directory for application data |

### CORS Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CORS_ORIGINS` | string | `http://localhost:3000,http://localhost:3001` | Comma-separated list of allowed origins |

### API Rate Limiting

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_RATE_LIMIT` | string | `100 per hour` | Rate limit format: "number per time_unit" |

### Logging Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_FILE` | string | (empty) | Log file path (empty = console only) |

### Performance Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `BATCH_SIZE` | int | `100` | Batch size for database operations |
| `MAX_WORKERS` | int | `4` | Maximum number of worker threads |

### Production-Specific Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GUNICORN_WORKERS` | int | `4` | Number of Gunicorn worker processes |
| `GUNICORN_TIMEOUT` | int | `120` | Worker timeout in seconds |
| `GUNICORN_BIND` | string | `0.0.0.0:5001` | Bind address for Gunicorn |
| `GUNICORN_MAX_REQUESTS` | int | `1000` | Max requests per worker before restart |
| `GUNICORN_MAX_REQUESTS_JITTER` | int | `100` | Jitter for max requests |

## 🔒 Security Notes

### Development
- Default `SECRET_KEY` is acceptable for development
- Debug mode is enabled
- Verbose logging is active

### Production
- **MUST** set a strong `SECRET_KEY`
- **MUST** set `FLASK_ENV=production`
- **SHOULD** use HTTPS origins in `CORS_ORIGINS`
- **SHOULD** set appropriate log levels and file paths
- **SHOULD** use production-grade database hosts

## 🚨 Common Issues & Solutions

### 1. Configuration Validation Errors
Run the validation script to check your configuration:
```bash
cd backend
python validate_config.py
```

### 2. Missing Directories
The application will automatically create required directories, but ensure the parent directories exist and are writable.

### 3. Qdrant Connection Issues
- Ensure Docker is running if `USE_DOCKER_QDRANT=true`
- Check if Qdrant container is started: `docker-compose up -d qdrant`
- Verify host and port settings

### 4. Model Loading Issues
- Ensure `MODEL_CACHE_DIR` exists and is writable
- Check internet connection for initial model download
- Verify HuggingFace model name is correct

## 📝 Example Configurations

### Development (.env)
```bash
FLASK_ENV=development
SECRET_KEY=dev-key-change-in-production
USE_DOCKER_QDRANT=true
LOG_LEVEL=DEBUG
```

### Production (.env)
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key
QDRANT_HOST=your-production-qdrant-host
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING
LOG_FILE=/var/log/app.log
```

### Testing (.env)
```bash
FLASK_ENV=testing
TESTING=true
QDRANT_COLLECTION=test_product_images
LOG_LEVEL=DEBUG
```
