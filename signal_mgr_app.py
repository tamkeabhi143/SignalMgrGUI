#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTreeWidgetItem, QPushButton
from PyQt5.QtCore import Qt  # Add this import for Qt namespace

from SignalMgrGUI import Ui_MainWindow

class SignalMgrApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(SignalMgrApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Initialize class variables
        self.current_file = None
        self.signals_data = {}
        self.copied_signal = None
        self.modified = False
        self.undo_stack = []
        self.redo_stack = []
        
        # Remove the Operation menu if it exists
        operation_menu = self.findChild(QtWidgets.QMenu, "menuOperation")
        if operation_menu:
            menubar = self.menuBar()
            menubar.removeAction(operation_menu.menuAction())
        
        # Connect UI elements to their respective functions
        self.setup_connections()
        
        # Setup tree widget for signal display
        self.setup_tree_widget()
        
        # Initialize SOC list and build types
        self.populate_soc_list()
        self.populate_build_types()
        
        # Initialize version fields
        self.initialize_version_fields()
        
        # Disable SignalCnt field
        self.ui.SignalCnt.setReadOnly(True)
        self.ui.SignalCnt.setEnabled(False)
        self.update_signal_count_display()
        
        # Set window title
        self.setWindowTitle("Signal Manager Tool")

    def initialize_version_fields(self):
        """Initialize version fields with default values"""
        # Set default version number
        self.ui.VersionNumber.setValue(1)
        
        # Set current date
        current_date = QtCore.QDate.currentDate()
        self.ui.VersionDate.setDate(current_date)
        
        # Save initial version info to signals_data
        if "metadata" not in self.signals_data:
            self.signals_data["metadata"] = {}
        
        self.signals_data["metadata"]["version"] = str(self.ui.VersionNumber.value())
        self.signals_data["metadata"]["date"] = current_date.toString("yyyy-MM-dd")
        self.signals_data["metadata"]["editor"] = self.ui.EditorName.toPlainText()

    def setup_connections(self):
        # Connect File menu actions
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save_file)
        self.ui.actionSave_As.triggered.connect(self.save_file_as)
        self.ui.actionCreate.triggered.connect(self.create_new_file)
        self.ui.actionExport_as_Excel.triggered.connect(self.export_to_excel)
        self.ui.actionExit.triggered.connect(self.close_application)
        self.ui.actionClose.triggered.connect(self.close_application)
        self.ui.actionExit_2.triggered.connect(self.close_application)
        
        # We don't need to connect Operation menu actions since we've removed them
        
        # Connect Database menu actions
        self.ui.actionAdd_Signal.triggered.connect(lambda: self.check_version_and_run(self.add_signal))
        self.ui.actionDelete_Signal.triggered.connect(lambda: self.check_version_and_run(self.delete_signal))
        self.ui.actionUpdate_Signal.triggered.connect(lambda: self.check_version_and_run(self.update_signal))
        self.ui.actionRename_Signal.triggered.connect(lambda: self.check_version_and_run(self.rename_signal))
        self.ui.actionCopy_Signal.triggered.connect(lambda: self.check_version_and_run(self.copy_signal))
        self.ui.actionPaste_Signal.triggered.connect(lambda: self.check_version_and_run(self.paste_signal))
        
        # Connect Code Generation menu actions
        self.ui.actionSignalMgr.triggered.connect(self.generate_signal_mgr)
        self.ui.actionIpcManager.triggered.connect(self.generate_ipc_manager)
        self.ui.actionIpcOvEthMgr.triggered.connect(self.generate_ipc_eth_mgr)
        
        # Connect Help menu actions
        self.ui.actionAbout_Tool_Usage.triggered.connect(self.show_tool_usage)
        self.ui.actionLicense.triggered.connect(self.show_license)
        self.ui.actionVersion.triggered.connect(self.show_version)
        
        # Connect buttons
        #self.ui.SaveButton.clicked.connect(self.save_file)
        self.ui.SaveButton_2.clicked.connect(self.save_file)
        #self.ui.UndoButton.clicked.connect(self.undo_action)
        self.ui.UndoButton_2.clicked.connect(self.undo_action)
        #self.ui.RedoButton.clicked.connect(self.redo_action)
        self.ui.RedoButton_2.clicked.connect(self.redo_action)
        #self.ui.UpdateConfig.clicked.connect(lambda: self.check_version_and_run(self.open_configuration_manager))
        self.ui.UpdateConfig_2.clicked.connect(lambda: self.check_version_and_run(self.open_configuration_manager))
        
        # Connect combo boxes
        self.ui.SOCList.currentIndexChanged.connect(self.soc_selection_changed)
        self.ui.BuildImageType.currentIndexChanged.connect(self.build_type_changed)
        
        # Connect version fields
        self.ui.VersionNumber.valueChanged.connect(self.update_version_info)
        self.ui.VersionDate.dateChanged.connect(self.update_version_info)
        self.ui.EditorName.textChanged.connect(self.update_version_info)

        # Add Excel import action
        self.ui.actionImport_from_Excel = QtWidgets.QAction("Import from Excel", self)
        self.ui.menuFile.addAction(self.ui.actionImport_from_Excel)
        self.ui.actionImport_from_Excel.triggered.connect(self.import_from_excel)

    def check_version_and_run(self, func):
        """Check if version info is filled before executing a function"""
        if self.is_version_info_filled():
            # If version info is filled, execute the function
            func()
        else:
            # If version info is not filled, show a warning
            QMessageBox.warning(self, "Version Required", 
                              "Please fill in version information before making changes.")
            # Switch to the Core Configuration tab
            self.ui.tabWidget.setCurrentIndex(0)

    def is_version_info_filled(self):
        """Check if all version fields are filled"""
        editor_name = self.ui.EditorName.toPlainText().strip()
        return (self.ui.VersionNumber.value() > 0 and 
               not editor_name.isspace() and 
               not editor_name.lower() == "enter your name" and 
               len(editor_name) > 0)

    def update_version_info(self):
        """Update version info in signals_data when version fields change"""
        if "metadata" not in self.signals_data:
            self.signals_data["metadata"] = {}
        
        self.signals_data["metadata"]["version"] = str(self.ui.VersionNumber.value())
        self.signals_data["metadata"]["date"] = self.ui.VersionDate.date().toString("yyyy-MM-dd")
        self.signals_data["metadata"]["editor"] = self.ui.EditorName.toPlainText()
        
        # Mark as modified
        self.modified = True
        self.update_window_title()

    def update_signal_count_display(self):
        """Update the signal count display in the UI"""
        signal_count = len(self.signals_data.get("signals", {}))
        # Update the signal count in both locations
        self.ui.SignalCnt.setValue(signal_count)
        # Also update in Core Info if it exists
        self.update_core_info()

    def setup_tree_widget(self):
        # Set up a tree widget in the scroll area for signal list
        self.signal_tree = QtWidgets.QTreeWidget()
        self.signal_tree.setHeaderLabels(["Signal Name", "Type", "Description"])
        self.signal_tree.setColumnWidth(0, 150)
        self.signal_tree.setColumnWidth(1, 100)
        
        # Change from itemClicked to itemSelectionChanged for more reliable selection handling
        self.signal_tree.itemSelectionChanged.connect(self.on_signal_selection_changed)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.signal_tree)
        
        self.ui.scrollAreaWidgetContents.setLayout(layout)

    def populate_soc_list(self):
        # Clear current entries
        self.ui.SOCList.clear()
        
        # Add default entry
        self.ui.SOCList.addItem("Select SOC")
        
        # Add configured SOC types
        soc_types = self.signals_data.get("soc_list", ["ARM", "x86", "RISC-V", "PowerPC", "MIPS"])
        for soc in soc_types:
            self.ui.SOCList.addItem(soc)
            
        # Set current SOC if defined
        current_soc = self.signals_data.get("soc_type", "")
        if current_soc:
            index = self.ui.SOCList.findText(current_soc)
            if index >= 0:
                self.ui.SOCList.setCurrentIndex(index)
            else:
                # If the current SOC isn't in the list, add it and select it
                self.ui.SOCList.addItem(current_soc)
                self.ui.SOCList.setCurrentText(current_soc)

    def populate_build_types(self):
        # Clear current entries
        self.ui.BuildImageType.clear()
        
        # Add default entry
        self.ui.BuildImageType.addItem("Select Build Type")
        
        # Add configured build types
        build_types = self.signals_data.get("build_list", ["Debug", "Release", "Test", "Production"])
        for build_type in build_types:
            self.ui.BuildImageType.addItem(build_type)
            
        # Set current build type if defined
        current_build = self.signals_data.get("build_type", "")
        if current_build:
            index = self.ui.BuildImageType.findText(current_build)
            if index >= 0:
                self.ui.BuildImageType.setCurrentIndex(index)
            else:
                # If the current build type isn't in the list, add it and select it
                self.ui.BuildImageType.addItem(current_build)
                self.ui.BuildImageType.setCurrentText(current_build)

    # File operations
    def open_file(self):
        if self.check_unsaved_changes():
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Signal Configuration", "", 
                                                      "JSON Files (*.json);;All Files (*)")
            if file_path:
                try:
                    with open(file_path, 'r') as file:
                        self.signals_data = json.load(file)
                    self.current_file = file_path
                    self.modified = False
                    self.update_window_title()
                    
                    # First populate the SOC and Build Type lists from the loaded configuration
                    self.populate_soc_list()
                    self.populate_build_types()
                    
                    # Then refresh the signal tree and core info
                    self.refresh_signal_tree()
                    self.update_core_info()
                    
                    # After loading, update version fields from metadata
                    metadata = self.signals_data.get("metadata", {})
                    try:
                        version = int(metadata.get("version", "1"))
                        self.ui.VersionNumber.setValue(version)
                    except ValueError:
                        self.ui.VersionNumber.setValue(1)
                    
                    date_str = metadata.get("date", "")
                    if date_str:
                        try:
                            date = QtCore.QDate.fromString(date_str, "yyyy-MM-dd")
                            if date.isValid():
                                self.ui.VersionDate.setDate(date)
                        except:
                            self.ui.VersionDate.setDate(QtCore.QDate.currentDate())
                            
                    editor = metadata.get("editor", "")
                    if editor:
                        self.ui.EditorName.setPlainText(editor)
                        
                    # Update signal count display
                    self.update_signal_count_display()
                    
                    QMessageBox.information(self, "Success", f"File loaded: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")

    def save_file(self):
        if not self.current_file:
            self.save_file_as()
        else:
            try:
                with open(self.current_file, 'w') as file:
                    json.dump(self.signals_data, file, indent=4)
                self.modified = False
                self.update_window_title()
                QMessageBox.information(self, "Success", f"File saved: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Signal Configuration", "", 
                                                  "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.current_file = file_path
            self.save_file()

    def create_new_file(self):
        if self.check_unsaved_changes():
            # Open configuration manager to set up the new file
            self.open_configuration_manager(is_new_file=True)

    def export_to_excel(self):
        if not self.signals_data:
            QMessageBox.warning(self, "Warning", "No configuration data to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", 
                                                 "Excel Files (*.xlsx);;All Files (*)")
        if file_path:
            try:
                # Create Excel writer with xlsxwriter
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    # Export configuration data to Config sheet
                    self.export_config_data(writer, 'Config')
                    
                    # Export signals data to LookUpTable sheet
                    if self.signals_data.get("signals"):
                        self.export_signals_data(writer, 'LookUpTable')
                    
                QMessageBox.information(self, "Success", f"Exported to Excel: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export to Excel: {str(e)}")
                import traceback
                traceback.print_exc()  # Print detailed error for debugging

    def export_config_data(self, writer, sheet_name):
        # Create a DataFrame with SOC and Build Type information
        soc_build_data = {
            'SOC Name': [self.signals_data.get('soc_type', '')],
            'TypeOfBin': [self.signals_data.get('build_type', '')]
        }
        soc_build_df = pd.DataFrame(soc_build_data)
        
        # Create a DataFrame with Core information
        core_info = self.signals_data.get("core_info", {})
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
                        self.signals_data["core_info"][soc_name][core_name] = legacy_props
                        
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
            'SOC Name': [self.signals_data.get('soc_type', '')],
            'TypeOfBin': [self.signals_data.get('build_type', '')]
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
        signals = self.signals_data.get("signals", {})
        if not signals:
            return
        
        # Get the list of all configured cores
        available_cores = self.get_available_cores()
        
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
                'Checksum': signal_info.get('Checksum', '') if signal_info.get('Checksum') else 'None'
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

    def close_application(self):
        if self.check_unsaved_changes():
            self.close()

    def import_from_excel(self):
        """Import configuration from Excel file"""
        if self.check_unsaved_changes():
            file_path, _ = QFileDialog.getOpenFileName(self, "Import from Excel", "", 
                                                     "Excel Files (*.xlsx);;All Files (*)")
            if file_path:
                try:
                    # Read Excel file
                    config_data = self.read_excel_config(file_path)
                    
                    if not config_data:
                        QMessageBox.warning(self, "Warning", "No valid configuration found in Excel file")
                        return
                    
                    # Update signals data with imported configuration
                    self.signals_data = config_data
                    self.current_file = None  # No JSON file associated yet
                    self.modified = True
                    self.update_window_title()
                    
                    # Refresh UI with new configuration
                    self.populate_soc_list()
                    self.populate_build_types()
                    self.refresh_signal_tree()
                    self.update_core_info()
                    
                    # After importing, update the signal count
                    self.update_signal_count_display()
                    
                    QMessageBox.information(self, "Success", "Configuration imported from Excel")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to import from Excel: {str(e)}")
                    import traceback
                    traceback.print_exc()  # Print detailed error for debugging

    def read_excel_config(self, file_path):
        """Read configuration from Excel file"""
        # Initialize config data
        config_data = {
            "metadata": {
                "version": "1.0",
                "created": "",
                "modified": "",
                "description": "Imported from Excel"
            },
            "soc_type": "",
            "build_type": "",
            "core_info": {},
            "signals": {}
        }
        
        # Read Excel file with pandas
        try:
            # Try to read Config sheet
            config_df = pd.read_excel(file_path, sheet_name='Config')
            
            # Extract SOC and Build Type from first row
            if not config_df.empty and 'SOC Name' in config_df.columns and 'TypeOfBin' in config_df.columns:
                config_data["soc_type"] = str(config_df.iloc[0]['SOC Name'])
                config_data["build_type"] = str(config_df.iloc[0]['TypeOfBin'])
            
            # Extract core info from Config sheet
            core_cols = ['SOC', 'CORE', 'Master/Slave', 'Is Qnx Core ?', 
                        'Is Autosar Compliant ?', 'Is Sim Core ?', 'OS', 'SOC Family']
            
            # Check if core columns exist
            if all(col in config_df.columns for col in core_cols[:2]):  # At least SOC and CORE required
                # Initialize core_info structure
                core_info = {}
                
                # Process core rows
                for _, row in config_df.iterrows():
                    if pd.notna(row.get('SOC')) and pd.notna(row.get('CORE')):
                        soc_name = str(row['SOC'])
                        core_name = str(row['CORE'])
                        
                        # Initialize SOC in core_info if not exists
                        if soc_name not in core_info:
                            core_info[soc_name] = {}
                        
                        # Create core properties
                        core_props = {
                            "name": core_name,
                            "description": str(row.get('Description', "")),
                            "is_master": str(row.get('Master/Slave', "")).lower() == "master",
                            "is_qnx": str(row.get('Is Qnx Core ?', "")).lower() == "yes",
                            "is_autosar": str(row.get('Is Autosar Compliant ?', "")).lower() == "yes",
                            "is_sim": str(row.get('Is Sim Core ?', "")).lower() == "yes",
                            "os": str(row.get('OS', "Unknown")),
                            "soc_family": str(row.get('SOC Family', "Unknown"))
                        }
                        
                        # Add core to SOC
                        core_info[soc_name][core_name] = core_props
                
                # Add core_info to config_data
                config_data["core_info"] = core_info
        except Exception as e:
            print(f"Error reading Config sheet: {str(e)}")
        
        try:
            # Try to read LookUpTable sheet for signals
            signals_df = pd.read_excel(file_path, sheet_name='LookUpTable')
            
            if not signals_df.empty and 'Data_Type' in signals_df.columns:
                signals = {}
                
                for _, row in signals_df.iterrows():
                    signal_name = str(row['Data_Type'])
                    
                    # Create signal properties dictionary
                    signal_props = {
                        "Variable_Port_Name": str(row.get('Variable_Port_Name', signal_name)),
                        "Memory Region": str(row.get('Memory Region', "DDR")),
                        "Buffer count_IPC": int(row.get('Buffer count_IPC', 1)),
                        "Type": str(row.get('Type', "Concurrent")),
                        "InitValue": str(row.get('InitValue', "ZeroMemory")),
                        "Notifiers": str(row.get('Notifiers', "No")).lower() == "yes",
                        "Source": str(row.get('Source', "")),
                        "Impl_Approach": str(row.get('Impl_Approach', "SharedMemory")),
                        "GetObjRef": str(row.get('GetObjRef', "No")).lower() == "yes",
                        "SM_Buff_Count": int(row.get('SM_Buff_Count', 1)),
                        "Timeout": int(row.get('Timeout', 10)),
                        "Periodicity": int(row.get('Periodicity', 10)),
                        "ASIL": str(row.get('ASIL', "QM")),
                        "Checksum": str(row.get('Checksum', "None")),
                        "DataType": str(row.get('DataType', "INT32")),
                        "description": str(row.get('description', "Imported signal")),
                        "is_struct": False,
                        "struct_fields": {}
                    }
                    
                    # Look for core destination columns
                    for col in signals_df.columns:
                        if col not in ['Data_Type', 'Variable_Port_Name', 'Memory Region', 'Buffer count_IPC',
                                     'Type', 'InitValue', 'Notifiers', 'Source', 'Impl_Approach', 'GetObjRef',
                                     'SM_Buff_Count', 'Timeout', 'Periodicity', 'ASIL', 'Checksum', 'DataType',
                                     'description']:
                            # This could be a core name
                            core_name = col
                            core_key = f"core_{core_name.replace('.', '_')}"
                            signal_props[core_key] = str(row.get(col, "No")).lower() == "yes"
                    
                    # Add signal to signals dictionary
                    signals[signal_name] = signal_props
                
                # Add signals to config_data
                config_data["signals"] = signals
        except Exception as e:
            print(f"Error reading LookUpTable sheet: {str(e)}")
        
        return config_data

    def close_application(self):
        if self.check_unsaved_changes():
            self.close()

    def add_operation(self):
        # Generic add operation - could be customized based on context
        QMessageBox.information(self, "Information", "Add operation triggered")

    def delete_operation(self):
        # Generic delete operation
        QMessageBox.information(self, "Information", "Delete operation triggered")

    def copy_operation(self):
        # Generic copy operation
        QMessageBox.information(self, "Information", "Copy operation triggered")

    def paste_operation(self):
        # Generic paste operation
        QMessageBox.information(self, "Information", "Paste operation triggered")

    def move_operation(self):
        # Generic move operation
        QMessageBox.information(self, "Information", "Move operation triggered")

    def rename_operation(self):
        # Generic rename operation
        QMessageBox.information(self, "Information", "Rename operation triggered")

    # Signal operations
    def add_signal(self):
        signal_name, ok = QtWidgets.QInputDialog.getText(self, "Add Signal", "Enter signal name:")
        if ok and signal_name:
            if signal_name in self.signals_data.get("signals", {}):
                QMessageBox.warning(self, "Warning", f"Signal '{signal_name}' already exists")
                return
            # Save current state for undo
            self.save_undo_state()
            # Initialize signals dict if not exists
            if "signals" not in self.signals_data:
                self.signals_data["signals"] = {}
            # Add new signal with default properties
            self.signals_data["signals"][signal_name] = {
                "Variable_Port_Name": signal_name,
                "Memory Region": "DDR",
                "Buffer count_IPC": 1,
                "Type": "Concurrent",
                "InitValue": "ZeroMemory",
                "Notifiers": False,
                "Source": "",  # This will be populated from core list
                "Impl_Approach": "SharedMemory",
                "GetObjRef": False,
                "SM_Buff_Count": 1,
                "Timeout": 10,
                "Periodicity": 10,
                "ASIL": "QM",
                "Checksum": "Additive",
                "DataType": "INT32",
                "description": "New signal",
                "is_struct": False,  # Added for structure type support
                "struct_fields": {}  # For storing fields if it's a structure
            }
            # Open the signal details dialog for further configuration
            self.edit_signal_details(signal_name)
            
            self.modified = True
            self.update_window_title()
            self.refresh_signal_tree()
            # Select the newly added signal to show its details
            for i in range(self.signal_tree.topLevelItemCount()):
                item = self.signal_tree.topLevelItem(i)
                if item.text(0) == signal_name:
                    self.signal_tree.setCurrentItem(item)
                    # Force display of signal details
                    self.display_signal_details(signal_name, self.signals_data["signals"][signal_name])
                    break
            # After successfully adding a signal, update the count
            self.update_signal_count_display()

    def delete_signal(self):
        if not self.signal_tree.currentItem():
            QMessageBox.warning(self, "Warning", "No signal selected")
            return
        signal_name = self.signal_tree.currentItem().text(0)
        reply = QMessageBox.question(self, "Confirm Delete", 
                                    f"Are you sure you want to delete signal '{signal_name}'?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Save current state for undo
            self.save_undo_state()
            # Delete the signal
            if "signals" in self.signals_data and signal_name in self.signals_data["signals"]:
                del self.signals_data["signals"][signal_name]
                self.modified = True
                self.update_window_title()
                self.refresh_signal_tree()
                QMessageBox.information(self, "Success", f"Signal '{signal_name}' deleted")
                # After successfully deleting a signal, update the count
                self.update_signal_count_display()

    def update_signal(self):
        if not self.signal_tree.currentItem():
            QMessageBox.warning(self, "Warning", "No signal selected")
            return
        signal_name = self.signal_tree.currentItem().text(0)
        self.edit_signal_details(signal_name)

    def rename_signal(self):
        if not self.signal_tree.currentItem():
            QMessageBox.warning(self, "Warning", "No signal selected")
            return
        old_name = self.signal_tree.currentItem().text(0)
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename Signal", 
                                                     "Enter new signal name:", text=old_name)
        if ok and new_name and new_name != old_name:
            if new_name in self.signals_data.get("signals", {}):
                QMessageBox.warning(self, "Warning", f"Signal '{new_name}' already exists")
                return
            # Save current state for undo
            self.save_undo_state()
            # Rename the signal
            if "signals" in self.signals_data and old_name in self.signals_data["signals"]:
                self.signals_data["signals"][new_name] = self.signals_data["signals"][old_name]
                del self.signals_data["signals"][old_name]
                self.modified = True
                self.update_window_title()
                self.refresh_signal_tree()
                QMessageBox.information(self, "Success", f"Signal renamed to '{new_name}'")

    def copy_signal(self):
        if not self.signal_tree.currentItem():
            QMessageBox.warning(self, "Warning", "No signal selected")
            return
        signal_name = self.signal_tree.currentItem().text(0)
        if "signals" in self.signals_data and signal_name in self.signals_data["signals"]:
            self.copied_signal = {
                "name": signal_name,
                "properties": self.signals_data["signals"][signal_name].copy()
            }
            QMessageBox.information(self, "Success", f"Signal '{signal_name}' copied")

    def paste_signal(self):
        if not self.copied_signal:
            QMessageBox.warning(self, "Warning", "No signal copied")
            return
        original_name = self.copied_signal["name"]
        new_name = f"{original_name}_copy"
        # Find a unique name
        counter = 1
        while new_name in self.signals_data.get("signals", {}):
            new_name = f"{original_name}_copy{counter}"
            counter += 1
        # Save current state for undo
        self.save_undo_state()
        # Initialize signals dict if not exists
        if "signals" not in self.signals_data:
            self.signals_data["signals"] = {}
        # Add the copied signal with the new name
        self.signals_data["signals"][new_name] = self.copied_signal["properties"].copy()
        self.modified = True
        self.update_window_title()
        self.refresh_signal_tree()
        QMessageBox.information(self, "Success", f"Signal pasted as '{new_name}'")
        # After pasting a signal, update the count
        self.update_signal_count_display()

    # Code generation functions
    def generate_signal_mgr(self):
        if not self.signals_data or not self.signals_data.get("signals"):
            QMessageBox.warning(self, "Warning", "No signals to generate code")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save SignalMgr Code", "", 
                                                 "C Files (*.c);;Header Files (*.h);;All Files (*)")
        if file_path:
            try:
                # Simple code generation example
                code = self.generate_signal_mgr_code()
                with open(file_path, 'w') as file:
                    file.write(code)
                QMessageBox.information(self, "Success", f"SignalMgr code generated: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate code: {str(e)}")

    def generate_ipc_manager(self):
        QMessageBox.information(self, "Information", "IPC Manager code generation would happen here")

    def generate_ipc_eth_mgr(self):
        QMessageBox.information(self, "Information", "IPC Over Ethernet Manager code generation would happen here")

    def generate_signal_mgr_code(self):
        # Simple code generation example
        code = "/* Auto-generated Signal Manager Code */\n\n"
        code += "#include <stdio.h>\n"
        code += "#include <stdlib.h>\n"
        code += "#include \"signal_mgr.h\"\n\n"
        
        # Define signals
        code += "/* Signal definitions */\n"
        for signal_name, signal_info in self.signals_data.get("signals", {}).items():
            signal_type = signal_info.get("type", "INT32")
            code += f"static {signal_type} {signal_name}_value = {signal_info.get('default_value', '0')};\n"
        
        # Create getter/setter functions
        code += "\n/* Signal accessor functions */\n"
        for signal_name, signal_info in self.signals_data.get("signals", {}).items():
            signal_type = signal_info.get("type", "INT32")
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

    # Help functions
    def show_tool_usage(self):
        help_text = (
            "Signal Manager Tool Usage\n\n"
            "This tool helps you manage signal definitions for embedded systems.\n\n"
            "1. Create or open a signal configuration file\n"
            "2. Add, edit, or delete signals as needed\n"
            "3. Generate code for your target platform\n"
            "4. Save your configuration for future use"
        )
        QMessageBox.information(self, "Tool Usage", help_text)

    def show_license(self):
        license_text = (
            "Signal Manager Tool License\n\n"
            "Copyright (c) 2023\n"
            "All Rights Reserved\n\n"
            "This software is provided 'as-is', without any express or implied warranty."
        )
        QMessageBox.information(self, "License", license_text)

    def show_version(self):
        version_text = "Signal Manager Tool v1.0.0"
        QMessageBox.information(self, "Version", version_text)

    # Utility functions
    def on_signal_selected(self, item):
        signal_name = item.text(0)
        if "signals" in self.signals_data and signal_name in self.signals_data["signals"]:
            signal_info = self.signals_data["signals"][signal_name]
            self.display_signal_details(signal_name, signal_info)

    def on_signal_selection_changed(self):
        # This handles when the signal selection changes
        selected_items = self.signal_tree.selectedItems()
        if selected_items:
            signal_name = selected_items[0].text(0)
            if "signals" in self.signals_data and signal_name in self.signals_data["signals"]:
                signal_info = self.signals_data["signals"][signal_name]
                self.display_signal_details(signal_name, signal_info)

    def display_signal_details(self, signal_name, signal_info):
        """Display signal details in the SignalInternalInfo widget"""
        # Create a widget to display signal details with all configurable options
        detail_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(detail_widget)

        # Add a scroll area for better handling of many fields
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(scroll_content)

        # Add signal name as a title
        title_label = QtWidgets.QLabel(signal_name)
        title_font = QtGui.QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addRow(QtWidgets.QLabel("Signal Name:"), title_label)

        # Add separator line
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addRow(line)

        # Display key signal properties in a readable format
        for key in ['Variable_Port_Name', 'DataType', 'Memory Region', 'Buffer count_IPC',
                   'Type', 'InitValue', 'Notifiers', 'Source', 'Impl_Approach',
                   'GetObjRef', 'SM_Buff_Count', 'Timeout', 'Periodicity',
                   'ASIL', 'Checksum', 'description']:
            if key in signal_info:
                value = signal_info[key]
                # Format boolean values as Yes/No
                if isinstance(value, bool):
                    value = "Yes" if value else "No"
                # Create a label with the value
                value_label = QtWidgets.QLabel(str(value))
                value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                layout.addRow(f"{key.replace('_', ' ').title()}:", value_label)

        # If it's a structure type, show fields
        if signal_info.get("is_struct", False) and "struct_fields" in signal_info:
            struct_group = QGroupBox("Structure Fields")
            struct_layout = QtWidgets.QVBoxLayout(struct_group)
            
            # Create a tree for structure fields
            field_tree = QtWidgets.QTreeWidget()
            field_tree.setHeaderLabels(["Field Name", "Type", "Description"])
            field_tree.setColumnWidth(0, 150)
            field_tree.setColumnWidth(1, 100)
            
            # Add fields to tree
            for field_name, field_info in signal_info["struct_fields"].items():
                field_item = QtWidgets.QTreeWidgetItem([
                    field_name,
                    field_info.get("type", ""),
                    field_info.get("description", "")
                ])
                field_tree.addTopLevelItem(field_item)
            struct_layout.addWidget(field_tree)
            layout.addRow(struct_group)

        # Show core destinations if available
        core_targets = []
        for key in signal_info:
            if key.startswith("core_") and signal_info[key]:
                core_name = key[5:].replace('_', '.')
                core_targets.append(core_name)
        
        if core_targets:
            dest_label = QtWidgets.QLabel(", ".join(core_targets))
            dest_label.setWordWrap(True)
            layout.addRow("Destination Cores:", dest_label)

        # Complete the scroll area
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Add Edit button at the bottom
        edit_button = QPushButton("Edit Signal")
        edit_button.clicked.connect(lambda: self.edit_signal_details(signal_name))
        main_layout.addWidget(edit_button)

        # Set as the current widget in the stacked widget
        if self.ui.SignalInternalInfo.count() > 0:
            # Remove any existing custom pages
            while self.ui.SignalInternalInfo.count() > 0:
                widget = self.ui.SignalInternalInfo.widget(0)
                self.ui.SignalInternalInfo.removeWidget(widget)
        self.ui.SignalInternalInfo.addWidget(detail_widget)
        self.ui.SignalInternalInfo.setCurrentWidget(detail_widget)

    def update_core_info(self):
        # Update both CoreInfo and CoreInfo_2 widgets with metadata
        for core_info_widget in [self.ui.CoreInfo_2]:
            core_info_widget.clear()
            
            # Add metadata
            metadata = self.signals_data.get("metadata", {})
            metadata_item = QTreeWidgetItem(core_info_widget, ["Metadata"])
            
            for key, value in metadata.items():
                QTreeWidgetItem(metadata_item, [key, str(value)])
            
            # Add export reference
            export_sheet = self.signals_data.get("export_sheet_name", "Config")
            QTreeWidgetItem(core_info_widget, ["Export Sheet", export_sheet])
                
            # Add SOC and build type
            QTreeWidgetItem(core_info_widget, ["SOC Type", self.signals_data.get("soc_type", "")])
            QTreeWidgetItem(core_info_widget, ["Build Type", self.signals_data.get("build_type", "")])
            
            # Add core information
            core_info = self.signals_data.get("core_info", {})
            if core_info:
                core_item = QTreeWidgetItem(core_info_widget, ["Core Configuration"])
                for soc_name, cores in core_info.items():
                    soc_item = QTreeWidgetItem(core_item, [soc_name])
                    for core_name, core_data in cores.items():
                        # Handle both string descriptions and dictionary properties
                        if isinstance(core_data, dict):
                            props = core_data
                            desc = props.get("description", "")
                            # Create core node with detailed info
                            core_node = QTreeWidgetItem(soc_item, [core_name])
                            
                            # Add property nodes
                            QTreeWidgetItem(core_node, ["Description", desc])
                            QTreeWidgetItem(core_node, ["Master/Slave", "Master" if props.get("is_master", False) else "Slave"])
                            QTreeWidgetItem(core_node, ["QNX Core", "Yes" if props.get("is_qnx", False) else "No"])
                            QTreeWidgetItem(core_node, ["Autosar Core", "Yes" if props.get("is_autosar", False) else "No"])
                            QTreeWidgetItem(core_node, ["Sim Core", "Yes" if props.get("is_sim", False) else "No"])
                            QTreeWidgetItem(core_node, ["OS", props.get("os", "Unknown")])
                            QTreeWidgetItem(core_node, ["SOC Family", props.get("soc_family", "Unknown")])
                        else:
                            # Legacy format - just show description
                            QTreeWidgetItem(soc_item, [core_name, str(core_data)])
            
            # Add signal count
            signal_count = len(self.signals_data.get("signals", {}))
            QTreeWidgetItem(core_info_widget, ["Signal Count", str(signal_count)])
            
            # Expand all items
            core_info_widget.expandAll()

    def refresh_signal_tree(self):
        # Clear and repopulate the signal tree
        self.signal_tree.clear()
        if "signals" in self.signals_data:
            for signal_name, signal_info in self.signals_data["signals"].items():
                item = QTreeWidgetItem([
                    signal_name,
                    signal_info.get("DataType", ""),  # Changed from "type" to "DataType"
                    signal_info.get("description", "")
                ])
                self.signal_tree.addTopLevelItem(item)  # Fixed: addItem -> addTopLevelItem

    def soc_selection_changed(self, index):
        if index > 0:  # Not the default "Select SOC" item
            soc_type = self.ui.SOCList.currentText()
            self.signals_data["soc_type"] = soc_type
            self.modified = True
            self.update_window_title()
            self.update_core_info()

    def build_type_changed(self, index):
        if index > 0:  # Not the default "Select Build Type" item
            build_type = self.ui.BuildImageType.currentText()
            self.signals_data["build_type"] = build_type
            self.modified = True
            self.update_window_title()
            self.update_core_info()

    def open_configuration_manager(self, is_new_file=False):
        from config_manager_dialog import ConfigManagerDialog
        # Open the configuration manager dialog
        config_dialog = ConfigManagerDialog(self.signals_data, self)
        if is_new_file:
            # Initialize new empty configuration
            self.signals_data = {
                "metadata": {
                    "version": "1.0",
                    "created": "",
                    "modified": "",
                    "description": "Signal Configuration"
                },
                "soc_type": "",
                "build_type": "",
                "core_info": {},  # For storing core configuration
                "signals": {}
            }
            self.current_file = None
            self.modified = True
            self.update_window_title()
        # Show the configuration manager dialog
        if config_dialog.exec_():
            # If user clicked OK, update the configuration
            self.signals_data = config_dialog.get_updated_config()
            self.modified = True
            self.update_window_title()
            self.populate_soc_list()
            self.populate_build_types()
            self.refresh_signal_tree()
            self.update_core_info()

    def save_undo_state(self):
        # Save current state to undo stack
        self.undo_stack.append(self.signals_data.copy())
        # Clear redo stack after a new action
        self.redo_stack.clear()

    def undo_action(self):
        if self.undo_stack:
            # Save current state to redo stack
            self.redo_stack.append(self.signals_data.copy())
            # Restore previous state
            self.signals_data = self.undo_stack.pop()
            self.modified = True
            self.update_window_title()
            self.refresh_signal_tree()
            self.update_core_info()
            # After undo, update the signal count
            self.update_signal_count_display()

    def redo_action(self):
        if self.redo_stack:
            # Save current state to undo stack
            self.undo_stack.append(self.signals_data.copy())
            # Restore next state
            self.signals_data = self.redo_stack.pop()
            self.modified = True
            self.update_window_title()
            self.refresh_signal_tree()
            self.update_core_info()
            # After redo, update the signal count
            self.update_signal_count_display()

    def check_unsaved_changes(self):
        if self.modified:
            reply = QMessageBox.question(self, "Unsaved Changes", 
                                        "You have unsaved changes. Do you want to save them?",
                                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if reply == QMessageBox.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.Discard:
                return True
            else:
                return False
        return True

    def update_window_title(self):
        title = "Signal Manager Tool"
        if self.current_file:
            filename = os.path.basename(self.current_file)
            title = f"{filename} - {title}"
        if self.modified:
            title = f"*{title}"
        self.setWindowTitle(title)

    def edit_signal_details(self, signal_name):
        if "signals" in self.signals_data and signal_name in self.signals_data["signals"]:
            from signal_details_dialog import SignalDetailsDialog
            # Get available cores for source selection
            available_cores = self.get_available_cores()
            # Create and show the signal details dialog
            dialog = SignalDetailsDialog(self, signal_name, self.signals_data["signals"][signal_name], available_cores)
            if dialog.exec_():
                # Save current state for undo
                self.save_undo_state()
                # Update signal with new properties
                self.signals_data["signals"][signal_name] = dialog.get_signal_properties()
                self.modified = True
                self.update_window_title()
                self.refresh_signal_tree()
                # If currently selected, update display
                current_item = self.signal_tree.currentItem()
                if current_item and current_item.text(0) == signal_name:
                    self.display_signal_details(signal_name, self.signals_data["signals"][signal_name])

    def get_available_cores(self):
        # Extract all core names from the configuration
        cores = []
        core_info = self.signals_data.get("core_info", {})
        for soc_name, soc_cores in core_info.items():
            for core_name in soc_cores.keys():
                cores.append(f"{soc_name}.{core_name}")
        return cores

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SignalMgrApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()