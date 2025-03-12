#!/usr/bin/env python3
import os
import sys
import json
import shutil
import argparse
import subprocess
import platform
from pathlib import Path

def read_config():
    """Read configuration from pkg_config.json"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "Cfg", "AppConfig.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "app_name": "SignalMgrGUI",
        "version": "1.0.0",
        "description": "Signal Manager GUI Tool",
        "author": "Your Name",
        "windows_icon": "app_icon.ico",
        "linux_icon": "app_icon.png",
        "add_data": []
    }

def ensure_icons_exist(config):
    """Ensure that icon files exist, create default ones if they don't"""
    script_dir = os.path.dirname(__file__)
    
    # Windows icon path
    windows_icon = os.path.join(script_dir, config["windows_icon"])
    if not os.path.exists(windows_icon):
        print(f"Windows icon not found at {windows_icon}, creating default icon...")
        # Create a minimal .ico file
        try:
            from PIL import Image
            img = Image.new('RGB', (48, 48), color=(0, 120, 215))
            img.save(windows_icon, format='ICO')
            print(f"Created default Windows icon at {windows_icon}")
        except ImportError:
            print("PIL (Pillow) not installed, can't create default icon")
            print("You may need to install Pillow: pip install Pillow")
            # Create an empty file as a fallback
            with open(windows_icon, 'wb') as f:
                f.write(b'')
    
    # Linux icon path
    linux_icon = os.path.join(script_dir, config["linux_icon"])
    if not os.path.exists(linux_icon):
        print(f"Linux icon not found at {linux_icon}, creating default icon...")
        # Create a minimal .png file
        try:
            from PIL import Image
            img = Image.new('RGB', (48, 48), color=(0, 120, 215))
            img.save(linux_icon, format='PNG')
            print(f"Created default Linux icon at {linux_icon}")
        except ImportError:
            print("PIL (Pillow) not installed, can't create default icon")
            print("You may need to install Pillow: pip install Pillow")
            # Create an empty file as a fallback
            with open(linux_icon, 'wb') as f:
                f.write(b'')
    
    return windows_icon, linux_icon

def create_spec_file(config, platform_name):
    """Create a PyInstaller spec file based on configuration"""
    app_name = config["app_name"]
    version = config["version"]
    description = config["description"]
    author = config["author"]
    
    # Root directory (parent of BuildScript)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Main script
    main_script = os.path.join(root_dir, "App", "SignalMgrApp.py")
    if not os.path.exists(main_script):
        print(f"Error: Main script not found at {main_script}")
        return None
    
    # Make sure icons exist
    windows_icon, linux_icon = ensure_icons_exist(config)
    
    # Icon path
    icon_path = ""
    if platform_name == "windows" and os.path.exists(windows_icon):
        icon_path = windows_icon
    elif platform_name == "linux" and os.path.exists(linux_icon):
        icon_path = linux_icon
    
    # Create spec file content
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{main_script.replace('\\', '\\\\')}'],
    pathex=['{root_dir.replace('\\', '\\\\')}'],
    binaries=[],
    datas=["""
    
    # Add data files
    for data_item in config.get("add_data", []):
        src = data_item.get("src", "")
        dest = data_item.get("dest", "")
        if src and dest:
            # Convert relative paths to absolute
            if src.startswith("../"):
                src = os.path.abspath(os.path.join(os.path.dirname(__file__), src))
            spec_content += f"""
        ('{src.replace('\\', '\\\\')}', '{dest}'),"""
    
    spec_content += f"""
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,"""
    
    if icon_path:
        spec_content += f"""
    icon='{icon_path.replace('\\', '\\\\')}',"""
    
    spec_content += f"""
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{app_name}',
)
"""
    
    # For macOS, add app bundle
    if platform_name == "darwin":
        spec_content += f"""
app = BUNDLE(
    coll,
    name='{app_name}.app',
    icon=None,
    bundle_identifier=None,
)
"""
    
    # Write spec file
    spec_path = os.path.join(os.path.dirname(__file__), f"{app_name}.spec")
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    return spec_path

def build_package(platform_name):
    """Build package for the specified platform"""
    print(f"Building package for {platform_name}...")
    
    # Read configuration
    config = read_config()
    app_name = config["app_name"]
    
    # Create spec file
    spec_path = create_spec_file(config, platform_name)
    if not spec_path:
        print("Failed to create spec file")
        return False
    
    # Build command
    build_cmd = ["pyinstaller", "--clean", "--dist-dir", "../dist", spec_path]
    
    # Run build
    result = subprocess.run(build_cmd, check=False)
    if result.returncode != 0:
        print(f"Build failed with exit code {result.returncode}")
        return False
    
    # Clean up spec file
    os.unlink(spec_path)
    
    # Move files to correct location
    dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist"))
    app_dir = os.path.join(dist_dir, app_name)
    
    # For Windows, create a zip file
    if platform_name == "windows":
        import zipfile
        zip_path = os.path.join(dist_dir, f"{app_name}_v{config['version']}_win.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(app_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, dist_dir)
                    zipf.write(file_path, arcname)
        print(f"Created zip archive: {zip_path}")
    
    # For Linux, create a tar.gz file
    elif platform_name == "linux":
        import tarfile
        tar_path = os.path.join(dist_dir, f"{app_name}_v{config['version']}_linux.tar.gz")
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(app_dir, arcname=app_name)
        print(f"Created tar.gz archive: {tar_path}")
    
    print(f"Build completed successfully for {platform_name}")
    return True

def install_requirements():
    """Install required packages"""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path], check=True)
    else:
        subprocess.run([sys.executable, "-m", "pip", "install", "PyInstaller", "PyQt5"], check=True)

def main():
    parser = argparse.ArgumentParser(description="Build Signal Manager GUI executable")
    parser.add_argument("--platform", choices=["windows", "linux", "auto"], default="auto",
                        help="Target platform (windows, linux, or auto-detect)")
    args = parser.parse_args()
    
    # Determine platform
    if args.platform == "auto":
        system = platform.system().lower()
        if system == "windows":
            platform_name = "windows"
        elif system == "linux":
            platform_name = "linux"
        else:
            print(f"Unsupported platform: {system}")
            return 1
    else:
        platform_name = args.platform
    
    # Install requirements
    print("Installing required packages...")
    try:
        install_requirements()
    except Exception as e:
        print(f"Failed to install requirements: {e}")
        return 1
    
    # Build package
    success = build_package(platform_name)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
