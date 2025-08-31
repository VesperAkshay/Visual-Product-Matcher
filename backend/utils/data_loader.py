"""
Data loading utilities for real product data with S3 support
"""

import os
import json
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
from PIL import Image

logger = logging.getLogger(__name__)

def load_real_products(vector_db, clip_model, s3_service=None):
    """Load and process real products from images folder and JSON data"""
    
    if s3_service:
        return load_products_from_s3(vector_db, clip_model, s3_service)
    else:
        return load_products_from_local(vector_db, clip_model)


def load_products_from_s3(vector_db, clip_model, s3_service):
    """Load products from S3 storage"""
    logger.info("Loading products from S3...")
    
    # Download metadata from S3
    metadata = s3_service.download_metadata()
    if not metadata:
        logger.warning("No metadata found in S3, using local fallback")
        return load_products_from_local(vector_db, clip_model)
    
    # Get existing products from database to avoid duplicates
    existing_products = vector_db.get_all_products(limit=1000)
    existing_ids = {p['id'] for p in existing_products}
    
    # Process products from S3 metadata
    batch_products = []
    for product in metadata:
        try:
            product_id = product['id']
            
            # Skip if already exists in database
            if product_id in existing_ids:
                continue
            
            # Get S3 image URL
            s3_key = f"{s3_service.image_prefix}{product['image_path']}"
            image_url = s3_service.get_image_url(s3_key)
            
            # Generate embedding from S3 image URL
            embedding = clip_model.encode_image_from_url(image_url)
            
            # Prepare metadata with S3 URL
            metadata_dict = {
                'name': product['name'],
                'category': product['category'],
                'price': product['price'],
                'description': product['description'],
                'image_path': product['image_path'],  # Keep original filename
                'image_url': image_url,  # Add S3 URL
                'brand': product.get('brand', 'Unknown'),
                'rating': product.get('rating', 0.0)
            }
            
            batch_products.append((product_id, embedding, metadata_dict))
            
        except Exception as e:
            logger.error(f"Error processing S3 product {product['id']}: {str(e)}")
    
    # Add products to database in batch
    if batch_products:
        added_count = vector_db.add_products_batch(batch_products)
        logger.info(f"Added {added_count} new products from S3 to vector database")
    else:
        logger.info("No new products to add from S3 - all existing products are already in database")


def load_products_from_local(vector_db, clip_model):
    """Load and process real products from local images folder and JSON data"""
    
    # Load product metadata from JSON file
    products_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'images')
    
    if not os.path.exists(products_file):
        logger.warning(f"Products JSON file not found: {products_file}")
        return
    
    if not os.path.exists(images_dir):
        logger.warning(f"Images directory not found: {images_dir}")
        return
    
    # Load existing product data
    with open(products_file, 'r') as f:
        products_data = json.load(f)
    
    logger.info(f"Processing {len(products_data)} real products from local storage...")
    
    # Get existing products from database to avoid duplicates
    existing_products = vector_db.get_all_products(limit=1000)
    existing_ids = {p['id'] for p in existing_products}
    
    # Process products and add to vector database
    batch_products = []
    for product in products_data:
        try:
            product_id = product['id']
            
            # Skip if already exists in database
            if product_id in existing_ids:
                continue
            
            # Look for image file (support multiple formats)
            image_path = find_product_image(images_dir, product_id)
            if not image_path:
                logger.warning(f"No image found for product {product_id}")
                continue
            
            # Generate embedding for product image
            embedding = clip_model.encode_image_from_path(image_path)
            
            # Prepare metadata (local storage format)
            metadata = {
                'name': product['name'],
                'category': product['category'],
                'price': product['price'],
                'description': product['description'],
                'image_path': os.path.basename(image_path),  # Store just filename
                'brand': product.get('brand', 'Unknown'),
                'rating': product.get('rating', 0.0)
            }
            
            batch_products.append((product_id, embedding, metadata))
            
        except Exception as e:
            logger.error(f"Error processing product {product['id']}: {str(e)}")
    
    # Add products to database in batch
    if batch_products:
        added_count = vector_db.add_products_batch(batch_products)
        logger.info(f"Added {added_count} new products to vector database")
    else:
        logger.info("No new products to add - all existing products are already in database")

def find_product_image(images_dir: str, product_id: str) -> Optional[str]:
    """Find image file for a product supporting multiple formats"""
    supported_formats = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
    
    for ext in supported_formats:
        image_path = os.path.join(images_dir, f"{product_id}{ext}")
        if os.path.exists(image_path):
            return image_path
    
    return None

