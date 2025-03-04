#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFormLayout

class StructFieldDialog(QDialog):
    """Dialog for adding or editing a structure field"""
    def __init__(self, parent=None, field_name="", field_type="INT32", field_description=""):
        super(StructFieldDialog, self).__init__(parent)
        
        self.setWindowTitle("Structure Field")
        self.resize(400, 200)
        
        self.field_name = field_name
        self.field_type = field_type
        self.field_description = field_description
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Field name
        self.name_edit = QLineEdit()
        layout.addRow("Field Name:", self.name_edit)
        
        # Field type
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems([
            "INT8", "UINT8", "INT16", "UINT16", "INT32", "UINT32", 
            "INT64", "UINT64", "FLOAT32", "FLOAT64", "BOOLEAN", "CHAR", 
            "STRING", "STRUCT"  # Support for nested structures
        ])
        layout.addRow("Data Type:", self.type_combo)
        
        # Field description
        self.description_edit = QLineEdit()
        layout.addRow("Description:", self.description_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow("", button_layout)
        
        # Connect buttons
        self.ok_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)
        
    def load_data(self):
        # Fill the form with existing data if editing
        self.name_edit.setText(self.field_name)
        
        # Set field type
        index = self.type_combo.findText(self.field_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        else:
            self.type_combo.setCurrentText(self.field_type)
            
        self.description_edit.setText(self.field_description)
    
    def validate_and_accept(self):
        # Validate form data
        if not self.name_edit.text():
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Field name cannot be empty")
            return
            
        self.accept()
    
    def get_field_data(self):
        # Return the field data as a tuple
        return (
            self.name_edit.text(),
            self.type_combo.currentText(),
            self.description_edit.text()
        )
