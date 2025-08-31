#!/usr/bin/env python3
"""
Migration script to move local images and metadata to AWS S3
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from config.settings import get_config
from services.s3_service import create_s3_service
from utils.data_loader import migrate_local_to_s3

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_prerequisites():
    """Check if all prerequisites are met for migration"""
    logger.info("Checking migration prerequisites...")
    
    # Check if local data exists
    data_dir = os.path.join(backend_dir, 'data')
    images_dir = os.path.join(data_dir, 'images')
    products_file = os.path.join(data_dir, 'products.json')
    
    if not os.path.exists(images_dir):
        logger.error(f"Images directory not found: {images_dir}")
        return False
    
    if not os.path.exists(products_file):
        logger.error(f"Products metadata file not found: {products_file}")
        return False
    
    # Count images
    image_count = len([f for f in os.listdir(images_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))])
    
    logger.info(f"Found {image_count} images to migrate")
    
    if image_count == 0:
        logger.warning("No images found to migrate")
        return False
    
    return True


def check_s3_configuration():
    """Check if S3 is properly configured"""
    logger.info("Checking S3 configuration...")
    
    config = get_config()
    
    if not config.S3_ENABLED:
        logger.error("S3 is not enabled. Set S3_ENABLED=true in your environment")
        return False
    
    if not config.S3_BUCKET_NAME:
        logger.error("S3_BUCKET_NAME is not set")
        return False
    
    logger.info(f"S3 bucket: {config.S3_BUCKET_NAME}")
    logger.info(f"S3 region: {config.S3_REGION}")
    
    return True


def test_s3_connection(s3_service):
    """Test S3 connection and permissions"""
    logger.info("Testing S3 connection...")
    
    try:
        # Try to list objects in bucket (this will create bucket if it doesn't exist)
        images = s3_service.list_images()
        logger.info(f"S3 connection successful. Found {len(images)} existing images in bucket")
        return True
    except Exception as e:
        logger.error(f"S3 connection failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Migrate local images and metadata to AWS S3')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be migrated without actually doing it')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompts')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check prerequisites and configuration')
    
    args = parser.parse_args()
    
    print("🚀 Visual Product Matcher - S3 Migration Tool")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    # Check S3 configuration
    if not check_s3_configuration():
        logger.error("S3 configuration invalid. Please set the required environment variables.")
        sys.exit(1)
    
    # Create S3 service
    try:
        config = get_config()
        config_dict = {
            'S3_ENABLED': config.S3_ENABLED,
            'S3_BUCKET_NAME': config.S3_BUCKET_NAME,
            'S3_REGION': config.S3_REGION,
            'AWS_ACCESS_KEY_ID': config.AWS_ACCESS_KEY_ID,
            'AWS_SECRET_ACCESS_KEY': config.AWS_SECRET_ACCESS_KEY,
            'S3_IMAGE_PREFIX': config.S3_IMAGE_PREFIX,
            'S3_METADATA_KEY': config.S3_METADATA_KEY
        }
        
        s3_service = create_s3_service(config_dict)
        if not s3_service:
            logger.error("Failed to create S3 service")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to initialize S3 service: {e}")
        sys.exit(1)
    
    # Test S3 connection
    if not test_s3_connection(s3_service):
        logger.error("S3 connection test failed")
        sys.exit(1)
    
    if args.check_only:
        print("\n✅ All checks passed! Ready for migration.")
        return
    
    # Show migration summary
    print("\n📋 Migration Summary:")
    print(f"   • Source: Local storage ({backend_dir}/data/)")
    print(f"   • Destination: S3 bucket '{config.S3_BUCKET_NAME}'")
    print(f"   • Region: {config.S3_REGION}")
    print(f"   • Image prefix: {config.S3_IMAGE_PREFIX}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No actual changes will be made")
    
    # Confirmation
    if not args.force and not args.dry_run:
        response = input("\nContinue with migration? [y/N]: ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return
    
    # Perform migration
    if args.dry_run:
        print("\n🔍 Dry run completed - use --force to perform actual migration")
    else:
        print("\n🔄 Starting migration...")
        successful, failed = migrate_local_to_s3(s3_service)
        
        print("\n" + "=" * 50)
        print("🎉 Migration completed!")
        print(f"   • Successfully migrated: {successful} images")
        print(f"   • Failed migrations: {failed} images")
        
        if successful > 0:
            print("\n✨ Next steps:")
            print("   1. Update your application configuration to use S3:")
            print("      Set S3_ENABLED=true in your environment")
            print("   2. Restart your backend server")
            print("   3. Verify that images are loading from S3 URLs")
            print("   4. (Optional) You can now remove local images to save space")
        
        if failed > 0:
            print(f"\n⚠️  {failed} images failed to migrate. Check the logs above for details.")


if __name__ == "__main__":
    main()
