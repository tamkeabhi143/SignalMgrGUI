#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QVBoxLayout

class StructFieldDialog(QDialog):
    """Dialog for adding/editing structure fields"""
    def __init__(self, parent=None, field_name="", field_type="INT32", field_description=""):
        super(StructFieldDialog, self).__init__(parent)
        
        self.field_name = field_name
        self.field_type = field_type
        self.field_description = field_description
        
        self.setup_ui()
        self.load_field_data()
        
    def setup_ui(self):
        self.setWindowTitle("Structure Field")
        self.resize(400, 200)
        
        # Create layout
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Field name
        self.name_edit = QLineEdit()
        form_layout.addRow("Field Name:", self.name_edit)
        
        # Field type
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems([
            "INT8", "UINT8", "INT16", "UINT16", "INT32", "UINT32", 
            "INT64", "UINT64", "FLOAT32", "FLOAT64", "BOOLEAN", "CHAR", 
            "STRING", "ENUM", "ARRAY"
        ])
        form_layout.addRow("Field Type:", self.type_combo)
        
        # Description
        self.description_edit = QLineEdit()
        form_layout.addRow("Description:", self.description_edit)
        
        # Add form layout to main layout
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_field_data(self):
        # Load field data into UI elements
        self.name_edit.setText(self.field_name)
        
        # Set field type
        index = self.type_combo.findText(self.field_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        else:
            self.type_combo.setCurrentText(self.field_type)
        
        self.description_edit.setText(self.field_description)
    
    def get_field_data(self):
        """Return the field data as a tuple (name, type, description)"""
        return (
            self.name_edit.text(),
            self.type_combo.currentText(),
            self.description_edit.text()
        )
