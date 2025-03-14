@echo off
:: Script to build SignalMgrGUI executable for Windows
echo Building SignalMgrGUI for Windows...

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

:: Install required packages
echo Installing required packages...
python -m pip install --upgrade pip
if exist "requirements.txt" (
    echo Installing from requirements.txt
    python -m pip install -r requirements.txt
) else (
    echo Installing essential packages
    python -m pip install PyInstaller Pillow
)

:: Verify PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Warning: PyInstaller module not accessible. Retrying installation...
    python -m pip install --force-reinstall PyInstaller
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