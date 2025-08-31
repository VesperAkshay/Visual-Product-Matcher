"""
Configuration settings for the Visual Product Matcher API
"""

import os
from pathlib import Path
from typing import List, Optional, Union
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass

class Config:
    """Base configuration with proper validation and environment handling"""
    
    def __init__(self):
        """Initialize configuration with validation"""
        self._validate_required_env_vars()
        self._setup_paths()
    
    # Flask settings
    @property
    def SECRET_KEY(self) -> str:
        key = os.environ.get('SECRET_KEY')
        if not key:
            if self.is_production():
                raise ConfigError("SECRET_KEY must be set in production environment")
            return 'dev-secret-key-change-in-production'
        return key
    
    @property
    def MAX_CONTENT_LENGTH(self) -> int:
        """Maximum file upload size in bytes"""
        size = os.environ.get('MAX_CONTENT_LENGTH', '16777216')  # 16MB default
        try:
            return int(size)
        except ValueError:
            raise ConfigError(f"Invalid MAX_CONTENT_LENGTH value: {size}")
    
    @property
    def DEBUG(self) -> bool:
        return os.environ.get('FLASK_ENV', 'production').lower() == 'development'
    
    # File upload settings
    @property
    def UPLOAD_FOLDER(self) -> str:
        custom_path = os.environ.get('UPLOAD_FOLDER')
        if custom_path:
            return os.path.abspath(custom_path)
        return os.path.join(os.path.dirname(__file__), '..', 'uploads')
    
    @property
    def ALLOWED_EXTENSIONS(self) -> set:
        extensions = os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,webp')
        return {ext.strip().lower() for ext in extensions.split(',')}
    
    # Qdrant settings
    @property
    def QDRANT_HOST(self) -> str:
        return os.environ.get('QDRANT_HOST', 'localhost')
    
    @property
    def QDRANT_PORT(self) -> int:
        port = os.environ.get('QDRANT_PORT', '6333')
        try:
            return int(port)
        except ValueError:
            raise ConfigError(f"Invalid QDRANT_PORT value: {port}")
    
    @property
    def QDRANT_URL(self) -> str:
        """Construct full Qdrant URL"""
        # For cloud Qdrant, use the full URL if host contains protocol
        if self.QDRANT_HOST.startswith(('http://', 'https://')):
            return self.QDRANT_HOST
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"
    
    @property
    def QDRANT_API_KEY(self) -> Optional[str]:
        """Qdrant API key for cloud instances"""
        return os.environ.get('QDRANT_API_KEY')
    
    @property
    def QDRANT_COLLECTION(self) -> str:
        return os.environ.get('QDRANT_COLLECTION', 'product_images')
    
    @property
    def USE_DOCKER_QDRANT(self) -> bool:
        return os.environ.get('USE_DOCKER_QDRANT', 'true').lower() == 'true'
    
    @property
    def QDRANT_TIMEOUT(self) -> int:
        timeout = os.environ.get('QDRANT_TIMEOUT', '30')
        try:
            return int(timeout)
        except ValueError:
            raise ConfigError(f"Invalid QDRANT_TIMEOUT value: {timeout}")
    
    # CLIP model settings
    @property
    def CLIP_MODEL_NAME(self) -> str:
        return os.environ.get('CLIP_MODEL_NAME', 'openai/clip-vit-base-patch32')
    
    @property
    def VECTOR_DIMENSION(self) -> int:
        dimension = os.environ.get('VECTOR_DIMENSION', '512')
        try:
            return int(dimension)
        except ValueError:
            raise ConfigError(f"Invalid VECTOR_DIMENSION value: {dimension}")
    
    @property
    def MODEL_CACHE_DIR(self) -> Optional[str]:
        """Directory to cache downloaded models"""
        cache_dir = os.environ.get('MODEL_CACHE_DIR')
        if cache_dir:
            return os.path.abspath(cache_dir)
        return None
    
    # API settings
    @property
    def CORS_ORIGINS(self) -> List[str]:
        origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000')
        return [origin.strip() for origin in origins.split(',') if origin.strip()]
    
    @property
    def API_RATE_LIMIT(self) -> str:
        return os.environ.get('API_RATE_LIMIT', '100 per hour')
    
    @property
    def API_VERSION(self) -> str:
        return os.environ.get('API_VERSION', 'v1')
    
    # Database settings
    @property
    def DATA_FOLDER(self) -> str:
        custom_path = os.environ.get('DATA_FOLDER')
        if custom_path:
            return os.path.abspath(custom_path)
        return os.path.join(os.path.dirname(__file__), '..', 'data')

    # AWS S3 settings
    @property
    def S3_ENABLED(self) -> bool:
        """Enable S3 storage for images and metadata"""
        return os.environ.get('S3_ENABLED', 'false').lower() == 'true'
    
    @property
    def S3_BUCKET_NAME(self) -> str:
        """S3 bucket name for storing images"""
        bucket = os.environ.get('S3_BUCKET_NAME', 'visual-product-matcher-images')
        if self.S3_ENABLED and not bucket:
            raise ConfigError("S3_BUCKET_NAME must be set when S3_ENABLED is true")
        return bucket
    
    @property
    def S3_REGION(self) -> str:
        """AWS region for S3 bucket"""
        return os.environ.get('S3_REGION', 'us-east-1')
    
    @property
    def AWS_ACCESS_KEY_ID(self) -> Optional[str]:
        """AWS access key ID (optional if using IAM roles)"""
        return os.environ.get('AWS_ACCESS_KEY_ID')
    
    @property
    def AWS_SECRET_ACCESS_KEY(self) -> Optional[str]:
        """AWS secret access key (optional if using IAM roles)"""
        return os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    @property
    def S3_IMAGE_PREFIX(self) -> str:
        """Prefix for image objects in S3"""
        return os.environ.get('S3_IMAGE_PREFIX', 'images/')
    
    @property
    def S3_METADATA_KEY(self) -> str:
        """S3 key for metadata file"""
        return os.environ.get('S3_METADATA_KEY', 'metadata/products.json')
    
    @property
    def S3_CDN_URL(self) -> Optional[str]:
        """CloudFront CDN URL for faster image delivery (optional)"""
        return os.environ.get('S3_CDN_URL')

    # Logging settings
    @property
    def LOG_LEVEL(self) -> str:
        return os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    @property
    def LOG_FILE(self) -> Optional[str]:
        log_file = os.environ.get('LOG_FILE')
        if log_file:
            return os.path.abspath(log_file)
        return None
    
    # Performance settings
    @property
    def BATCH_SIZE(self) -> int:
        batch_size = os.environ.get('BATCH_SIZE', '100')
        try:
            return int(batch_size)
        except ValueError:
            raise ConfigError(f"Invalid BATCH_SIZE value: {batch_size}")
    
    @property
    def MAX_WORKERS(self) -> int:
        workers = os.environ.get('MAX_WORKERS', '4')
        try:
            return int(workers)
        except ValueError:
            raise ConfigError(f"Invalid MAX_WORKERS value: {workers}")
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return os.environ.get('FLASK_ENV', 'development').lower() == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return os.environ.get('FLASK_ENV', 'development').lower() == 'development'
    
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return os.environ.get('TESTING', 'false').lower() == 'true'
    
    def _validate_required_env_vars(self):
        """Validate required environment variables"""
        required_in_production = ['SECRET_KEY']
        
        if self.is_production():
            for var in required_in_production:
                if not os.environ.get(var):
                    raise ConfigError(f"Required environment variable {var} is not set in production")
    
    def _setup_paths(self):
        """Ensure required directories exist"""
        paths_to_create = [
            self.UPLOAD_FOLDER,
            self.DATA_FOLDER,
        ]
        
        if self.MODEL_CACHE_DIR:
            paths_to_create.append(self.MODEL_CACHE_DIR)
        
        for path in paths_to_create:
            try:
                os.makedirs(path, exist_ok=True)
                logger.info(f"Ensured directory exists: {path}")
            except OSError as e:
                logger.warning(f"Failed to create directory {path}: {e}")
    
    def get_qdrant_config(self) -> dict:
        """Get Qdrant configuration as dictionary"""
        config = {
            'host': self.QDRANT_HOST,
            'port': self.QDRANT_PORT,
            'url': self.QDRANT_URL,
            'collection_name': self.QDRANT_COLLECTION,
            'vector_size': self.VECTOR_DIMENSION,
            'use_docker': self.USE_DOCKER_QDRANT,
            'timeout': self.QDRANT_TIMEOUT,
        }
        
        # Add API key if available (for cloud instances)
        if self.QDRANT_API_KEY:
            config['api_key'] = self.QDRANT_API_KEY
            
        return config
    
    def get_clip_config(self) -> dict:
        """Get CLIP model configuration as dictionary"""
        config = {
            'model_name': self.CLIP_MODEL_NAME,
            'vector_dimension': self.VECTOR_DIMENSION,
        }
        if self.MODEL_CACHE_DIR:
            config['cache_dir'] = self.MODEL_CACHE_DIR
        return config
    
    def validate_config(self) -> bool:
        """Validate entire configuration"""
        try:
            # Test all properties to trigger validation
            _ = self.SECRET_KEY
            _ = self.MAX_CONTENT_LENGTH
            _ = self.QDRANT_PORT
            _ = self.VECTOR_DIMENSION
            _ = self.BATCH_SIZE
            _ = self.MAX_WORKERS
            logger.info("Configuration validation successful")
            return True
        except ConfigError as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
