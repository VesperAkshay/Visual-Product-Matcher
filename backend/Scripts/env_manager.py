#!/usr/bin/env python3
"""
Environment management utility for Visual Product Matcher
"""

import os
import shutil
import sys
from pathlib import Path

def create_env_from_example():
    """Create .env file from .env.example"""
    backend_path = Path(__file__).parent
    env_example = backend_path / '.env.example'
    env_file = backend_path / '.env'
    
    if not env_example.exists():
        print("❌ .env.example file not found!")
        return False
    
    if env_file.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("✋ Operation cancelled")
            return False
    
    try:
        # Copy the example file
        shutil.copy2(env_example, env_file)
        print(f"✅ Created {env_file} from {env_example}")
        
        # Update some development-specific values
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Make development-friendly modifications
        content = content.replace(
            'SECRET_KEY=change-this-in-production-very-important',
            'SECRET_KEY=dev-secret-key-for-development-only-change-in-production'
        )
        content = content.replace('LOG_LEVEL=INFO', 'LOG_LEVEL=DEBUG')
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("🔧 Applied development-friendly defaults")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def switch_environment(env_type):
    """Switch to a specific environment configuration"""
    backend_path = Path(__file__).parent
    source_file = backend_path / f'.env.{env_type}.example'
    env_file = backend_path / '.env'
    
    if not source_file.exists():
        print(f"❌ {source_file} not found!")
        return False
    
    if env_file.exists():
        backup_file = backend_path / f'.env.backup.{env_type}'
        shutil.copy2(env_file, backup_file)
        print(f"📦 Backed up current .env to {backup_file}")
    
    try:
        shutil.copy2(source_file, env_file)
        print(f"✅ Switched to {env_type} environment")
        print(f"📝 Remember to customize values in {env_file}")
        return True
    except Exception as e:
        print(f"❌ Error switching environment: {e}")
        return False

def validate_current_env():
    """Validate current environment configuration"""
    try:
        from validate_config import validate_environment
        return validate_environment()
    except ImportError:
        print("❌ Cannot import validation module")
        return False

def show_current_env():
    """Show current environment configuration"""
    backend_path = Path(__file__).parent
    env_file = backend_path / '.env'
    
    if not env_file.exists():
        print("❌ No .env file found")
        return
    
    print("📋 Current Environment Configuration:")
    print("=" * 40)
    
    with open(env_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                print(f"{line_num:2d}: {line}")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("🔧 Visual Product Matcher Environment Manager")
        print("=" * 45)
        print("Usage:")
        print("  python env_manager.py create     - Create .env from .env.example")
        print("  python env_manager.py production - Switch to production config")
        print("  python env_manager.py validate   - Validate current configuration")
        print("  python env_manager.py show       - Show current configuration")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        success = create_env_from_example()
    elif command == 'production':
        success = switch_environment('production')
    elif command == 'validate':
        success = validate_current_env()
    elif command == 'show':
        show_current_env()
        success = True
    else:
        print(f"❌ Unknown command: {command}")
        success = False
    
    if success:
        print("\n✅ Operation completed successfully!")
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
