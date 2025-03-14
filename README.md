# Signal Manager GUI

A graphical user interface tool for managing signal configurations.

## Overview

Signal Manager GUI is a PyQt5-based application that provides a user-friendly interface for creating, managing, and configuring signal definitions. It allows you to visualize and edit signal properties, import/export data, and generate code.

## Building the Application

### Requirements

- Python 3.6+
- PyQt5
- Required packages listed in `requirements.txt`

Install dependencies:
```bash
pip install -r requirements.txt
```

### Build on Windows

You have three options to build the application on Windows:

#### Option 1: Using PowerShell (Recommended)

```powershell
cd BuildScript
powershell -ExecutionPolicy Bypass -File .\Build_Windows_App.ps1
```

#### Option 2: Using Command Prompt

```cmd
cd BuildScript
Build_Windows_App.bat
```

#### Option 3: Using Python Directly

```cmd
cd BuildScript
python -m PyInstaller --clean SignalMgrGUI.spec
```

### Build on Linux

```bash
cd BuildScript
bash ./Build_Linux_App.sh
```

Or make it executable first:

```bash
cd BuildScript
chmod +x ./Build_Linux_App.sh
./Build_Linux_App.sh
```

## Output Files

After building, you will find the following output:

### Windows
- Executable: `dist/SignalMgrGUI/SignalMgrGUI.exe`
- ZIP Archive: `dist/SignalMgrGUI_win.zip` (for easy distribution)

### Linux
- Executable: `dist/SignalMgrGUI/SignalMgrGUI`
- TAR.GZ Archive: `dist/SignalMgrGUI_v1.0.0_linux.tar.gz` (for easy distribution)

## Running the Application

### From Source

```bash
python App/SignalMgrApp.py
```

### From Built Executable

#### Windows
Navigate to the `dist/SignalMgrGUI` directory and run `SignalMgrGUI.exe`, or extract the ZIP file (`dist/SignalMgrGUI_win.zip`) to any location and run the executable.

#### Linux
Navigate to the `dist/SignalMgrGUI` directory and run the executable, or extract the TAR.GZ file (`dist/SignalMgrGUI_v1.0.0_linux.tar.gz`) to any location and run the executable.

## Project Structure

- **App/**: Contains the main application code
  - `SignalMgrApp.py`: Entry point for the application
- **Modules/**: Contains the core functionality modules
- **utils/**: Contains utility functions and helper code
- **Cfg/**: Contains configuration files
- **BuildScript/**: Contains build scripts for generating executables
  - `build.py`: Core build script
  - `Build_Windows_App.bat`: Windows batch script for building
  - `Build_Windows_App.ps1`: PowerShell script for building
  - `Build_Linux_App.sh`: Linux shell script for building
  - `SignalMgrGUI.spec`: PyInstaller specification file

## Build Process Details

The build process performs the following steps:

1. Installs required dependencies
2. Creates a PyInstaller spec file if not present
3. Builds the executable using PyInstaller
4. Creates a portable distribution with all dependencies
5. Packages the distribution into a ZIP (Windows) or TAR.GZ (Linux) file

## Troubleshooting

### Common Issues

#### "pathlib" package error
If you encounter an error related to the "pathlib" package being incompatible with PyInstaller, uninstall it using:
```
python -m pip uninstall -y pathlib
```

#### Recursion Error
If you encounter a recursion error, make sure you're using the provided spec file which increases the recursion limit.

#### PyInstaller Command Arguments
If you encounter an error with PyInstaller command arguments, ensure you're using `--distpath` instead of `--dist-dir` in newer versions of PyInstaller.

## Version History

- 1.0.0: Initial release

## Contributors

[Add contributors information here]

## License

[Add license information here] 