"""
API Routes for Visual Product Matcher
"""

from flask import Blueprint, request, jsonify, send_file, current_app
import os
import tempfile
import uuid
import time
from PIL import Image
import numpy as np
import logging
from typing import Dict, List, Optional
from contextlib import contextmanager

from services import get_clip_model, get_vector_db, get_services_status, get_s3_service
from utils.image_utils import allowed_file, process_uploaded_image
from utils.data_loader import load_sample_products, add_uploaded_image_to_database, scan_and_add_new_images

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)


@contextmanager
def temporary_file_manager(file):
    """Context manager for temporary files"""
    temp_path = None
    try:
        temp_path = process_uploaded_image(file)
        yield temp_path
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.debug(f"Cleaned up temporary file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary file {temp_path}: {e}")


def ensure_services_available():
    """Ensure services are available, raise error if not"""
    try:
        # Try to access services to trigger initialization if needed
        _ = get_services_status()
    except Exception as e:
        logger.error(f"Services not available: {e}")
        raise RuntimeError("Application services not available")


@api_bp.before_request
def check_services():
    """Check if services are available before handling requests"""
    # Skip service check for health endpoints
    if request.endpoint in ['api.health_check', 'api.get_status']:
        return
    
    try:
        ensure_services_available()
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 503

@api_bp.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload and find similar products"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format'}), 400
        
        # Get search parameters
        limit = int(request.form.get('limit', 5))
        min_score = float(request.form.get('min_score', 0.0))
        category_filter = request.form.get('category')
        
        # Get services
        clip_model = get_clip_model()
        vector_db = get_vector_db()
        
        # Process uploaded image with proper cleanup
        with temporary_file_manager(file) as temp_path:
            # Generate embedding for uploaded image
            query_embedding = clip_model.encode_image_from_path(temp_path)
            
            # Search for similar products
            results = vector_db.search_similar(
                query_embedding=query_embedding,
                limit=limit,
                score_threshold=min_score,
                category_filter=category_filter if category_filter else None
            )
            
            # Format results for frontend
            formatted_results = format_search_results(results)
            
            return jsonify({
                'success': True,
                'results': formatted_results,
                'total_found': len(formatted_results)
            })
                
    except Exception as e:
        logger.error(f"Error in upload_image: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@api_bp.route('/search-url', methods=['POST'])
def search_by_url():
    """Search for similar products using image URL"""
    try:
        data = request.get_json()
        if not data or 'image_url' not in data:
            return jsonify({'error': 'No image URL provided'}), 400
        
        image_url = data['image_url']
        limit = data.get('limit', 5)
        min_score = data.get('min_score', 0.0)
        category_filter = data.get('category')
        
        # Get services
        clip_model = get_clip_model()
        vector_db = get_vector_db()
        
        # Generate embedding for image from URL
        query_embedding = clip_model.encode_image_from_url(image_url)
        
        # Search for similar products
        results = vector_db.search_similar(
            query_embedding=query_embedding,
            limit=limit,
            score_threshold=min_score,
            category_filter=category_filter if category_filter else None
        )
        
        # Format results for frontend
        formatted_results = format_search_results(results)
        
        return jsonify({
            'success': True,
            'results': formatted_results,
            'total_found': len(formatted_results)
        })
        
    except Exception as e:
        logger.error(f"Error in search_by_url: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
@api_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products in the database"""
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        category = request.args.get('category')
        
        # Get services
        vector_db = get_vector_db()
        
        # Get products from vector database
        if category:
            # If category filter is specified, we need to search with a dummy embedding
            # and filter by category. This is a limitation of current implementation.
            all_products = vector_db.get_all_products(limit=1000)
            products = [p for p in all_products if p['metadata'].get('category') == category][:limit]
        else:
            products = vector_db.get_all_products(limit=limit)
        
        # Format for frontend
        s3_service = get_s3_service()
        formatted_products = []
        for product in products:
            # Determine image URL (S3 or local)
            if 'image_url' in product['metadata'] and product['metadata']['image_url']:
                # Use S3 URL if available
                image_url = product['metadata']['image_url']
            else:
                # Fallback to local API endpoint
                image_url = f"/api/images/{product['metadata']['image_path'].split('/')[-1]}"
            
            formatted_product = {
                'id': product['id'],
                'name': product['metadata']['name'],
                'category': product['metadata']['category'],
                'price': product['metadata']['price'],
                'description': product['metadata']['description'],
                'image_url': image_url,
                'brand': product['metadata'].get('brand', 'Unknown'),
                'rating': product['metadata'].get('rating', 0.0)
            }
            formatted_products.append(formatted_product)
        
        return jsonify({
            'success': True,
            'products': formatted_products,
            'total_count': len(formatted_products)
        })
        
    except Exception as e:
        logger.error(f"Error in get_products: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all available product categories"""
    try:
        # Get services
        vector_db = get_vector_db()
        
        products = vector_db.get_all_products(limit=1000)
        categories = list(set(p['metadata']['category'] for p in products))
        categories.sort()
        
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        logger.error(f"Error in get_categories: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Get services status
        services_status = get_services_status()
        
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '2.0.0',
            'components': services_status
        }
        
        # Test vector database connection
        try:
            vector_db = get_vector_db()
            db_info = vector_db.get_collection_info()
            health_status['components']['vector_db'] = 'healthy'
            health_status['database'] = {
                'collection': db_info.get('name', 'unknown'),
                'points_count': db_info.get('points_count', 0),
                'status': db_info.get('status', 'unknown')
            }
        except Exception as e:
            health_status['components']['vector_db'] = 'unhealthy'
            health_status['database_error'] = str(e)
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 503

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get application and database status"""
    try:
        # Get services status
        services_status = get_services_status()
        
        status = {
            'app_status': 'running',
            **services_status
        }
        
        try:
            vector_db = get_vector_db()
            db_info = vector_db.get_collection_info()
            status['database_info'] = db_info
        except Exception as e:
            status['database_error'] = str(e)
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error in get_status: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@api_bp.route('/add-product', methods=['POST'])
def add_product():
    """Add a new product with image upload"""
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image.'}), 400
        
        # Get product information from form data
        product_info = {
            'name': request.form.get('name', ''),
            'category': request.form.get('category', 'Unknown'),
            'price': request.form.get('price', 0.0),
            'description': request.form.get('description', ''),
            'brand': request.form.get('brand', 'Unknown'),
            'rating': request.form.get('rating', 0.0)
        }
        
        # Validate required fields
        if not product_info['name']:
            return jsonify({'error': 'Product name is required'}), 400
        
        # Get services
        vector_db = get_vector_db()
        clip_model = get_clip_model()
        
        # Add the product to database
        success = add_uploaded_image_to_database(vector_db, clip_model, file, product_info)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Product added successfully'
            })
        else:
            return jsonify({'error': 'Failed to add product to database'}), 500
            
    except Exception as e:
        logger.error(f"Error in add_product: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@api_bp.route('/scan-images', methods=['POST'])
def scan_images():
    """Scan images folder for new images and add them to database"""
    try:
        # Get services
        vector_db = get_vector_db()
        clip_model = get_clip_model()
        
        # Scan for new images
        new_count = scan_and_add_new_images(vector_db, clip_model)
        
        return jsonify({
            'success': True,
            'message': f'Scanned images folder and added {new_count} new products',
            'new_products_count': new_count
        })
        
    except Exception as e:
        logger.error(f"Error in scan_images: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@api_bp.route('/images/<path:filename>')
def serve_image(filename):
    """Serve product images"""
    try:
        # Construct the full path to the image
        image_path = os.path.join(current_app.root_path, 'data', 'images', filename)
        
        # Check if file exists
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404
            
        # Serve the image file
        return send_file(image_path, as_attachment=False)
        
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        return jsonify({'error': 'Error serving image'}), 500

# Helper functions
def format_search_results(results: List[Dict]) -> List[Dict]:
    """Format search results for API response"""
    formatted_results = []
    for result in results:
        # Determine image URL (S3 or local)
        if 'image_url' in result['metadata'] and result['metadata']['image_url']:
            # Use S3 URL if available
            image_url = result['metadata']['image_url']
        else:
            # Fallback to local API endpoint
            image_url = f"/api/images/{result['metadata']['image_path'].split('/')[-1]}"
            
        formatted_result = {
            'id': result['id'],
            'similarity_score': round(result['score'], 3),
            'name': result['metadata']['name'],
            'category': result['metadata']['category'],
            'price': result['metadata']['price'],
            'description': result['metadata']['description'],
            'image_url': image_url,
            'brand': result['metadata'].get('brand', 'Unknown'),
            'rating': result['metadata'].get('rating', 0.0)
        }
        formatted_results.append(formatted_result)
    return formatted_results

# Error handlers
@api_bp.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File is too large. Maximum size is 16MB.'}), 413

@api_bp.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@api_bp.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500
