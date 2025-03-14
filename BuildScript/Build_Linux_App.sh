#!/bin/bash
# Script to build SignalMgrGUI executable for Linux

echo "Building SignalMgrGUI for Linux..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed."
    exit 1
fi

# Install required packages
echo "Installing required packages..."
python3 -m pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt"
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error installing from requirements.txt. Installing essential packages individually..."
        python3 -m pip install PyInstaller
        python3 -m pip install Pillow
    fi
else
    echo "Installing essential packages"
    python3 -m pip install PyInstaller Pillow
fi

# Verify PyInstaller is installed
python3 -c "import PyInstaller" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Warning: PyInstaller module not accessible. Retrying installation..."
    python3 -m pip install --force-reinstall PyInstaller
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