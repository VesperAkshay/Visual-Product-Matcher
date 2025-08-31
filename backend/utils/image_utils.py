"""
Image processing utilities
"""

import os
import tempfile
import uuid
from PIL import Image
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False
    
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def process_uploaded_image(file):
    """Process uploaded image file and return temporary path"""
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    temp_filename = f"temp_{uuid.uuid4()}.jpg"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    try:
        # Convert and save image
        image = Image.open(file.stream).convert('RGB')
        image.save(temp_path, 'JPEG', quality=85)
        logger.info(f"Processed uploaded image: {temp_path}")
        return temp_path
    except Exception as e:
        logger.error(f"Error processing uploaded image: {str(e)}")
        raise

def validate_image_url(url):
    """Validate if URL is a valid image URL"""
    if not url:
        return False
    
    # Basic URL validation
    url = url.lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    # Check if URL ends with valid image extension or contains image keywords
    return any(ext in url for ext in valid_extensions) or 'image' in url

def resize_image_if_needed(image_path, max_size=(1024, 1024)):
    """Resize image if it's too large"""
    try:
        with Image.open(image_path) as img:
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(image_path, 'JPEG', quality=85)
                logger.info(f"Resized image to {img.size}")
    except Exception as e:
        logger.error(f"Error resizing image: {str(e)}")
        raise
