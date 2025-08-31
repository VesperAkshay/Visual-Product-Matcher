# 🐍 Visual Product Matcher - Backend

> **AI-Powered Flask API with CLIP Model Integration**

A sophisticated Python backend that provides REST API endpoints for visual product similarity search using OpenAI's CLIP model and Qdrant vector database.

## ✨ Features

🤖 **CLIP Model Integration** - OpenAI vision-language model for embeddings  
🗄️ **Vector Database** - Qdrant for high-performance similarity search  
🔄 **Service Architecture** - Thread-safe singleton service management  
⚙️ **Configuration Management** - Environment-based configuration system  
🛡️ **Input Validation** - Comprehensive request validation and sanitization  
📊 **Health Monitoring** - System status and performance tracking  
🧪 **Testing Suite** - Comprehensive test coverage with pytest  

## 🏗️ Architecture

```
Flask Application
├── 🔧 Service Layer (Thread-Safe Singletons)
│   ├── CLIP Model Service
│   └── Qdrant Database Service
├── 🌐 API Layer (RESTful Endpoints)
│   ├── Search Routes
│   ├── Product Routes
│   └── Health Routes
├── ⚙️ Configuration Layer
│   ├── Environment Management
│   └── Settings Validation
└── 🛠️ Utility Layer
    ├── Image Processing
    ├── Data Loading
    └── File Management
```

## 🚀 Quick Start

### **1. Environment Setup**
```bash
# Create environment configuration
python env_manager.py create

# Validate configuration
python validate_config.py
```

### **2. Install Dependencies**
```bash
# Install Python packages
pip install -r requirements.txt
```

### **3. Start Services**
```bash
# Start Qdrant database (Docker)
docker-compose up -d qdrant

# Start Flask application
python app.py
```

### **4. Verify Installation**
```bash
# Check backend health
curl http://localhost:5000/api/health

# Check services status
curl http://localhost:5000/api/status
```

## 📁 Project Structure

```
backend/
├── 📄 app.py                    # Flask application entry point
├── 📄 requirements.txt          # Python dependencies
├── 📄 env_manager.py            # Environment management utility
├── 📄 validate_config.py        # Configuration validation
├── 📁 api/                      # REST API endpoints
│   ├── __init__.py
│   └── routes.py               # API route definitions
├── 📁 config/                   # Configuration management
│   ├── __init__.py
│   └── settings.py             # Environment configuration
├── 📁 services/                 # Service layer architecture
│   ├── __init__.py
│   └── service_manager.py      # Thread-safe service management
├── 📁 models/                   # AI model integration
│   ├── __init__.py
│   ├── clip_model.py           # CLIP model wrapper
│   └── qdrant_db.py            # Qdrant database client
├── 📁 utils/                    # Utility functions
│   ├── __init__.py
│   ├── image_utils.py          # Image processing utilities
│   └── data_loader.py          # Data loading utilities
├── 📁 data/                     # Sample data and images
│   ├── products.json           # Product catalog
│   └── images/                 # Sample product images
├── 📁 docs/                     # Documentation
│   ├── GLOBAL_STATE_FIXED.md   # Architecture improvements
│   └── ENVIRONMENT_SETUP.md    # Environment setup guide
├── 📁 tests/                    # Test suite
│   ├── conftest.py             # Test configuration
│   ├── test_api.py             # API endpoint tests
│   ├── test_services.py        # Service layer tests
│   ├── test_models.py          # Model integration tests
│   └── test_utils.py           # Utility function tests
└── 📁 uploads/                  # Temporary file uploads
```

## 🔧 Configuration

