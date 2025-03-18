# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UserDataTypeDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DataTypeSelectionDialog(object):
    def setupUi(self, DataTypeSelectionDialog):
        DataTypeSelectionDialog.setObjectName("DataTypeSelectionDialog")
        DataTypeSelectionDialog.resize(600, 500)
        self.main_layout = QtWidgets.QVBoxLayout(DataTypeSelectionDialog)
        self.main_layout.setObjectName("main_layout")
        self.type_group = QtWidgets.QGroupBox(DataTypeSelectionDialog)
        self.type_group.setObjectName("type_group")
        self.type_layout = QtWidgets.QVBoxLayout(self.type_group)
        self.type_layout.setObjectName("type_layout")
        self.radio_layout = QtWidgets.QHBoxLayout()
        self.radio_layout.setObjectName("radio_layout")
        self.primitive_radio = QtWidgets.QRadioButton(self.type_group)
        self.primitive_radio.setChecked(True)
        self.primitive_radio.setObjectName("primitive_radio")
        self.radio_layout.addWidget(self.primitive_radio)
        self.struct_radio = QtWidgets.QRadioButton(self.type_group)
        self.struct_radio.setObjectName("struct_radio")
        self.radio_layout.addWidget(self.struct_radio)
        self.array_radio = QtWidgets.QRadioButton(self.type_group)
        self.array_radio.setObjectName("array_radio")
        self.radio_layout.addWidget(self.array_radio)
        self.type_layout.addLayout(self.radio_layout)
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setObjectName("form_layout")
        self.type_label = QtWidgets.QLabel(self.type_group)
        self.type_label.setObjectName("type_label")
        self.form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.type_label)
        self.type_combo = QtWidgets.QComboBox(self.type_group)
        self.type_combo.setObjectName("type_combo")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.type_combo)
        self.type_layout.addLayout(self.form_layout)
        self.array_layout = QtWidgets.QHBoxLayout()
        self.array_layout.setObjectName("array_layout")
        self.array_type_label = QtWidgets.QLabel(self.type_group)
        self.array_type_label.setVisible(False)
        self.array_type_label.setObjectName("array_type_label")
        self.array_layout.addWidget(self.array_type_label)
        self.array_display = QtWidgets.QLineEdit(self.type_group)
        self.array_display.setReadOnly(True)
        self.array_display.setVisible(False)
        self.array_display.setObjectName("array_display")
        self.array_layout.addWidget(self.array_display)
        self.configure_array_button = QtWidgets.QPushButton(self.type_group)
        self.configure_array_button.setVisible(False)
        self.configure_array_button.setObjectName("configure_array_button")
        self.array_layout.addWidget(self.configure_array_button)
        self.type_layout.addLayout(self.array_layout)
        self.main_layout.addWidget(self.type_group)
        self.struct_group = QtWidgets.QGroupBox(DataTypeSelectionDialog)
        self.struct_group.setVisible(False)
        self.struct_group.setObjectName("struct_group")
        self.struct_layout = QtWidgets.QVBoxLayout(self.struct_group)
        self.struct_layout.setObjectName("struct_layout")
        self.struct_fields_label = QtWidgets.QLabel(self.struct_group)
        self.struct_fields_label.setObjectName("struct_fields_label")
        self.struct_layout.addWidget(self.struct_fields_label)
        self.struct_fields_tree = QtWidgets.QTreeWidget(self.struct_group)
        self.struct_fields_tree.setColumnCount(3)
        self.struct_fields_tree.setObjectName("struct_fields_tree")
        self.struct_layout.addWidget(self.struct_fields_tree)
        self.field_buttons_layout = QtWidgets.QHBoxLayout()
        self.field_buttons_layout.setObjectName("field_buttons_layout")
        self.add_field_button = QtWidgets.QPushButton(self.struct_group)
        self.add_field_button.setObjectName("add_field_button")
        self.field_buttons_layout.addWidget(self.add_field_button)
        self.edit_field_button = QtWidgets.QPushButton(self.struct_group)
        self.edit_field_button.setObjectName("edit_field_button")
        self.field_buttons_layout.addWidget(self.edit_field_button)
        self.remove_field_button = QtWidgets.QPushButton(self.struct_group)
        self.remove_field_button.setObjectName("remove_field_button")
        self.field_buttons_layout.addWidget(self.remove_field_button)
        self.struct_layout.addLayout(self.field_buttons_layout)
        self.main_layout.addWidget(self.struct_group)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.button_layout.addItem(spacerItem)
        self.ok_button = QtWidgets.QPushButton(DataTypeSelectionDialog)
        self.ok_button.setObjectName("ok_button")
        self.button_layout.addWidget(self.ok_button)
        self.cancel_button = QtWidgets.QPushButton(DataTypeSelectionDialog)
        self.cancel_button.setObjectName("cancel_button")
        self.button_layout.addWidget(self.cancel_button)
        self.main_layout.addLayout(self.button_layout)

        self.retranslateUi(DataTypeSelectionDialog)
        self.cancel_button.clicked.connect(DataTypeSelectionDialog.reject) # type: ignore
        self.ok_button.clicked.connect(DataTypeSelectionDialog.accept) # type: ignore
        self.struct_radio.toggled['bool'].connect(self.struct_group.setVisible) # type: ignore
        self.struct_radio.toggled['bool'].connect(self.type_combo.setHidden) # type: ignore
        self.array_radio.toggled['bool'].connect(self.array_type_label.setVisible) # type: ignore
        self.array_radio.toggled['bool'].connect(self.array_display.setVisible) # type: ignore
        self.array_radio.toggled['bool'].connect(self.configure_array_button.setVisible) # type: ignore
        self.array_radio.toggled['bool'].connect(self.type_combo.setHidden) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(DataTypeSelectionDialog)

    def retranslateUi(self, DataTypeSelectionDialog):
        _translate = QtCore.QCoreApplication.translate
        DataTypeSelectionDialog.setWindowTitle(_translate("DataTypeSelectionDialog", "Select Data Type"))
        self.type_group.setTitle(_translate("DataTypeSelectionDialog", "Data Type"))
        self.primitive_radio.setText(_translate("DataTypeSelectionDialog", "Primitive Type"))
        self.struct_radio.setText(_translate("DataTypeSelectionDialog", "Structure Type"))
        self.array_radio.setText(_translate("DataTypeSelectionDialog", "Array Type"))
        self.type_label.setText(_translate("DataTypeSelectionDialog", "Data Type:"))
        self.type_combo.setItemText(0, _translate("DataTypeSelectionDialog", "bool_t"))
        self.type_combo.setItemText(1, _translate("DataTypeSelectionDialog", "uint8"))
        self.type_combo.setItemText(2, _translate("DataTypeSelectionDialog", "uint16"))
        self.type_combo.setItemText(3, _translate("DataTypeSelectionDialog", "uint32"))
        self.type_combo.setItemText(4, _translate("DataTypeSelectionDialog", "uint64"))
        self.type_combo.setItemText(5, _translate("DataTypeSelectionDialog", "sint8"))
        self.type_combo.setItemText(6, _translate("DataTypeSelectionDialog", "sint16"))
        self.type_combo.setItemText(7, _translate("DataTypeSelectionDialog", "sint32"))
        self.type_combo.setItemText(8, _translate("DataTypeSelectionDialog", "sint64"))
        self.type_combo.setItemText(9, _translate("DataTypeSelectionDialog", "char_t"))
        self.type_combo.setItemText(10, _translate("DataTypeSelectionDialog", "float32"))
        self.type_combo.setItemText(11, _translate("DataTypeSelectionDialog", "float64"))
        self.array_type_label.setText(_translate("DataTypeSelectionDialog", "Array of:"))
        self.configure_array_button.setText(_translate("DataTypeSelectionDialog", "Configure..."))
        self.struct_group.setTitle(_translate("DataTypeSelectionDialog", "Structure Definition"))
        self.struct_fields_label.setText(_translate("DataTypeSelectionDialog", "Structure Fields:"))
        self.struct_fields_tree.headerItem().setText(0, _translate("DataTypeSelectionDialog", "Field Name"))
        self.struct_fields_tree.headerItem().setText(1, _translate("DataTypeSelectionDialog", "Data Type"))
        self.struct_fields_tree.headerItem().setText(2, _translate("DataTypeSelectionDialog", "Description"))
        self.add_field_button.setText(_translate("DataTypeSelectionDialog", "Add Field"))
        self.edit_field_button.setText(_translate("DataTypeSelectionDialog", "Edit Field"))
        self.remove_field_button.setText(_translate("DataTypeSelectionDialog", "Remove Field"))
        self.ok_button.setText(_translate("DataTypeSelectionDialog", "OK"))
        self.cancel_button.setText(_translate("DataTypeSelectionDialog", "Cancel"))
