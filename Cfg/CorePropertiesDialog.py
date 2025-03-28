# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CorePropertiesDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CorePropertiesDialog(object):
    def setupUi(self, CorePropertiesDialog):
        CorePropertiesDialog.setObjectName("CorePropertiesDialog")
        CorePropertiesDialog.resize(400, 400)
        self.verticalLayout = QtWidgets.QVBoxLayout(CorePropertiesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.name_label = QtWidgets.QLabel(CorePropertiesDialog)
        self.name_label.setObjectName("name_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.name_label)
        self.name_edit = QtWidgets.QLineEdit(CorePropertiesDialog)
        self.name_edit.setObjectName("name_edit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.name_edit)
        self.description_label = QtWidgets.QLabel(CorePropertiesDialog)
        self.description_label.setObjectName("description_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.description_label)
        self.description_edit = QtWidgets.QLineEdit(CorePropertiesDialog)
        self.description_edit.setObjectName("description_edit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.description_edit)
        self.empty_label_1 = QtWidgets.QLabel(CorePropertiesDialog)
        self.empty_label_1.setText("")
        self.empty_label_1.setObjectName("empty_label_1")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.empty_label_1)
        self.master_checkbox = QtWidgets.QCheckBox(CorePropertiesDialog)
        self.master_checkbox.setObjectName("master_checkbox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.master_checkbox)
        self.os_label = QtWidgets.QLabel(CorePropertiesDialog)
        self.os_label.setObjectName("os_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.os_label)
        self.os_combo = QtWidgets.QComboBox(CorePropertiesDialog)
        self.os_combo.setObjectName("os_combo")
        self.os_combo.addItem("")
        self.os_combo.addItem("")
        self.os_combo.addItem("")
        self.os_combo.addItem("")
        self.os_combo.addItem("")
        self.os_combo.addItem("")
        self.os_combo.addItem("")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.os_combo)
        self.empty_label_2 = QtWidgets.QLabel(CorePropertiesDialog)
        self.empty_label_2.setText("")
        self.empty_label_2.setObjectName("empty_label_2")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.empty_label_2)
        self.custom_os_edit = QtWidgets.QLineEdit(CorePropertiesDialog)
        self.custom_os_edit.setVisible(False)
        self.custom_os_edit.setObjectName("custom_os_edit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.custom_os_edit)
        self.soc_family_label = QtWidgets.QLabel(CorePropertiesDialog)
        self.soc_family_label.setObjectName("soc_family_label")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.soc_family_label)
        self.soc_family_combo = QtWidgets.QComboBox(CorePropertiesDialog)
        self.soc_family_combo.setObjectName("soc_family_combo")
        self.soc_family_combo.addItem("")
        self.soc_family_combo.addItem("")
        self.soc_family_combo.addItem("")
        self.soc_family_combo.addItem("")
        self.soc_family_combo.addItem("")
        self.soc_family_combo.addItem("")
        self.soc_family_combo.addItem("")
        self.soc_family_combo.addItem("")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.soc_family_combo)
        self.empty_label_3 = QtWidgets.QLabel(CorePropertiesDialog)
        self.empty_label_3.setText("")
        self.empty_label_3.setObjectName("empty_label_3")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.empty_label_3)
        self.custom_soc_family_edit = QtWidgets.QLineEdit(CorePropertiesDialog)
        self.custom_soc_family_edit.setVisible(False)
        self.custom_soc_family_edit.setObjectName("custom_soc_family_edit")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.custom_soc_family_edit)
        self.empty_label_4 = QtWidgets.QLabel(CorePropertiesDialog)
        self.empty_label_4.setText("")
        self.empty_label_4.setObjectName("empty_label_4")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.empty_label_4)
        self.qnx_checkbox = QtWidgets.QCheckBox(CorePropertiesDialog)
        self.qnx_checkbox.setObjectName("qnx_checkbox")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.qnx_checkbox)
        self.empty_label_5 = QtWidgets.QLabel(CorePropertiesDialog)
        self.empty_label_5.setText("")
        self.empty_label_5.setObjectName("empty_label_5")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.empty_label_5)
        self.autosar_checkbox = QtWidgets.QCheckBox(CorePropertiesDialog)
        self.autosar_checkbox.setObjectName("autosar_checkbox")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.autosar_checkbox)
        self.empty_label_6 = QtWidgets.QLabel(CorePropertiesDialog)
        self.empty_label_6.setText("")
        self.empty_label_6.setObjectName("empty_label_6")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.empty_label_6)
        self.sim_checkbox = QtWidgets.QCheckBox(CorePropertiesDialog)
        self.sim_checkbox.setObjectName("sim_checkbox")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.sim_checkbox)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.button_layout.addItem(spacerItem1)
        self.ok_button = QtWidgets.QPushButton(CorePropertiesDialog)
        self.ok_button.setObjectName("ok_button")
        self.button_layout.addWidget(self.ok_button)
        self.cancel_button = QtWidgets.QPushButton(CorePropertiesDialog)
        self.cancel_button.setObjectName("cancel_button")
        self.button_layout.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.button_layout)

        self.retranslateUi(CorePropertiesDialog)
        QtCore.QMetaObject.connectSlotsByName(CorePropertiesDialog)

    def retranslateUi(self, CorePropertiesDialog):
        _translate = QtCore.QCoreApplication.translate
        CorePropertiesDialog.setWindowTitle(_translate("CorePropertiesDialog", "Core Properties"))
        self.name_label.setText(_translate("CorePropertiesDialog", "Core Name:"))
        self.description_label.setText(_translate("CorePropertiesDialog", "Description:"))
        self.master_checkbox.setText(_translate("CorePropertiesDialog", "Is Master Core"))
        self.os_label.setText(_translate("CorePropertiesDialog", "OS Type:"))
        self.os_combo.setItemText(0, _translate("CorePropertiesDialog", "Unknown"))
        self.os_combo.setItemText(1, _translate("CorePropertiesDialog", "Linux"))
        self.os_combo.setItemText(2, _translate("CorePropertiesDialog", "QNX"))
        self.os_combo.setItemText(3, _translate("CorePropertiesDialog", "AUTOSAR"))
        self.os_combo.setItemText(4, _translate("CorePropertiesDialog", "FreeRTOS"))
        self.os_combo.setItemText(5, _translate("CorePropertiesDialog", "Windows"))
        self.os_combo.setItemText(6, _translate("CorePropertiesDialog", "Other"))
        self.custom_os_edit.setPlaceholderText(_translate("CorePropertiesDialog", "Enter custom OS type"))
        self.soc_family_label.setText(_translate("CorePropertiesDialog", "SOC Family:"))
        self.soc_family_combo.setItemText(0, _translate("CorePropertiesDialog", "Unknown"))
        self.soc_family_combo.setItemText(1, _translate("CorePropertiesDialog", "TI"))
        self.soc_family_combo.setItemText(2, _translate("CorePropertiesDialog", "Tricore"))
        self.soc_family_combo.setItemText(3, _translate("CorePropertiesDialog", "NXP"))
        self.soc_family_combo.setItemText(4, _translate("CorePropertiesDialog", "Intel"))
        self.soc_family_combo.setItemText(5, _translate("CorePropertiesDialog", "AMD"))
        self.soc_family_combo.setItemText(6, _translate("CorePropertiesDialog", "Raspberry Pi"))
        self.soc_family_combo.setItemText(7, _translate("CorePropertiesDialog", "Other"))
        self.custom_soc_family_edit.setPlaceholderText(_translate("CorePropertiesDialog", "Enter custom SOC family"))
        self.qnx_checkbox.setText(_translate("CorePropertiesDialog", "Is QNX Core"))
        self.autosar_checkbox.setText(_translate("CorePropertiesDialog", "Is Autosar Compliant"))
        self.sim_checkbox.setText(_translate("CorePropertiesDialog", "Is Simulation Core"))
        self.ok_button.setText(_translate("CorePropertiesDialog", "OK"))
        self.cancel_button.setText(_translate("CorePropertiesDialog", "Cancel"))
