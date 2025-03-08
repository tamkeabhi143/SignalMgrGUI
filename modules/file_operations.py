import os
import json
import pandas as pd
import numpy as np
import copy  # Make sure this import is at the top
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from icecream import ic

class FileOperations:
    def __init__(self, app):
        self.app = app
        
    def open_file(self):
        # Only check for unsaved changes if:
        # 1. Modified flag is True AND
        # 2. There's a current file OR actual signal data
        if self.app.modified and (self.app.current_file is not None or 
                                 len(self.app.signals_data.get("signals", {})) > 0):
            if not self.app.ui_helpers.check_unsaved_changes():
                return
    
        file_path, _ = QFileDialog.getOpenFileName(self.app, "Open Signal Configuration", "", 
                                                  "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.app.signals_data = json.load(file)
                self.app.current_file = file_path
                self.app.modified = False
                
                # Store a deep copy of the initial state after loading
                self.app.ui_helpers.original_signals_data = copy.deepcopy(self.app.signals_data)
                
                # First populate the SOC and Build Type lists from the loaded configuration
                self.app.ui_helpers.populate_soc_list()
                self.app.ui_helpers.populate_build_types()
                
                # Then refresh the signal tree and core info
                self.app.ui_helpers.refresh_signal_tree()
                self.app.ui_helpers.update_core_info()
                
                # Make sure the metadata fields in signals_data are correctly formatted
                self.ensure_metadata_fields()
                
                # After loading, update version fields from metadata
                self.app.ui_helpers.initialize_version_fields()
                
                # Update signal count display
                self.app.ui_helpers.update_signal_count_display()
                self.app.ui_helpers.update_window_title()
                
                QMessageBox.information(self.app, "Success", f"File loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self.app, "Error", f"Failed to open file: {str(e)}")
                import traceback
                traceback.print_exc()  # Print detailed error for debugging

    def save_file(self):
        """Save file with version check"""
        # Check version information before saving
        if not self.app.ui_helpers.check_version_for_export():
            return
        
        # Additional validation for editor name
        editor_name = self.app.ui.EditorName.toPlainText().strip()
        if not editor_name or editor_name.isspace() or editor_name.lower() == "enter your name":
            QMessageBox.warning(
                self.app,
                "Invalid Editor Name",
                "Please enter your name in the 'Modifier Name' field before saving."
            )
            # Switch to Core Configuration tab and focus on editor name field
            self.app.ui.tabWidget.setCurrentIndex(0)
            self.app.ui.EditorName.setFocus()
            return
        
        # Continue with save
        if not self.app.current_file:
            self.save_file_as()
        else:
            try:
                with open(self.app.current_file, 'w') as file:
                    json.dump(self.app.signals_data, file, indent=4)
                self.app.modified = False
                self.app.ui_helpers.update_window_title()
                QMessageBox.information(self.app, "Success", f"File saved: {self.app.current_file}")
            except Exception as e:
                QMessageBox.critical(self.app, "Error", f"Failed to save file: {str(e)}")

    def save_file_as(self):
        """Save file as with version check"""
        # Check version information before saving
        if not self.app.ui_helpers.check_version_for_export():
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self.app, "Save Signal Configuration", "", 
                                                  "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.app.current_file = file_path
            self.save_file()

    def create_new_file(self):
        if self.app.ui_helpers.check_unsaved_changes():
            # Open configuration manager to set up the new file
            self.app.signal_ops.open_configuration_manager(is_new_file=True)

    def export_to_excel(self):
        """Export to Excel with version check"""
        # Check version information before exporting
        if not self.app.ui_helpers.check_version_for_export():
            return
        
        if not self.app.signals_data:
            QMessageBox.warning(self.app, "Warning", "No configuration data to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self.app, "Export to Excel", "", 
                                                 "Excel Files (*.xlsx);;All Files (*)")
        if file_path:
            try:
                # Create Excel writer with xlsxwriter
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    # Export Version data to Version sheet
                    self.export_version_data(writer, 'Version')
                    
                    # Export configuration data to Config sheet
                    self.export_config_data(writer, 'Config')
                    
                    # Export signals data to LookUpTable sheet
                    if self.app.signals_data.get("signals"):
                        self.export_signals_data(writer, 'LookUpTable')
                
                QMessageBox.information(self.app, "Success", f"Exported to Excel: {file_path}")
            except Exception as e:
                QMessageBox.critical(self.app, "Error", f"Failed to export to Excel: {str(e)}")
                import traceback
                traceback.print_exc()  # Print detailed error for debugging

    def export_version_data(self, writer, sheet_name):
        """Export version metadata to Excel"""
        # Get version metadata
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
        
        # Write to Excel
        version_data.to_excel(writer, sheet_name=sheet_name, index=False)

    def export_config_data(self, writer, sheet_name):
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
        
        # Write combined config data to the sheet
        # First, create a single DataFrame with all configuration data
        
        # Start with SOC and Build Type
        combined_data = pd.DataFrame({
            'SOC Name': [self.app.signals_data.get('soc_type', '')],
            'TypeOfBin': [self.app.signals_data.get('build_type', '')]
        })
        
        # Then add core info if available
        if core_data:
            # Convert core_data list to DataFrame
            cores_df = pd.DataFrame(core_data)
            
            # Write both to Excel with no index
            # SOC and Build Type on the left (columns A-B)
            combined_data.to_excel(writer, sheet_name=sheet_name, startrow=0, index=False)
            
            # Core data to the right (columns E-K)
            cores_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=4, index=False)
        else:
            # Just write the SOC and Build Type if no core data
            combined_data.to_excel(writer, sheet_name=sheet_name, startrow=0, index=False)

    def export_signals_data(self, writer, sheet_name):
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
                'description': signal_info.get('description', '')
            }
            
            # Add core destinations
            for core in available_cores:
                core_key = f"core_{core.replace('.', '_')}"
                row[core] = 'Yes' if signal_info.get(core_key, False) else 'No'
                
            signal_rows.append(row)
        
        if signal_rows:
            # Create DataFrame and write to Excel
            signals_df = pd.DataFrame(signal_rows)
            signals_df.to_excel(writer, sheet_name=sheet_name, index=False)

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
                # Update signals data
                self.app.signals_data = copy.deepcopy(imported_data)
                
                # Store a deep copy of the initial state after importing
                self.app.ui_helpers.original_signals_data = copy.deepcopy(imported_data)
                
                # Make sure the metadata fields in signals_data are correctly formatted
                self.ensure_metadata_fields()
                
                # Explicitly set the description in the UI to ensure it's displayed
                if hasattr(self.app.ui, 'VersionDescription') and "metadata" in imported_data:
                    description = imported_data["metadata"].get("description", "")
                    print(f"Setting description field to: {description}")
                    self.app.ui.VersionDescription.setPlainText(description)
                
                # Update UI with imported data
                self.app.ui_helpers.refresh_signal_tree()
                self.app.ui_helpers.update_signal_count_display()
                self.app.ui_helpers.update_core_info()
                
                # Set modified flag
                self.app.modified = True
                
                # Update window title
                self.app.ui_helpers.update_window_title()
                
                # Update SOC and Build Type lists with values from imported data
                self.app.ui_helpers.populate_soc_list()
                self.app.ui_helpers.populate_build_types()
                
                # Update version fields from metadata - this will set EditorName to the imported value
                self.app.ui_helpers.initialize_version_fields()
                
                # Clear current file path for new imported data
                if not self.app.current_file:
                    self.app.current_file = None
                
                QMessageBox.information(
                    self.app, 
                    "Import Successful", 
                    f"Successfully imported configuration from Excel."
                )
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

    def close_file(self):
        """Close the current file without exiting the application"""
        # Check for unsaved changes
        if self.app.modified:
            reply = QMessageBox.question(
                self.app, 
                "Unsaved Changes", 
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return False
        
        # Reset to an empty state
        self.app.signals_data = {
            "metadata": {
                "version": "1.0",
                "date": "",
                "editor": "",
                "description": ""  # Empty description
            },
            "soc_type": "Windows",  # Default SOC
            "build_type": "SMP",    # Default Build Type
            "soc_list": ["Windows"],
            "build_list": ["SMP"],
            "core_info": {},
            "signals": {}
        }
        self.app.current_file = None
        self.app.modified = False
        
        # Clear editor name and description fields directly
        self.app.ui.EditorName.setPlainText("")
        if hasattr(self.app.ui, 'VersionDescription'):
            self.app.ui.VersionDescription.setPlainText("")
        
        # Update UI
        self.app.ui_helpers.update_window_title()
        self.app.ui_helpers.populate_soc_list()
        self.app.ui_helpers.populate_build_types()
        self.app.ui_helpers.refresh_signal_tree()
        self.app.ui_helpers.update_core_info()
        self.app.ui_helpers.initialize_version_fields()
        self.app.ui_helpers.update_signal_count_display()
        
        QMessageBox.information(self.app, "File Closed", "File has been closed.")
        return True

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
        self.app.ui.EditorName.setPlainText(metadata.get("editor", ""))
        
        if hasattr(self.app.ui, 'VersionDescription'):
            print(f"Setting VersionDescription to: {metadata.get('description', '')}")
            self.app.ui.VersionDescription.setPlainText(metadata.get("description", ""))