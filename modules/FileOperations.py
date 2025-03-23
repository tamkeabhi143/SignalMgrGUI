import os
import json
import pandas as pd
import numpy as np
import copy  # Make sure this import is at the top
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from icecream import ic
from datetime import datetime

class FileOperations:
    def __init__(self, app):
        self.app = app

    def open_file(self, specified_file_path=None):
        """Open signal manager file and load data"""
        try:
            # Determine file path to open
            file_path = specified_file_path

            # If not specified, show file dialog
            if file_path is None:
                file_path, _ = QFileDialog.getOpenFileName(
                    self.app,
                    "Open Signal Manager File",
                    "",
                    "Signal Manager Files (*.sgm *.json);;All Files (*)"
                )

            if not file_path:
                return False  # User cancelled

            print(f"Open file operation starting")

            # Disconnect UI signals to prevent crashes during loading
            """ try:
                if hasattr(self.app.ui_helpers, '_disconnect_ui_signals'):
                    self.app.ui_helpers._disconnect_ui_signals()
                    print("UI signals temporarily disconnected")
            except Exception as e:
                print(f"Error disconnecting UI signals: {e}") """

            # Make sure UI is responsive during file loading
            QtWidgets.QApplication.processEvents()

            # Load file content
            with open(file_path, 'r') as f:
                loaded_data = json.load(f)

            print("File loaded successfully")

            # Update the app with loaded data
            self.app.signals_data = loaded_data
            self.app.modified = False
            self.app.current_file = file_path

            print("Populating UI with loaded data")

            # Initialize the current_section from metadata
            metadata = loaded_data.get("metadata", {})
            if "current_section" in metadata:
                self.app.current_section = metadata["current_section"]

            # Process events to keep UI responsive
            QtWidgets.QApplication.processEvents()

            # Ensure SOC and Build type lists are populated
            self.app.ui_helpers.populate_soc_list()
            self.app.ui_helpers.populate_build_types()

            # Process events again before refreshing tree
            QtWidgets.QApplication.processEvents()

            print("Refreshing signal tree")
            self.app.ui_helpers.refresh_signal_tree()

            # Process events before updating core info
            QtWidgets.QApplication.processEvents()

            print("Updating core info")
            self.app.ui_helpers.update_core_info()

            # Initialize version fields from metadata without validation
            print("Initializing version fields")
            self.app.ui_helpers.initialize_version_fields(skip_validation=False)

            # Explicitly update editor and description fields from metadata
            editor_name = metadata.get("editor", "")
            description = metadata.get("description", "")

            # Force set the UI elements
            # Handle VersionUpdateName field if it exists
            if hasattr(self.app.ui, 'VersionUpdateName'):
                self.app.ui.VersionUpdateName.setPlaceholderText(editor_name)
                self.app.ui.VersionUpdateName.setPlainText("")  # Clear text to show placeholder

            # Set editor name in EditorName field
            elif hasattr(self.app.ui, 'EditorName'):
                if hasattr(self.app.ui.EditorName, 'setPlaceholderText'):
                    self.app.ui.EditorName.setPlaceholderText(editor_name)
                else:
                    # Fallback to traditional methods if setPlaceholderText isn't available
                    if hasattr(self.app.ui.EditorName, 'setPlainText'):
                        self.app.ui.EditorName.setPlainText(editor_name)
                    elif hasattr(self.app.ui.EditorName, 'setText'):
                        self.app.ui.EditorName.setText(editor_name)

            if hasattr(self.app.ui, 'VersionDescription'):
                if hasattr(self.app.ui.VersionDescription, 'setPlainText'):
                    self.app.ui.VersionDescription.setPlainText(description)
                elif hasattr(self.app.ui.VersionDescription, 'setText'):
                    self.app.ui.VersionDescription.setText(description)

            # Update signal count and window title - this is a critical section
            # that might cause the segfault
            print("Updating signal count display")
            try:
                # Process events before attempting to update UI
                QtWidgets.QApplication.processEvents()

                # First ensure SignalCnt exists or is properly set up
                # This is a defensive approach where we double-check that
                # the signal count widget exists before accessing it
                if not hasattr(self.app.ui, 'SignalCnt') or self.app.ui.SignalCnt is None:
                    print("Initializing SignalCnt widget before updating")
                    # Find the widget by name/type in the UI
                    signal_cnt = self.app.findChild(QtWidgets.QSpinBox, "SignalCnt")
                    if signal_cnt:
                        print("Found SignalCnt widget via search")
                        self.app.ui.SignalCnt = signal_cnt
                    else:
                        # If not found, try to create it
                        self.app.ui_helpers._create_signal_count_widgets()

                # Process events after widget setup
                QtWidgets.QApplication.processEvents()

                # Once we're sure widget exists, calculate and set the count
                if hasattr(self.app.ui, 'SignalCnt') and self.app.ui.SignalCnt is not None:
                    signal_count = len(self.app.signals_data.get("signals", {}))
                    self.app.ui.SignalCnt.setValue(signal_count)
                    print(f"Signal count updated to {signal_count}")
                else:
                    print("WARNING: SignalCnt widget not available after init attempt")

                # Update window title separately from signal count
                self.app.ui_helpers.update_window_title()
            except Exception as e:
                print(f"Error updating UI after file load: {e}")
                import traceback
                traceback.print_exc()

            # Make sure UI is responsive during file loading complete
            QtWidgets.QApplication.processEvents()

            # Reconnect UI signals
            try:
                if hasattr(self.app.ui_helpers, '_reconnect_ui_signals'):
                    self.app.ui_helpers._reconnect_ui_signals()
                    print("UI signals reconnected")
            except Exception as e:
                print(f"Error reconnecting UI signals: {e}")

            # Final processEvents to ensure UI is updated
            QtWidgets.QApplication.processEvents()

            # Only show success message if file was opened via dialog
            if specified_file_path is None:
                QMessageBox.information(self.app, "Success", f"File loaded: {file_path}")

            self.app.modified = False
            self.app.ui_helpers.update_window_title()
            return True

        except json.JSONDecodeError as e:
            QMessageBox.critical(self.app, "Error", f"Invalid JSON format in file: {str(e)}")
            print(f"JSON decode error: {e}")
            # Make sure UI elements remain responsive
            QtWidgets.QApplication.processEvents()
            # Try to reconnect signals that might have been disconnected
            try:
                self.app.ui_helpers._reconnect_ui_signals()
                print("UI signals reconnected after error")
            except:
                pass
            return False
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Failed to read file: {str(e)}")
            print(f"File read error: {e}")
            import traceback
            traceback.print_exc()
            # Make sure UI elements remain responsive
            QtWidgets.QApplication.processEvents()
            # Try to reconnect signals that might have been disconnected
            try:
                self.app.ui_helpers._reconnect_ui_signals()
                print("UI signals reconnected after error")
            except:
                pass
            return False

    def save_file(self):
        """Save file with version check"""
        # Check version information before saving
        if not self.app.ui_helpers.check_version_for_export():
            return

        # Additional validation for editor name
        editor_name = ""
        # First check for EditorName field
        if hasattr(self.app.ui, 'EditorName'):
            editor_name = self.app.ui.EditorName.toPlainText().strip()
        # If EditorName is not available or empty, check for VersionUpdateName
        if (not hasattr(self.app.ui, 'EditorName') or not editor_name) and hasattr(self.app.ui, 'VersionUpdateName'):
            editor_name = self.app.ui.VersionUpdateName.toPlainText().strip()

        # Validate editor name
        if not editor_name or editor_name.isspace() or editor_name.lower() == "enter your name":
            QMessageBox.warning(
                self.app,
                "Invalid Editor Name",
                "Please enter your name in the 'Modifier Name' field before saving."
            )
            # Switch to Core Configuration tab and focus on appropriate name field
            self.app.ui.tabWidget.setCurrentIndex(0)
            if hasattr(self.app.ui, 'EditorName'):
                self.app.ui.EditorName.setFocus()
            elif hasattr(self.app.ui, 'VersionUpdateName'):
                self.app.ui.VersionUpdateName.setFocus()
            return

        # Ensure the latest version information from UI is captured in signals_data
        self.app.ui_helpers.update_version_info(skip_validation=True)

        # Continue with save
        if not self.app.current_file or not os.path.exists(self.app.current_file):
            # If current_file doesn't exist (e.g., it was a temporary file that was deleted)
            # or if no current file is set, prompt for save location
            self.save_file_as()
        else:
            try:
                with open(self.app.current_file, 'w') as file:
                    json.dump(self.app.signals_data, file, indent=4)
                self.app.modified = False

                # After saving, the file is no longer using default values
                self.app.ui_helpers.using_default_values = False

                # Store a copy of the saved state as the original for future comparisons
                import copy
                self.app.ui_helpers.original_signals_data = copy.deepcopy(self.app.signals_data)

                self.app.ui_helpers.update_window_title()
                QMessageBox.information(self.app, "Success", f"File saved: {self.app.current_file}")
            except Exception as e:
                QMessageBox.critical(self.app, "Error", f"Failed to save file: {str(e)}")
                # If save fails, offer to save as a different file
                reply = QMessageBox.question(
                    self.app,
                    "Save Error",
                    f"Failed to save to {self.app.current_file}. Would you like to save to a different location?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.save_file_as()

    def save_file_as(self):
        """Save file as with version check"""
        # Check version information before saving
        if not self.app.ui_helpers.check_version_for_export():
            return

        # Ensure the latest version information from UI is captured in signals_data
        self.app.ui_helpers.update_version_info(skip_validation=True)

        file_path, _ = QFileDialog.getSaveFileName(self.app, "Save Signal Configuration", "",
                                                  "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.app.current_file = file_path
            self.save_file()

    def create_new_file(self):
        if self.app.ui_helpers.check_unsaved_changes():
            # Clear current file path
            self.app.current_file = None

            # Reset to default signal data structure with proper metadata
            self.app.signals_data = {
                "metadata": {
                    "version": self.app.ui_helpers.default_version_info["version"],
                    "date": self.app.ui_helpers.default_version_info["date"],
                    "editor": self.app.ui_helpers.default_version_info["editor"],
                    "description": self.app.ui_helpers.default_version_info["description"]
                },
                "soc_type": "Windows",
                "build_type": "SMP",
                "soc_list": ["Windows"],
                "build_list": ["SMP"],
                "core_info": {},
                "signals": {}
            }

            # For create_new_file, we don't want to use default values automatically
            # Instead, let the user provide their own values
            self.app.ui_helpers.using_default_values = False
            self.app.ui_helpers.first_run_or_closed = False

            # Reset modified flag
            self.app.modified = False

            # Update UI elements
            self.app.ui_helpers.initialize_version_fields()
            self.app.ui_helpers.refresh_signal_tree()
            self.app.ui_helpers.update_signal_count_display()
            self.app.ui_helpers.update_window_title()

            # Open configuration manager to set up the new file
            self.app.signal_ops.open_configuration_manager(is_new_file=True)

    def export_to_excel(self, excel_path=None):
        """Export to Excel with version check"""
        # Check version information before exporting
        if not self.app.ui_helpers.check_version_for_export():
            return

        if not self.app.signals_data:
            QMessageBox.warning(self.app, "Warning", "No configuration data to export")
            return

        # Get editor name from EditorName or VersionUpdateName
        editor_name = ""
        if hasattr(self.app.ui, 'EditorName') and hasattr(self.app.ui.EditorName, 'toPlainText'):
            editor_name = self.app.ui.EditorName.toPlainText().strip()
        elif hasattr(self.app.ui, 'VersionUpdateName') and hasattr(self.app.ui.VersionUpdateName, 'toPlainText'):
            editor_name = self.app.ui.VersionUpdateName.toPlainText().strip()

        if not editor_name or editor_name.lower() == "enter your name":
            if excel_path is None:
                # Highlight appropriate name field and show warning
                self.app.ui.tabWidget.setCurrentIndex(0)
                field = self.app.ui.EditorName if hasattr(self.app.ui, 'EditorName') else self.app.ui.VersionUpdateName
                field.setFocus()
                field.setStyleSheet("background-color: #ffcccc;")
                QMessageBox.warning(self.app, "Required Field Missing",
                                   "Export stopped. Please enter your name in the name field and try again.")
                QtCore.QTimer.singleShot(3000, lambda: field.setStyleSheet(""))
                return

        if excel_path is not None or excel_path == "":
            # Export to the specified path
            file_path = excel_path
        else:
            file_path, _ = QFileDialog.getSaveFileName(self.app, "Export to Excel", "",
                                                     "Excel Files (*.xlsx *.xls)")
        if file_path:
            try:
                # Create Excel writer with xlsxwriter
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    # Get workbook and create formats
                    workbook = writer.book

                    # Create formatting options
                    center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
                    header_format = workbook.add_format({
                        'align': 'center',
                        'valign': 'vcenter',
                        'bg_color': '#c6efce',  # Light green color for headers
                        'bold': True,
                        'border': 1  # Add border to all cells
                    })
                    data_format = workbook.add_format({
                        'align': 'center',
                        'valign': 'vcenter',
                        'bg_color': '#c0c0c0',   # Darker gray color
                        'border': 1  # Add border to all cells
                    })

                    # Export Version data to Version sheet
                    if not self.export_version_data(writer, 'Version', header_format, data_format):
                        return  # Exit if version data export fails (missing fields)

                    # Export configuration data to Config sheet
                    self.export_config_data(writer, 'Config', header_format, data_format)

                    # Export signals data to LookUpTable sheet
                    if self.app.signals_data.get("signals"):
                        self.export_signals_data(writer, 'LookUpTable', header_format, data_format)

                QMessageBox.information(self.app, "Success", f"Exported to Excel: {file_path}")
            except Exception as e:
                QMessageBox.critical(self.app, "Error", f"Failed to export to Excel: {str(e)}")
                import traceback
                traceback.print_exc()  # Print detailed error for debugging

    def export_version_data(self, writer, sheet_name, header_format=None, data_format=None):
        """Export version metadata to Excel"""
        # Check if version fields are properly filled in the UI
        editor_name = ""
        description = ""

        # Get editor name from GUI
        # Try to get editor name from EditorName or VersionUpdateName
        editor_name = ""
        if hasattr(self.app.ui, 'EditorName'):
            editor_name = self.app.ui.EditorName.toPlainText().strip() if hasattr(self.app.ui.EditorName, 'toPlainText') else self.app.ui.EditorName.text().strip()

        # If EditorName is missing or empty, check VersionUpdateName
        if not editor_name and hasattr(self.app.ui, 'VersionUpdateName'):
            editor_name = self.app.ui.VersionUpdateName.toPlainText().strip() if hasattr(self.app.ui.VersionUpdateName, 'toPlainText') else self.app.ui.VersionUpdateName.text().strip()

        # Check if editor name is missing or has default value
        if not editor_name or editor_name.lower() == "enter your name":
            QMessageBox.warning(
            self.app,
            "Required Information Missing",
            "Please enter your name in the Editor Name field before exporting."
            )

            # Switch to Core Configuration tab and focus on appropriate field
            self.app.ui.tabWidget.setCurrentIndex(0)

            # Focus on the available field
            field = self.app.ui.EditorName if hasattr(self.app.ui, 'EditorName') else self.app.ui.VersionUpdateName
            field.setFocus()
            field.setStyleSheet("background-color: #ffcccc;")  # Light red background
            QtWidgets.QTimer.singleShot(3000, lambda: field.setStyleSheet(""))
            return False

        # Check if description is available in the UI
        if hasattr(self.app.ui, 'VersionDescription'):
            if hasattr(self.app.ui.VersionDescription, 'toPlainText'):
                description = self.app.ui.VersionDescription.toPlainText().strip()
            elif hasattr(self.app.ui.VersionDescription, 'text'):
                description = self.app.ui.VersionDescription.text().strip()
        else:
            # If VersionDescription is missing, prompt user for a description
            description = ""
            msg_box = QtWidgets.QInputDialog(self.app)
            msg_box.setWindowTitle("Description Required")
            msg_box.setLabelText("Please enter a description for this export:")
            msg_box.setInputMode(QtWidgets.QInputDialog.TextInput)
            msg_box.resize(400, 200)

            if msg_box.exec_() == QtWidgets.QInputDialog.Accepted:
                description = msg_box.textValue()
                # Update both the UI element and the signals_data
                self.app.signals_data["metadata"]["description"] = description
                # Create VersionDescription if it doesn't exist
                if not hasattr(self.app.ui, 'VersionDescription'):
                    self.app.ui.VersionDescription = QtWidgets.QPlainTextEdit()
                self.app.ui.VersionDescription.setPlainText(description)
            else:
                # Default description if user cancels
                description = "Exported configuration"
                self.app.signals_data["metadata"]["description"] = description

        # Always update metadata from GUI to ensure we have latest values
        self.app.ui_helpers.update_version_info(skip_validation=True)

        # Get updated metadata after the update
        metadata = self.app.signals_data.get("metadata", {})
        version = metadata.get("version", "1.0")
        date = metadata.get("date", pd.Timestamp("today").strftime('%Y-%m-%d'))
        editor = metadata.get("editor", "")
        description = metadata.get("description", "")

        # Create DataFrame with version information
        version_data = pd.DataFrame({
            'Version': [version],
            'Date': [date],
            'Last Modified By': [editor],
            'Description': [description]
        })

        # Don't write with pandas and then overwrite - use one approach
        # Create the worksheet
        worksheet = writer.book.add_worksheet(sheet_name)
        writer.sheets[sheet_name] = worksheet

        # Apply formatting if formats are provided
        if header_format and data_format:
            # Auto-fit column widths based on content
            for i, col in enumerate(version_data.columns):
                # Find the maximum length in the column (including header)
                max_len = max(
                    len(str(col)),
                    version_data[col].astype(str).map(len).max()
                )
                # Set column width (add a little padding)
                worksheet.set_column(i, i, max_len + 2)

            # Apply header formatting
            for col_num, col_name in enumerate(version_data.columns):
                worksheet.write(0, col_num, col_name, header_format)

            # Apply data formatting to all data cells
            for row_num in range(1, len(version_data) + 1):
                for col_num in range(len(version_data.columns)):
                    worksheet.write(row_num, col_num, version_data.iloc[row_num-1, col_num], data_format)
        else:
            # If no formatting provided, just use pandas
            version_data.to_excel(writer, sheet_name=sheet_name, index=False)

        if self.app.current_file is not None:
            # Update Window State
            self.app.modified = False
            self.app.ui_helpers.update_window_title()

        return True  # Indicate successful export

    def export_config_data(self, writer, sheet_name, header_format=None, data_format=None):
        """Export configuration data to Excel sheet"""
        # Create a DataFrame with SOC and Build Type information
        soc_build_data = {
            'SOC Name': [self.app.signals_data.get('soc_type', '')],
            'TypeOfBin': [self.app.signals_data.get('build_type', '')]
        }
        soc_build_df = pd.DataFrame(soc_build_data)

        # Create a DataFrame with Core information
        core_info = self.app.signals_data.get("core_info", {})
        core_data = []

        if core_info:
            for soc_name, cores in core_info.items():
                for core_name, core_data_entry in cores.items():
                    # Check if it's a dictionary (updated format) or string (legacy format)
                    if isinstance(core_data_entry, dict):
                        # Extract core properties correctly from the dictionary
                        core_data.append({
                            'SOC': soc_name,
                            'CORE': core_name,
                            'Master/Slave': 'Master' if core_data_entry.get('is_master', False) else 'Slave',
                            'Is Qnx Core ?': 'Yes' if core_data_entry.get('is_qnx', False) else 'No',
                            'Is Autosar Compliant ?': 'Yes' if core_data_entry.get('is_autosar', False) else 'No',
                            'Is Sim Core ?': 'Yes' if core_data_entry.get('is_sim', False) else 'No',
                            'OS': core_data_entry.get('os', 'Unknown'),
                            'SOC Family': core_data_entry.get('soc_family', 'Unknown')
                        })
                    else:
                        # Legacy format with just a description string
                        # Update in-memory representation for future operations
                        legacy_props = {
                            "description": str(core_data_entry),
                            "is_master": False,
                            "is_qnx": False,
                            "is_autosar": False,
                            "is_sim": False,
                            "os": "Unknown",
                            "soc_family": "Unknown"
                        }
                        self.app.signals_data["core_info"][soc_name][core_name] = legacy_props

                        # Add to core_data for export
                        core_data.append({
                            'SOC': soc_name,
                            'CORE': core_name,
                            'Master/Slave': 'Slave',  # Default value
                            'Is Qnx Core ?': 'No',
                            'Is Autosar Compliant ?': 'No',
                            'Is Sim Core ?': 'No',
                            'OS': 'Unknown',
                            'SOC Family': 'Unknown'
                        })

        # Create the worksheet before accessing it
        worksheet = writer.book.add_worksheet(sheet_name)
        writer.sheets[sheet_name] = worksheet

        # Create formatting if not provided
        if data_format is None:
            data_format = writer.book.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#c0c0c0',  # Darker gray background for data cells
                'border': 1  # Add border for all cells
            })

        if header_format is None:
            header_format = writer.book.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#c6efce',  # Light green for headers
                'bold': True,
                'border': 1  # Add border for all cells
            })

        # Write SOC and Build Type to Excel
        soc_build_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0, index=False)

        # Apply formatting to SOC and Build Type
        # Auto-fit column widths for SOC and Build Type
        for i, col in enumerate(soc_build_df.columns):
            max_len = max(
                len(str(col)),
                soc_build_df[col].astype(str).map(len).max()
            )
            worksheet.set_column(i, i, max_len + 2)

        # Apply header formatting for SOC and Build Type
        for col_num, col_name in enumerate(soc_build_df.columns):
            worksheet.write(0, col_num, col_name, header_format)

        # Apply data formatting for SOC and Build Type - explicitly format each cell
        for row_num in range(1, len(soc_build_df) + 1):
            for col_num in range(len(soc_build_df.columns)):
                cell_value = soc_build_df.iloc[row_num-1, col_num]
                # Ensure empty cells still get formatting
                if pd.isna(cell_value):
                    cell_value = ""
                worksheet.write(row_num, col_num, cell_value, data_format)

        # Write Core data if available
        if core_data:
            cores_df = pd.DataFrame(core_data)
            cores_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=4, index=False)

            # Apply formatting to Core data
            # Auto-fit column widths for core data
            for i, col in enumerate(cores_df.columns):
                max_len = max(
                    len(str(col)),
                    cores_df[col].astype(str).map(len).max()
                )
                worksheet.set_column(i+4, i+4, max_len + 2)

            # Apply header formatting for core data
            for col_num, col_name in enumerate(cores_df.columns):
                worksheet.write(0, col_num+4, col_name, header_format)

            # Apply data formatting for core data - explicitly format each cell
            for row_num in range(1, len(cores_df) + 1):
                for col_num in range(len(cores_df.columns)):
                    cell_value = cores_df.iloc[row_num-1, col_num]
                    # Ensure empty cells still get formatting
                    if pd.isna(cell_value):
                        cell_value = ""
                    worksheet.write(row_num, col_num+4, cell_value, data_format)

    def export_signals_data(self, writer, sheet_name, header_format=None, data_format=None):
        """Export signal data to Excel sheet"""
        # Get signal data
        signals = self.app.signals_data.get("signals", {})
        if not signals:
            return

        # Get the list of all configured cores
        available_cores = self.app.ui_helpers.get_available_cores()

        # Prepare data for DataFrame
        signal_rows = []

        for signal_name, signal_info in signals.items():
            # Create base row without description first
            row = {
                'Data_Type': signal_name,
                'Variable_Port_Name': signal_info.get('Variable_Port_Name', ''),
                'Memory Region': signal_info.get('Memory Region', ''),
                'Buffer count_IPC': signal_info.get('Buffer count_IPC', ''),
                'Type': signal_info.get('Type', ''),
                'InitValue': signal_info.get('InitValue', ''),
                'Notifiers': 'Yes' if signal_info.get('Notifiers', False) else 'No',
                'Source': signal_info.get('Source', ''),
                'Impl_Approach': signal_info.get('Impl_Approach', ''),
                'GetObjRef': 'Yes' if signal_info.get('GetObjRef', False) else 'No',
                'SM_Buff_Count': signal_info.get('SM_Buff_Count', ''),
                'Timeout': signal_info.get('Timeout', ''),
                'Periodicity': signal_info.get('Periodicity', ''),
                'ASIL': signal_info.get('ASIL', ''),
                'Checksum': signal_info.get('Checksum', '') if signal_info.get('Checksum') else 'None',
                'DataType': signal_info.get('DataType', 'INT32'),
            }

            # Add core destinations before description
            for core in available_cores:
                core_key = f"core_{core.replace('.', '_')}"
                row[core] = 'Yes' if signal_info.get(core_key, False) else 'No'

            # Add description at the end
            row['description'] = signal_info.get('description', '')

            signal_rows.append(row)

        if signal_rows:
            # Create DataFrame and write to Excel
            signals_df = pd.DataFrame(signal_rows)
            signals_df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Apply formatting if formats are provided
            if header_format and data_format:
                worksheet = writer.sheets[sheet_name]

                # Auto-fit column widths
                for i, col in enumerate(signals_df.columns):
                    # Find the maximum length in the column (including header)
                    max_len = max(
                        len(str(col)),
                        signals_df[col].astype(str).map(len).max()
                    )
                    # Set column width (add a little padding)
                    worksheet.set_column(i, i, max_len + 2)

                # Write 'Index' header first, then the other headers (shifted right by 1)
                worksheet.write(0, 0, 'Index', header_format)
                for col_num, col_name in enumerate(signals_df.columns):
                    worksheet.write(0, col_num + 1, col_name, header_format)

                # Calculate max lengths for each column including the index column
                col_widths = [len('Index')]  # For index column
                for col in signals_df.columns:
                    # Find max length between column name and data
                    max_len = max(
                        len(str(col)),
                        signals_df[col].astype(str).map(len).max()
                    )
                    col_widths.append(max_len)

                # Set column widths (adding padding)
                for col_num, width in enumerate(col_widths):
                    worksheet.set_column(col_num, col_num, width + 2)

                # Write row number as index, then the data (shifted right by 1)
                for row_num in range(1, len(signals_df) + 1):
                    # Write the row number in column 0 as 'Index'
                    worksheet.write(row_num, 0, row_num, data_format)
                    # Write the actual data shifted right by 1
                    for col_num in range(len(signals_df.columns)):
                        worksheet.write(row_num, col_num + 1, signals_df.iloc[row_num-1, col_num], data_format)

                # Freeze the first three columns (Index, Data_Type, Variable_Port_Name)
                worksheet.freeze_panes(1, 3)

    def import_from_excel(self):
        """Import signal data from an Excel file"""
        # Only prompt to save if:
        # 1. Modified flag is True AND
        # 2. There's a current file OR actual signal data
        if self.app.modified and (self.app.current_file is not None or
                                 len(self.app.signals_data.get("signals", {})) > 0):
            reply = QMessageBox.question(
                self.app, 'Unsaved Changes',
                'You have unsaved changes. Do you want to save them before importing?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        file_path, _ = QFileDialog.getOpenFileName(
            self.app,
            "Import Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if not file_path:
            return

        try:
            # Read configuration from Excel
            imported_data = self.read_excel_config(file_path)

            if imported_data:
                # Create temporary file name based on the Excel file
                excel_name = os.path.basename(file_path)
                excel_name_without_ext = os.path.splitext(excel_name)[0]
                temp_file_name = f"{excel_name_without_ext}_imported.json"

                # Create temporary file path in the same directory as the Excel file
                excel_dir = os.path.dirname(file_path)
                temp_json_path = os.path.join(excel_dir, temp_file_name)

                # Write the imported data to the temporary JSON file
                with open(temp_json_path, 'w') as temp_file:
                    json.dump(imported_data, temp_file, indent=4)

                # Open the temporary file
                success = self.open_file(temp_json_path)

                if success:
                    # Ensure metadata was properly imported
                    metadata = imported_data.get("metadata", {})

                    # Explicitly set editor name and description again to ensure they are properly updated
                    editor_name = metadata.get("editor", "")
                    description = metadata.get("description", "")

                    # Force update the UI fields
                    if hasattr(self.app.ui, 'EditorName'):
                        self.app.ui.EditorName.setPlaceholderText(editor_name)
                        self.app.ui.EditorName.setPlainText("")  # Clear text to show placeholder
                    elif hasattr(self.app.ui, 'VersionUpdateName'):
                        self.app.ui.VersionUpdateName.setPlaceholderText(editor_name)
                        self.app.ui.VersionUpdateName.setPlainText("")  # Clear text to show placeholder

                    # Update description field
                    if hasattr(self.app.ui, 'VersionDescription'):
                        self.app.ui.VersionDescription.setPlainText(description)

                    # Per user requirement: mark as NOT modified after import
                    # Store the current state as the baseline to prevent detecting changes
                    import copy
                    self.app.ui_helpers.original_signals_data = copy.deepcopy(self.app.signals_data)

                    # Set to unmodified state (no changes)
                    self.app.modified = False

                    # Keep the temporary file path as current file for UI display
                    # self.app.current_file is already set by open_file()

                    # Update window title to reflect the imported Excel filename
                    self.app.ui_helpers.update_window_title()

                    QMessageBox.information(
                        self.app,
                        "Import Successful",
                        f"Successfully imported configuration from Excel: {excel_name}"
                    )

                # Delete the temporary file but keep the path for display
                try:
                    if os.path.exists(temp_json_path):
                        os.remove(temp_json_path)
                        print(f"Temporary file deleted: {temp_json_path}")
                except Exception as e:
                    print(f"Could not delete temporary file: {e}")
            else:
                QMessageBox.warning(
                    self.app,
                    "Import Warning",
                    "No valid data found in the Excel file."
                )

        except Exception as e:
            QMessageBox.critical(
                self.app,
                "Import Failed",
                f"Failed to import Excel file:\n{str(e)}"
            )

    def read_excel_config(self, file_path):
        """Read configuration from Excel file"""
        try:
            # Get all sheet names
            xl = pd.ExcelFile(file_path)
            sheet_names = xl.sheet_names

            # Initialize config data with default metadata
            current_date = pd.Timestamp('today').strftime('%Y-%m-%d')
            config_data = {
                "metadata": {
                    "version": "1.0",
                    "date": current_date,
                    "editor": "",
                    "description": "Imported from Excel"
                },
                "soc_type": "Windows",  # Default SOC
                "build_type": "SMP",    # Default Build Type
                "soc_list": ["Windows"],    # List containing only the current SOC
                "build_list": ["SMP"],      # List containing only the current build type
                "core_info": {},
                "signals": {}
            }

            # Try to read Version sheet first
            if 'Version' in sheet_names:
                try:
                    version_df = pd.read_excel(file_path, sheet_name='Version')
                    if not version_df.empty:
                        # Extract version data from first row
                        row = version_df.iloc[0]
                        if pd.notna(row.get('Version')):
                            config_data["metadata"]["version"] = str(row['Version'])
                        if pd.notna(row.get('Date')):
                            # Try to format the date properly
                            try:
                                date_value = pd.to_datetime(row['Date'])
                                config_data["metadata"]["date"] = date_value.strftime('%Y-%m-%d')
                            except:
                                # If date parsing fails, keep default
                                pass
                        if pd.notna(row.get('Last Modified By')):
                            config_data["metadata"]["editor"] = str(row['Last Modified By'])
                        elif pd.notna(row.get('Editor')):  # Try alternative column name
                            config_data["metadata"]["editor"] = str(row['Editor'])
                        # Ensure Description is captured and preserved
                        for desc_column in ['Description', 'description', 'DESCRIPTION', 'Desc', 'DESC']:
                            if desc_column in version_df.columns and pd.notna(row.get(desc_column)):
                                config_data["metadata"]["description"] = str(row[desc_column])
                                print(f"Found description in column '{desc_column}': {config_data['metadata']['description']}")  # Debug print to help troubleshoot
                        print(f"Imported metadata: {config_data['metadata']}")  # Debug print
                except Exception as e:
                    print(f"Error parsing Version sheet: {str(e)}")

            # Check if Config sheet exists
            if 'Config' in sheet_names:
                try:
                    config_df = pd.read_excel(file_path, sheet_name='Config')
                    if not config_df.empty:
                        if 'SOC Name' in config_df.columns:
                            soc_name = config_df.iloc[0]['SOC Name']
                            if pd.notna(soc_name):
                                config_data["soc_type"] = str(soc_name)
                                if str(soc_name) not in config_data["soc_list"]:
                                    config_data["soc_list"].append(str(soc_name))
                        if 'TypeOfBin' in config_df.columns:
                            build_type = config_df.iloc[0]['TypeOfBin']
                            if pd.notna(build_type):
                                config_data["build_type"] = str(build_type)
                                if str(build_type) not in config_data["build_list"]:
                                    config_data["build_list"].append(str(build_type))

                        # Check if core columns exist
                        core_cols = ['SOC', 'CORE']
                        if all(col in config_df.columns for col in core_cols):
                            # Initialize core_info structure
                            core_info = {}
                            for _, row in config_df.iterrows():
                                soc_name = str(row['SOC'])
                                core_name = str(row['CORE'])

                                # Initialize SOC in core_info if not exists
                                if soc_name not in core_info:
                                    core_info[soc_name] = {}

                                # Convert NaN to appropriate values for boolean fields
                                is_master = str(row.get('Master/Slave', '')).lower() == "master" if pd.notna(row.get('Master/Slave', '')) else False
                                is_qnx = str(row.get('Is Qnx Core ?', '')).lower() == "yes" if pd.notna(row.get('Is Qnx Core ?', '')) else False
                                is_autosar = str(row.get('Is Autosar Compliant ?', '')).lower() == "yes" if pd.notna(row.get('Is Autosar Compliant ?', '')) else False
                                is_sim = str(row.get('Is Sim Core ?', '')).lower() == "yes" if pd.notna(row.get('Is Sim Core ?', '')) else False

                                # Create core properties
                                core_props = {
                                    "description": str(row.get('Description', "")) if pd.notna(row.get('Description', '')) else "",
                                    "is_master": is_master,
                                    "is_qnx": is_qnx,
                                    "is_autosar": is_autosar,
                                    "is_sim": is_sim,
                                    "os": str(row.get('OS', "Unknown")) if pd.notna(row.get('OS', '')) else "Unknown",
                                    "soc_family": str(row.get('SOC Family', "Unknown")) if pd.notna(row.get('SOC Family', '')) else "Unknown"
                                }

                                # Add core to SOC
                                core_info[soc_name][core_name] = core_props

                                # Make sure SOC is in soc_list
                                if soc_name not in config_data["soc_list"]:
                                    config_data["soc_list"].append(soc_name)

                        # Add core_info to config_data
                        config_data["core_info"] = core_info
                except Exception as e:
                    print(f"Error parsing Config sheet: {str(e)}")

            # Check if LookUpTable sheet exists
            if 'LookUpTable' in sheet_names:
                try:
                    signals_df = pd.read_excel(file_path, sheet_name='LookUpTable')
                    if not signals_df.empty and 'Data_Type' in signals_df.columns:
                        signals = {}

                        # Get all the potential core columns
                        standard_fields = {
                            'Data_Type', 'Variable_Port_Name', 'Memory Region',
                            'Buffer count_IPC', 'Type', 'InitValue', 'Notifiers',
                            'Source', 'Impl_Approach', 'GetObjRef', 'SM_Buff_Count',
                            'Timeout', 'Periodicity', 'ASIL', 'Checksum', 'DataType', 'description'
                        }
                        potential_core_cols = [col for col in signals_df.columns if col not in standard_fields]

                        for _, row in signals_df.iterrows():
                            if pd.isna(row.get('Data_Type', np.nan)):
                                continue

                            signal_name = str(row['Data_Type'])
                            # Handle boolean fields correctly by checking if the value is Yes/No
                            notifiers = str(row.get('Notifiers', 'No')).lower() == "yes" if pd.notna(row.get('Notifiers', '')) else False
                            get_obj_ref = str(row.get('GetObjRef', 'No')).lower() == "yes" if pd.notna(row.get('GetObjRef', '')) else False
                            buffer_count = int(row.get('Buffer count_IPC', 1)) if pd.notna(row.get('Buffer count_IPC', '')) else 1
                            sm_buff_count = int(row.get('SM_Buff_Count', 1)) if pd.notna(row.get('SM_Buff_Count', '')) else 1
                            timeout = int(row.get('Timeout', 10)) if pd.notna(row.get('Timeout', '')) else 10
                            periodicity = int(row.get('Periodicity', 10)) if pd.notna(row.get('Periodicity', '')) else 10

                            # Create signal properties dictionary with proper default values
                            signal_props = {
                                "Variable_Port_Name": str(row.get('Variable_Port_Name', signal_name)) if pd.notna(row.get('Variable_Port_Name', '')) else signal_name,
                                "Memory Region": str(row.get('Memory Region', "DDR")) if pd.notna(row.get('Memory Region', '')) else "DDR",
                                "Type": str(row.get('Type', "Concurrent")) if pd.notna(row.get('Type', '')) else "Concurrent",
                                "InitValue": str(row.get('InitValue', "ZeroMemory")) if pd.notna(row.get('InitValue', '')) else "ZeroMemory",
                                "Notifiers": notifiers,
                                "Source": str(row.get('Source', "")) if pd.notna(row.get('Source', '')) else "",
                                "Impl_Approach": str(row.get('Impl_Approach', "SharedMemory")) if pd.notna(row.get('Impl_Approach', '')) else "SharedMemory",
                                "GetObjRef": get_obj_ref,
                                "Buffer count_IPC": buffer_count,
                                "SM_Buff_Count": sm_buff_count,
                                "Timeout": timeout,
                                "Periodicity": periodicity,
                                "ASIL": str(row.get('ASIL', "QM")) if pd.notna(row.get('ASIL', '')) else "QM",
                                "Checksum": str(row.get('Checksum', "None")) if pd.notna(row.get('Checksum', '')) else "None",
                                "DataType": str(row.get('DataType', "INT32")) if pd.notna(row.get('DataType', '')) else "INT32",
                                "description": str(row.get('description', "Imported signal")) if pd.notna(row.get('description', '')) else "Imported signal",
                                "is_struct": False,  # Default to non-struct
                                "struct_fields": {}  # Empty struct fields
                            }

                            # Process potential core destinations
                            for core_col in potential_core_cols:
                                # If column value is "Yes", mark it as a destination
                                core_key = f"core_{core_col.replace('.', '_')}"
                                signal_props[core_key] = str(row.get(core_col, "No")).lower() == "yes" if pd.notna(row.get(core_col, '')) else False

                            # Add signal to signals dictionary
                            signals[signal_name] = signal_props

                        # Add signals to config_data
                        config_data["signals"] = signals
                except Exception as e:
                    print(f"Error parsing LookUpTable sheet: {str(e)}")

            # If we have at least some data, return the configuration
            if config_data["soc_type"] or config_data["signals"]:
                final_config = copy.deepcopy(config_data)

                # Double check description is present
                if "description" not in final_config["metadata"] or not final_config["metadata"]["description"]:
                    final_config["metadata"]["description"] = "Imported from Excel"
                return final_config
            else:
                return None
        except Exception as e:
            print(f"Error reading Excel file: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _clear_signal_attribute_section(self):
        """Clear the signal attribute section to remove any displayed signal details"""
        try:
            # Get the SiganlDetailsFrame (note the spelling matches the UI structure)
            if hasattr(self.app.ui, 'SiganlDetailsFrame'):
                details_frame = self.app.ui.SiganlDetailsFrame

                # Find the SignalAttributeSection scroll area
                attr_scroll = details_frame.findChild(QtWidgets.QScrollArea, "SignalAttributeSection")

                if attr_scroll:
                    # Create an empty widget to replace the current content
                    empty_widget = QtWidgets.QWidget()
                    empty_layout = QtWidgets.QVBoxLayout(empty_widget)
                    empty_label = QtWidgets.QLabel("No signal selected")
                    empty_layout.addWidget(empty_label)

                    # Set the empty widget as the content of the scroll area
                    attr_scroll.setWidget(empty_widget)

                    # Process events to ensure UI updates
                    QtWidgets.QApplication.processEvents()

                    print("Signal attribute section cleared")
        except Exception as e:
            print(f"Error clearing signal attribute section: {e}")
            import traceback
            traceback.print_exc()

    def close_file(self):
        """Close the current file and reset the UI state"""
        if self.app.modified:
            reply = QMessageBox.question(
                self.app,
                'Unsaved Changes',
                'You have unsaved changes. Do you want to save them before closing?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Yes:
                if not self.save_file():  # If save failed or was cancelled
                    return
            elif reply == QMessageBox.Cancel:
                return

        try:
            print("Starting close file operation...")

            # Disconnect UI signals to prevent crash during UI updates - IMPORTANT!
            # Don't try to reconnect later, as this causes the crash
            if hasattr(self.app.ui_helpers, '_disconnect_ui_signals'):
                self.app.ui_helpers._disconnect_ui_signals()
                print("Disconnected UI signals for close operation")

            # Process events to ensure UI is responsive
            QtWidgets.QApplication.processEvents()

            # Reset the app to initial state
            self.app.current_file = None

            # Create a default values object with empty description and editor
            empty_defaults = {
                "version": self.app.ui_helpers.default_version_info["version"],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "editor": "",
                "description": ""  # Empty description as requested
            }

            # Reset signals data with empty default values
            self.app.signals_data = {
                "metadata": {
                    "version": empty_defaults["version"],
                    "date": empty_defaults["date"],
                    "editor": empty_defaults["editor"],
                    "description": empty_defaults["description"]
                },
                "soc_type": "Windows",
                "build_type": "SMP",
                "soc_list": ["Windows"],
                "build_list": ["SMP"],
                "core_info": {},
                "signals": {}
            }

            # Clear API configuration UI elements
            if hasattr(self.app.ui_helpers, 'clear_api_configuration'):
                self.app.ui_helpers.clear_api_configuration()

            print("Reset signals data to empty state")

            # Store the clean state as the original state to avoid marking as modified
            import copy
            self.app.ui_helpers.original_signals_data = copy.deepcopy(self.app.signals_data)

            # Set the flags to use default values
            self.app.ui_helpers.using_default_values = True
            self.app.ui_helpers.first_run_or_closed = True

            # Reset modified flag before updating UI elements to prevent marking as modified
            self.app.modified = False

            # Process events to ensure UI is responsive
            QtWidgets.QApplication.processEvents()

            # Safely clear UI elements one by one

            # 1. Clear editor name and description fields
            if hasattr(self.app.ui, 'EditorName'):
                self.app.ui.EditorName.setPlaceholderText("Please Entry Your Name")
                self.app.ui.EditorName.setPlainText("")  # Clear text to show placeholder
                print("Cleared editor name")
            elif hasattr(self.app.ui, 'VersionUpdateName'):
                self.app.ui.VersionUpdateName.setPlaceholderText("Please Entry Your Name")
                self.app.ui.VersionUpdateName.setPlainText("")  # Clear text to show placeholder
                print("Cleared version update name")

            if hasattr(self.app.ui, 'VersionDescription'):
                self.app.ui.VersionDescription.setPlainText("")
                print("Cleared version description")

            # Process events after clearing text fields
            QtWidgets.QApplication.processEvents()

            # 2. Update version fields
            if hasattr(self.app.ui_helpers, 'initialize_version_fields'):
                self.app.ui_helpers.initialize_version_fields(skip_validation=True)
                print("Initialized version fields")

            # Process events after version field update
            QtWidgets.QApplication.processEvents()

            # 3. Clear the signal tree
            if hasattr(self.app.ui_helpers, 'refresh_signal_tree'):
                self.app.ui_helpers.refresh_signal_tree()
                print("Refreshed signal tree")

            # Process events after refreshing tree
            QtWidgets.QApplication.processEvents()

            # 4. Update signal count display
            if hasattr(self.app.ui_helpers, 'update_signal_count_display'):
                self.app.ui_helpers.update_signal_count_display()
                print("Updated signal count")

            # Process events after updating signal count
            QtWidgets.QApplication.processEvents()

            # 5. Clear core info display
            if hasattr(self.app.ui_helpers, 'update_core_info'):
                self.app.ui_helpers.update_core_info()
                print("Cleared core info display")

            # Process events after updating core info
            QtWidgets.QApplication.processEvents()

            # 6. Clear signal attribute section
            if hasattr(self.app.ui_helpers, 'clear_signal_attribute_section'):
                self.app.ui_helpers.clear_signal_attribute_section()
                print("Cleared signal attribute section")
            else:
                # Fallback to simple method if available
                self._clear_signal_attribute_section()

            # Process events after clearing attribute section
            QtWidgets.QApplication.processEvents()

            # Double-check that the editor name and description are still empty
            # (in case initialize_version_fields changed them)
            if hasattr(self.app.ui, 'EditorName'):
                self.app.ui.EditorName.setPlaceholderText("Please Entry Your Name")
                self.app.ui.EditorName.setPlainText("")  # Clear text to show placeholder

            if hasattr(self.app.ui, 'VersionUpdateName'):
                self.app.ui.VersionUpdateName.setPlaceholderText("Please Entry Your Name")
                self.app.ui.VersionUpdateName.setPlainText("")  # Clear text to show placeholder

            if hasattr(self.app.ui, 'VersionDescription'):
                self.app.ui.VersionDescription.setPlainText("")

            # Process events after final field clearing
            QtWidgets.QApplication.processEvents()

            # 7. Update window title
            if hasattr(self.app.ui_helpers, 'update_window_title'):
                # Ensure modified flag is still False after all UI updates
                self.app.modified = False
                self.app.ui_helpers.update_window_title()
                print("Updated window title")

            # Final process events
            QtWidgets.QApplication.processEvents()

            # Show success message
            QMessageBox.information(self.app, "File Closed", "File closed successfully.")
            print("Close file operation completed successfully")

            return True

        except Exception as e:
            print(f"Error during close file operation: {e}")
            import traceback
            traceback.print_exc()

            # Ensure UI remains responsive even after error
            QtWidgets.QApplication.processEvents()

            # Inform user of error
            QMessageBox.critical(self.app, "Error", f"Error closing file: {str(e)}")
            return False

    def close_application(self):
        """Close the application with prompt for unsaved changes"""
        if self.app.ui_helpers.check_unsaved_changes():
            self.app.close()

    def ensure_metadata_fields(self):
        """Ensure all necessary metadata fields exist and are properly formatted"""
        if not self.app.signals_data:
            return

        # Make sure metadata exists
        if "metadata" not in self.app.signals_data:
            self.app.signals_data["metadata"] = {}

        metadata = self.app.signals_data["metadata"]

        # Set default values only if fields don't exist
        if "version" not in metadata:
            metadata["version"] = "1.0"

        if "date" not in metadata or not metadata["date"]:
            metadata["date"] = pd.Timestamp("today").strftime('%Y-%m-%d')

        # Only set empty editor field if it doesn't exist
        if "editor" not in metadata:
            metadata["editor"] = ""

        # Ensure description field exists
        if "description" not in metadata:
            metadata["description"] = "Signal Configuration"

        # Always explicitly set both editor and description UI fields
        editor_name = metadata.get("editor", "")

        # First try EditorName field
        if hasattr(self.app.ui, 'EditorName'):
            self.app.ui.EditorName.setPlaceholderText(editor_name)
            self.app.ui.EditorName.setPlainText("")  # Clear text to show placeholder
        # If EditorName doesn't exist, try VersionUpdateName
        elif hasattr(self.app.ui, 'VersionUpdateName'):
            self.app.ui.VersionUpdateName.setPlaceholderText(editor_name)
            self.app.ui.VersionUpdateName.setPlainText("")  # Clear text to show placeholder

        if hasattr(self.app.ui, 'VersionDescription'):
            print(f"Setting VersionDescription to: {metadata.get('description', '')}")
            self.app.ui.VersionDescription.setPlainText(metadata.get("description", ""))

    def save_configuration_to_file(self, file_path):
        """Save configuration to file"""
        try:
            # Save API configuration before saving file
            self.app.ui_helpers.save_api_configuration()

            # ... existing save code ...
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
