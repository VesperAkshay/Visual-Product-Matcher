# AWS S3 Integration Guide

## Overview

This guide explains how to integrate AWS S3 cloud storage with the Visual Product Matcher application. With S3 integration, your product images and metadata will be stored in the cloud, making your application production-ready and scalable.

## Benefits of S3 Integration

1. **Scalability**: Store unlimited images without local storage constraints
2. **Performance**: Fast image delivery via AWS CloudFront CDN
3. **Reliability**: 99.999999999% (11 9's) durability for your images
4. **Cost-effective**: Pay only for what you use
5. **Global availability**: Serve images worldwide with low latency

## Prerequisites

1. AWS Account
2. AWS CLI installed (optional but recommended)
3. Appropriate AWS credentials (Access Key or IAM role)

## Setup Instructions

### 1. Create AWS S3 Bucket

**Option A: Using AWS Console**
1. Log into AWS Console
2. Navigate to S3 service
3. Click "Create bucket"
4. Enter bucket name (e.g., `your-company-product-images`)
5. Choose region closest to your users
6. Configure public access settings (see security section below)
7. Click "Create bucket"

**Option B: Using AWS CLI**
```bash
aws s3 mb s3://your-company-product-images --region us-east-1
```

### 2. Configure AWS Credentials

**Option A: Using Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

**Option B: Using AWS CLI**
```bash
aws configure
```

**Option C: Using IAM Roles (Recommended for production)**
- Attach appropriate IAM role to your EC2 instance or container

### 3. Configure Application

Create a `.env` file in the backend directory with S3 settings:

```env
# Enable S3 storage
S3_ENABLED=true

# S3 Configuration
S3_BUCKET_NAME=your-company-product-images
S3_REGION=us-east-1

# AWS Credentials (if not using IAM roles)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Storage Configuration
S3_IMAGE_PREFIX=images/
S3_METADATA_KEY=metadata/products.json

# Optional: CloudFront CDN URL
S3_CDN_URL=https://your-cloudfront-distribution.cloudfront.net
```

### 4. Install Dependencies

```bash
cd backend
pip install boto3 botocore
```

### 5. Migrate Existing Data (if any)

If you have existing local images, use the migration script:

```bash
cd backend
python migrate_to_s3.py --check-only  # Check prerequisites
python migrate_to_s3.py --dry-run     # See what would be migrated
python migrate_to_s3.py --force       # Perform actual migration
```

### 6. Start Application

```bash
cd backend
python app.py
```

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `S3_ENABLED` | Yes | `false` | Enable/disable S3 storage |
| `S3_BUCKET_NAME` | Yes* | - | S3 bucket name for images |
| `S3_REGION` | No | `us-east-1` | AWS region |
| `AWS_ACCESS_KEY_ID` | No** | - | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | No** | - | AWS secret key |
| `S3_IMAGE_PREFIX` | No | `images/` | Prefix for image objects |
| `S3_METADATA_KEY` | No | `metadata/products.json` | S3 key for metadata |
| `S3_CDN_URL` | No | - | CloudFront CDN URL |

*Required when S3_ENABLED=true  
**Not required if using IAM roles

### Bucket Structure

Your S3 bucket will be organized as follows:
```
your-bucket/
├── images/
│   ├── product_001.png
│   ├── product_002.jpg
│   └── ...
└── metadata/
    └── products.json
```

## Security Considerations

### Bucket Permissions

For public image access, configure your bucket policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/images/*"
        }
    ]
}
```

### IAM Policy

For application access, create an IAM policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

## Performance Optimization

### CloudFront CDN

For global performance, set up CloudFront:

1. Create CloudFront distribution
2. Set S3 bucket as origin
3. Configure caching rules
4. Update `S3_CDN_URL` in configuration

### Image Optimization

Consider implementing image optimization:
- Automatic resizing for different screen sizes
- WebP format conversion for better compression
- Lazy loading for better page performance

## API Usage

### Upload New Images

When S3 is enabled, uploaded images are automatically stored in S3:

```bash
curl -X POST http://localhost:5001/api/upload \
  -F "image=@path/to/image.jpg" \
  -F "name=Product Name" \
  -F "category=Electronics"
```

### Image URLs

Response will include S3 URLs:
```json
{
  "success": true,
  "product": {
    "id": "product_123",
    "name": "Product Name",
    "image_url": "https://your-bucket.s3.amazonaws.com/images/product_123.jpg"
  }
}
```

## Troubleshooting

### Common Issues

1. **Access Denied Error**
   - Check AWS credentials
   - Verify IAM permissions
   - Ensure bucket exists

2. **Images Not Loading**
   - Check bucket policy for public read access
   - Verify S3_CDN_URL if using CloudFront
   - Check CORS configuration

3. **Migration Fails**
   - Run with `--check-only` flag first
   - Verify local data exists
   - Check AWS credentials and permissions

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

### Health Check

Check service status:
```bash
curl http://localhost:5001/api/health
```

## Cost Estimation

### S3 Storage Costs (US East 1)
- First 50 TB: $0.023 per GB/month
- Example: 1000 images (10 MB each) = ~$0.23/month

### S3 Request Costs
- PUT requests: $0.0005 per 1,000 requests
- GET requests: $0.0004 per 1,000 requests

### CloudFront Costs
- First 1 TB: $0.085 per GB for data transfer

## Migration from Local Storage

The migration process:
1. Uploads all local images to S3
2. Updates metadata with S3 URLs
3. Updates database records
4. Preserves all existing product data

No data is lost during migration, and you can keep local files as backup.

## Production Deployment

For production environments:
1. Use IAM roles instead of access keys
2. Enable CloudFront CDN
3. Set up monitoring and logging
4. Configure backup and versioning
5. Use encrypted storage (S3-SSE)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review AWS CloudWatch logs
3. Enable debug logging for detailed error information
