#!/usr/bin/env python3
"""
Update existing Qdrant database records with S3 URLs
"""

import sys
import os
import logging

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from services.service_manager import get_service_manager, initialize_services
from services.s3_service import create_s3_service
from config.settings import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_database_with_s3_urls():
    """Update existing database records with S3 URLs"""
    
    print("🔄 Updating database records with S3 URLs...")
    
    try:
        # Get configuration
        config = get_config()
        
        # Initialize services
        service_config = {
            'qdrant_config': config.get_qdrant_config(),
            'clip_config': config.get_clip_config(),
            'S3_ENABLED': config.S3_ENABLED,
            'S3_BUCKET_NAME': config.S3_BUCKET_NAME,
            'S3_REGION': config.S3_REGION,
            'AWS_ACCESS_KEY_ID': config.AWS_ACCESS_KEY_ID,
            'AWS_SECRET_ACCESS_KEY': config.AWS_SECRET_ACCESS_KEY,
            'S3_IMAGE_PREFIX': config.S3_IMAGE_PREFIX,
            'S3_METADATA_KEY': config.S3_METADATA_KEY
        }
        
        initialize_services(service_config)
        
        # Get services
        service_manager = get_service_manager()
        vector_db = service_manager.vector_db
        s3_service = service_manager.s3_service
        
        if not s3_service:
            print("❌ S3 service not available")
            return False
        
        print(f"✅ Connected to S3 bucket: {s3_service.bucket_name}")
        
        # Get all existing products from database
        print("📊 Fetching existing products from database...")
        existing_products = vector_db.get_all_products(limit=1000)
        print(f"Found {len(existing_products)} products in database")
        
        if not existing_products:
            print("No products found in database")
            return True
        
        # Get list of images in S3
        print("📊 Fetching images from S3...")
        s3_images = s3_service.list_images()
        s3_image_map = {}
        
        # Create a mapping of filename to S3 URL
        for img in s3_images:
            filename = img['key'].split('/')[-1]  # Get filename from S3 key
            s3_image_map[filename] = img['url']
        
        print(f"Found {len(s3_images)} images in S3")
        
        # Update products with S3 URLs
        updated_count = 0
        skipped_count = 0
        
        for product in existing_products:
            try:
                product_id = product['id']
                metadata = product['metadata']
                image_path = metadata.get('image_path', '')
                
                # Check if product already has S3 URL
                if 'image_url' in metadata and metadata['image_url'].startswith('https://'):
                    print(f"⏭️  {product_id}: Already has S3 URL")
                    skipped_count += 1
                    continue
                
                # Find corresponding S3 URL
                if image_path in s3_image_map:
                    s3_url = s3_image_map[image_path]
                    
                    # Update metadata with S3 URL
                    updated_metadata = metadata.copy()
                    updated_metadata['image_url'] = s3_url
                    
                    # Update the product in database
                    success = vector_db.update_product_metadata(product_id, updated_metadata)
                    
                    if success:
                        print(f"✅ {product_id}: Updated with S3 URL")
                        updated_count += 1
                    else:
                        print(f"❌ {product_id}: Failed to update")
                else:
                    print(f"⚠️  {product_id}: No S3 image found for {image_path}")
                    
            except Exception as e:
                print(f"❌ Error updating {product_id}: {e}")
        
        print(f"\n📊 Update Summary:")
        print(f"   • Updated: {updated_count}")
        print(f"   • Skipped: {skipped_count}")
        print(f"   • Total: {len(existing_products)}")
        
        if updated_count > 0:
            print(f"\n🎉 Successfully updated {updated_count} products with S3 URLs!")
            return True
        else:
            print(f"\n⚠️  No products were updated")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_database_urls():
    """Verify that database has correct S3 URLs"""
    
    print("\n🔍 Verifying database URLs...")
    
    try:
        # Get configuration
        config = get_config()
        
        # Initialize services
        service_config = {
            'qdrant_config': config.get_qdrant_config(),
            'clip_config': config.get_clip_config(),
            'S3_ENABLED': config.S3_ENABLED,
            'S3_BUCKET_NAME': config.S3_BUCKET_NAME,
            'S3_REGION': config.S3_REGION,
            'AWS_ACCESS_KEY_ID': config.AWS_ACCESS_KEY_ID,
            'AWS_SECRET_ACCESS_KEY': config.AWS_SECRET_ACCESS_KEY,
            'S3_IMAGE_PREFIX': config.S3_IMAGE_PREFIX,
            'S3_METADATA_KEY': config.S3_METADATA_KEY
        }
        
        initialize_services(service_config)
        
        # Get services
        service_manager = get_service_manager()
        vector_db = service_manager.vector_db
        
        # Get sample products
        products = vector_db.get_all_products(limit=5)
        
        print(f"\n📋 Sample of database records:")
        for i, product in enumerate(products[:3]):
            print(f"\n{i+1}. Product ID: {product['id']}")
            print(f"   Name: {product['metadata'].get('name', 'N/A')}")
            print(f"   Image Path: {product['metadata'].get('image_path', 'N/A')}")
            print(f"   Image URL: {product['metadata'].get('image_url', 'Not set')}")
        
        # Count products with S3 URLs
        s3_url_count = 0
        local_path_count = 0
        
        for product in vector_db.get_all_products(limit=1000):
            image_url = product['metadata'].get('image_url', '')
            if image_url.startswith('https://'):
                s3_url_count += 1
            else:
                local_path_count += 1
        
        print(f"\n📊 URL Status:")
        print(f"   • Products with S3 URLs: {s3_url_count}")
        print(f"   • Products with local paths: {local_path_count}")
        
        return s3_url_count > 0
        
    except Exception as e:
        print(f"❌ Error verifying URLs: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Database S3 URL Updater")
    print("=" * 40)
    
    # First, verify current state
    verify_database_urls()
    
    # Ask for confirmation
    response = input("\nDo you want to update the database with S3 URLs? [y/N]: ")
    if response.lower() != 'y':
        print("Update cancelled.")
        sys.exit(0)
    
    # Update database
    if update_database_with_s3_urls():
        print("\n✨ Update completed successfully!")
        
        # Verify results
        verify_database_urls()
        
        print("\n🎉 Next steps:")
        print("1. Restart your backend server")
        print("2. Test your frontend - images should now be visible!")
        print("3. All image URLs are now served from S3")
    else:
        print("\n❌ Update failed")
        print("Please check the logs above for details")
