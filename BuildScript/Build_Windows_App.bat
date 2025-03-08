@echo off
:: Script to build SignalMgrGUI executable for Windows
echo Building SignalMgrGUI for Windows...

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

:: Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo PyInstaller is not installed. Installing...
    python -m pip install PyInstaller
)

:: Create build directory if it doesn't exist
if not exist "..\dist" mkdir "..\dist"

:: Build the executable
echo Building executable...
python build.py --platform windows

:: Check if build was successful
if %ERRORLEVEL% neq 0 (
    echo Build failed!
    exit /b 1
)

echo Build completed successfully! Executable is in the dist folder.