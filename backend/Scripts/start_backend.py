"""
Backend startup script for Visual Product Matcher
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_docker():
    """Check if Docker is available and running"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Docker is available: {result.stdout.strip()}")
            return True
        else:
            logger.error("❌ Docker is not available")
            return False
    except FileNotFoundError:
        logger.error("❌ Docker is not installed")
        return False

def start_qdrant():
    """Start Qdrant container"""
    try:
        logger.info("🚀 Starting Qdrant container...")
        result = subprocess.run([
            'docker', 'compose', 'up', '-d', 'qdrant'
        ], capture_output=True, text=True, cwd='..')
        
        if result.returncode == 0:
            logger.info("✅ Qdrant container started successfully")
            return True
        else:
            logger.error(f"❌ Failed to start Qdrant: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Error starting Qdrant: {str(e)}")
        return False

def wait_for_qdrant(timeout=30):
    """Wait for Qdrant to be ready"""
    import requests
    
    logger.info("⏳ Waiting for Qdrant to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get('http://localhost:6333/collections', timeout=5)
            if response.status_code == 200:
                logger.info("✅ Qdrant is ready!")
                return True
        except Exception:
            pass
        
        time.sleep(2)
        print("   Waiting for Qdrant...")
    
    logger.error("❌ Timeout waiting for Qdrant")
    return False

def start_backend():
    """Start the Flask backend"""
    logger.info("🎯 Starting Visual Product Matcher backend API...")
    
    # Check if virtual environment exists
    if os.path.exists('.venv'):
        if os.name == 'nt':  # Windows
            python_cmd = '.venv\\Scripts\\python.exe'
        else:  # Unix/Linux
            python_cmd = '.venv/bin/python'
    else:
        python_cmd = 'python'
    
    # Start Flask app
    env = os.environ.copy()
    env['FLASK_APP'] = 'app.py'
    env['FLASK_ENV'] = 'development'
    
    try:
        subprocess.run([python_cmd, 'app.py'], env=env)
    except KeyboardInterrupt:
        logger.info("⏹️ Backend stopped by user")

def main():
    """Main startup function"""
    logger.info("🚀 Visual Product Matcher Backend Startup")
    logger.info("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Check Docker
    if not check_docker():
        sys.exit(1)
    
    # Start Qdrant
    if not start_qdrant():
        sys.exit(1)
    
    # Wait for Qdrant
    if not wait_for_qdrant():
        sys.exit(1)
    
    # Start backend
    start_backend()

if __name__ == '__main__':
    main()