class DevelopmentConfig(Config):
    """Development configuration"""
    
    def __init__(self):
        # Set development environment
        os.environ.setdefault('FLASK_ENV', 'development')
        super().__init__()
    
    @property
    def DEBUG(self) -> bool:
        return True
    
    @property
    def LOG_LEVEL(self) -> str:
        return 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    
    def __init__(self):
        # Set production environment
        os.environ.setdefault('FLASK_ENV', 'production')
        super().__init__()
    
    @property
    def DEBUG(self) -> bool:
        return False
    
    @property
    def API_RATE_LIMIT(self) -> str:
        return os.environ.get('API_RATE_LIMIT', '1000 per hour')
    
    def _validate_required_env_vars(self):
        """Enhanced validation for production"""
        super()._validate_required_env_vars()
        
        # Additional production requirements
        production_vars = ['QDRANT_HOST', 'CORS_ORIGINS']
        for var in production_vars:
            if not os.environ.get(var):
                logger.warning(f"Production environment variable {var} is not set, using default")

class TestingConfig(Config):
    """Testing configuration"""
    
    def __init__(self):
        # Set testing environment
        os.environ.setdefault('FLASK_ENV', 'testing')
        os.environ.setdefault('TESTING', 'true')
        super().__init__()
    
    @property
    def DEBUG(self) -> bool:
        return True
    
    @property
    def TESTING(self) -> bool:
        return True
    
    @property
    def QDRANT_COLLECTION(self) -> str:
        return 'test_product_images'
    
    @property
    def LOG_LEVEL(self) -> str:
        return 'DEBUG'

# Configuration factory
def get_config(config_name: Optional[str] = None) -> Config:
    """
    Factory function to get appropriate configuration
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, determined from FLASK_ENV environment variable
    
    Returns:
        Config: Appropriate configuration instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    config_class = config_map.get(config_name, ProductionConfig)
    return config_class()

# Configuration dictionary (for backward compatibility)
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
