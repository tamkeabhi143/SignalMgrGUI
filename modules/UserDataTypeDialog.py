#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QVBoxLayout, QLabel, QMessageBox, QSpinBox

class StructFieldDialog(QDialog):
    """Dialog for adding/editing structure fields"""
    def __init__(self, parent=None, field_name="", field_type="INT32", field_description="", nesting_level=0):
        super(StructFieldDialog, self).__init__(parent)

        self.field_name = field_name
        self.field_type = field_type
        self.field_description = field_description
        self.nesting_level = nesting_level
        self.struct_fields = []
        self.array_type = "UINT8"
        self.array_size = 1
        self.enum_name = ""

        self.setup_ui()
        self.load_field_data()

        # Connect type combo change handler
        self.type_combo.currentTextChanged.connect(self.on_type_changed)

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
            "STRING", "ENUM<1Byte>", "ENUM<4Byte>", "ARRAY", "STRUCT"
        ])
        form_layout.addRow("Field Type:", self.type_combo)

        # Description
        self.description_edit = QLineEdit()
        form_layout.addRow("Description:", self.description_edit)

        # Add array configuration widget
        self.array_widget = QtWidgets.QWidget()
        array_layout = QFormLayout(self.array_widget)

        self.array_type_combo = QComboBox()
        self.array_type_combo.addItems([
            "INT8", "UINT8", "INT16", "UINT16", "INT32", "UINT32",
            "INT64", "UINT64", "FLOAT32", "FLOAT64", "BOOLEAN", "CHAR"
        ])
        array_layout.addRow("Element Type:", self.array_type_combo)

        self.array_size_spin = QSpinBox()
        self.array_size_spin.setMinimum(1)
        self.array_size_spin.setMaximum(65535)
        array_layout.addRow("Size:", self.array_size_spin)

        # Add enum configuration widget
        self.enum_widget = QtWidgets.QWidget()
        enum_layout = QFormLayout(self.enum_widget)

        self.enum_name_edit = QLineEdit()
        enum_layout.addRow("Enum Name:", self.enum_name_edit)
        enum_note = QLabel("Note: <EnumName>_MAX will be added automatically")
        enum_layout.addRow("", enum_note)

        # Hide config widgets initially
        self.array_widget.setVisible(False)
        self.enum_widget.setVisible(False)

        # Add widgets to main layout
        layout.addLayout(form_layout)
        layout.addWidget(self.array_widget)
        layout.addWidget(self.enum_widget)

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

    def on_type_changed(self, type_text):
        """Handle changes to the type selection"""
        # Hide all config widgets first
        self.array_widget.setVisible(False)
        self.enum_widget.setVisible(False)

        if type_text == "STRUCT":
            if self.nesting_level < 3:
                self.handle_struct_type()
            else:
                QMessageBox.warning(self, "Nesting Limit",
                    "Maximum nesting level (3) for structs reached.")
                self.type_combo.setCurrentText("INT32")

        elif type_text == "ARRAY":
            self.array_widget.setVisible(True)

        elif type_text in ["ENUM<1Byte>", "ENUM<4Byte>"]:
            self.enum_widget.setVisible(True)

        elif type_text == "BOOLEAN":
            # Auto-convert to AUTOSAR type
            self.type_combo.setCurrentText("bool_t")

    def handle_struct_type(self):
        """Handle nested struct configuration"""
        # Create nested struct dialog
        struct_dialog = StructFieldDialog(
            parent=self,
            nesting_level=self.nesting_level + 1
        )

        if struct_dialog.exec_() == QDialog.Accepted:
            field_data = struct_dialog.get_field_data()
            # Store the nested struct info
            self.struct_fields.append({
                'name': field_data[0],
                'type': field_data[1],
                'description': field_data[2]
            })

            # Ask if user wants to add more fields
            reply = QMessageBox.question(self, "Add Field",
                "Do you want to add another field to this struct?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.handle_struct_type()

    def accept(self):
        """Validate inputs before accepting"""
        field_type = self.type_combo.currentText()

        if field_type == "ARRAY" and self.array_widget.isVisible():
            # Array validation already handled by QSpinBox
            pass

        elif (field_type in ["ENUM<1Byte>", "ENUM<4Byte>"] and
              self.enum_widget.isVisible() and
              not self.enum_name_edit.text()):
            QMessageBox.warning(self, "Missing Data",
                "Please provide an Enum name.")
            return

        super().accept()

    def get_field_data(self):
        """Return the field data as a tuple (name, type, description)"""
        field_type = self.type_combo.currentText()

        if field_type == "ARRAY" and self.array_widget.isVisible():
            array_type = self.array_type_combo.currentText()
            array_size = self.array_size_spin.value()
            formatted_type = f"ARRAY[{array_size}] OF {array_type}"

        elif field_type == "ENUM<4Byte>" and self.enum_widget.isVisible():
            enum_name = self.enum_name_edit.text()
            formatted_type = f"ENUM<4Byte>({enum_name})"
            # Note: _MAX entry handling would be done by the caller

        else:
            formatted_type = field_type

        return (
            self.name_edit.text(),
            formatted_type,
            self.description_edit.text()
        )
