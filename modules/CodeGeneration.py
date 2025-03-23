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

    def check_get_required_details_for_generation(self) -> tuple:
        # Check version information before exporting
        if not self.app.ui_helpers.check_version_for_export():
            return

        # Get UI paths and settings
        ui = self.app.ui_helpers
        if not hasattr(self.app, 'ui_helpers'):
            QMessageBox.critical(self.app, "Error", "UI helpers not initialized.")
            return

        # Get script directory path
        if hasattr(ui, 'ScriptPathLineEdit'):
            script_directory = ui.ScriptPathLineEdit.text()
        else:
            QMessageBox.critical(self.app, "Error", "ScriptPathLineEdit not found.")
            return

        if not script_directory or not os.path.exists(script_directory):
            QMessageBox.critical(self.app, "Error", "Script directory path is not configured.")
            return

        # Get board name
        if hasattr(ui, 'boardListComboBox'):
            board_name = ui.boardListComboBox.currentText()
            if not board_name:
                QMessageBox.critical(self.app, "Error", "No board selected.")
                return
        else:
            QMessageBox.critical(self.app, "Error", "boardListComboBox not found.")
            return

        # Get output directory
        if hasattr(ui, 'OutPutPathLineEdit'):
            output_dir = ui.OutPutPathLineEdit.text()
        else:
            QMessageBox.critical(self.app, "Error", "OutPutPathLineEdit not found.")
            return

        if not output_dir:
            output_dir = QFileDialog.getExistingDirectory(self.app, "Select Output Directory", os.path.expanduser("~/"))
            if not output_dir:
                return
            if hasattr(ui, 'OutPutPathLineEdit'):
                ui.OutPutPathLineEdit.setText(output_dir)

        if output_dir and script_directory and board_name:
            return (script_directory, board_name, output_dir)
        else:
            return None

    def generate_signal_mgr(self):
        """Generate Signal Manager code"""

        #check and get required parameters
        details = self.check_get_required_details_for_generation()
        if not details:
            return

        output_dir, board_name, script_directory = details

        # Export data to Excel using existing function
        excel_path = os.path.join(output_dir, "signal_data.xlsx")
        if hasattr(self.app, 'file_ops') and hasattr(self.app.file_ops, 'export_to_excel'):
            success = self.app.file_ops.export_to_excel(excel_path)
            if not success or not os.path.exists(excel_path):
                QMessageBox.critical(self.app, "Error", "Failed to export data to Excel.")
                return
            else:
                # Determine python command
                python_cmd = "python"
                try:
                    import subprocess
                    result = subprocess.run(["python", "--version"], capture_output=True, text=True)
                    if result.returncode != 0:
                        result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
                        if result.returncode == 0:
                            python_cmd = "python3"
                        else:
                            QMessageBox.critical(self.app, "Error", "Python command not available.")
                            return
                except Exception:
                    pass

                # Run the generator script
                try:
                    script_path = os.path.join(script_directory, "main.py")
                    if not os.path.isfile(script_path):
                        QMessageBox.critical(self.app, "Error", f"Script not found: {script_path}")
                        return

                    cmd = [python_cmd, script_path, "-f", excel_path, "-i", "SigM", "-B", board_name, "-O", output_dir]
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    if result.returncode == 0:
                        QMessageBox.information(self.app, "Success", f"Signal Manager code generated in {output_dir}")
                    else:
                        QMessageBox.critical(self.app, "Error", f"Failed to generate code:\n{result.stderr}")
                except Exception as e:
                    QMessageBox.critical(self.app, "Error", f"Error: {str(e)}")

        else:
            QMessageBox.critical(self.app, "Error", "Export function not available.")
            return

    def generate_ipc_manager(self):
        """Generate IPC Manager code"""

        #check and get required parameters
        details = self.check_get_required_details_for_generation()
        if not details:
            return

        output_dir, board_name, script_directory = details

        # Export data to Excel using existing function
        excel_path = os.path.join(output_dir, "signal_data.xlsx")
        if hasattr(self.app, 'file_ops') and hasattr(self.app.file_ops, 'export_to_excel'):
            success = self.app.file_ops.export_to_excel(excel_path)
            if not success or not os.path.exists(excel_path):
                QMessageBox.critical(self.app, "Error", "Failed to export data to Excel.")
                return
            else:
                # Determine python command
                python_cmd = "python"
                try:
                    import subprocess
                    result = subprocess.run(["python", "--version"], capture_output=True, text=True)
                    if result.returncode != 0:
                        result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
                        if result.returncode == 0:
                            python_cmd = "python3"
                        else:
                            QMessageBox.critical(self.app, "Error", "Python command not available.")
                            return
                except Exception:
                    pass

                # Run the generator script
                try:
                    script_path = os.path.join(script_directory, "main.py")
                    if not os.path.isfile(script_path):
                        QMessageBox.critical(self.app, "Error", f"Script not found: {script_path}")
                        return

                    cmd = [python_cmd, script_path, "-f", excel_path, "-i", "IPC", "-B", board_name, "-O", output_dir]
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    if result.returncode == 0:
                        QMessageBox.information(self.app, "Success", f"IpcManager code generated in {output_dir}")
                    else:
                        QMessageBox.critical(self.app, "Error", f"Failed to generate code:\n{result.stderr}")
                except Exception as e:
                    QMessageBox.critical(self.app, "Error", f"Error: {str(e)}")

        else:
            QMessageBox.critical(self.app, "Error", "Export function not available.")
            return

    def generate_ipc_eth_mgr(self):
        """Generate IPC over Ethernet Manager code"""

        #check and get required parameters
        details = self.check_get_required_details_for_generation()
        if not details:
            return

        output_dir, board_name, script_directory = details

        # Export data to Excel using existing function
        excel_path = os.path.join(output_dir, "signal_data.xlsx")
        if hasattr(self.app, 'file_ops') and hasattr(self.app.file_ops, 'export_to_excel'):
            success = self.app.file_ops.export_to_excel(excel_path)
            if not success or not os.path.exists(excel_path):
                QMessageBox.critical(self.app, "Error", "Failed to export data to Excel.")
                return
            else:
                # Determine python command
                python_cmd = "python"
                try:
                    import subprocess
                    result = subprocess.run(["python", "--version"], capture_output=True, text=True)
                    if result.returncode != 0:
                        result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
                        if result.returncode == 0:
                            python_cmd = "python3"
                        else:
                            QMessageBox.critical(self.app, "Error", "Python command not available.")
                            return
                except Exception:
                    pass

                # Run the generator script
                try:
                    script_path = os.path.join(script_directory, "main.py")
                    if not os.path.isfile(script_path):
                        QMessageBox.critical(self.app, "Error", f"Script not found: {script_path}")
                        return

                    cmd = [python_cmd, script_path, "-f", excel_path, "-i", "IpcOvEth", "-B", board_name, "-O", output_dir]
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    if result.returncode == 0:
                        QMessageBox.information(self.app, "Success", f"Signal Manager code generated in {output_dir}")
                    else:
                        QMessageBox.critical(self.app, "Error", f"Failed to generate code:\n{result.stderr}")
                except Exception as e:
                    QMessageBox.critical(self.app, "Error", f"Error: {str(e)}")

        else:
            QMessageBox.critical(self.app, "Error", "Export function not available.")
            return

    def generate_header_file(self, output_path=None):
        """
        Generate a header file (.h) containing signal definitions.

        Args:
            output_path (str, optional): Path where the header file should be saved.
                If None, a file dialog will prompt for the location.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            if output_path is None:
                # Get the default directory from settings or use a default
                default_dir = self.settings.get('last_export_dir', '')
                # Open file dialog to get the save location
                output_path, _ = QFileDialog.getSaveFileName(
                    self.parent,
                    "Save Header File",
                    default_dir,
                    "Header Files (*.h)"
                )

                if not output_path:  # User canceled
                    return False

                # Save the directory for next time
                self.settings['last_export_dir'] = os.path.dirname(output_path)

            # Ensure the file has the correct extension
            if not output_path.lower().endswith('.h'):
                output_path += '.h'

            # Generate the header file content
            header_content = self._generate_header_content()

            # Write to file
            with open(output_path, 'w') as file:
                file.write(header_content)

            QMessageBox.information(
                self.parent,
                "Success",
                f"Header file generated successfully at:\n{output_path}"
            )
            return True

        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Failed to generate header file:\n{str(e)}"
            )
            return False

    def _generate_header_content(self):
        """
        Generate the content for the header file.

        Returns:
            str: The content of the header file.
        """
        # Get the current date and time
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        # Start with the header guard and includes
        header = f"""/**
        * @file signal_definitions.h
        * @brief Auto-generated signal definitions
        * @date {date_str}
        */

        #ifndef SIGNAL_DEFINITIONS_H
        #define SIGNAL_DEFINITIONS_H

        #include <stdint.h>

        """

        # Add signal definitions
        # This will depend on your specific requirements and data structure
        signals = self._get_signals()

        # Add enum or define statements for each signal
        header += "/* Signal Definitions */\n"
        header += "typedef enum {\n"

        for i, signal in enumerate(signals):
            header += f"    {signal['name']} = {signal['id']},\n"

        header += "    SIGNAL_COUNT\n"
        header += "} SignalId_t;\n\n"

        # Add any additional structures or declarations

        # Close the header guard
        header += "\n#endif /* SIGNAL_DEFINITIONS_H */\n"

        return header

    def _get_signals(self):
        """
        Get the list of signals to include in the header file.

        Returns:
            list: A list of signal dictionaries.
        """
        # This implementation will depend on how signals are stored in your application
        # For now, return a placeholder
        return self.parent.signal_model.get_all_signals() if hasattr(self.parent, 'signal_model') else []
