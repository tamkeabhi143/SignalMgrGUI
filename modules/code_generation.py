import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog

class CodeGeneration:
    def __init__(self, app):
        self.app = app
        self.script_paths = {
            "signal_mgr": "/usr/local/bin/signal_mgr_generator.py",
            "ipc_manager": "/usr/local/bin/ipc_manager_generator.py",
            "ipc_eth_mgr": "/usr/local/bin/ipc_eth_mgr_generator.py"
        }
        # Load saved script paths if available
        self.load_script_paths()
    
    def load_script_paths(self):
        """Load script paths from configuration"""
        if "script_paths" in self.app.signals_data:
            self.script_paths.update(self.app.signals_data["script_paths"])
    
    def save_script_paths(self):
        """Save script paths to configuration"""
        self.app.signals_data["script_paths"] = self.script_paths
        self.app.modified = True
    
    def check_script_path(self, script_type):
        """Check if script exists, prompt for path if not found"""
        script_path = self.script_paths.get(script_type, "")
        
        if not script_path or not os.path.isfile(script_path):
            QMessageBox.information(
                self.app,
                "Script Not Found",
                f"The script for {script_type} generation was not found. Please select the script file."
            )
            
            file_path, _ = QFileDialog.getOpenFileName(
                self.app,
                f"Select {script_type.replace('_', ' ').title()} Script",
                "",
                "Python Files (*.py);;All Files (*)"
            )
            
            if file_path:
                self.script_paths[script_type] = file_path
                self.save_script_paths()
                return file_path
            else:
                return None
        
        return script_path
    
    def generate_signal_mgr(self):
        """Generate Signal Manager code"""
        # Check version information before exporting
        if not self.app.ui_helpers.check_version_for_export():
            return
            
        script_path = self.check_script_path("signal_mgr")
        if not script_path:
            return
        
        # Generate output folder dialog
        output_dir = QFileDialog.getExistingDirectory(
            self.app,
            "Select Output Directory for Signal Manager Code",
            os.path.expanduser("~/")
        )
        
        if not output_dir:
            return
        
        # Now run your script generation code
        try:
            # Execute the script with appropriate parameters
            import subprocess
            
            # Create a temporary JSON file to pass to the generator
            temp_json = os.path.join(output_dir, "temp_config.json")
            with open(temp_json, 'w') as f:
                import json
                json.dump(self.app.signals_data, f)
            
            # Run the generator script
            cmd = [
                "python", script_path,
                "--config", temp_json,
                "--output", output_dir
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temporary file
            if os.path.exists(temp_json):
                os.remove(temp_json)
                
            if result.returncode == 0:
                QMessageBox.information(
                    self.app,
                    "Success",
                    f"Signal Manager code generated successfully in {output_dir}"
                )
            else:
                QMessageBox.critical(
                    self.app,
                    "Error",
                    f"Failed to generate code:\n{result.stderr}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self.app,
                "Error",
                f"Failed to generate Signal Manager code: {str(e)}"
            )
    
    def generate_ipc_manager(self):
        """Generate IPC Manager code"""
        # Check version information before exporting
        if not self.app.ui_helpers.check_version_for_export():
            return
            
        script_path = self.check_script_path("ipc_manager")
        if not script_path:
            return
        
        # Similar implementation to generate_signal_mgr
        # ...
    
    def generate_ipc_eth_mgr(self):
        """Generate IPC over Ethernet Manager code"""
        # Check version information before exporting
        if not self.app.ui_helpers.check_version_for_export():
            return
            
        script_path = self.check_script_path("ipc_eth_mgr")
        if not script_path:
            return
        
        # Similar implementation to generate_signal_mgr
        # ...
    
    def generate_signal_mgr_code(self):
        # Simple code generation example
        code = "/* Auto-generated Signal Manager Code */\n\n"
        code += "#include <stdio.h>\n"
        code += "#include <stdlib.h>\n"
        code += "#include \"signal_mgr.h\"\n\n"
        
        # Define signals
        code += "/* Signal definitions */\n"
        for signal_name, signal_info in self.app.signals_data.get("signals", {}).items():
            signal_type = signal_info.get("DataType", "INT32")
            code += f"static {signal_type} {signal_name}_value = {signal_info.get('InitValue', '0')};\n"
        
        # Create getter/setter functions
        code += "\n/* Signal accessor functions */\n"
        for signal_name, signal_info in self.app.signals_data.get("signals", {}).items():
            signal_type = signal_info.get("DataType", "INT32")
            # Getter
            code += f"{signal_type} get_{signal_name}(void)\n"
            code += "{\n"
            code += f"    return {signal_name}_value;\n"
            code += "}\n\n"
            # Setter
            code += f"void set_{signal_name}({signal_type} value)\n"
            code += "{\n"
            code += f"    {signal_name}_value = value;\n"
            code += "}\n\n"
        
        return code
