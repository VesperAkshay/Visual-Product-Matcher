"""
Service layer for managing application services and models
"""

import logging
from typing import Optional, Dict, Any, TYPE_CHECKING
from threading import Lock
import weakref
import atexit

from models.clip_model import CLIPImageEncoder
from models.qdrant_db import QdrantVectorDB
from utils.data_loader import load_sample_products

if TYPE_CHECKING:
    from .s3_service import S3Service

logger = logging.getLogger(__name__)


class ServiceManager:
    """
    Thread-safe singleton service manager for application services
    Manages CLIP model and Qdrant database instances
    """
    
    _instance: Optional['ServiceManager'] = None
    _lock: Lock = Lock()
    _initialized: bool = False
    
    def __new__(cls) -> 'ServiceManager':
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize service manager (called only once)"""
        if ServiceManager._initialized:
            return
            
        self._clip_model: Optional[CLIPImageEncoder] = None
        self._vector_db: Optional[QdrantVectorDB] = None
        self._s3_service: Optional[Any] = None  # Use Any to avoid circular import
        self._config: Optional[Dict[str, Any]] = None
        self._model_lock = Lock()
        self._db_lock = Lock()
        self._s3_lock = Lock()
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
        
        ServiceManager._initialized = True
        logger.info("ServiceManager initialized")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize services with configuration
        
        Args:
            config: Application configuration dictionary
        """
        self._config = config
        logger.info("ServiceManager configuration set")
    
    @property
    def clip_model(self) -> CLIPImageEncoder:
        """
        Get CLIP model instance (lazy initialization)
        
        Returns:
            CLIPImageEncoder: Initialized CLIP model
            
        Raises:
            RuntimeError: If configuration not set or model fails to load
        """
        if self._clip_model is None:
            with self._model_lock:
                if self._clip_model is None:
                    self._initialize_clip_model()
        return self._clip_model
    
    @property
    def vector_db(self) -> QdrantVectorDB:
        """
        Get Qdrant database instance (lazy initialization)
        
        Returns:
            QdrantVectorDB: Initialized vector database
            
        Raises:
            RuntimeError: If configuration not set or database fails to connect
        """
        if self._vector_db is None:
            with self._db_lock:
                if self._vector_db is None:
                    self._initialize_vector_db()
        return self._vector_db

    @property
    def s3_service(self) -> Optional["S3Service"]:
        """
        Get S3 service instance (lazy initialization)
        
        Returns:
            S3Service: Initialized S3 service, or None if disabled
        """
        if self._s3_service is None:
            with self._s3_lock:
                if self._s3_service is None:
                    self._initialize_s3_service()
        return self._s3_service
    
    def _initialize_clip_model(self) -> None:
        """Initialize CLIP model (thread-safe)"""
        if self._config is None:
            raise RuntimeError("ServiceManager not configured. Call initialize() first.")
        
        try:
            logger.info("Initializing CLIP model...")
            clip_config = self._config.get('clip_config', {})
            
            self._clip_model = CLIPImageEncoder(
                model_name=clip_config.get('model_name', 'openai/clip-vit-base-patch32'),
                cache_dir=clip_config.get('cache_dir')
            )
            logger.info("CLIP model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CLIP model: {e}")
            raise RuntimeError(f"CLIP model initialization failed: {e}")
    
    def _initialize_vector_db(self) -> None:
        """Initialize vector database (thread-safe)"""
        if self._config is None:
            raise RuntimeError("ServiceManager not configured. Call initialize() first.")
        
        try:
            logger.info("Initializing Qdrant vector database...")
            qdrant_config = self._config.get('qdrant_config', {})
            
            self._vector_db = QdrantVectorDB(
                collection_name=qdrant_config.get('collection_name', 'product_images'),
                vector_size=qdrant_config.get('vector_size', 512),
                qdrant_host=qdrant_config.get('host', 'localhost'),
                qdrant_port=qdrant_config.get('port', 6333),
                use_docker=qdrant_config.get('use_docker', True),
                timeout=qdrant_config.get('timeout', 30),
                api_key=qdrant_config.get('api_key'),
                url=qdrant_config.get('url')
            )
            logger.info("Qdrant database initialized successfully")
            
            # Load sample products if database is empty and CLIP model is available
            if self._clip_model is not None:
                # Initialize S3 service first if needed
                if self._s3_service is None:
                    self._initialize_s3_service()
                load_sample_products(self._vector_db, self._clip_model, self._s3_service)
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            raise RuntimeError(f"Vector database initialization failed: {e}")
    
    def _initialize_s3_service(self) -> None:
        """Initialize S3 service (thread-safe)"""
        if self._config is None:
            raise RuntimeError("ServiceManager not configured. Call initialize() first.")
        
        try:
            logger.info("Initializing S3 service...")
            # Import here to avoid circular dependencies
            from .s3_service import create_s3_service
            self._s3_service = create_s3_service(self._config)
            
            if self._s3_service:
                logger.info("S3 service initialized successfully")
            else:
                logger.info("S3 service disabled or not configured")
            
        except Exception as e:
            logger.warning(f"Failed to initialize S3 service: {e}")
            self._s3_service = None  # Continue without S3
    
    def is_initialized(self) -> bool:
        """Check if services are initialized"""
        return (self._clip_model is not None and 
                self._vector_db is not None)
    
    def get_status(self) -> Dict[str, str]:
        """
        Get status of all services
        
        Returns:
            Dict: Status of each service
        """
        return {
            'clip_model': 'loaded' if self._clip_model else 'not_loaded',
            'vector_db': 'connected' if self._vector_db else 'not_connected',
            's3_service': 'enabled' if self._s3_service else 'disabled',
            'configured': 'yes' if self._config else 'no'
        }
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if self._vector_db:
                self._vector_db.close()
                logger.info("Vector database connection closed")
            
            # CLIP model cleanup (if needed)
            if self._clip_model:
                # Clear CUDA cache if using GPU
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except ImportError:
                    pass
                logger.info("CLIP model resources cleaned up")
            
            self._clip_model = None
            self._vector_db = None
            logger.info("ServiceManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def reset(self) -> None:
        """Reset services (useful for testing)"""
        with self._model_lock:
            with self._db_lock:
                self.cleanup()
                logger.info("ServiceManager reset completed")


# Global service manager instance
_service_manager: Optional[ServiceManager] = None


def get_service_manager() -> ServiceManager:
    """
    Get the global service manager instance
    
    Returns:
        ServiceManager: Global service manager
    """
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager


def initialize_services(config: Dict[str, Any]) -> None:
    """
    Initialize services with configuration
    
    Args:
        config: Application configuration
    """
    service_manager = get_service_manager()
    service_manager.initialize(config)


def get_clip_model() -> CLIPImageEncoder:
    """Get CLIP model instance"""
    return get_service_manager().clip_model


def get_vector_db() -> QdrantVectorDB:
    """Get vector database instance"""
    return get_service_manager().vector_db


def get_s3_service() -> Optional["S3Service"]:
    """Get S3 service instance"""
    return get_service_manager().s3_service


def get_services_status() -> Dict[str, str]:
    """Get status of all services"""
    return get_service_manager().get_status()


def cleanup_services() -> None:
    """Cleanup all services"""
    global _service_manager
    if _service_manager:
        _service_manager.cleanup()


def reset_services() -> None:
    """Reset all services (for testing)"""
    global _service_manager
    if _service_manager:
        _service_manager.reset()
