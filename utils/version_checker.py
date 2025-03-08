import os
import json
import requests
from PyQt5.QtWidgets import QMessageBox
import version_info

class VersionChecker:
    def __init__(self, app):
        self.app = app
        self.current_version = version_info.VERSION
        self.version_url = "https://example.com/signalmgr/version.json"
        self.download_url = "https://example.com/signalmgr/download"
    
    def check_for_updates(self, silent=False):
        """Check if a newer version is available
        
        Args:
            silent: If True, no message is shown if using latest version
        """
        try:
            response = requests.get(self.version_url, timeout=5)
            if response.status_code == 200:
                version_data = response.json()
                latest_version = version_data.get("version", "0.0.0")
                
                # Compare versions
                if self._is_newer_version(latest_version):
                    # Show update available message
                    changelog = version_data.get("changelog", "")
                    self._show_update_dialog(latest_version, changelog)
                elif not silent:
                    # Only show "up to date" message if not in silent mode
                    QMessageBox.information(
                        self.app,
                        "Up to Date",
                        f"You are using the latest version ({self.current_version})."
                    )
        except Exception as e:
            if not silent:
                QMessageBox.warning(
                    self.app,
                    "Update Check Failed",
                    f"Unable to check for updates: {str(e)}"
                )
    
    def _is_newer_version(self, version_string):
        """Compare version strings to determine if the new version is newer"""
        current_parts = [int(p) for p in self.current_version.split('.')]
        new_parts = [int(p) for p in version_string.split('.')]
        
        # Pad with zeros if needed
        while len(current_parts) < len(new_parts):
            current_parts.append(0)
        while len(new_parts) < len(current_parts):
            new_parts.append(0)
        
        # Compare each part
        for current, new in zip(current_parts, new_parts):
            if new > current:
                return True
            if new < current:
                return False
        
        # If we get here, they're equal
        return False
    
    def _show_update_dialog(self, new_version, changelog):
        """Show dialog to inform user about the new version"""
        msg = QMessageBox(self.app)
        msg.setWindowTitle("Update Available")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"A new version ({new_version}) is available!")
        
        details = f"You are currently using version {self.current_version}.\n\n"
        details += f"Changes in version {new_version}:\n{changelog}"
        msg.setDetailedText(details)
        
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Help)
        msg.setDefaultButton(QMessageBox.Ok)
        
        result = msg.exec_()
        if result == QMessageBox.Help:
            import webbrowser
            webbrowser.open(self.download_url)
