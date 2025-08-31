"""
AWS S3 service for handling cloud storage of product images
"""

import os
import boto3
import logging
from typing import Optional, Dict, List
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
import mimetypes
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class S3Service:
    """Service for managing product images in AWS S3"""
    
    def __init__(self, bucket_name: str, region: str = 'us-east-1', 
                 access_key: Optional[str] = None, secret_key: Optional[str] = None,
                 image_prefix: str = 'images/'):
        """
        Initialize S3 service
        
        Args:
            bucket_name: S3 bucket name for storing images
            region: AWS region
            access_key: AWS access key (optional, can use IAM roles)
            secret_key: AWS secret key (optional, can use IAM roles)
            image_prefix: Prefix for image objects in S3
        """
        self.bucket_name = bucket_name
        self.region = region
        self.image_prefix = image_prefix
        
        # Configure boto3 client
        config = Config(
            region_name=region,
            retries={'max_attempts': 3, 'mode': 'standard'},
            max_pool_connections=50
        )
        
        try:
            if access_key and secret_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    config=config
                )
            else:
                # Use default credentials (IAM roles, environment variables, etc.)
                self.s3_client = boto3.client('s3', config=config)
            
            # Test connection
            self._test_connection()
            logger.info(f"S3 service initialized for bucket: {bucket_name}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure AWS credentials.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 service: {e}")
            raise
    
    def _test_connection(self):
        """Test S3 connection and bucket access"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.warning(f"Bucket {self.bucket_name} does not exist. Attempting to create...")
                self._create_bucket()
            else:
                logger.error(f"Cannot access bucket {self.bucket_name}: {e}")
                raise
    
    def _create_bucket(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            if self.region == 'us-east-1':
                # For us-east-1, don't specify LocationConstraint
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            
            # Configure bucket for public read access to images
            self._configure_bucket_policy()
            logger.info(f"Created S3 bucket: {self.bucket_name}")
            
        except ClientError as e:
            logger.error(f"Failed to create bucket {self.bucket_name}: {e}")
            raise
    
    def _configure_bucket_policy(self):
        """Configure bucket policy for public read access to images"""
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                                            "Resource": f"arn:aws:s3:::{self.bucket_name}/{self.image_prefix}*"
                }
            ]
        }
        
        try:
            self.s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=str(bucket_policy).replace("'", '"')
            )
            logger.info("Configured bucket policy for public read access")
        except ClientError as e:
            logger.warning(f"Could not set bucket policy: {e}")
    
    def upload_image(self, local_path: str, s3_key: str, 
                    metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Upload an image to S3
        
        Args:
            local_path: Local file path
            s3_key: S3 object key (path in bucket)
            metadata: Optional metadata to attach to object
            
        Returns:
            S3 URL if successful, None if failed
        """
        try:
            # Determine content type
            content_type, _ = mimetypes.guess_type(local_path)
            if not content_type:
                content_type = 'image/jpeg'
            
            # Prepare extra arguments for upload
            extra_args = {
                'ContentType': content_type,
                'CacheControl': 'max-age=31536000'  # Cache for 1 year
            }
            
            if metadata:
                extra_args['Metadata'] = {k: str(v) for k, v in metadata.items()}
            
            # Upload file
            with open(local_path, 'rb') as file:
                self.s3_client.upload_fileobj(
                    file, 
                    self.bucket_name, 
                    s3_key, 
                    ExtraArgs=extra_args
                )
            
            # Return public URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            logger.debug(f"Uploaded {local_path} to {url}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload {local_path} to S3: {e}")
            return None
    
    def download_image(self, s3_key: str, local_path: str) -> bool:
        """
        Download an image from S3
        
        Args:
            s3_key: S3 object key
            local_path: Local file path to save to
            
        Returns:
            True if successful, False if failed
        """
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.debug(f"Downloaded {s3_key} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {s3_key} from S3: {e}")
            return False
    
    def get_image_url(self, s3_key: str) -> str:
        """Get public URL for an S3 object"""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
    
    def delete_image(self, s3_key: str) -> bool:
        """
        Delete an image from S3
        
        Args:
            s3_key: S3 object key to delete
            
        Returns:
            True if successful, False if failed
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.debug(f"Deleted {s3_key} from S3")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {s3_key} from S3: {e}")
            return False
    
    def list_images(self, prefix: Optional[str] = None) -> List[Dict]:
        """
        List images in S3 bucket
        
        Args:
            prefix: S3 key prefix to filter objects (defaults to image_prefix)
            
        Returns:
            List of image objects with metadata
        """
        if prefix is None:
            prefix = self.image_prefix
            
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            images = []
            for obj in response.get('Contents', []):
                images.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'url': self.get_image_url(obj['Key'])
                })
            
            return images
        except Exception as e:
            logger.error(f"Failed to list images from S3: {e}")
            return []
    
    def upload_metadata(self, metadata: Dict, s3_key: str = "metadata/products.json") -> bool:
        """
        Upload product metadata as JSON to S3
        
        Args:
            metadata: Product metadata dictionary
            s3_key: S3 key for metadata file
            
        Returns:
            True if successful, False if failed
        """
        try:
            import json
            json_data = json.dumps(metadata, indent=2)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data,
                ContentType='application/json'
            )
            
            logger.info(f"Uploaded metadata to {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload metadata to S3: {e}")
            return False
    
    def download_metadata(self, s3_key: str = "metadata/products.json") -> Optional[Dict]:
        """
        Download product metadata from S3
        
        Args:
            s3_key: S3 key for metadata file
            
        Returns:
            Metadata dictionary if successful, None if failed
        """
        try:
            import json
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.info("No metadata file found in S3")
            else:
                logger.error(f"Failed to download metadata from S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to parse metadata from S3: {e}")
            return None


def create_s3_service(config: Dict) -> Optional[S3Service]:
    """
    Factory function to create S3 service from configuration
    
    Args:
        config: Configuration dictionary with S3 settings
        
    Returns:
        S3Service instance or None if disabled/failed
    """
    if not config.get('S3_ENABLED', False):
        logger.info("S3 storage is disabled")
        return None
    
    try:
        return S3Service(
            bucket_name=config['S3_BUCKET_NAME'],
            region=config.get('S3_REGION', 'us-east-1'),
            access_key=config.get('AWS_ACCESS_KEY_ID'),
            secret_key=config.get('AWS_SECRET_ACCESS_KEY'),
            image_prefix=config.get('S3_IMAGE_PREFIX', 'images/')
        )
    except Exception as e:
        logger.error(f"Failed to create S3 service: {e}")
        return None
