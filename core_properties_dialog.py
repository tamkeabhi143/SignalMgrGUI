#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QComboBox, QCheckBox, QPushButton, QFormLayout)

class CorePropertiesDialog(QDialog):
    """Dialog for configuring core properties"""
    def __init__(self, parent=None, properties=None):
        super(CorePropertiesDialog, self).__init__(parent)
        self.setWindowTitle("Core Properties")
        self.resize(400, 300)
        
        # Initialize with default or given properties
        self.properties = properties or {
            "name": "",
            "description": "",
            "is_master": False,
            "is_qnx": False,
            "is_autosar": False,
            "is_sim": False,
            "os": "Unknown",
            "soc_family": "Unknown"
        }
        
        self.setup_ui()
        self.load_properties()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Core name
        self.name_edit = QLineEdit(self.properties.get("name", ""))
        layout.addRow("Core Name:", self.name_edit)
        
        # Description
        self.description_edit = QLineEdit(self.properties.get("description", ""))
        layout.addRow("Description:", self.description_edit)
        
        # Master/Slave selection
        self.master_checkbox = QCheckBox("Is Master Core")
        self.master_checkbox.setChecked(self.properties.get("is_master", False))
        layout.addRow("", self.master_checkbox)
        
        # OS Type dropdown with "Other" option
        self.os_combo = QComboBox()
        os_options = ["Unknown", "Linux", "QNX", "AUTOSAR", "FreeRTOS", "Windows", "Other"]
        self.os_combo.addItems(os_options)
        
        # Custom OS input field (initially hidden)
        self.custom_os_edit = QLineEdit()
        self.custom_os_edit.setPlaceholderText("Enter custom OS type")
        self.custom_os_edit.hide()
        
        # Set current OS or select Other
        current_os = self.properties.get("os", "Unknown")
        index = self.os_combo.findText(current_os)
        if index >= 0:
            self.os_combo.setCurrentIndex(index)
        else:
            # If current OS is not in the list, select "Other" and show custom field
            other_index = self.os_combo.findText("Other")
            self.os_combo.setCurrentIndex(other_index)
            self.custom_os_edit.setText(current_os)
            self.custom_os_edit.show()
            
        # Connect OS dropdown to show/hide custom field
        self.os_combo.currentTextChanged.connect(self.on_os_changed)
        
        layout.addRow("OS Type:", self.os_combo)
        layout.addRow("", self.custom_os_edit)
        
        # SOC Family dropdown with "Other" option
        self.soc_family_combo = QComboBox()
        soc_options = ["Unknown", "TI", "Tricore" ,"NXP", "Intel", "AMD", "Raspberry Pi", "Other"]
        self.soc_family_combo.addItems(soc_options)
        
        # Custom SOC Family input field (initially hidden)
        self.custom_soc_family_edit = QLineEdit()
        self.custom_soc_family_edit.setPlaceholderText("Enter custom SOC family")
        self.custom_soc_family_edit.hide()
        
        # Set current SOC family or select Other
        current_family = self.properties.get("soc_family", "Unknown")
        index = self.soc_family_combo.findText(current_family)
        if index >= 0:
            self.soc_family_combo.setCurrentIndex(index)
        else:
            # If current SOC family is not in the list, select "Other" and show custom field
            other_index = self.soc_family_combo.findText("Other")
            self.soc_family_combo.setCurrentIndex(other_index)
            self.custom_soc_family_edit.setText(current_family)
            self.custom_soc_family_edit.show()
            
        # Connect SOC family dropdown to show/hide custom field
        self.soc_family_combo.currentTextChanged.connect(self.on_soc_family_changed)
        
        layout.addRow("SOC Family:", self.soc_family_combo)
        layout.addRow("", self.custom_soc_family_edit)
        
        # Additional checkboxes
        self.qnx_checkbox = QCheckBox("Is QNX Core")
        self.qnx_checkbox.setChecked(self.properties.get("is_qnx", False))
        layout.addRow("", self.qnx_checkbox)
        
        self.autosar_checkbox = QCheckBox("Is Autosar Compliant")
        self.autosar_checkbox.setChecked(self.properties.get("is_autosar", False))
        layout.addRow("", self.autosar_checkbox)
        
        self.sim_checkbox = QCheckBox("Is Simulation Core")
        self.sim_checkbox.setChecked(self.properties.get("is_sim", False))
        layout.addRow("", self.sim_checkbox)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow("", button_layout)
        
        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def on_os_changed(self, text):
        """Show or hide the custom OS input field based on selection"""
        if text == "Other":
            self.custom_os_edit.show()
        else:
            self.custom_os_edit.hide()
            
    def on_soc_family_changed(self, text):
        """Show or hide the custom SOC family input field based on selection"""
        if text == "Other":
            self.custom_soc_family_edit.show()
        else:
            self.custom_soc_family_edit.hide()
    
    def load_properties(self):
        # Load properties into UI elements
        self.name_edit.setText(self.properties["name"])
        self.description_edit.setText(self.properties["description"])
        self.master_checkbox.setChecked(self.properties["is_master"])
        self.qnx_checkbox.setChecked(self.properties["is_qnx"])
        self.autosar_checkbox.setChecked(self.properties["is_autosar"])
        self.sim_checkbox.setChecked(self.properties["is_sim"])
        
        # Set OS type
        os_type = self.properties["os"]
        index = self.os_combo.findText(os_type)
        if index >= 0:
            self.os_combo.setCurrentIndex(index)
        else:
            self.os_combo.setCurrentText(os_type)
        
        # Set SOC family
        soc_family = self.properties["soc_family"]
        index = self.soc_family_combo.findText(soc_family)
        if index >= 0:
            self.soc_family_combo.setCurrentIndex(index)
        else:
            self.soc_family_combo.setCurrentText(soc_family)
    
    def get_properties(self):
        """Get the configured properties"""
        # Get OS value - use custom field if "Other" is selected
        os_value = self.os_combo.currentText()
        if os_value == "Other":
            os_value = self.custom_os_edit.text()
        
        # Get SOC family value - use custom field if "Other" is selected
        soc_family = self.soc_family_combo.currentText()
        if soc_family == "Other":
            soc_family = self.custom_soc_family_edit.text()
        
        return {
            "name": self.name_edit.text(),
            "description": self.description_edit.text(),
            "is_master": self.master_checkbox.isChecked(),
            "is_qnx": self.qnx_checkbox.isChecked(),
            "is_autosar": self.autosar_checkbox.isChecked(),
            "is_sim": self.sim_checkbox.isChecked(),
            "os": os_value,
            "soc_family": soc_family
        }
