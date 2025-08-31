#!/usr/bin/env python3
"""
Fix S3 bucket policy for public read access to images
"""

import sys
import os
import json

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from services.s3_service import create_s3_service
from config.settings import get_config

def fix_bucket_policy():
    """Fix bucket policy to allow public read access to images"""
    
    print("🔧 Fixing S3 bucket policy for public image access...")
    
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
            print("❌ Failed to create S3 service")
            return False
        
        # Create bucket policy for public read access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{s3_service.bucket_name}/{s3_service.image_prefix}*"
                }
            ]
        }
        
        # Apply the bucket policy
        try:
            s3_service.s3_client.put_bucket_policy(
                Bucket=s3_service.bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            print(f"✅ Bucket policy applied successfully to {s3_service.bucket_name}")
            print(f"   Images under '{s3_service.image_prefix}' are now publicly accessible")
            
            # Test access to a sample image
            images = s3_service.list_images()
            if images:
                test_url = images[0]['url']
                print(f"\n🔍 Testing image access: {test_url}")
                
                import requests
                try:
                    response = requests.head(test_url, timeout=5)
                    if response.status_code == 200:
                        print("✅ Images are now publicly accessible!")
                    else:
                        print(f"⚠️  Status code: {response.status_code}")
                except Exception as e:
                    print(f"⚠️  Could not test URL: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply bucket policy: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_current_policy():
    """Check current bucket policy"""
    
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
            print("❌ Failed to create S3 service")
            return
        
        try:
            response = s3_service.s3_client.get_bucket_policy(Bucket=s3_service.bucket_name)
            policy = json.loads(response['Policy'])
            print("📋 Current bucket policy:")
            print(json.dumps(policy, indent=2))
        except s3_service.s3_client.exceptions.NoSuchBucketPolicy:
            print("📋 No bucket policy currently set")
        except Exception as e:
            print(f"❌ Error getting bucket policy: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 S3 Bucket Policy Fixer")
    print("=" * 40)
    
    # Check current policy
    print("\n1. Checking current bucket policy...")
    check_current_policy()
    
    # Fix policy
    print("\n2. Applying public read policy...")
    if fix_bucket_policy():
        print("\n🎉 Bucket policy fixed successfully!")
        print("\nNext steps:")
        print("1. Restart your backend server")
        print("2. Test image loading in your frontend")
        print("3. Images should now be visible!")
    else:
        print("\n❌ Failed to fix bucket policy")
        print("Please check your AWS credentials and bucket permissions")
