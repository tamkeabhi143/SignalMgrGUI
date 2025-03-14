# PowerShell Script to build SignalMgrGUI executable for Windows
Write-Host "Building SignalMgrGUI for Windows..." -ForegroundColor Green

# Get the script directory path
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

# Check if Python is installed
try {
    $PythonVersion = python --version
    Write-Host "Found Python: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if PyInstaller is installed
try {
    python -c "import PyInstaller" -ErrorAction Stop
    Write-Host "PyInstaller is installed" -ForegroundColor Green
} catch {
    Write-Host "PyInstaller is not installed. Installing..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    python -m pip install PyInstaller
    
    # Verify installation was successful
    try {
        python -c "import PyInstaller" -ErrorAction Stop
        Write-Host "PyInstaller installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "PyInstaller installation failed. Trying force reinstall..." -ForegroundColor Red
        python -m pip install --force-reinstall PyInstaller
        
        # Final verification
        try {
            python -c "import PyInstaller" -ErrorAction Stop
            Write-Host "PyInstaller force reinstall successful" -ForegroundColor Green
        } catch {
            Write-Host "PyInstaller installation failed even with force reinstall. Build may fail." -ForegroundColor Red
        }
    }
}

# Check if required files and directories exist
$MainAppPath = Join-Path -Path $RootDir -ChildPath "App\SignalMgrApp.py"
$ConfigPath = Join-Path -Path $RootDir -ChildPath "Cfg\AppConfig.json"

if (-not (Test-Path -Path $MainAppPath)) {
    Write-Host "Error: Main application file not found at: $MainAppPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -Path $ConfigPath)) {
    Write-Host "Warning: Configuration file not found at: $ConfigPath" -ForegroundColor Yellow
    Write-Host "Will use default configuration from build.py" -ForegroundColor Yellow
}

# Create build directory if it doesn't exist
$DistDir = Join-Path -Path $RootDir -ChildPath "dist"
if (-not (Test-Path -Path $DistDir)) {
    New-Item -Path $DistDir -ItemType Directory -Force | Out-Null
    Write-Host "Created distribution directory: $DistDir" -ForegroundColor Green
}

# Navigate to the BuildScript directory
Set-Location -Path $ScriptDir

# Build the executable
Write-Host "Building executable..." -ForegroundColor Green
python build.py --platform windows

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Verify the build output
$AppName = "SignalMgrGUI"
try {
    $ConfigJson = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
    $AppName = $ConfigJson.app_name
} catch {
    Write-Host "Using default app name: $AppName" -ForegroundColor Yellow
}

$AppPath = Join-Path -Path $DistDir -ChildPath $AppName
$ZipPattern = Join-Path -Path $DistDir -ChildPath "$AppName*_win.zip"

if (Test-Path -Path $AppPath) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "Executable directory: $AppPath" -ForegroundColor Green
    
    $ZipFiles = Get-ChildItem -Path $ZipPattern
    if ($ZipFiles.Count -gt 0) {
        Write-Host "ZIP archive created: $($ZipFiles[0].FullName)" -ForegroundColor Green
    }
} else {
    Write-Host "Warning: Expected output directory not found: $AppPath" -ForegroundColor Yellow
    Write-Host "Check the dist directory for build output." -ForegroundColor Yellow
}

Write-Host "Build process complete." -ForegroundColor Green 