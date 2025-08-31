#!/usr/bin/env python3
"""
Script to fetch real product data from multiple APIs and convert to our format
Now supports 100+ products from various sources
"""

import requests
import json
import os
from PIL import Image
import time
import random

def fetch_fakestore_products():
    """Fetch products from FakeStore API"""
    print("🔄 Fetching products from FakeStore API...")
    
    try:
        response = requests.get('https://fakestoreapi.com/products')
        response.raise_for_status()
        products = response.json()
        
        print(f"✅ Fetched {len(products)} products from FakeStore API")
        return products
    except Exception as e:
        print(f"❌ Error fetching from FakeStore API: {e}")
        return []

def fetch_dummyjson_products():
    """Fetch products from DummyJSON API"""
    print("🔄 Fetching products from DummyJSON API...")
    
    all_products = []
    try:
        # DummyJSON has 100 products, fetch in batches
        for skip in range(0, 100, 30):
            response = requests.get(f'https://dummyjson.com/products?limit=30&skip={skip}')
            response.raise_for_status()
            data = response.json()
            all_products.extend(data['products'])
            time.sleep(0.5)  # Be nice to the API
        
        print(f"✅ Fetched {len(all_products)} products from DummyJSON API")
        return all_products
    except Exception as e:
        print(f"❌ Error fetching from DummyJSON API: {e}")
        return []

def generate_additional_products():
    """Generate additional product variations to reach 100+ products"""
    print("🔄 Generating additional product variations...")
    
    additional_products = []
    
    # Additional clothing items
    clothing_products = [
        {
            "title": "Classic White Sneakers",
            "price": 89.99,
            "description": "Comfortable white sneakers perfect for everyday wear. Made with premium materials and cushioned sole for all-day comfort.",
            "category": "men's clothing",
            "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
            "rating": {"rate": 4.5}
        },
        {
            "title": "Wireless Bluetooth Headphones",
            "price": 79.99,
            "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life. Perfect for music lovers.",
            "category": "electronics",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
            "rating": {"rate": 4.3}
        },
        {
            "title": "Vintage Leather Wallet",
            "price": 45.99,
            "description": "Handcrafted leather wallet with multiple card slots and bill compartments. Ages beautifully with time.",
            "category": "men's clothing",
            "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
            "rating": {"rate": 4.7}
        },
        # Add more products here...
    ]
    
    additional_products.extend(clothing_products)
    
    print(f"✅ Generated {len(additional_products)} additional products")
    return additional_products

def fetch_all_products():
    """Fetch products from all sources"""
    all_products = []
    
    # Fetch from FakeStore API
    fakestore_products = fetch_fakestore_products()
    all_products.extend(fakestore_products)
    
    # Fetch from DummyJSON API
    dummyjson_products = fetch_dummyjson_products()
    all_products.extend(dummyjson_products)
    
    # Generate additional products if needed
    if len(all_products) < 80:
        additional_products = generate_additional_products()
        all_products.extend(additional_products)
    
    print(f"📊 Total products collected: {len(all_products)}")
    return all_products[:100]  # Limit to 100 products

def convert_to_our_format(api_products):
    """Convert multiple API formats to our format"""
    converted_products = []
    
    category_mapping = {
        "men's clothing": "Clothing",
        "women's clothing": "Clothing", 
        "jewelery": "Jewelry",
        "jewelry": "Jewelry",
        "electronics": "Electronics",
        "smartphones": "Electronics",
        "laptops": "Electronics",
        "fragrances": "Beauty",
        "skincare": "Beauty",
        "groceries": "Food",
        "home-decoration": "Home",
        "furniture": "Home",
        "tops": "Clothing",
        "womens-dresses": "Clothing",
        "womens-shoes": "Clothing",
        "mens-shirts": "Clothing",
        "mens-shoes": "Clothing",
        "mens-watches": "Jewelry",
        "womens-watches": "Jewelry",
        "womens-bags": "Accessories",
        "womens-jewellery": "Jewelry",
        "sunglasses": "Accessories",
        "automotive": "Automotive",
        "motorcycle": "Automotive",
        "lighting": "Home"
    }
    
    for i, product in enumerate(api_products, 1):
        # Generate a proper product ID
        product_id = f"product_{i:03d}"
        
        # Handle different API formats
        if 'thumbnail' in product:
            # DummyJSON format
            image_url = product.get('thumbnail', product.get('images', [''])[0])
            title = product.get('title', '')
            price = float(product.get('price', 0))
            description = product.get('description', '')
            category = product.get('category', 'general')
            rating = float(product.get('rating', 0))
            brand = product.get('brand', 'Various')
        else:
            # FakeStore API format
            image_url = product.get('image', '')
            title = product.get('title', '')
            price = float(product.get('price', 0))
            description = product.get('description', '')
            category = product.get('category', 'general')
            rating = float(product.get('rating', {}).get('rate', 0))
            brand = "Various"
        
        # Get image extension from URL
        if image_url.endswith('.png'):
            image_ext = 'png'
        elif image_url.endswith('.webp'):
            image_ext = 'jpg'  # Convert webp to jpg
        else:
            image_ext = 'jpg'
        
        # Truncate description if too long
        if len(description) > 200:
            description = description[:200] + "..."
        
        converted_product = {
            "id": product_id,
            "name": title,
            "category": category_mapping.get(category.lower(), category.title()),
            "price": price,
            "description": description,
            "image_path": f"{product_id}.{image_ext}",
            "image_url": image_url,  # Keep original URL for downloading
            "brand": brand,
            "rating": rating
        }
        
        converted_products.append(converted_product)
    
    return converted_products

