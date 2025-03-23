#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QPushButton, QCheckBox, QComboBox, QSpinBox, QGroupBox,
                            QFormLayout, QTabWidget, QScrollArea)

# Import the struct field dialog
from Modules.UserDataTypeDialog import StructFieldDialog

class CustomValueDialog(QDialog):
    """Dialog for entering custom initialization values"""
    def __init__(self, parent=None, current_value=""):
        super(CustomValueDialog, self).__init__(parent)

        self.setWindowTitle("Enter Custom Initialization Value")
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        # Add instructions
        layout.addWidget(QLabel("Enter a custom initialization value:"))

        # Text input field (multiline)
        self.value_edit = QtWidgets.QTextEdit()
        self.value_edit.setText(current_value)
        layout.addWidget(self.value_edit)

        # Add buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.on_cancel)

    def get_value(self):
        return self.value_edit.toPlainText()

class SignalDetailsDialog(QDialog):
    """Dialog for editing signal details with all configurable options"""
    def __init__(self, parent=None, signal_name="", signal_properties=None, available_cores=None):
        super(SignalDetailsDialog, self).__init__(parent)

        self.signal_name = signal_name
        self.signal_properties = signal_properties or {}
        self.available_cores = available_cores or []
        self.custom_init_value = ""
        self.cancelled = False

        self.setup_ui()
        self.load_signal_properties()

    def setup_ui(self):
        self.setWindowTitle(f"Signal Details - {self.signal_name}")
        self.resize(600, 600)

        main_layout = QVBoxLayout(self)

        # Create a tab widget for better organization
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Basic properties tab
        basic_tab = QtWidgets.QWidget()
        self.setup_basic_tab(basic_tab)
        self.tab_widget.addTab(basic_tab, "Basic Properties")

        # Advanced properties tab
        advanced_tab = QtWidgets.QWidget()
        self.setup_advanced_tab(advanced_tab)
        self.tab_widget.addTab(advanced_tab, "Advanced Properties")

        # Core routing tab
        routing_tab = QtWidgets.QWidget()
        self.setup_routing_tab(routing_tab)
        self.tab_widget.addTab(routing_tab, "Core Routing")

        # Bottom buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def setup_basic_tab(self, tab):
        layout = QFormLayout(tab)

        # Signal Name (display only)
        self.signal_name_label = QLabel(self.signal_name)
        layout.addRow("Signal Name:", self.signal_name_label)

        # Variable Port Name
        self.variable_port_name_edit = QLineEdit()
        layout.addRow("Variable Port Name:", self.variable_port_name_edit)

        # Data Type
        self.data_type_combo = QComboBox()
        self.data_type_combo.setEditable(True)
        self.data_type_combo.addItems([
            "INT8", "UINT8", "INT16", "UINT16", "INT32", "UINT32",
            "INT64", "UINT64", "FLOAT32", "FLOAT64", "BOOLEAN", "CHAR",
            "STRING", "STRUCT", "ARRAY", "ENUM<1Byte>", "ENUM<4Bytes>"
        ])
        # Add configuration storage for array and enum types
        self.array_config = {"base_type": "UINT8", "size": 1}
        self.enum_config = {"name": "", "entries": []}
        # Create array configuration widgets (initially hidden)
        self.array_group = QGroupBox("Array Configuration")
        self.array_group.setVisible(False)
        array_layout = QFormLayout(self.array_group)

        self.array_type_combo = QComboBox()
        self.array_type_combo.addItems([
            "INT8", "UINT8", "INT16", "UINT16", "INT32", "UINT32",
            "INT64", "UINT64", "FLOAT32", "FLOAT64"
        ])
        array_layout.addRow("Element Type:", self.array_type_combo)

        self.array_size_spin = QSpinBox()
        self.array_size_spin.setRange(1, 1000)
        self.array_size_spin.setValue(1)
        array_layout.addRow("Size (elements):", self.array_size_spin)

        # Create enum configuration widgets (initially hidden)
        self.enum_group = QGroupBox("Enum Configuration")
        self.enum_group.setVisible(False)
        enum_layout = QFormLayout(self.enum_group)

        self.enum_name_edit = QLineEdit()
        enum_layout.addRow("Enum Block Name:", self.enum_name_edit)

        # Enum entries list
        enum_layout.addRow("Enum Entries:", QLabel())
        self.enum_entries_list = QtWidgets.QListWidget()
        enum_layout.addRow("", self.enum_entries_list)

        # Buttons for enum entry management
        enum_buttons_layout = QHBoxLayout()
        self.add_enum_button = QPushButton("Add Entry")
        self.edit_enum_button = QPushButton("Edit Entry")
        self.remove_enum_button = QPushButton("Remove Entry")
        enum_buttons_layout.addWidget(self.add_enum_button)
        enum_buttons_layout.addWidget(self.edit_enum_button)
        enum_buttons_layout.addWidget(self.remove_enum_button)
        enum_layout.addRow("", enum_buttons_layout)

        # Preview of the MAX entry (read-only)
        self.enum_max_label = QLabel()
        enum_layout.addRow("MAX Entry:", self.enum_max_label)

        # Connect enum buttons
        self.add_enum_button.clicked.connect(self.add_enum_entry)
        self.edit_enum_button.clicked.connect(self.edit_enum_entry)
        self.remove_enum_button.clicked.connect(self.remove_enum_entry)
        self.enum_name_edit.textChanged.connect(self.update_enum_max_entry)

        # Add the array and enum groups to the layout
        layout.addRow("", self.array_group)
        layout.addRow("", self.enum_group)
        self.data_type_combo.currentTextChanged.connect(self.on_data_type_changed)
        layout.addRow("Data Type:", self.data_type_combo)

        # Structure Details (initially hidden)
        self.struct_group = QGroupBox("Structure Definition")
        self.struct_group.setVisible(False)
        struct_layout = QVBoxLayout(self.struct_group)

        # Structure fields list
        struct_layout.addWidget(QLabel("Structure Fields:"))
        self.struct_fields_tree = QtWidgets.QTreeWidget()
        self.struct_fields_tree.setHeaderLabels(["Field Name", "Data Type", "Description"])
        self.struct_fields_tree.setColumnWidth(0, 150)
        self.struct_fields_tree.setColumnWidth(1, 100)
        struct_layout.addWidget(self.struct_fields_tree)

        # Buttons for field management
        field_buttons_layout = QHBoxLayout()
        self.add_field_button = QPushButton("Add Field")
        self.edit_field_button = QPushButton("Edit Field")
        self.remove_field_button = QPushButton("Remove Field")
        field_buttons_layout.addWidget(self.add_field_button)
        field_buttons_layout.addWidget(self.edit_field_button)
        field_buttons_layout.addWidget(self.remove_field_button)
        struct_layout.addLayout(field_buttons_layout)

        # Connect structure buttons
        self.add_field_button.clicked.connect(self.add_struct_field)
        self.edit_field_button.clicked.connect(self.edit_struct_field)
        self.remove_field_button.clicked.connect(self.remove_struct_field)

        layout.addRow("", self.struct_group)

        # Description
        self.description_edit = QLineEdit()
        layout.addRow("Description:", self.description_edit)

        # Memory Region
        self.memory_region_combo = QComboBox()
        self.memory_region_combo.addItems(["DDR", "Cached", "NonCached"])
        layout.addRow("Memory Region:", self.memory_region_combo)

        # Type (Concurrent/Sequential)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Concurrent", "Sequential"])
        layout.addRow("Type:", self.type_combo)

        # Init Value
        self.init_value_combo = QComboBox()
        self.init_value_combo.addItems(["ZeroMemory", "Custom"])
        self.init_value_combo.currentIndexChanged.connect(self.on_init_value_changed)
        layout.addRow("Init Value:", self.init_value_combo)

        # Custom init value button
        self.custom_value_button = QPushButton("Enter Custom Value...")
        self.custom_value_button.clicked.connect(self.enter_custom_value)
        self.custom_value_button.setVisible(False)  # Hidden by default
        layout.addRow("", self.custom_value_button)

        # ASIL
        self.asil_combo = QComboBox()
        self.asil_combo.addItems(["QM", "A", "B", "C", "D"])
        layout.addRow("ASIL:", self.asil_combo)

    def on_data_type_changed(self, text):
        # Get uppercase text for comparison
        text_upper = text.upper()

        # Determine which configuration to show
        is_struct = (text_upper == "STRUCT")
        is_array = (text_upper == "ARRAY")
        is_enum = text_upper.startswith("ENUM")

        # Show/hide the appropriate configuration sections
        self.struct_group.setVisible(is_struct)
        self.array_group.setVisible(is_array)
        self.enum_group.setVisible(is_enum)

        # Resize the dialog if needed when showing configuration controls
        if is_struct or is_array or is_enum:
            current_size = self.size()
            if current_size.height() < 700:  # Only resize if it's not already large
                self.resize(current_size.width(), 700)

    def add_struct_field(self):
        # Add a new field to the structure definition
        dialog = StructFieldDialog(self)
        if dialog.exec_():
            field_name, field_type, field_desc = dialog.get_field_data()

            # Check for duplicate field names
            for i in range(self.struct_fields_tree.topLevelItemCount()):
                if self.struct_fields_tree.topLevelItem(i).text(0) == field_name:
                    QtWidgets.QMessageBox.warning(self, "Duplicate Field",
                                          f"Field '{field_name}' already exists")
                    return

            # Add the new field
            item = QtWidgets.QTreeWidgetItem([field_name, field_type, field_desc])
            self.struct_fields_tree.addTopLevelItem(item)

    def edit_struct_field(self):
        # Edit the selected structure field
        item = self.struct_fields_tree.currentItem()
        if not item:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a field to edit")
            return

        dialog = StructFieldDialog(self,
                                 item.text(0),  # field name
                                 item.text(1),  # field type
                                 item.text(2))  # field description

        if dialog.exec_():
            field_name, field_type, field_desc = dialog.get_field_data()

            # Check for duplicate field names if name changed
            if field_name != item.text(0):
                for i in range(self.struct_fields_tree.topLevelItemCount()):
                    other_item = self.struct_fields_tree.topLevelItem(i)
                    if other_item != item and other_item.text(0) == field_name:
                        QtWidgets.QMessageBox.warning(self, "Duplicate Field",
                                             f"Field '{field_name}' already exists")
                        return

            # Update the field data
            item.setText(0, field_name)
            item.setText(1, field_type)
            item.setText(2, field_desc)

    def remove_struct_field(self):
        # Remove the selected structure field
        item = self.struct_fields_tree.currentItem()
        if not item:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a field to remove")
            return

        reply = QtWidgets.QMessageBox.question(self, "Confirm Removal",
                               f"Are you sure you want to remove field '{item.text(0)}'?",
                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            index = self.struct_fields_tree.indexOfTopLevelItem(item)
            self.struct_fields_tree.takeTopLevelItem(index)

    def setup_advanced_tab(self, tab):
        layout = QFormLayout(tab)

        # Buffer count IPC
        self.buffer_count_ipc_spin = QSpinBox()
        self.buffer_count_ipc_spin.setRange(1, 8)
        layout.addRow("Buffer Count IPC:", self.buffer_count_ipc_spin)

        # Implementation Approach
        self.impl_approach_combo = QComboBox()
        self.impl_approach_combo.addItems(["SharedMemory", "IPC", "IPCOverEthernet"])
        layout.addRow("Implementation Approach:", self.impl_approach_combo)

        # Get Object Reference
        self.get_obj_ref_combo = QComboBox()
        self.get_obj_ref_combo.addItems(["False", "True"])
        layout.addRow("Get Object Reference:", self.get_obj_ref_combo)

        # Notifiers
        self.notifiers_combo = QComboBox()
        self.notifiers_combo.addItems(["False", "True"])
        layout.addRow("Notifiers:", self.notifiers_combo)

        # SM Buffer Count
        self.sm_buff_count_spin = QSpinBox()
        self.sm_buff_count_spin.setRange(1, 8)
        layout.addRow("SM Buffer Count:", self.sm_buff_count_spin)

        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 1000)
        self.timeout_spin.setSingleStep(10)
        self.timeout_spin.setSuffix(" ms")
        layout.addRow("Timeout:", self.timeout_spin)

        # Periodicity
        self.periodicity_spin = QSpinBox()
        self.periodicity_spin.setRange(10, 1000)
        self.periodicity_spin.setSingleStep(10)
        self.periodicity_spin.setSuffix(" ms")
        layout.addRow("Periodicity:", self.periodicity_spin)

        # Checksum
        self.checksum_combo = QComboBox()
        self.checksum_combo.addItems(["None", "Additive", "CustomChecksum"])
        layout.addRow("Checksum:", self.checksum_combo)

    def setup_routing_tab(self, tab):
        layout = QVBoxLayout(tab)

        # Create scroll area for many cores
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Source Core selection
        source_group = QGroupBox("Source Core")
        source_layout = QVBoxLayout(source_group)
        self.source_combo = QComboBox()
        self.source_combo.addItem("<None>")
        self.source_combo.addItems(self.available_cores)
        self.source_combo.currentIndexChanged.connect(self.update_destination_checkboxes)
        source_layout.addWidget(self.source_combo)
        scroll_layout.addWidget(source_group)

        # Destination Cores selection
        dest_group = QGroupBox("Destination Cores")
        dest_layout = QVBoxLayout(dest_group)

        self.core_checkboxes = {}
        for core in self.available_cores:
            checkbox = QCheckBox(core)
            self.core_checkboxes[core] = checkbox
            dest_layout.addWidget(checkbox)

        scroll_layout.addWidget(dest_group)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def load_signal_properties(self):
        # Basic tab
        self.variable_port_name_edit.setText(self.signal_properties.get("Variable_Port_Name", ""))

        # Set Data Type
        data_type = self.signal_properties.get("DataType", "INT32")
        index = self.data_type_combo.findText(data_type)
        if index >= 0:
            self.data_type_combo.setCurrentIndex(index)
        else:
            self.data_type_combo.setCurrentText(data_type)

        self.description_edit.setText(self.signal_properties.get("description", ""))

        # Set Memory Region
        memory_region = self.signal_properties.get("Memory Region", "DDR")
        index = self.memory_region_combo.findText(memory_region)
        if index >= 0:
            self.memory_region_combo.setCurrentIndex(index)

        # Set Type
        type_value = self.signal_properties.get("Type", "Concurrent")
        index = self.type_combo.findText(type_value)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)

        # Set Init Value
        init_value = self.signal_properties.get("InitValue", "ZeroMemory")
        if init_value == "Custom":
            self.custom_init_value = self.signal_properties.get("CustomInitValue", "")
            index = self.init_value_combo.findText("Custom")
            if index >= 0:
                self.init_value_combo.setCurrentIndex(index)
        else:
            index = self.init_value_combo.findText(init_value)
            if index >= 0:
                self.init_value_combo.setCurrentIndex(index)

        # Set ASIL
        asil = self.signal_properties.get("ASIL", "QM")
        index = self.asil_combo.findText(asil)
        if index >= 0:
            self.asil_combo.setCurrentIndex(index)

        # Show structure fields if this is a structure type
        if self.signal_properties.get("is_struct", False) or self.signal_properties.get("DataType", "").upper() == "STRUCT":
            # Make sure STRUCT is selected in the combobox
            self.data_type_combo.setCurrentText("STRUCT")

            # Load structure fields
            struct_fields = self.signal_properties.get("struct_fields", {})
            for field_name, field_info in struct_fields.items():
                item = QtWidgets.QTreeWidgetItem([
                    field_name,
                    field_info.get("type", ""),
                    field_info.get("description", "")
                ])
                self.struct_fields_tree.addTopLevelItem(item)

        # Advanced tab
        self.buffer_count_ipc_spin.setValue(self.signal_properties.get("Buffer count_IPC", 1))

        # Set Implementation Approach
        impl_approach = self.signal_properties.get("Impl_Approach", "SharedMemory")
        index = self.impl_approach_combo.findText(impl_approach)
        if index >= 0:
            self.impl_approach_combo.setCurrentIndex(index)

        # Set Get Object Reference
        get_obj_ref = str(self.signal_properties.get("GetObjRef", False))
        index = self.get_obj_ref_combo.findText(get_obj_ref)
        if index >= 0:
            self.get_obj_ref_combo.setCurrentIndex(index)

        # Set Notifiers
        notifiers = str(self.signal_properties.get("Notifiers", False))
        index = self.notifiers_combo.findText(notifiers)
        if index >= 0:
            self.notifiers_combo.setCurrentIndex(index)

        self.sm_buff_count_spin.setValue(self.signal_properties.get("SM_Buff_Count", 1))
        self.timeout_spin.setValue(self.signal_properties.get("Timeout", 10))
        self.periodicity_spin.setValue(self.signal_properties.get("Periodicity", 10))

        # Set Checksum
        checksum = self.signal_properties.get("Checksum", "Additive")
        index = self.checksum_combo.findText(checksum)
        if index >= 0:
            self.checksum_combo.setCurrentIndex(index)

        # Routing tab
        source = self.signal_properties.get("Source", "")
        if source:
            index = self.source_combo.findText(source)
            if index >= 0:
                self.source_combo.setCurrentIndex(index)

        # Set destination cores
        for core, checkbox in self.core_checkboxes.items():
            core_key = f"core_{core.replace('.', '_')}"
            checkbox.setChecked(self.signal_properties.get(core_key, False))

        # Update destination checkboxes based on source
        self.update_destination_checkboxes()

    def on_init_value_changed(self, _):
        # Show or hide the custom value button based on selection
        self.custom_value_button.setVisible(self.init_value_combo.currentText() == "Custom")

    def enter_custom_value(self):
        dialog = CustomValueDialog(self, self.custom_init_value)
        if dialog.exec_():
            self.custom_init_value = dialog.get_value()

    def update_destination_checkboxes(self):
        # Disable the source core in destinations
        source = self.source_combo.currentText()
        for core, checkbox in self.core_checkboxes.items():
            if core == source or source == "<None>":
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
            else:
                checkbox.setEnabled(True)

    def add_enum_entry(self):
        # Add a new enum entry
        name, ok = QtWidgets.QInputDialog.getText(self, "Add Enum Entry", "Enter enum entry name:")
        if ok and name:
            # Check for duplicate entry names
            for i in range(self.enum_entries_list.count()):
                if self.enum_entries_list.item(i).text() == name:
                    QtWidgets.QMessageBox.warning(self, "Duplicate Entry",
                                                 f"Entry '{name}' already exists")
                    return

            # Add the new entry
            self.enum_entries_list.addItem(name)
            self.update_enum_max_entry()

    def edit_enum_entry(self):
        # Edit the selected enum entry
        current_item = self.enum_entries_list.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select an entry to edit")
            return

        old_name = current_item.text()
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Edit Enum Entry",
                                                    "Enter new name:", text=old_name)

        if ok and new_name:
            # Check for duplicate entry names if name changed
            if new_name != old_name:
                for i in range(self.enum_entries_list.count()):
                    item = self.enum_entries_list.item(i)
                    if item != current_item and item.text() == new_name:
                        QtWidgets.QMessageBox.warning(self, "Duplicate Entry",
                                                    f"Entry '{new_name}' already exists")
                        return

            # Update the entry name
            current_item.setText(new_name)
            self.update_enum_max_entry()

    def remove_enum_entry(self):
        # Remove the selected enum entry
        current_item = self.enum_entries_list.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select an entry to remove")
            return

        reply = QtWidgets.QMessageBox.question(self, "Confirm Removal",
                                             f"Are you sure you want to remove entry '{current_item.text()}'?",
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            row = self.enum_entries_list.row(current_item)
            self.enum_entries_list.takeItem(row)
            self.update_enum_max_entry()

    def update_enum_max_entry(self):
        # Update the MAX entry label based on enum name
        enum_name = self.enum_name_edit.text().strip()
        if enum_name:
            max_name = f"{enum_name}_MAX"
            self.enum_max_label.setText(max_name)
        else:
            self.enum_max_label.setText("<Enum Name>_MAX")

    def on_cancel(self):
        self.cancelled = True
        self.reject()

    def reject(self):
        # Handle cancel button
        self.cancelled = True
        return super().reject()

    def get_signal_properties(self):
        # Return None if the dialog was cancelled
        if self.cancelled:
            return None

        # Collect all properties from UI
        properties = self.signal_properties.copy()
        # Basic properties
        properties["Variable_Port_Name"] = self.variable_port_name_edit.text()
        properties["DataType"] = self.data_type_combo.currentText()
        properties["description"] = self.description_edit.text()
        properties["Memory Region"] = self.memory_region_combo.currentText()
        properties["Type"] = self.type_combo.currentText()
        properties["InitValue"] = self.init_value_combo.currentText()

        # Store custom init value if selected
        if properties["InitValue"] == "Custom":
            properties["CustomInitValue"] = self.custom_init_value

        properties["ASIL"] = self.asil_combo.currentText()

        # Handle structure type properties
        properties["is_struct"] = (self.data_type_combo.currentText().upper() == "STRUCT")
        if properties["is_struct"]:
            struct_fields = {}
            for i in range(self.struct_fields_tree.topLevelItemCount()):
                item = self.struct_fields_tree.topLevelItem(i)
                field_name = item.text(0)
                struct_fields[field_name] = {
                    "type": item.text(1),
                    "description": item.text(2)
                }
            properties["struct_fields"] = struct_fields

        # Advanced properties
        properties["Buffer count_IPC"] = self.buffer_count_ipc_spin.value()
        properties["Impl_Approach"] = self.impl_approach_combo.currentText()
        properties["GetObjRef"] = self.get_obj_ref_combo.currentText() == "True"
        properties["Notifiers"] = self.notifiers_combo.currentText() == "True"
        properties["SM_Buff_Count"] = self.sm_buff_count_spin.value()
        properties["Timeout"] = self.timeout_spin.value()
        properties["Periodicity"] = self.periodicity_spin.value()
        properties["Checksum"] = self.checksum_combo.currentText()

        # Routing properties
        source = self.source_combo.currentText()
        if source != "<None>":
            properties["Source"] = source
        else:
            properties["Source"] = ""

        # Store destination cores
        for core, checkbox in self.core_checkboxes.items():
            core_key = f"core_{core.replace('.', '_')}"
            properties[core_key] = checkbox.isChecked()

        return properties
