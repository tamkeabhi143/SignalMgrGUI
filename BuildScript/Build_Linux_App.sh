#!/bin/bash
# Script to build SignalMgrGUI executable for Linux

echo "Building SignalMgrGUI for Linux..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed."
    exit 1
fi

# Check if PyInstaller is installed
python3 -c "import PyInstaller" &> /dev/null
if [ $? -ne 0 ]; then
    echo "PyInstaller is not installed. Installing..."
    python3 -m pip install PyInstaller
fi

# Create build directory if it doesn't exist
mkdir -p ../dist

# Build the executable
echo "Building executable..."
python3 build.py --platform linux

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

# Make the binary executable
chmod +x ../dist/SignalMgrGUI

echo "Build completed successfully! Binary is in the dist folder."