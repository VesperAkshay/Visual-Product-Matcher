"""
Visual Product Matcher Backend API
Flask-based REST API for image similarity search using OpenAI CLIP and Qdrant
"""

from flask import Flask
from flask_cors import CORS
from config.settings import get_config, ConfigError
from api.routes import api_bp
import logging
import os

def setup_logging(config):
    """Setup logging based on configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=config.LOG_FILE if config.LOG_FILE else None
    )
    
    # Also log to console if log file is specified
    if config.LOG_FILE:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)

def create_app(config_name=None):
    """Application factory pattern with improved configuration"""
    try:
        # Get configuration
        config = get_config(config_name)
        
        # Validate configuration
        if not config.validate_config():
            raise ConfigError("Configuration validation failed")
        
        # Setup logging
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        # Create Flask app
        app = Flask(__name__)
        
        # Configure Flask app with our config object
        app.config['SECRET_KEY'] = config.SECRET_KEY
        app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
        app.config['DEBUG'] = config.DEBUG
        
        # Store config object for access in other modules
        app.config['APP_CONFIG'] = config
        
        # Initialize services with configuration
        from services import initialize_services, cleanup_services
        
        service_config = {
            'qdrant_config': config.get_qdrant_config(),
            'clip_config': config.get_clip_config(),
            # S3 configuration
            'S3_ENABLED': config.S3_ENABLED,
            'S3_BUCKET_NAME': config.S3_BUCKET_NAME,
            'S3_REGION': config.S3_REGION,
            'AWS_ACCESS_KEY_ID': config.AWS_ACCESS_KEY_ID,
            'AWS_SECRET_ACCESS_KEY': config.AWS_SECRET_ACCESS_KEY,
            'S3_IMAGE_PREFIX': config.S3_IMAGE_PREFIX,
            'S3_METADATA_KEY': config.S3_METADATA_KEY
        }
        initialize_services(service_config)
        logger.info("Services initialized with configuration")
        
        # Register cleanup function
        import atexit
        atexit.register(cleanup_services)
        
        # Enable CORS with configured origins
        CORS(app, origins=config.CORS_ORIGINS)
        logger.info(f"CORS enabled for origins: {config.CORS_ORIGINS}")
        
        # Register blueprints
        app.register_blueprint(api_bp, url_prefix='/api')
        
        # Health check route
        @app.route('/health')
        def health():
            return {
                'status': 'healthy', 
                'service': 'visual-product-matcher-api',
                'version': config.API_VERSION,
                'environment': 'production' if config.is_production() else 'development'
            }
        
        # Configuration info endpoint (development only)
        if config.is_development():
            @app.route('/config-info')
            def config_info():
                return {
                    'qdrant_config': config.get_qdrant_config(),
                    'clip_config': config.get_clip_config(),
                    'cors_origins': config.CORS_ORIGINS,
                    'debug': config.DEBUG,
                    'log_level': config.LOG_LEVEL
                }
        
        logger.info(f"Flask app created successfully with config: {config.__class__.__name__}")
        return app
        
    except ConfigError as e:
        print(f"Configuration error: {e}")
        raise
    except Exception as e:
        print(f"Failed to create app: {e}")
        raise

# Create app instance for gunicorn
app = create_app()

if __name__ == '__main__':
    try:
        app = create_app()
        config = app.config['APP_CONFIG']
        logger = logging.getLogger(__name__)
        
        port = int(os.environ.get('PORT', 5001))  # Different port for API
        debug = config.DEBUG
        
        logger.info(f"Starting Visual Product Matcher API on port {port}")
        logger.info(f"Environment: {'development' if config.is_development() else 'production'}")
        logger.info(f"Debug mode: {debug}")
        
        app.run(host='0.0.0.0', port=port, debug=debug)
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        exit(1)