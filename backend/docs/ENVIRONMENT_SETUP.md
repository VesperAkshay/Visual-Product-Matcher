# Environment Setup Guide

## Quick Start

1. **Create your environment file:**
   ```bash
   cd backend
   python env_manager.py create
   ```

2. **Validate your configuration:**
   ```bash
   python validate_config.py
   ```

3. **Start the application:**
   ```bash
   python app.py
   ```

## Environment Management Commands

### Create Environment File
```bash
python env_manager.py create
```
Creates `.env` from `.env.example` with development-friendly defaults.

### Show Current Configuration
```bash
python env_manager.py show
```
Displays all environment variables from your `.env` file.

### Validate Configuration
```bash
python env_manager.py validate
# OR
python validate_config.py
```
Validates your current configuration and shows detailed status.

### Switch to Production
```bash
python env_manager.py production
```
Switches to production configuration (requires `.env.production.example`).

## Configuration Files

- **`.env.example`** - Template for development environment
- **`.env.production.example`** - Template for production environment  
- **`.env`** - Your actual environment configuration (git-ignored)
- **`ENV_VARIABLES.md`** - Complete documentation of all variables

## Key Configuration Areas

### 🔧 Flask Application
- `FLASK_ENV` - Environment mode (development/production)
- `SECRET_KEY` - Security key (must be changed in production)
- `MAX_CONTENT_LENGTH` - File upload size limit

### 🗄️ Qdrant Database
- `QDRANT_HOST` - Database host
- `QDRANT_PORT` - Database port  
- `USE_DOCKER_QDRANT` - Use Docker container (true/false)

### 🤖 CLIP Model
- `CLIP_MODEL_NAME` - HuggingFace model identifier
- `MODEL_CACHE_DIR` - Model cache directory

### 📝 Logging
- `LOG_LEVEL` - Logging verbosity (DEBUG/INFO/WARNING/ERROR)
- `LOG_FILE` - Log file path (empty for console only)

## Troubleshooting

### Configuration Errors
Run validation to see detailed error messages:
```bash
python validate_config.py
```

### Missing Directories
The application will create required directories automatically.

### Qdrant Connection Issues
1. Check if Docker is running: `docker ps`
2. Start Qdrant: `docker-compose up -d qdrant`
3. Verify connection settings in `.env`

### Model Download Issues
1. Check internet connection
2. Verify `MODEL_CACHE_DIR` is writable
3. Check HuggingFace model name is correct

## Development vs Production

### Development (Default)
- Debug mode enabled
- Verbose logging
- Local Qdrant instance
- Default secret key (insecure)

### Production
- Debug mode disabled
- Warning-level logging
- Production database
- Strong secret key (required)
- HTTPS CORS origins
