from PyQt5.QtWidgets import QMessageBox, QInputDialog, QTreeWidgetItem

class SignalOperations:
    def __init__(self, app):
        self.app = app

    def add_signal(self):
        signal_name, ok = QInputDialog.getText(self.app, "Add Signal", "Enter signal name:")
        if ok and signal_name:
            if signal_name in self.app.signals_data.get("signals", {}):
                QMessageBox.warning(self.app, "Warning", f"Signal '{signal_name}' already exists")
                return
            # Save current state for undo
            self.app.ui_helpers.save_undo_state()
            # Initialize signals dict if not exists
            if "signals" not in self.app.signals_data:
                self.app.signals_data["signals"] = {}
            # Add new signal with default properties
            self.app.signals_data["signals"][signal_name] = {
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
            
            self.app.modified = True
            self.app.ui_helpers.update_window_title()
            self.app.ui_helpers.refresh_signal_tree()
            # Select the newly added signal to show its details
            for i in range(self.app.ui_helpers.signal_tree.topLevelItemCount()):
                item = self.app.ui_helpers.signal_tree.topLevelItem(i)
                if item.text(0) == signal_name:
                    self.app.ui_helpers.signal_tree.setCurrentItem(item)
                    # Force display of signal details
                    self.app.ui_helpers.display_signal_details(signal_name, self.app.signals_data["signals"][signal_name])
                    break
            # After successfully adding a signal, update the count
            self.app.ui_helpers.update_signal_count_display()

    def delete_signal(self):
        if not self.app.ui_helpers.signal_tree.currentItem():
            QMessageBox.warning(self.app, "Warning", "No signal selected")
            return
        signal_name = self.app.ui_helpers.signal_tree.currentItem().text(0)
        reply = QMessageBox.question(self.app, "Confirm Delete", 
                                    f"Are you sure you want to delete signal '{signal_name}'?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Save current state for undo
            self.app.ui_helpers.save_undo_state()
            # Delete the signal
            if "signals" in self.app.signals_data and signal_name in self.app.signals_data["signals"]:
                del self.app.signals_data["signals"][signal_name]
                self.app.modified = True
                self.app.ui_helpers.update_window_title()
                self.app.ui_helpers.refresh_signal_tree()
                QMessageBox.information(self.app, "Success", f"Signal '{signal_name}' deleted")
                # After successfully deleting a signal, update the count
                self.app.ui_helpers.update_signal_count_display()

    def update_signal(self):
        if not self.app.ui_helpers.signal_tree.currentItem():
            QMessageBox.warning(self.app, "Warning", "No signal selected")
            return
        signal_name = self.app.ui_helpers.signal_tree.currentItem().text(0)
        self.edit_signal_details(signal_name)

    def rename_signal(self):
        if not self.app.ui_helpers.signal_tree.currentItem():
            QMessageBox.warning(self.app, "Warning", "No signal selected")
            return
        old_name = self.app.ui_helpers.signal_tree.currentItem().text(0)
        new_name, ok = QInputDialog.getText(self.app, "Rename Signal", 
                                                     "Enter new signal name:", text=old_name)
        if ok and new_name and new_name != old_name:
            if new_name in self.app.signals_data.get("signals", {}):
                QMessageBox.warning(self.app, "Warning", f"Signal '{new_name}' already exists")
                return
            # Save current state for undo
            self.app.ui_helpers.save_undo_state()
            # Rename the signal
            if "signals" in self.app.signals_data and old_name in self.app.signals_data["signals"]:
                self.app.signals_data["signals"][new_name] = self.app.signals_data["signals"][old_name]
                del self.app.signals_data["signals"][old_name]
                self.app.modified = True
                self.app.ui_helpers.update_window_title()
                self.app.ui_helpers.refresh_signal_tree()
                QMessageBox.information(self.app, "Success", f"Signal renamed to '{new_name}'")

    def copy_signal(self):
        if not self.app.ui_helpers.signal_tree.currentItem():
            QMessageBox.warning(self.app, "Warning", "No signal selected")
            return
        signal_name = self.app.ui_helpers.signal_tree.currentItem().text(0)
        if "signals" in self.app.signals_data and signal_name in self.app.signals_data["signals"]:
            self.app.copied_signal = {
                "name": signal_name,
                "properties": self.app.signals_data["signals"][signal_name].copy()
            }
            QMessageBox.information(self.app, "Success", f"Signal '{signal_name}' copied")

    def paste_signal(self):
        if not self.app.copied_signal:
            QMessageBox.warning(self.app, "Warning", "No signal copied")
            return
        original_name = self.app.copied_signal["name"]
        new_name = f"{original_name}_copy"
        # Find a unique name
        counter = 1
        while new_name in self.app.signals_data.get("signals", {}):
            new_name = f"{original_name}_copy{counter}"
            counter += 1
        # Save current state for undo
        self.app.ui_helpers.save_undo_state()
        # Initialize signals dict if not exists
        if "signals" not in self.app.signals_data:
            self.app.signals_data["signals"] = {}
        # Add the copied signal with the new name
        self.app.signals_data["signals"][new_name] = self.app.copied_signal["properties"].copy()
        self.app.modified = True
        self.app.ui_helpers.update_window_title()
        self.app.ui_helpers.refresh_signal_tree()
        QMessageBox.information(self.app, "Success", f"Signal pasted as '{new_name}'")
        # After pasting a signal, update the count
        self.app.ui_helpers.update_signal_count_display()

    def edit_signal_details(self, signal_name):
        if "signals" in self.app.signals_data and signal_name in self.app.signals_data["signals"]:
            from signal_details_dialog import SignalDetailsDialog
            # Get available cores for source selection
            available_cores = self.app.ui_helpers.get_available_cores()
            # Create and show the signal details dialog
            dialog = SignalDetailsDialog(self.app, signal_name, self.app.signals_data["signals"][signal_name], available_cores)
            if dialog.exec_():
                # Save current state for undo
                self.app.ui_helpers.save_undo_state()
                # Update signal with new properties
                self.app.signals_data["signals"][signal_name] = dialog.get_signal_properties()
                self.app.modified = True
                self.app.ui_helpers.update_window_title()
                self.app.ui_helpers.refresh_signal_tree()
                # If currently selected, update display
                current_item = self.app.ui_helpers.signal_tree.currentItem()
                if current_item and current_item.text(0) == signal_name:
                    self.app.ui_helpers.display_signal_details(signal_name, self.app.signals_data["signals"][signal_name])

    def open_configuration_manager(self, is_new_file=False):
        """Open configuration manager with proper handling for UI structure"""
        from config_manager_dialog import ConfigManagerDialog
        
        # Open the configuration manager dialog without requiring version checks
        config_dialog = ConfigManagerDialog(self.app.signals_data, self.app)
        if is_new_file:
            # Initialize new empty configuration
            self.app.signals_data = {
                "metadata": {
                    "version": "1.0",
                    "date": "",
                    "editor": "",
                    "description": "Signal Configuration"
                },
                "soc_type": "Windows",  # Default to Windows
                "build_type": "SMP",    # Default to SMP
                "soc_list": ["Windows"],    # Default SOC list with Windows
                "build_list": ["SMP"],      # Default build list with SMP
                "core_info": {},            # For storing core configuration
                "signals": {}               # For storing signals
            }
            self.app.current_file = None
            self.app.modified = True
            self.app.ui_helpers.update_window_title()
        
        # Show the configuration manager dialog
        if config_dialog.exec_():
            # If user clicked OK, update the configuration
            updated_config = config_dialog.get_updated_config()
            self.app.signals_data = updated_config
            self.app.modified = True
            self.app.ui_helpers.update_window_title()
            self.app.ui_helpers.populate_soc_list()
            self.app.ui_helpers.populate_build_types()
            self.app.ui_helpers.refresh_signal_tree()
            self.app.ui_helpers.update_core_info()

    def load_config(self, config_data):
        """Load configuration data into the UI"""
        # Get the CoreInfo_2 widget and check if it's a QScrollArea
        core_info_widget = getattr(self.app.ui, "CoreInfo_2", None)
        
        if core_info_widget and isinstance(core_info_widget, QtWidgets.QScrollArea):
            # For the new UI with scroll area
            if hasattr(self.app.ui, 'coreInfoContents') and hasattr(self.app.ui, 'coreInfoLayout'):
                # Clear existing content
                while self.app.ui.coreInfoLayout.count():
                    item = self.app.ui.coreInfoLayout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                # Create a tree widget to add to the scroll area
                tree = QtWidgets.QTreeWidget()
                tree.setHeaderLabels(["Core Details"])
                self.app.ui.coreInfoLayout.addWidget(tree)
                
                # Now populate the tree
                if "core_info" in config_data:
                    core_info = config_data["core_info"]
                    
                    for soc_name, cores in core_info.items():
                        for core_name, core_data in cores.items():
                            # Create core item directly under root (not under SOC)
                            core_item = QTreeWidgetItem(tree)
                            core_item.setText(0, f"Core: {core_name}")
                            
                            # Add properties based on data type
                            if isinstance(core_data, dict):
                                # Show core properties for dictionary format
                                role_str = "Master" if core_data.get("is_master", False) else "Slave"
                                role_item = QTreeWidgetItem(core_item)
                                role_item.setText(0, f"Role: {role_str}")
                                
                                # OS info
                                os_str = str(core_data.get("os", "Unknown"))
                                os_item = QTreeWidgetItem(core_item)
                                os_item.setText(0, f"OS: {os_str}")
                                
                                # Boolean properties
                                for prop_name, display_name in [
                                    ("is_qnx", "QNX Core"),
                                    ("is_autosar", "Autosar Compliant"),
                                    ("is_sim", "Simulation Core")
                                ]:
                                    if core_data.get(prop_name, False):
                                        prop_item = QTreeWidgetItem(core_item)
                                        prop_item.setText(0, f"{display_name}: Yes")
                            else:
                                # If it's just a string or other scalar value
                                desc_item = QTreeWidgetItem(core_item)
                                desc_item.setText(0, str(core_data))
                    
                    tree.expandAll()
        
        # Update the other parts of the UI as needed
        # ... existing code...