def scan_and_add_new_images(vector_db, clip_model, s3_service=None):
    """Scan images folder for new images and add them to database"""
    
    if s3_service:
        return sync_new_images_to_s3(vector_db, clip_model, s3_service)
    
    # Fallback to local scanning
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'images')
    
    if not os.path.exists(images_dir):
        logger.warning(f"Images directory not found: {images_dir}")
        return
    
    # Get existing products from database
    existing_products = vector_db.get_all_products(limit=1000)
    existing_ids = {p['id'] for p in existing_products}
    
    # Scan for image files
    supported_formats = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
    new_products = []
    
    for filename in os.listdir(images_dir):
        if not any(filename.lower().endswith(ext) for ext in supported_formats):
            continue
        
        # Extract product ID from filename
        product_id = os.path.splitext(filename)[0]
        
        # Skip if already exists
        if product_id in existing_ids:
            continue
        
        try:
            image_path = os.path.join(images_dir, filename)
            
            # Generate embedding
            embedding = clip_model.encode_image_from_path(image_path)
            
            # Create basic metadata (can be updated later via frontend)
            metadata = {
                'name': f"Product {product_id}",
                'category': 'Unknown',
                'price': 0.0,
                'description': f"Product imported from image {filename}",
                'image_path': filename,
                'brand': 'Unknown',
                'rating': 0.0
            }
            
            new_products.append((product_id, embedding, metadata))
            
        except Exception as e:
            logger.error(f"Error processing image {filename}: {str(e)}")
    
    # Add new products to database
    if new_products:
        added_count = vector_db.add_products_batch(new_products)
        logger.info(f"Added {added_count} new products from images folder")
        
        # Update JSON file with new products
        update_products_json_with_new_images(new_products)
    
    return len(new_products)

def update_products_json_with_new_images(new_products: List):
    """Update products.json with newly discovered images"""
    products_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')
    
    try:
        # Load existing products
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                existing_products = json.load(f)
        else:
            existing_products = []
        
        # Add new products
        for product_id, embedding, metadata in new_products:
            product_data = {
                'id': product_id,
                'name': metadata['name'],
                'category': metadata['category'],
                'price': metadata['price'],
                'description': metadata['description'],
                'image_path': metadata['image_path'],
                'brand': metadata['brand'],
                'rating': metadata['rating']
            }
            existing_products.append(product_data)
        
        # Save updated products
        with open(products_file, 'w') as f:
            json.dump(existing_products, f, indent=2)
        
        logger.info(f"Updated products.json with {len(new_products)} new products")
        
    except Exception as e:
        logger.error(f"Error updating products.json: {str(e)}")

def add_uploaded_image_to_database(vector_db, clip_model, uploaded_file, product_info: Dict) -> bool:
    """Add an uploaded image to the database with provided product information"""
    try:
        # Generate new product ID
        existing_products = vector_db.get_all_products(limit=1000)
        existing_numbers = []
        for p in existing_products:
            if p['id'].startswith('product_'):
                try:
                    num = int(p['id'].split('_')[1])
                    existing_numbers.append(num)
                except:
                    pass
        
        next_number = max(existing_numbers, default=0) + 1
        product_id = f"product_{next_number:03d}"
        
        # Save uploaded file
        images_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        # Determine file extension
        filename = uploaded_file.filename
        if not filename:
            filename = f"{product_id}.jpg"
        
        file_ext = os.path.splitext(filename)[1].lower()
        if not file_ext:
            file_ext = '.jpg'
        
        final_filename = f"{product_id}{file_ext}"
        image_path = os.path.join(images_dir, final_filename)
        
        # Save the uploaded file
        uploaded_file.save(image_path)
        
        # Generate embedding
        embedding = clip_model.encode_image_from_path(image_path)
        
        # Prepare metadata
        metadata = {
            'name': product_info.get('name', f'Product {product_id}'),
            'category': product_info.get('category', 'Unknown'),
            'price': float(product_info.get('price', 0.0)),
            'description': product_info.get('description', ''),
            'image_path': final_filename,
            'brand': product_info.get('brand', 'Unknown'),
            'rating': float(product_info.get('rating', 0.0))
        }
        
        # Add to vector database
        success = vector_db.add_product(product_id, embedding, metadata)
        
        if success:
            # Update products.json
            products_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')
            
            if os.path.exists(products_file):
                with open(products_file, 'r') as f:
                    products_data = json.load(f)
            else:
                products_data = []
            
            # Add new product
            product_data = {
                'id': product_id,
                'name': metadata['name'],
                'category': metadata['category'],
                'price': metadata['price'],
                'description': metadata['description'],
                'image_path': metadata['image_path'],
                'brand': metadata['brand'],
                'rating': metadata['rating']
            }
            products_data.append(product_data)
            
            # Save updated products
            with open(products_file, 'w') as f:
                json.dump(products_data, f, indent=2)
            
            logger.info(f"Successfully added new product {product_id} from uploaded image")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error adding uploaded image to database: {str(e)}")
        return False