def download_images(products, images_dir):
    """Download product images with enhanced error handling"""
    print(f"\n📥 Downloading images to {images_dir}...")
    
    # Create images directory
    os.makedirs(images_dir, exist_ok=True)
    
    successful_downloads = 0
    
    for i, product in enumerate(products, 1):
        try:
            image_url = product['image_url']
            image_filename = product['image_path']
            image_path = os.path.join(images_dir, image_filename)
            
            print(f"⬇️  [{i}/{len(products)}] Downloading {image_filename}...")
            
            # Download image with headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Save image
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify and process image
            try:
                with Image.open(image_path) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'P', 'LA'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        if img.mode in ('RGBA', 'LA'):
                            rgb_img.paste(img, mask=img.split()[-1])
                        img = rgb_img
                    
                    # Resize if too large
                    if img.width > 800 or img.height > 800:
                        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                    
                    # Save as JPEG if it was converted from another format
                    if image_filename.endswith('.jpg') or image_filename.endswith('.jpeg'):
                        img.save(image_path, 'JPEG', quality=85)
                    else:
                        img.save(image_path)
                
                successful_downloads += 1
                print(f"✅ {image_filename} downloaded successfully")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not process image {image_filename}: {e}")
                # Remove corrupted file
                if os.path.exists(image_path):
                    os.remove(image_path)
                
        except Exception as e:
            print(f"❌ Failed to download {product['image_path']}: {e}")
        
        # Add a small delay to be nice to the servers
        if i % 10 == 0:
            time.sleep(1)
    
    print(f"\n📊 Downloaded {successful_downloads}/{len(products)} images successfully")
    return successful_downloads

def save_products_json(products, output_file):
    """Save products to JSON file"""
    # Remove image_url from final output (only needed for downloading)
    clean_products = []
    for product in products:
        clean_product = {k: v for k, v in product.items() if k != 'image_url'}
        clean_products.append(clean_product)
    
    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(clean_products, f, indent=2)
    
    print(f"✅ Saved {len(clean_products)} products to {output_file}")

def main():
    print("🚀 Real Product Data Setup for Visual Product Matcher")
    print("=" * 55)
    print("🎯 Target: 100 real products from multiple sources")
    
    # Set up paths
    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(script_dir, 'data')
    images_dir = os.path.join(data_dir, 'images')
    products_file = os.path.join(data_dir, 'products.json')
    
    # Create backup of existing data
    if os.path.exists(products_file):
        backup_file = os.path.join(data_dir, 'products_backup.json')
        print(f"📋 Creating backup: {backup_file}")
        import shutil
        shutil.copy2(products_file, backup_file)
    
    # Fetch real product data from multiple sources
    api_products = fetch_all_products()
    if not api_products:
        print("❌ No products were fetched from any source")
        return
    
    # Convert to our format
    print(f"\n🔄 Converting {len(api_products)} products to our format...")
    converted_products = convert_to_our_format(api_products)
    
    # Download images
    successful_downloads = download_images(converted_products, images_dir)
    
    if successful_downloads == 0:
        print("❌ No images were downloaded successfully")
        return
    
    # Save products JSON
    save_products_json(converted_products, products_file)
    
    print("\n" + "=" * 55)
    print("🎉 Real product data setup completed!")
    print(f"📁 Products: {products_file}")
    print(f"🖼️  Images: {images_dir}")
    print(f"📊 Total products: {len(converted_products)}")
    print(f"✅ Ready for Visual Product Matcher!")
    
    print("\n🔄 Next steps:")
    print("1. Start Qdrant: docker-compose up -d qdrant")
    print("2. Start backend: cd backend && python app.py")
    print("3. The new products will be automatically loaded on first API request")

if __name__ == "__main__":
    # Check if requests and PIL are available
    try:
        import requests
        from PIL import Image
    except ImportError as e:
        print("❌ Missing required packages. Please install:")
        print("pip install requests Pillow")
        exit(1)
    
    main()
