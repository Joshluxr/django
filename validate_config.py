#!/usr/bin/env python3
"""
Configuration validation script for Labubu Monitor Bot
Run this to check if your configuration is valid before starting the bot.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filename, required=True):
    """Check if a file exists."""
    exists = Path(filename).exists()
    status = "✅" if exists else ("❌" if required else "⚠️ ")
    print(f"{status} {filename}: {'Found' if exists else 'Missing'}")
    return exists


def validate_env():
    """Validate .env configuration."""
    print("\n📋 Validating Environment Variables")
    print("=" * 50)
    
    if not check_file_exists('.env', required=True):
        print("   Create .env from .env.example: cp .env.example .env")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('DISCORD_TOKEN')
    proxy = os.getenv('HTTP_PROXY')
    
    if not token:
        print("❌ DISCORD_TOKEN is not set in .env")
        return False
    
    if token == '' or token == 'your_token_here':
        print("❌ DISCORD_TOKEN is not configured (still default value)")
        return False
    
    print(f"✅ DISCORD_TOKEN: Set (length: {len(token)} chars)")
    
    if proxy:
        print(f"✅ HTTP_PROXY: {proxy}")
    else:
        print("ℹ️  HTTP_PROXY: Not set (optional)")
    
    return True


def validate_config_yaml():
    """Validate config.yaml configuration."""
    print("\n📋 Validating config.yaml")
    print("=" * 50)
    
    if not check_file_exists('config.yaml', required=True):
        print("   Create config.yaml from config.yaml.example:")
        print("   cp config.yaml.example config.yaml")
        return False
    
    try:
        from config import load_config
        cfg = load_config()
    except Exception as e:
        print(f"❌ Failed to load config.yaml: {e}")
        return False
    
    # Validate source_channels
    if not cfg.get('source_channels'):
        print("❌ source_channels is empty")
        return False
    
    if isinstance(cfg['source_channels'], list):
        # Check if still has example IDs
        example_ids = [123456789012345678, 987654321098765432]
        if any(ch in example_ids for ch in cfg['source_channels']):
            print("⚠️  source_channels contains example IDs - please update with real channel IDs")
        else:
            print(f"✅ source_channels: {len(cfg['source_channels'])} channel(s) configured")
    else:
        print("❌ source_channels must be a list")
        return False
    
    # Validate destination_channel_id
    if not cfg.get('destination_channel_id'):
        print("❌ destination_channel_id is not set")
        return False
    
    if cfg['destination_channel_id'] == 987654321098765432:
        print("⚠️  destination_channel_id is still the example ID - please update")
    else:
        print(f"✅ destination_channel_id: {cfg['destination_channel_id']}")
    
    # Validate allowed_domains
    if not cfg.get('allowed_domains'):
        print("⚠️  allowed_domains is empty - bot will reject all URLs")
    else:
        print(f"✅ allowed_domains: {len(cfg['allowed_domains'])} domain(s)")
    
    # Validate keywords
    if not cfg.get('labubu_keywords'):
        print("⚠️  labubu_keywords is empty - bot won't filter any messages")
    else:
        print(f"✅ labubu_keywords: {len(cfg['labubu_keywords'])} keyword(s)")
    
    # Validate numeric settings
    print(f"✅ concurrency_limit: {cfg.get('concurrency_limit', 'not set')}")
    print(f"✅ verification_timeout_seconds: {cfg.get('verification_timeout_seconds', 'not set')}")
    
    return True


def validate_dependencies():
    """Validate that all dependencies are installed."""
    print("\n📋 Validating Dependencies")
    print("=" * 50)
    
    required_modules = [
        'discord',
        'aiohttp',
        'beautifulsoup4',
        'cachetools',
        'loguru',
        'pydantic',
        'pytest',
        'python-dotenv',
        'yaml',
    ]
    
    all_installed = True
    for module in required_modules:
        # Handle package name differences
        import_name = module.replace('-', '_')
        if module == 'beautifulsoup4':
            import_name = 'bs4'
        elif module == 'yaml':
            import_name = 'yaml'
        
        try:
            __import__(import_name)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - Not installed")
            all_installed = False
    
    if not all_installed:
        print("\n⚠️  Install missing dependencies:")
        print("   pip install -r requirements.txt")
    
    return all_installed


def validate_permissions():
    """Check file permissions."""
    print("\n📋 Validating File Permissions")
    print("=" * 50)
    
    files_to_check = ['bot.py', 'parser.py', 'verifier.py', 'config.py']
    
    for file in files_to_check:
        if Path(file).exists():
            if os.access(file, os.R_OK):
                print(f"✅ {file}: Readable")
            else:
                print(f"❌ {file}: Not readable")
                return False
    
    return True


def run_tests():
    """Run the test suite."""
    print("\n📋 Running Tests")
    print("=" * 50)
    
    try:
        import pytest
        result = pytest.main(['-q', 'tests/'])
        if result == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Some tests failed")
            return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False


def main():
    """Run all validations."""
    print("🐰 Labubu Monitor Bot - Configuration Validator")
    print("=" * 50)
    
    results = {
        'Files': check_file_exists('requirements.txt') and 
                 check_file_exists('bot.py') and 
                 check_file_exists('config.py'),
        'Dependencies': validate_dependencies(),
        'Environment': validate_env(),
        'Config': validate_config_yaml(),
        'Permissions': validate_permissions(),
        'Tests': run_tests(),
    }
    
    print("\n" + "=" * 50)
    print("📊 Validation Summary")
    print("=" * 50)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All validations passed! You're ready to run the bot.")
        print("\nStart the bot with: python bot.py")
        return 0
    else:
        print("❌ Some validations failed. Please fix the issues above.")
        print("\nRefer to SETUP_GUIDE.md for detailed instructions.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