# Legacy function for compatibility (now just calls load_real_products)
def load_sample_products(vector_db, clip_model, s3_service=None):
    """Legacy function - now loads real products instead of sample data"""
    logger.info("Loading real products instead of sample data...")
    load_real_products(vector_db, clip_model, s3_service)
    # Also scan for any new images in the folder
    scan_and_add_new_images(vector_db, clip_model, s3_service)


def migrate_local_to_s3(s3_service):
    """
    Migrate local images and metadata to S3
    
    Args:
        s3_service: Initialized S3 service
        
    Returns:
        Tuple[int, int]: (successful_uploads, failed_uploads)
    """
    if not s3_service:
        logger.error("S3 service not available for migration")
        return 0, 0
    
    logger.info("Starting migration from local storage to S3...")
    
    # Load local metadata
    products_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'images')
    
    if not os.path.exists(products_file):
        logger.error(f"Products JSON file not found: {products_file}")
        return 0, 0
    
    if not os.path.exists(images_dir):
        logger.error(f"Images directory not found: {images_dir}")
        return 0, 0
    
    with open(products_file, 'r') as f:
        products_data = json.load(f)
    
    successful_uploads = 0
    failed_uploads = 0
    
    # Upload images to S3
    for product in products_data:
        try:
            product_id = product['id']
            image_filename = product['image_path']
            
            # Find local image file
            local_image_path = find_product_image(images_dir, product_id)
            if not local_image_path:
                logger.warning(f"No local image found for product {product_id}")
                failed_uploads += 1
                continue
            
            # Upload to S3
            s3_key = f"{s3_service.image_prefix}{image_filename}"
            s3_url = s3_service.upload_image(
                local_path=local_image_path,
                s3_key=s3_key,
                metadata={
                    'product_id': product_id,
                    'name': product['name'],
                    'category': product['category']
                }
            )
            
            if s3_url:
                logger.info(f"Uploaded {product_id} to S3: {s3_url}")
                successful_uploads += 1
            else:
                logger.error(f"Failed to upload {product_id} to S3")
                failed_uploads += 1
                
        except Exception as e:
            logger.error(f"Error migrating product {product.get('id', 'unknown')}: {e}")
            failed_uploads += 1
    
    # Upload metadata to S3
    try:
        if s3_service.upload_metadata(products_data):
            logger.info("Successfully uploaded metadata to S3")
        else:
            logger.error("Failed to upload metadata to S3")
    except Exception as e:
        logger.error(f"Error uploading metadata to S3: {e}")
    
    logger.info(f"Migration completed: {successful_uploads} successful, {failed_uploads} failed")
    return successful_uploads, failed_uploads


def sync_new_images_to_s3(vector_db, clip_model, s3_service):
    """
    Scan local images and sync new ones to S3
    
    Args:
        vector_db: Vector database instance
        clip_model: CLIP model instance
        s3_service: S3 service instance
    """
    if not s3_service:
        logger.info("S3 service not available, skipping sync")
        return
    
    logger.info("Syncing new local images to S3...")
    
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'images')
    if not os.path.exists(images_dir):
        logger.warning(f"Images directory not found: {images_dir}")
        return
    
    # Get existing products to find new ones
    existing_products = vector_db.get_all_products(limit=1000)
    existing_ids = {p['id'] for p in existing_products}
    
    # Scan for new image files
    supported_formats = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
    new_products = []
    
    for filename in os.listdir(images_dir):
        name, ext = os.path.splitext(filename)
        if ext.lower() in supported_formats:
            # Extract product ID from filename
            if name.startswith('product_'):
                product_id = name
            else:
                product_id = name
            
            if product_id not in existing_ids:
                image_path = os.path.join(images_dir, filename)
                
                try:
                    # Upload to S3
                    s3_key = f"{s3_service.image_prefix}{filename}"
                    s3_url = s3_service.upload_image(
                        local_path=image_path,
                        s3_key=s3_key,
                        metadata={'product_id': product_id}
                    )
                    
                    if s3_url:
                        # Generate embedding and add to database
                        embedding = clip_model.encode_image_from_path(image_path)
                        
                        metadata = {
                            'name': f"Product {product_id}",
                            'category': 'Unknown',
                            'price': 0.0,
                            'description': f"Auto-generated entry for {filename}",
                            'image_path': filename,
                            'image_url': s3_url,
                            'brand': 'Unknown',
                            'rating': 0.0
                        }
                        
                        new_products.append((product_id, embedding, metadata))
                        logger.info(f"Synced new image {filename} to S3: {s3_url}")
                        
                except Exception as e:
                    logger.error(f"Error syncing {filename} to S3: {e}")
    
    # Add new products to database
    if new_products:
        added_count = vector_db.add_products_batch(new_products)
        logger.info(f"Added {added_count} new products from S3 sync")
    else:
        logger.info("No new images found to sync to S3")
