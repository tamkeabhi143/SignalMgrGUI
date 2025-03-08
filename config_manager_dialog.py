#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QListWidget, QListWidgetItem, QTabWidget, 
                            QTreeWidget, QTreeWidgetItem, QMessageBox, QGroupBox,
                            QFormLayout, QInputDialog, QMenu)
from PyQt5.QtCore import Qt

# Import CorePropertiesDialog
from core_properties_dialog import CorePropertiesDialog


class ConfigManagerDialog(QDialog):
    def __init__(self, config_data, parent=None):
        super(ConfigManagerDialog, self).__init__(parent)
        self.config_data = config_data.copy() if config_data else {}
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        self.setWindowTitle("Configuration Manager")
        self.resize(700, 500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_soc_tab()
        self.create_build_type_tab()
        self.create_core_info_tab()
        self.create_metadata_tab()
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)
        
        # Connect buttons
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def create_soc_tab(self):
        # Create SOC tab
        soc_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(soc_tab, "SOC List")
        
        # Layout for SOC tab
        layout = QVBoxLayout(soc_tab)
        
        # SOC list
        layout.addWidget(QLabel("SOC Types:"))
        self.soc_list = QListWidget()
        layout.addWidget(self.soc_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_soc_button = QPushButton("Add SOC")
        self.remove_soc_button = QPushButton("Remove SOC")
        button_layout.addWidget(self.add_soc_button)
        button_layout.addWidget(self.remove_soc_button)
        layout.addLayout(button_layout)
        
        # Connect buttons
        self.add_soc_button.clicked.connect(self.add_soc)
        self.remove_soc_button.clicked.connect(self.remove_soc)
        
        # Current SOC selection
        current_soc_group = QGroupBox("Current SOC Selection")
        form_layout = QFormLayout(current_soc_group)
        self.current_soc_combo = QtWidgets.QComboBox()
        form_layout.addRow("Selected SOC:", self.current_soc_combo)
        layout.addWidget(current_soc_group)
        
    def create_build_type_tab(self):
        # Create Build Type tab
        build_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(build_tab, "Build Types")
        
        # Layout for Build Type tab
        layout = QVBoxLayout(build_tab)
        
        # Build type list
        layout.addWidget(QLabel("Build Types:"))
        self.build_type_list = QListWidget()
        layout.addWidget(self.build_type_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_build_button = QPushButton("Add Build Type")
        self.remove_build_button = QPushButton("Remove Build Type")
        button_layout.addWidget(self.add_build_button)
        button_layout.addWidget(self.remove_build_button)
        layout.addLayout(button_layout)
        
        # Connect buttons
        self.add_build_button.clicked.connect(self.add_build_type)
        self.remove_build_button.clicked.connect(self.remove_build_type)
        
        # Current build type selection
        current_build_group = QGroupBox("Current Build Type Selection")
        form_layout = QFormLayout(current_build_group)
        self.current_build_combo = QtWidgets.QComboBox()
        form_layout.addRow("Selected Build Type:", self.current_build_combo)
        layout.addWidget(current_build_group)
        
        # Add export sheet reference
        export_group = QGroupBox("Export Reference")
        export_layout = QFormLayout(export_group)
        self.export_sheet_name = QLineEdit("Config")  # Default to 'Config'
        export_layout.addRow("Export Sheet Name:", self.export_sheet_name)
        layout.addWidget(export_group)
        
    def create_core_info_tab(self):
        # Create Core Info tab
        core_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(core_tab, "Core Info")
        
        # Layout for Core Info tab
        layout = QVBoxLayout(core_tab)
        
        # Core Info tree - update header labels to show more information
        layout.addWidget(QLabel("Core Configuration:"))
        self.core_tree = QTreeWidget()
        self.core_tree.setHeaderLabels(["Name", "Description", "Master/Slave", "OS Type", "SOC Family"])
        self.core_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.core_tree.customContextMenuRequested.connect(self.show_core_context_menu)
        layout.addWidget(self.core_tree)
        
        # Buttons for core management
        button_layout = QHBoxLayout()
        self.add_soc_node_button = QPushButton("Add SOC Node")
        self.add_core_button = QPushButton("Add Core")
        self.remove_node_button = QPushButton("Remove Selected")
        button_layout.addWidget(self.add_soc_node_button)
        button_layout.addWidget(self.add_core_button)
        button_layout.addWidget(self.remove_node_button)
        layout.addLayout(button_layout)
        
        # Connect buttons
        self.add_soc_node_button.clicked.connect(self.add_soc_node)
        self.add_core_button.clicked.connect(self.add_core_node)
        self.remove_node_button.clicked.connect(self.remove_selected_node)
        
    def create_metadata_tab(self):
        # Create Metadata tab
        meta_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(meta_tab, "Metadata")
        
        # Layout for Metadata tab
        layout = QFormLayout(meta_tab)
        
        # Version field
        self.version_edit = QLineEdit()
        layout.addRow("Version:", self.version_edit)
        
        # Description field
        self.description_edit = QLineEdit()
        layout.addRow("Description:", self.description_edit)

    def load_config(self):
        """Load existing configuration into the UI"""
        # Clear existing data first
        self.core_tree.clear()
        self.soc_list.clear()
        self.current_soc_combo.clear()
        self.build_type_list.clear()
        self.current_build_combo.clear()
        
        # Populate the tree with core information
        core_info = self.config_data.get("core_info", {})
        
        for soc_name, cores in core_info.items():
            # Create SOC item properly as a tree widget item
            soc_item = QTreeWidgetItem(self.core_tree)
            soc_item.setText(0, soc_name)
            
            # Add this SOC to the SOC list if it's not there
            if self.soc_list.findItems(soc_name, Qt.MatchExactly) == []:
                self.soc_list.addItem(soc_name)
                self.current_soc_combo.addItem(soc_name)
            
            for core_name, core_desc in cores.items():
                # Create core item properly as a tree widget item
                core_item = QTreeWidgetItem(soc_item)
                core_item.setText(0, core_name)
                
                # Handle core_desc depending on its type
                if isinstance(core_desc, dict):
                    # Create a summary string for display
                    summary = []
                    if core_desc.get("is_master", False):
                        summary.append("Master")
                        # Also set the Master/Slave column
                        core_item.setText(2, "Master")
                    else:
                        summary.append("Slave")
                        # Also set the Master/Slave column
                        core_item.setText(2, "Slave")
                    
                    # Add OS information
                    os_type = core_desc.get("os", "Unknown")
                    summary.append(f"OS: {os_type}")
                    # Set the OS column
                    core_item.setText(3, os_type)
                    
                    # Set the SOC family if available
                    soc_family = core_desc.get("soc_family", "Unknown")
                    core_item.setText(4, soc_family)
                    
                    # Set the description column
                    core_item.setText(1, core_desc.get("description", ", ".join(summary)))
                    
                    # Store the full dictionary in the item's data for retrieval later
                    core_item.setData(0, Qt.UserRole, core_desc)
                else:
                    # If it's a string or other simple type, just convert to string and show as description
                    core_item.setText(1, str(core_desc))
        
        # Load SOC list - ensure unique entries
        soc_list = self.config_data.get("soc_list", ["Windows"])
        for soc in soc_list:
            # Check if SOC already exists in the list
            if self.soc_list.findItems(soc, Qt.MatchExactly) == []:
                self.soc_list.addItem(soc)
                self.current_soc_combo.addItem(soc)
    
        # Add SOCs from core_info to soc_list if they're not already there
        for soc_name in core_info.keys():
            if self.soc_list.findItems(soc_name, Qt.MatchExactly) == []:
                self.soc_list.addItem(soc_name)
                self.current_soc_combo.addItem(soc_name)
        
        # Set current SOC selection
        current_soc = self.config_data.get("soc_type", "")
        index = self.current_soc_combo.findText(current_soc)
        if index >= 0:
            self.current_soc_combo.setCurrentIndex(index)
        
        # Load build type list
        build_types = self.config_data.get("build_list", ["SMP","MultiImage","Simulation"])
        for build_type in build_types:
            self.build_type_list.addItem(build_type)
            self.current_build_combo.addItem(build_type)
        
        # Set current build type selection
        current_build = self.config_data.get("build_type", "")
        index = self.current_build_combo.findText(current_build)
        if index >= 0:
            self.current_build_combo.setCurrentIndex(index)
        
        # Expand all items
        self.core_tree.expandAll()
        
        # Load metadata
        metadata = self.config_data.get("metadata", {})
        self.version_edit.setText(metadata.get("version", "1.0"))
        self.description_edit.setText(metadata.get("description", "Signal Configuration"))
        
        # Load export sheet name
        self.export_sheet_name.setText(self.config_data.get("export_sheet_name", "Config"))
    
    def get_updated_config(self):
        # Update config with current values
        
        # Update SOC list - make sure we include SOCs from core_info
        soc_list = []
        for i in range(self.soc_list.count()):
            soc_list.append(self.soc_list.item(i).text())
        
        # Also include any SOCs from the core_info tree that might not be in the SOC list
        root = self.core_tree.invisibleRootItem()
        for i in range(root.childCount()):
            soc_name = root.child(i).text(0)
            if soc_name not in soc_list:
                soc_list.append(soc_name)
            
        self.config_data["soc_list"] = soc_list
        
        # Update current SOC
        self.config_data["soc_type"] = self.current_soc_combo.currentText()
        
        # Update build type list
        build_list = []
        for i in range(self.build_type_list.count()):
            build_list.append(self.build_type_list.item(i).text())
        self.config_data["build_list"] = build_list
        
        # Update current build type
        self.config_data["build_type"] = self.current_build_combo.currentText()
        
        # Update core info
        core_info = {}
        root = self.core_tree.invisibleRootItem()
        for i in range(root.childCount()):
            soc_item = root.child(i)
            soc_name = soc_item.text(0)
            cores = {}
            
            for j in range(soc_item.childCount()):
                core_item = soc_item.child(j)
                core_name = core_item.text(0)
                
                # Get core properties from the item data or create default
                core_props = core_item.data(0, Qt.UserRole)
                if not core_props:
                    # Create default properties from displayed values
                    core_props = {
                        "name": core_name,
                        "description": core_item.text(1),
                        "is_master": core_item.text(2) == "Master" if len(core_item.text(2)) > 0 else False,
                        "is_qnx": False,
                        "is_autosar": False,
                        "is_sim": False,
                        "os": core_item.text(3) if len(core_item.text(3)) > 0 else "Unknown",
                        "soc_family": core_item.text(4) if len(core_item.text(4)) > 0 else "Unknown"
                    }
                
                # Store the dictionary with all properties
                cores[core_name] = core_props
            
            core_info[soc_name] = cores
        
        self.config_data["core_info"] = core_info
        
        # Update metadata
        if "metadata" not in self.config_data:
            self.config_data["metadata"] = {}
        
        self.config_data["metadata"]["version"] = self.version_edit.text()
        self.config_data["metadata"]["description"] = self.description_edit.text()
        
        # Update export sheet name
        self.config_data["export_sheet_name"] = self.export_sheet_name.text()
        
        return self.config_data
    
    # SOC Tab Methods
    def add_soc(self):
        soc_name, ok = QInputDialog.getText(self, "Add SOC", "Enter SOC name:")
        if ok and soc_name:
            # Check if SOC already exists
            for i in range(self.soc_list.count()):
                if self.soc_list.item(i).text() == soc_name:
                    QMessageBox.warning(self, "Warning", f"SOC '{soc_name}' already exists")
                    return
            
            # Add to SOC list and combo
            self.soc_list.addItem(soc_name)
            self.current_soc_combo.addItem(soc_name)
        
            # Also add to Core Info tree if not already there
            root = self.core_tree.invisibleRootItem()
            exists = False
            for i in range(root.childCount()):
                if root.child(i).text(0) == soc_name:
                    exists = True
                    break
                
            if not exists:
                # Add new SOC node to Core Info tree
                soc_item = QTreeWidgetItem([soc_name, "SOC"])
                self.core_tree.addTopLevelItem(soc_item)
                self.core_tree.expandItem(soc_item)
    
    def remove_soc(self):
        selected_items = self.soc_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No SOC selected")
            return
        
        for item in selected_items:
            soc_name = item.text()
            
            # Check if this SOC has cores in the Core Info tree
            root = self.core_tree.invisibleRootItem()
            has_cores = False
            for i in range(root.childCount()):
                if root.child(i).text(0) == soc_name and root.child(i).childCount() > 0:
                    has_cores = True
                    break
        
            if has_cores:
                reply = QMessageBox.question(
                    self, 
                    "Confirm SOC Removal",
                    f"SOC '{soc_name}' has configured cores. Are you sure you want to remove it?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    continue
                
            # Remove from SOC list
            self.soc_list.takeItem(self.soc_list.row(item))
            
            # Remove from combo
            index = self.current_soc_combo.findText(soc_name)
            if index >= 0:
                self.current_soc_combo.removeItem(index)
            
            # Remove from Core Info tree
            for i in range(root.childCount()):
                if root.child(i).text(0) == soc_name:
                    root.takeChild(i)
                    break
    
    # Build Type Tab Methods
    def add_build_type(self):
        build_name, ok = QInputDialog.getText(self, "Add Build Type", "Enter build type name:")
        if ok and build_name:
            # Check if build type already exists
            for i in range(self.build_type_list.count()):
                if self.build_type_list.item(i).text() == build_name:
                    QMessageBox.warning(self, "Warning", f"Build type '{build_name}' already exists")
                    return
            
            # Add to list and combo
            self.build_type_list.addItem(build_name)
            self.current_build_combo.addItem(build_name)
    
    def remove_build_type(self):
        selected_items = self.build_type_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No build type selected")
            return
        
        for item in selected_items:
            build_name = item.text()
            # Remove from list
            self.build_type_list.takeItem(self.build_type_list.row(item))
            
            # Remove from combo
            index = self.current_build_combo.findText(build_name)
            if index >= 0:
                self.current_build_combo.removeItem(index)
    
    # Core Info Tab Methods
    def add_soc_node(self):
        soc_name, ok = QInputDialog.getText(self, "Add SOC Node", "Enter SOC name:")
        if ok and soc_name:
            # Check if SOC already exists
            root = self.core_tree.invisibleRootItem()
            for i in range(root.childCount()):
                if root.child(i).text(0) == soc_name:
                    QMessageBox.warning(self, "Warning", f"SOC '{soc_name}' already exists")
                    return
            
            # Add new SOC node to Core Info tree
            soc_item = QTreeWidgetItem([soc_name, "SOC"])
            self.core_tree.addTopLevelItem(soc_item)
            self.core_tree.expandItem(soc_item)
        
            # Also add to SOC list if not already there
            if self.soc_list.findItems(soc_name, Qt.MatchExactly) == []:
                self.soc_list.addItem(soc_name)
                self.current_soc_combo.addItem(soc_name)
    
    def add_core_node(self):
        selected_items = self.core_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Select an SOC to add a core to")
            return
        
        selected_item = selected_items[0]
        
        # Check if selected item is an SOC node
        if selected_item.parent() is not None:
            selected_item = selected_item.parent()  # Navigate up to the parent SOC
        
        # Create a dialog for core properties
        core_dialog = CorePropertiesDialog(self)
        if core_dialog.exec_():
            core_props = core_dialog.get_properties()
            
            # Check if core already exists under this SOC
            for i in range(selected_item.childCount()):
                if selected_item.child(i).text(0) == core_props["name"]:
                    QMessageBox.warning(self, "Warning", f"Core '{core_props['name']}' already exists in this SOC")
                    return
            
            # Add core to SOC with properties
            core_item = QTreeWidgetItem([
                core_props["name"], 
                core_props["description"],
                "Master" if core_props["is_master"] else "Slave",
                core_props["os"],
                core_props["soc_family"]
            ])
            
            # Store all properties as data
            core_item.setData(0, Qt.UserRole, core_props)
            selected_item.addChild(core_item)
    
    def remove_selected_node(self):
        selected_items = self.core_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No item selected")
            return
        
        for item in selected_items:
            parent = item.parent()
            if parent:
                # Remove child item
                parent.removeChild(item)
            else:
                # Remove top-level item
                index = self.core_tree.indexOfTopLevelItem(item)
                if index >= 0:
                    self.core_tree.takeTopLevelItem(index)
    
    def show_core_context_menu(self, position):
        menu = QMenu()
        
        # Get selected item
        items = self.core_tree.selectedItems()
        if items:
            item = items[0]
            
            if item.parent() is None:
                # SOC node selected
                menu.addAction("Add Core", self.add_core_node)
                menu.addAction("Rename SOC", lambda: self.rename_node(item))
                menu.addAction("Remove SOC", lambda: self.remove_node(item))
            else:
                # Core node selected
                menu.addAction("Rename Core", lambda: self.rename_node(item))
                menu.addAction("Edit Description", lambda: self.edit_description(item))
                menu.addAction("Edit Core Properties", lambda: self.edit_core_properties(item))
                menu.addAction("Remove Core", lambda: self.remove_node(item))
        else:
            # No selection, show only add SOC option
            menu.addAction("Add SOC Node", self.add_soc_node)
            
        menu.exec_(self.core_tree.viewport().mapToGlobal(position))
    
    def rename_node(self, item):
        old_name = item.text(0)
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=old_name)
        
        if ok and new_name and new_name != old_name:
            # Check for duplicates
            parent = item.parent()
            if parent:
                # Check siblings for duplicates (for core nodes)
                for i in range(parent.childCount()):
                    if parent.child(i).text(0) == new_name:
                        QMessageBox.warning(self, "Warning", f"'{new_name}' already exists")
                        return
            else:
                # Check top-level items for duplicates (for SOC nodes)
                root = self.core_tree.invisibleRootItem()
                for i in range(root.childCount()):
                    if root.child(i).text(0) == new_name:
                        QMessageBox.warning(self, "Warning", f"SOC '{new_name}' already exists")
                        return
            
            # Rename the item
            item.setText(0, new_name)
    
    def edit_description(self, item):
        old_desc = item.text(1)
        new_desc, ok = QInputDialog.getText(self, "Edit Description", 
                                           "Enter new description:", text=old_desc)
        
        if ok:
            item.setText(1, new_desc)
    
    def edit_core_properties(self, item):
        # Get existing properties
        props = item.data(0, Qt.UserRole)
        if not props:
            # If no properties exist, create default ones
            props = {
                "name": item.text(0),
                "description": item.text(1),
                "is_master": item.text(2) == "Master",
                "is_qnx": False,
                "is_autosar": False,
                "is_sim": False,
                "os": "Autosar",
                "soc_family": "TI"
            }
        
        # Create and show dialog with existing properties
        core_dialog = CorePropertiesDialog(self, props)
        if core_dialog.exec_():
            # Update properties
            props = core_dialog.get_properties()
            
            # Update item display
            item.setText(0, props["name"])
            item.setText(1, props["description"])
            item.setText(2, "Master" if props["is_master"] else "Slave")
            item.setText(3, props["os"])
            item.setText(4, props["soc_family"])
            
            # Store updated properties
            item.setData(0, Qt.UserRole, props)
    
    def remove_node(self, item):
        name = item.text(0)
        msg = f"Are you sure you want to remove '{name}'?"
        if item.parent() is None:
            msg += f" This will also remove all cores under this SOC."
            
        reply = QMessageBox.question(self, "Confirm Removal", msg, 
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            parent = item.parent()
            if parent:
                # Remove child item
                parent.removeChild(item)
            else:
                # Remove top-level item
                index = self.core_tree.indexOfTopLevelItem(item)
                if index >= 0:
                    self.core_tree.takeTopLevelItem(index)
