#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QCheckBox, QComboBox, QGroupBox, QMessageBox,
                            QFormLayout)
from PyQt5.QtCore import Qt

class CorePropertiesDialog(QDialog):
    def __init__(self, parent=None, properties=None):
        super(CorePropertiesDialog, self).__init__(parent)
        
        # Default properties if not provided
        self.properties = properties or {
            "name": "",
            "description": "",
            "is_master": False,
            "is_qnx": False,
            "is_autosar": False,
            "is_sim": False,
            "os": "Autosar",
            "soc_family": "TI"
        }
        
        self.setup_ui()
        self.load_properties()
        self.connect_signals()
        
    def setup_ui(self):
        self.setWindowTitle("Core Properties")
        self.resize(400, 450)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Basic info group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        basic_layout.addRow("Core Name:", self.name_edit)
        
        self.description_edit = QLineEdit()
        basic_layout.addRow("Description:", self.description_edit)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Core type group
        type_group = QGroupBox("Core Type")
        type_layout = QFormLayout()
        
        self.master_slave_box = QCheckBox("Master Core")
        type_layout.addRow("Master/Slave:", self.master_slave_box)
        
        # QNX/Autosar/Sim exclusive options
        self.qnx_box = QCheckBox("QNX Core")
        type_layout.addRow("Is QNX Core:", self.qnx_box)
        
        self.autosar_box = QCheckBox("Autosar Core")
        type_layout.addRow("Is Autosar Core:", self.autosar_box)
        
        self.sim_box = QCheckBox("Simulation Core")
        type_layout.addRow("Is Sim Core:", self.sim_box)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # System info group
        system_group = QGroupBox("System Information")
        system_layout = QFormLayout()
        
        self.os_combo = QComboBox()
        self.os_combo.setEditable(True)
        self.os_combo.addItems(["Autosar", "QNX", "FreeRTOS", "SafeRTOS", "TI-RTOS", "Windows"])
        system_layout.addRow("Operating System:", self.os_combo)
        
        self.soc_family_combo = QComboBox()
        self.soc_family_combo.setEditable(True)
        self.soc_family_combo.addItems(["TI", "Infineon", "Qualcomm", "NVIDIA"])
        system_layout.addRow("SOC Family:", self.soc_family_combo)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
    def load_properties(self):
        # Set existing values
        self.name_edit.setText(self.properties["name"])
        self.description_edit.setText(self.properties["description"])
        self.master_slave_box.setChecked(self.properties["is_master"])
        self.qnx_box.setChecked(self.properties["is_qnx"])
        self.autosar_box.setChecked(self.properties["is_autosar"])
        self.sim_box.setChecked(self.properties["is_sim"])
        
        # Set OS
        index = self.os_combo.findText(self.properties["os"])
        if index >= 0:
            self.os_combo.setCurrentIndex(index)
        else:
            self.os_combo.setCurrentText(self.properties["os"])
            
        # Set SOC Family
        index = self.soc_family_combo.findText(self.properties["soc_family"])
        if index >= 0:
            self.soc_family_combo.setCurrentIndex(index)
        else:
            self.soc_family_combo.setCurrentText(self.properties["soc_family"])
            
        # Apply initial state based on selections
        self.update_checkboxes()
        
    def connect_signals(self):
        # Connect the checkboxes to update each other
        self.qnx_box.stateChanged.connect(self.update_checkboxes)
        self.autosar_box.stateChanged.connect(self.update_checkboxes)
        self.sim_box.stateChanged.connect(self.update_checkboxes)
        
        # Update OS combobox when checkbox changes
        self.qnx_box.stateChanged.connect(self.update_os_combo)
        self.autosar_box.stateChanged.connect(self.update_os_combo)
        
    def update_checkboxes(self):
        # Handle dependencies between checkboxes
        if self.sender() == self.qnx_box and self.qnx_box.isChecked():
            self.autosar_box.setChecked(False)
            self.autosar_box.setEnabled(not self.qnx_box.isChecked())
        
        if self.sender() == self.autosar_box and self.autosar_box.isChecked():
            self.qnx_box.setChecked(False)
            self.qnx_box.setEnabled(not self.autosar_box.isChecked())
        
        if self.sender() == self.sim_box and self.sim_box.isChecked():
            self.qnx_box.setChecked(False)
            self.autosar_box.setChecked(False)
            self.qnx_box.setEnabled(not self.sim_box.isChecked())
            self.autosar_box.setEnabled(not self.sim_box.isChecked())
        
        # Re-enable if Sim is unchecked
        if self.sender() == self.sim_box and not self.sim_box.isChecked():
            self.qnx_box.setEnabled(True)
            self.autosar_box.setEnabled(True)
            
    def update_os_combo(self):
        # Update OS combobox selection based on core type
        if self.sender() == self.qnx_box and self.qnx_box.isChecked():
            self.os_combo.setCurrentText("QNX")
        
        if self.sender() == self.autosar_box and self.autosar_box.isChecked():
            self.os_combo.setCurrentText("Autosar")
    
    def get_properties(self):
        # Gather all properties and return as dict
        return {
            "name": self.name_edit.text(),
            "description": self.description_edit.text(),
            "is_master": self.master_slave_box.isChecked(),
            "is_qnx": self.qnx_box.isChecked(),
            "is_autosar": self.autosar_box.isChecked(),
            "is_sim": self.sim_box.isChecked(),
            "os": self.os_combo.currentText(),
            "soc_family": self.soc_family_combo.currentText()
        }
        
    def accept(self):
        # Validate before accepting
        if not self.name_edit.text():
            QMessageBox.warning(self, "Validation Error", "Core name cannot be empty")
            return
        
        super().accept()