### **Environment Variables**
```bash
# 🌐 Flask Configuration
FLASK_ENV=development           # Environment mode
FLASK_HOST=0.0.0.0             # Server host
FLASK_PORT=5000                # Server port
SECRET_KEY=dev-secret-key      # Security key (change in production!)
MAX_CONTENT_LENGTH=16777216    # 16MB file upload limit

# 🗄️ Qdrant Database
QDRANT_HOST=localhost          # Database host
QDRANT_PORT=6333              # Database port
USE_DOCKER_QDRANT=true        # Use Docker container
QDRANT_COLLECTION_NAME=products # Collection name

# 🤖 CLIP Model
CLIP_MODEL_NAME=openai/clip-vit-base-patch32  # HuggingFace model
MODEL_CACHE_DIR=./models/cache                # Model cache directory

# 📝 Logging
LOG_LEVEL=INFO                 # Logging verbosity
LOG_FILE=logs/app.log         # Log file path (empty for console)

# 🔗 CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### **Configuration Management**
```bash
# Create development environment
python env_manager.py create

# Switch to production configuration  
python env_manager.py production

# Show current configuration
python env_manager.py show

# Validate configuration
python env_manager.py validate
```

## 🌐 API Endpoints

### **Search Endpoints**
```http
POST /api/search/upload
Content-Type: multipart/form-data

# Upload image file for similarity search
```

```http
POST /api/search/url
Content-Type: application/json

{
    "url": "https://example.com/product.jpg",
    "top_k": 5
}
```

### **Product Endpoints**
```http
GET /api/products
# Get all products with pagination

GET /api/products?category=electronics&limit=10&offset=0
# Get filtered products

POST /api/products
Content-Type: application/json

{
    "name": "Product Name",
    "description": "Product description",
    "image_url": "https://example.com/image.jpg",
    "price": "$29.99",
    "category": "Electronics"
}
```

### **System Endpoints**
```http
GET /api/health
# Basic health check

GET /api/status
# Detailed system status including services
```

### **Response Format**
```json
{
    "success": true,
    "data": {
        "similar_products": [
            {
                "id": "product_001",
                "name": "Similar Product",
                "similarity_score": 0.92,
                "image_url": "https://example.com/product.jpg",
                "price": "$29.99"
            }
        ]
    },
    "message": "Search completed successfully",
    "execution_time": 0.15
}
```

## 🤖 AI Model Integration

### **CLIP Model Service**
```python
from services import get_clip_model

# Get thread-safe CLIP model instance
clip_model = get_clip_model()

# Generate image embeddings
embedding = clip_model.encode_image(image_path)

# Generate text embeddings  
text_embedding = clip_model.encode_text("red sneakers")
```

### **Qdrant Database Service**
```python
from services import get_vector_db

# Get thread-safe Qdrant client
vector_db = get_vector_db()

# Search for similar vectors
results = vector_db.search(
    embedding=query_embedding,
    limit=5,
    score_threshold=0.7
)

# Add new product embedding
vector_db.add_point(
    point_id=product_id,
    embedding=product_embedding,
    payload={"name": "Product Name", "category": "Electronics"}
)
```

## 🔒 Service Management

### **Thread-Safe Architecture**
```python
# Service manager ensures thread safety
from services import ServiceManager

# Singleton pattern with thread locks
manager = ServiceManager.get_instance()

# Lazy initialization
clip_model = manager.clip_model  # Loads on first access
vector_db = manager.vector_db    # Loads on first access
```

### **Resource Management**
```python
# Automatic cleanup on application exit
from services import cleanup_services

# Manual cleanup for testing
reset_services()

# Service status monitoring
status = get_services_status()
print(f"CLIP Model: {status['clip_model']}")
print(f"Vector DB: {status['vector_db']}")
```

## 🧪 Testing

### **Run Test Suite**
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_api.py          # API tests
pytest tests/test_services.py     # Service tests
pytest tests/test_models.py       # Model tests

# Run with verbose output
pytest -v -s
```

### **Test Categories**

#### **API Tests** (`test_api.py`)
- Upload image endpoint testing
- URL search endpoint testing
- Product CRUD operations
- Error handling and validation
- Response format validation

#### **Service Tests** (`test_services.py`)
- Service manager singleton pattern
- Thread safety verification
- Lazy loading behavior
- Resource cleanup testing
- Configuration integration

