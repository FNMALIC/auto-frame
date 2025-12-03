#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Smart Meeting Camera...${NC}"

# Check for PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${RED}PyInstaller not found. Installing...${NC}"
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build with PyInstaller
echo "Running PyInstaller..."
pyinstaller smart-camera.spec

# Check if build was successful
if [ -f "dist/smart-camera/smart-camera" ]; then
    echo -e "${GREEN}Build successful!${NC}"
    echo "Executable is located at: dist/smart-camera/smart-camera"
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi

# Create distribution package
echo "Creating distribution package..."
mkdir -p dist/package
cp -r dist/smart-camera/* dist/package/
cp README.md dist/package/
cp -r resources dist/package/
cp install.sh dist/package/
cp uninstall.sh dist/package/

# Create tarball
cd dist
tar -czf smart-camera-linux.tar.gz package
cd ..

echo -e "${GREEN}Package created: dist/smart-camera-linux.tar.gz${NC}"
