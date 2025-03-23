# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SignalDetailsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SignalDetailsDialog(object):
    def setupUi(self, SignalDetailsDialog):
        SignalDetailsDialog.setObjectName("SignalDetailsDialog")
        SignalDetailsDialog.resize(600, 600)
        self.main_layout = QtWidgets.QVBoxLayout(SignalDetailsDialog)
        self.main_layout.setObjectName("main_layout")
        self.tab_widget = QtWidgets.QTabWidget(SignalDetailsDialog)
        self.tab_widget.setObjectName("tab_widget")
        self.basic_tab = QtWidgets.QWidget()
        self.basic_tab.setObjectName("basic_tab")
        self.signal_name_label_text = QtWidgets.QLabel(self.basic_tab)
        self.signal_name_label_text.setGeometry(QtCore.QRect(9, 9, 70, 16))
        self.signal_name_label_text.setObjectName("signal_name_label_text")
        self.signal_name_label = QtWidgets.QLabel(self.basic_tab)
        self.signal_name_label.setGeometry(QtCore.QRect(119, 9, 66, 16))
        font = QtGui.QFont()
        font.setBold(True)
        self.signal_name_label.setFont(font)
        self.signal_name_label.setObjectName("signal_name_label")
        self.var_port_name_label = QtWidgets.QLabel(self.basic_tab)
        self.var_port_name_label.setGeometry(QtCore.QRect(10, 40, 104, 16))
        self.var_port_name_label.setObjectName("var_port_name_label")
        self.variable_port_name_edit = QtWidgets.QLineEdit(self.basic_tab)
        self.variable_port_name_edit.setGeometry(QtCore.QRect(120, 40, 116, 22))
        self.variable_port_name_edit.setObjectName("variable_port_name_edit")
        self.data_type_label = QtWidgets.QLabel(self.basic_tab)
        self.data_type_label.setGeometry(QtCore.QRect(10, 68, 55, 16))
        self.data_type_label.setObjectName("data_type_label")
        self.data_type_combo = QtWidgets.QComboBox(self.basic_tab)
        self.data_type_combo.setGeometry(QtCore.QRect(120, 68, 79, 22))
        self.data_type_combo.setEditable(True)
        self.data_type_combo.setObjectName("data_type_combo")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.data_type_combo.addItem("")
        self.struct_group = QtWidgets.QGroupBox(self.basic_tab)
        self.struct_group.setGeometry(QtCore.QRect(0, 0, 100, 30))
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
        self.description_label = QtWidgets.QLabel(self.basic_tab)
        self.description_label.setGeometry(QtCore.QRect(10, 96, 63, 16))
        self.description_label.setObjectName("description_label")
        self.description_edit = QtWidgets.QLineEdit(self.basic_tab)
        self.description_edit.setGeometry(QtCore.QRect(120, 96, 116, 22))
        self.description_edit.setObjectName("description_edit")
        self.memory_region_label = QtWidgets.QLabel(self.basic_tab)
        self.memory_region_label.setGeometry(QtCore.QRect(10, 124, 88, 16))
        self.memory_region_label.setObjectName("memory_region_label")
        self.memory_region_combo = QtWidgets.QComboBox(self.basic_tab)
        self.memory_region_combo.setGeometry(QtCore.QRect(120, 124, 88, 22))
        self.memory_region_combo.setObjectName("memory_region_combo")
        self.memory_region_combo.addItem("")
        self.memory_region_combo.addItem("")
        self.memory_region_combo.addItem("")
        self.type_label = QtWidgets.QLabel(self.basic_tab)
        self.type_label.setGeometry(QtCore.QRect(10, 152, 28, 16))
        self.type_label.setObjectName("type_label")
        self.type_combo = QtWidgets.QComboBox(self.basic_tab)
        self.type_combo.setGeometry(QtCore.QRect(120, 152, 86, 22))
        self.type_combo.setObjectName("type_combo")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.init_value_label = QtWidgets.QLabel(self.basic_tab)
        self.init_value_label.setGeometry(QtCore.QRect(10, 180, 51, 16))
        self.init_value_label.setObjectName("init_value_label")
        self.init_value_combo = QtWidgets.QComboBox(self.basic_tab)
        self.init_value_combo.setGeometry(QtCore.QRect(120, 180, 96, 22))
        self.init_value_combo.setObjectName("init_value_combo")
        self.init_value_combo.addItem("")
        self.init_value_combo.addItem("")
        self.custom_value_button = QtWidgets.QPushButton(self.basic_tab)
        self.custom_value_button.setGeometry(QtCore.QRect(0, 0, 100, 30))
        self.custom_value_button.setVisible(False)
        self.custom_value_button.setObjectName("custom_value_button")
        self.asil_label = QtWidgets.QLabel(self.basic_tab)
        self.asil_label.setGeometry(QtCore.QRect(10, 214, 26, 16))
        self.asil_label.setObjectName("asil_label")
        self.asil_combo = QtWidgets.QComboBox(self.basic_tab)
        self.asil_combo.setGeometry(QtCore.QRect(120, 214, 45, 22))
        self.asil_combo.setObjectName("asil_combo")
        self.asil_combo.addItem("")
        self.asil_combo.addItem("")
        self.asil_combo.addItem("")
        self.asil_combo.addItem("")
        self.asil_combo.addItem("")
        self.tab_widget.addTab(self.basic_tab, "")
        self.advanced_tab = QtWidgets.QWidget()
        self.advanced_tab.setObjectName("advanced_tab")
        self.advanced_form_layout = QtWidgets.QFormLayout(self.advanced_tab)
        self.advanced_form_layout.setObjectName("advanced_form_layout")
        self.buffer_count_ipc_label = QtWidgets.QLabel(self.advanced_tab)
        self.buffer_count_ipc_label.setObjectName("buffer_count_ipc_label")
        self.advanced_form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.buffer_count_ipc_label)
        self.buffer_count_ipc_spin = QtWidgets.QSpinBox(self.advanced_tab)
        self.buffer_count_ipc_spin.setMinimum(1)
        self.buffer_count_ipc_spin.setMaximum(10)
        self.buffer_count_ipc_spin.setObjectName("buffer_count_ipc_spin")
        self.advanced_form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.buffer_count_ipc_spin)
        self.impl_approach_label = QtWidgets.QLabel(self.advanced_tab)
        self.impl_approach_label.setObjectName("impl_approach_label")
        self.advanced_form_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.impl_approach_label)
        self.impl_approach_combo = QtWidgets.QComboBox(self.advanced_tab)
        self.impl_approach_combo.setObjectName("impl_approach_combo")
        self.impl_approach_combo.addItem("")
        self.impl_approach_combo.addItem("")
        self.impl_approach_combo.addItem("")
        self.advanced_form_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.impl_approach_combo)
        self.get_obj_ref_label = QtWidgets.QLabel(self.advanced_tab)
        self.get_obj_ref_label.setObjectName("get_obj_ref_label")
        self.advanced_form_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.get_obj_ref_label)
        self.get_obj_ref_combo = QtWidgets.QComboBox(self.advanced_tab)
        self.get_obj_ref_combo.setObjectName("get_obj_ref_combo")
        self.get_obj_ref_combo.addItem("")
        self.get_obj_ref_combo.addItem("")
        self.advanced_form_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.get_obj_ref_combo)
        self.notifiers_label = QtWidgets.QLabel(self.advanced_tab)
        self.notifiers_label.setObjectName("notifiers_label")
        self.advanced_form_layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.notifiers_label)
        self.notifiers_combo = QtWidgets.QComboBox(self.advanced_tab)
        self.notifiers_combo.setObjectName("notifiers_combo")
        self.notifiers_combo.addItem("")
        self.notifiers_combo.addItem("")
        self.advanced_form_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.notifiers_combo)
        self.sm_buff_count_label = QtWidgets.QLabel(self.advanced_tab)
        self.sm_buff_count_label.setObjectName("sm_buff_count_label")
        self.advanced_form_layout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.sm_buff_count_label)
        self.sm_buff_count_spin = QtWidgets.QSpinBox(self.advanced_tab)
        self.sm_buff_count_spin.setMinimum(1)
        self.sm_buff_count_spin.setMaximum(10)
        self.sm_buff_count_spin.setObjectName("sm_buff_count_spin")
        self.advanced_form_layout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.sm_buff_count_spin)
        self.timeout_label = QtWidgets.QLabel(self.advanced_tab)
        self.timeout_label.setObjectName("timeout_label")
        self.advanced_form_layout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.timeout_label)
        self.timeout_spin = QtWidgets.QSpinBox(self.advanced_tab)
        self.timeout_spin.setMinimum(10)
        self.timeout_spin.setMaximum(200)
        self.timeout_spin.setSingleStep(10)
        self.timeout_spin.setObjectName("timeout_spin")
        self.advanced_form_layout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.timeout_spin)
        self.periodicity_label = QtWidgets.QLabel(self.advanced_tab)
        self.periodicity_label.setObjectName("periodicity_label")
        self.advanced_form_layout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.periodicity_label)
        self.periodicity_spin = QtWidgets.QSpinBox(self.advanced_tab)
        self.periodicity_spin.setMinimum(10)
        self.periodicity_spin.setMaximum(200)
        self.periodicity_spin.setSingleStep(10)
        self.periodicity_spin.setObjectName("periodicity_spin")
        self.advanced_form_layout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.periodicity_spin)
        self.checksum_label = QtWidgets.QLabel(self.advanced_tab)
        self.checksum_label.setObjectName("checksum_label")
        self.advanced_form_layout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.checksum_label)
        self.checksum_combo = QtWidgets.QComboBox(self.advanced_tab)
        self.checksum_combo.setObjectName("checksum_combo")
        self.checksum_combo.addItem("")
        self.checksum_combo.addItem("")
        self.checksum_combo.addItem("")
        self.advanced_form_layout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.checksum_combo)
        self.tab_widget.addTab(self.advanced_tab, "")
        self.routing_tab = QtWidgets.QWidget()
        self.routing_tab.setObjectName("routing_tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.routing_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.core_scroll_area = QtWidgets.QScrollArea(self.routing_tab)
        self.core_scroll_area.setWidgetResizable(True)
        self.core_scroll_area.setObjectName("core_scroll_area")
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_content.setGeometry(QtCore.QRect(0, 0, 556, 501))
        self.scroll_content.setObjectName("scroll_content")
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_layout.setObjectName("scroll_layout")
        self.source_group = QtWidgets.QGroupBox(self.scroll_content)
        self.source_group.setObjectName("source_group")
        self.source_layout = QtWidgets.QVBoxLayout(self.source_group)
        self.source_layout.setObjectName("source_layout")
        self.source_combo = QtWidgets.QComboBox(self.source_group)
        self.source_combo.setObjectName("source_combo")
        self.source_combo.addItem("")
        self.source_layout.addWidget(self.source_combo)
        self.scroll_layout.addWidget(self.source_group)
        self.dest_group = QtWidgets.QGroupBox(self.scroll_content)
        self.dest_group.setObjectName("dest_group")
        self.dest_layout = QtWidgets.QVBoxLayout(self.dest_group)
        self.dest_layout.setObjectName("dest_layout")
        self.scroll_layout.addWidget(self.dest_group)
        self.core_scroll_area.setWidget(self.scroll_content)
        self.verticalLayout.addWidget(self.core_scroll_area)
        self.tab_widget.addTab(self.routing_tab, "")
        self.main_layout.addWidget(self.tab_widget)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.button_layout.addItem(spacerItem)
        self.ok_button = QtWidgets.QPushButton(SignalDetailsDialog)
        self.ok_button.setObjectName("ok_button")
        self.button_layout.addWidget(self.ok_button)
        self.cancel_button = QtWidgets.QPushButton(SignalDetailsDialog)
        self.cancel_button.setObjectName("cancel_button")
        self.button_layout.addWidget(self.cancel_button)
        self.main_layout.addLayout(self.button_layout)

        self.retranslateUi(SignalDetailsDialog)
        self.tab_widget.setCurrentIndex(0)
        self.cancel_button.clicked.connect(SignalDetailsDialog.reject) # type: ignore
        self.ok_button.clicked.connect(SignalDetailsDialog.accept) # type: ignore
        self.data_type_combo.currentTextChanged['QString'].connect(SignalDetailsDialog.onDataTypeChanged) # type: ignore
        self.init_value_combo.currentTextChanged['QString'].connect(SignalDetailsDialog.onInitValueChanged) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(SignalDetailsDialog)

    def retranslateUi(self, SignalDetailsDialog):
        _translate = QtCore.QCoreApplication.translate
        SignalDetailsDialog.setWindowTitle(_translate("SignalDetailsDialog", "Signal Details"))
        self.signal_name_label_text.setText(_translate("SignalDetailsDialog", "Signal Name:"))
        self.signal_name_label.setText(_translate("SignalDetailsDialog", "SignalName"))
        self.var_port_name_label.setText(_translate("SignalDetailsDialog", "Variable Port Name:"))
        self.data_type_label.setText(_translate("SignalDetailsDialog", "Data Type:"))
        self.data_type_combo.setItemText(0, _translate("SignalDetailsDialog", "INT8"))
        self.data_type_combo.setItemText(1, _translate("SignalDetailsDialog", "UINT8"))
        self.data_type_combo.setItemText(2, _translate("SignalDetailsDialog", "INT16"))
        self.data_type_combo.setItemText(3, _translate("SignalDetailsDialog", "UINT16"))
        self.data_type_combo.setItemText(4, _translate("SignalDetailsDialog", "INT32"))
        self.data_type_combo.setItemText(5, _translate("SignalDetailsDialog", "UINT32"))
        self.data_type_combo.setItemText(6, _translate("SignalDetailsDialog", "INT64"))
        self.data_type_combo.setItemText(7, _translate("SignalDetailsDialog", "UINT64"))
        self.data_type_combo.setItemText(8, _translate("SignalDetailsDialog", "FLOAT32"))
        self.data_type_combo.setItemText(9, _translate("SignalDetailsDialog", "FLOAT64"))
        self.data_type_combo.setItemText(10, _translate("SignalDetailsDialog", "BOOLEAN"))
        self.data_type_combo.setItemText(11, _translate("SignalDetailsDialog", "CHAR"))
        self.data_type_combo.setItemText(12, _translate("SignalDetailsDialog", "STRING"))
        self.data_type_combo.setItemText(13, _translate("SignalDetailsDialog", "STRUCT"))
        self.struct_group.setTitle(_translate("SignalDetailsDialog", "Structure Definition"))
        self.struct_fields_label.setText(_translate("SignalDetailsDialog", "Structure Fields:"))
        self.struct_fields_tree.headerItem().setText(0, _translate("SignalDetailsDialog", "Field Name"))
        self.struct_fields_tree.headerItem().setText(1, _translate("SignalDetailsDialog", "Data Type"))
        self.struct_fields_tree.headerItem().setText(2, _translate("SignalDetailsDialog", "Description"))
        self.add_field_button.setText(_translate("SignalDetailsDialog", "Add Field"))
        self.edit_field_button.setText(_translate("SignalDetailsDialog", "Edit Field"))
        self.remove_field_button.setText(_translate("SignalDetailsDialog", "Remove Field"))
        self.description_label.setText(_translate("SignalDetailsDialog", "Description:"))
        self.memory_region_label.setText(_translate("SignalDetailsDialog", "Memory Region:"))
        self.memory_region_combo.setItemText(0, _translate("SignalDetailsDialog", "DDR"))
        self.memory_region_combo.setItemText(1, _translate("SignalDetailsDialog", "Cached"))
        self.memory_region_combo.setItemText(2, _translate("SignalDetailsDialog", "NonCached"))
        self.type_label.setText(_translate("SignalDetailsDialog", "Type:"))
        self.type_combo.setItemText(0, _translate("SignalDetailsDialog", "Concurrent"))
        self.type_combo.setItemText(1, _translate("SignalDetailsDialog", "Sequential"))
        self.init_value_label.setText(_translate("SignalDetailsDialog", "Init Value:"))
        self.init_value_combo.setItemText(0, _translate("SignalDetailsDialog", "ZeroMemory"))
        self.init_value_combo.setItemText(1, _translate("SignalDetailsDialog", "Custom"))
        self.custom_value_button.setText(_translate("SignalDetailsDialog", "Enter Custom Value..."))
        self.asil_label.setText(_translate("SignalDetailsDialog", "ASIL:"))
        self.asil_combo.setItemText(0, _translate("SignalDetailsDialog", "QM"))
        self.asil_combo.setItemText(1, _translate("SignalDetailsDialog", "A"))
        self.asil_combo.setItemText(2, _translate("SignalDetailsDialog", "B"))
        self.asil_combo.setItemText(3, _translate("SignalDetailsDialog", "C"))
        self.asil_combo.setItemText(4, _translate("SignalDetailsDialog", "D"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.basic_tab), _translate("SignalDetailsDialog", "Basic Properties"))
        self.buffer_count_ipc_label.setText(_translate("SignalDetailsDialog", "Buffer Count IPC:"))
        self.impl_approach_label.setText(_translate("SignalDetailsDialog", "Implementation Approach:"))
        self.impl_approach_combo.setItemText(0, _translate("SignalDetailsDialog", "SharedMemory"))
        self.impl_approach_combo.setItemText(1, _translate("SignalDetailsDialog", "VRING"))
        self.impl_approach_combo.setItemText(2, _translate("SignalDetailsDialog", "IpcOvEth"))
        self.get_obj_ref_label.setText(_translate("SignalDetailsDialog", "Get Object Reference:"))
        self.get_obj_ref_combo.setItemText(0, _translate("SignalDetailsDialog", "False"))
        self.get_obj_ref_combo.setItemText(1, _translate("SignalDetailsDialog", "True"))
        self.notifiers_label.setText(_translate("SignalDetailsDialog", "Notifiers:"))
        self.notifiers_combo.setItemText(0, _translate("SignalDetailsDialog", "False"))
        self.notifiers_combo.setItemText(1, _translate("SignalDetailsDialog", "True"))
        self.sm_buff_count_label.setText(_translate("SignalDetailsDialog", "SM Buffer Count:"))
        self.timeout_label.setText(_translate("SignalDetailsDialog", "Timeout:"))
        self.timeout_spin.setSuffix(_translate("SignalDetailsDialog", " ms"))
        self.periodicity_label.setText(_translate("SignalDetailsDialog", "Periodicity:"))
        self.periodicity_spin.setSuffix(_translate("SignalDetailsDialog", " ms"))
        self.checksum_label.setText(_translate("SignalDetailsDialog", "Checksum:"))
        self.checksum_combo.setItemText(0, _translate("SignalDetailsDialog", "None"))
        self.checksum_combo.setItemText(1, _translate("SignalDetailsDialog", "Additive"))
        self.checksum_combo.setItemText(2, _translate("SignalDetailsDialog", "CustomChecksum"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.advanced_tab), _translate("SignalDetailsDialog", "Advanced Properties"))
        self.source_group.setTitle(_translate("SignalDetailsDialog", "Source Core"))
        self.source_combo.setItemText(0, _translate("SignalDetailsDialog", "<None>"))
        self.dest_group.setTitle(_translate("SignalDetailsDialog", "Destination Cores"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.routing_tab), _translate("SignalDetailsDialog", "Core Routing"))
        self.ok_button.setText(_translate("SignalDetailsDialog", "OK"))
        self.cancel_button.setText(_translate("SignalDetailsDialog", "Cancel"))