#### **Model Tests** (`test_models.py`)
- CLIP model initialization
- Image embedding generation
- Qdrant database operations
- Vector similarity search
- Error handling for model failures

#### **Utility Tests** (`test_utils.py`)
- Image processing functions
- Data loading utilities
- File handling operations
- Input validation functions

### **Test Configuration**
```python
# conftest.py - Test fixtures and configuration
@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_image():
    """Sample image for testing"""
    return create_test_image()
```

## 🔧 Development Tools

### **Environment Management**
```bash
# Development environment
python env_manager.py create

# Production environment
python env_manager.py production

# Show current settings
python env_manager.py show
```

### **Configuration Validation**
```bash
# Validate current configuration
python validate_config.py

# Check specific components
python -c "from config import config; print(config.validate())"
```

### **Data Management**
```bash
# Load sample data
python utils/data_loader.py

# Setup real product data
python setup_real_data.py

# Scan and process images
python -c "from api.routes import scan_images; scan_images()"
```

## 🚨 Troubleshooting

### **Common Issues**

#### **Service Initialization Errors**
```bash
# Check service status
curl http://localhost:5000/api/status

# Restart services
python -c "from services import reset_services; reset_services()"
```

#### **Model Loading Issues**
```bash
# Clear model cache
rm -rf ~/.cache/huggingface/

# Set custom cache directory
export MODEL_CACHE_DIR=./models/cache

# Check model configuration
python -c "from config import config; print(config.get_clip_config())"
```

#### **Database Connection Issues**
```bash
# Check Qdrant status
curl http://localhost:6333/health

# Restart Qdrant container
docker-compose restart qdrant

# Check database configuration
python -c "from config import config; print(config.get_qdrant_config())"
```

#### **Configuration Problems**
```bash
# Validate environment
python validate_config.py

# Recreate environment file
python env_manager.py create --force

# Check environment variables
python env_manager.py show
```

### **Debug Mode**
```bash
# Start with debug logging
FLASK_ENV=development LOG_LEVEL=DEBUG python app.py

# Enable Flask debug mode
FLASK_DEBUG=1 python app.py
```

## 📊 Performance Monitoring

### **Health Checks**
```bash
# Basic health check
curl http://localhost:5000/api/health

# Detailed system status
curl http://localhost:5000/api/status
```

### **Performance Metrics**
- **Model Loading**: ~2-3 seconds on first request
- **Search Response**: < 100ms average
- **Memory Usage**: ~2GB with CLIP model loaded
- **Concurrent Requests**: Thread-safe service management

### **Monitoring Tools**
```python
# Service status monitoring
from services import get_services_status

status = get_services_status()
print(f"Services healthy: {all(status.values())}")

# Performance timing
import time
start_time = time.time()
# ... operation ...
execution_time = time.time() - start_time
```

## 🚀 Production Deployment

### **Production Configuration**
```bash
# Use production environment
cp .env.production.example .env

# Key production settings
FLASK_ENV=production
SECRET_KEY=strong-random-secret-key
LOG_LEVEL=WARNING
USE_DOCKER_QDRANT=true
```

### **Production Server**
```bash
# Install production server
pip install gunicorn

# Start with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

# Start with configuration file
gunicorn --config gunicorn.conf.py app:app
```

### **Production Checklist**
- ✅ Strong secret key configured
- ✅ Debug mode disabled
- ✅ Production logging level
- ✅ CORS origins properly configured
- ✅ Database connection secured
- ✅ File upload limits set
- ✅ Health monitoring enabled

## 📚 Additional Resources

- **🤖 CLIP Model**: [Hugging Face Documentation](https://huggingface.co/openai/clip-vit-base-patch32)
- **🗄️ Qdrant**: [Vector Database Documentation](https://qdrant.tech/documentation/)
- **🐍 Flask**: [Web Framework Documentation](https://flask.palletsprojects.com/)
- **🧪 pytest**: [Testing Framework Documentation](https://docs.pytest.org/)

---

**Built with ❤️ for AI-powered backend services**
