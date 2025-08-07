#!/usr/bin/env python3
"""
Deployment script for Robin Logistics Environment to PyPI.
Run this script to build and upload the package.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"   Error: {e.stderr.strip()}")
        return False

def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...")
    
    required_tools = ['python', 'pip', 'twine']
    for tool in required_tools:
        if not run_command(f"which {tool}", f"Checking {tool}"):
            print(f"❌ {tool} is required but not found")
            return False
    
    # Check if build package is installed
    try:
        import build
        print("✅ build package is available")
    except ImportError:
        print("📦 Installing build package...")
        if not run_command("pip install build", "Installing build package"):
            return False
    
    return True

def run_tests():
    """Run the test suite."""
    print("\n🧪 Running tests...")
    if os.path.exists("tests"):
        return run_command("python -m pytest tests/ -v", "Running test suite")
    else:
        print("⚠️  No tests directory found, skipping tests")
        return True

def lint_code():
    """Run code quality checks."""
    print("\n🔍 Running code quality checks...")
    
    # Check if flake8 is available
    try:
        import flake8
        if not run_command("flake8 robin_logistics/ --max-line-length=88", "Running flake8"):
            return False
    except ImportError:
        print("⚠️  flake8 not installed, skipping lint check")
    
    # Check if black is available  
    try:
        import black
        if not run_command("black --check robin_logistics/", "Checking black formatting"):
            print("💡 Run 'black robin_logistics/' to fix formatting")
            return False
    except ImportError:
        print("⚠️  black not installed, skipping format check")
    
    return True

def clean_build():
    """Clean previous builds."""
    print("\n🧹 Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        run_command(f"rm -rf {pattern}", f"Removing {pattern}")
    
    return True

def build_package():
    """Build the package."""
    print("\n🏗️  Building package...")
    return run_command("python -m build", "Building wheel and source distribution")

def check_package():
    """Check the built package."""
    print("\n🔍 Checking package...")
    return run_command("twine check dist/*", "Checking package with twine")

def upload_to_testpypi():
    """Upload to Test PyPI."""
    print("\n📤 Uploading to Test PyPI...")
    print("💡 Make sure you have configured your Test PyPI credentials")
    
    response = input("Upload to Test PyPI? (y/N): ").lower()
    if response != 'y':
        print("⏭️  Skipping Test PyPI upload")
        return True
    
    return run_command(
        "twine upload --repository testpypi dist/*",
        "Uploading to Test PyPI"
    )

def upload_to_pypi():
    """Upload to PyPI."""
    print("\n📤 Uploading to PyPI...")
    print("🚨 This will publish to the real PyPI!")
    print("💡 Make sure you have configured your PyPI credentials")
    
    response = input("Are you sure you want to upload to PyPI? (y/N): ").lower()
    if response != 'y':
        print("⏭️  Skipping PyPI upload")
        return True
    
    return run_command("twine upload dist/*", "Uploading to PyPI")

def main():
    """Main deployment process."""
    print("🚀 Robin Logistics Environment Deployment Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed! Please fix issues before deploying.")
        sys.exit(1)
    
    # Check code quality
    if not lint_code():
        print("❌ Code quality checks failed! Please fix issues before deploying.")
        sys.exit(1)
    
    # Clean build
    if not clean_build():
        sys.exit(1)
    
    # Build package
    if not build_package():
        sys.exit(1)
    
    # Check package
    if not check_package():
        sys.exit(1)
    
    # Upload to Test PyPI (optional)
    if not upload_to_testpypi():
        print("⚠️  Test PyPI upload failed, but continuing...")
    
    # Upload to PyPI
    if not upload_to_pypi():
        sys.exit(1)
    
    print("\n🎉 Deployment completed successfully!")
    print("📦 Package is now available on PyPI")
    print("💡 Users can install with: pip install robin-logistics-env")

if __name__ == "__main__":
    main()