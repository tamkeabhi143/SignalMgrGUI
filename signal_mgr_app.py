#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from SignalMgrGUI import Ui_MainWindow

# Import the new modules
from modules.file_operations import FileOperations
from modules.signal_operations import SignalOperations
from modules.code_generation import CodeGeneration
from modules.ui_helpers import UIHelpers

class SignalMgrApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(SignalMgrApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Initialize class variables with properly structured metadata
        self.current_file = None
        self.signals_data = {
            "metadata": {
                "version": "1.0",
                "date": "",  # Leave empty for initialize_version_fields to set current date
                "editor": "", # Leave empty initially
                "description": ""
            },
            "soc_type": "Windows",
            "build_type": "SMP",
            "soc_list": ["Windows"],
            "build_list": ["SMP"],
            "core_info": {},
            "signals": {}
        }
        self.copied_signal = None
        self.modified = False  # Explicitly set to False on initialization
        self.undo_stack = []
        self.redo_stack = []
        
        # Remove the Operation menu if it exists
        operation_menu = self.findChild(QtWidgets.QMenu, "menuOperation")
        if (operation_menu):
            menubar = self.menuBar()
            menubar.removeAction(operation_menu.menuAction())
        
        # Initialize modules
        self.file_ops = FileOperations(self)
        self.signal_ops = SignalOperations(self)
        self.code_gen = CodeGeneration(self)
        self.ui_helpers = UIHelpers(self)
        
        # Clear default "Enter Your Name" text before setting up connections
        self.ui.EditorName.setPlainText("")
        
        # Connect UI elements to their respective functions
        self.setup_connections()
        
        # Setup tree widget for signal display
        self.ui_helpers.setup_tree_widget()
        
        # Initialize SOC list and build types
        self.ui_helpers.populate_soc_list()
        self.ui_helpers.populate_build_types()
        
        # Initialize version fields
        self.ui_helpers.initialize_version_fields()
        
        # Disable SignalCnt field
        self.ui.SignalCnt.setReadOnly(True)
        self.ui.SignalCnt.setEnabled(False)
        self.ui_helpers.update_signal_count_display()
        
        # Set window title
        self.setWindowTitle("Signal Manager Tool")

    def setup_connections(self):
        # Connect File menu actions
        self.ui.actionOpen.triggered.connect(self.file_ops.open_file)
        self.ui.actionSave.triggered.connect(self.file_ops.save_file)
        self.ui.actionSave_As.triggered.connect(self.file_ops.save_file_as)
        self.ui.actionCreate.triggered.connect(self.file_ops.create_new_file)
        self.ui.actionExport_as_Excel.triggered.connect(self.file_ops.export_to_excel)
        self.ui.actionImport_From_Excel.triggered.connect(self.file_ops.import_from_excel)  # Connect the existing UI action
        self.ui.actionClose.triggered.connect(self.file_ops.close_file)  # Update the Close action to call close_file instead of close_application
        self.ui.actionExit.triggered.connect(self.file_ops.close_application)
        self.ui.actionExit_2.triggered.connect(self.file_ops.close_application)
        
        # Connect Database menu actions - remove version check
        self.ui.actionAdd_Signal.triggered.connect(self.signal_ops.add_signal)
        self.ui.actionDelete_Signal.triggered.connect(self.signal_ops.delete_signal)
        self.ui.actionUpdate_Signal.triggered.connect(self.signal_ops.update_signal)
        self.ui.actionRename_Signal.triggered.connect(self.signal_ops.rename_signal)
        self.ui.actionCopy_Signal.triggered.connect(self.signal_ops.copy_signal)
        self.ui.actionPaste_Signal.triggered.connect(self.signal_ops.paste_signal)
        
        # Connect Code Generation menu actions (still using check_version_for_export inside methods)
        self.ui.actionSignalMgr.triggered.connect(self.code_gen.generate_signal_mgr)
        self.ui.actionIpcManager.triggered.connect(self.code_gen.generate_ipc_manager)
        self.ui.actionIpcOvEthMgr.triggered.connect(self.code_gen.generate_ipc_eth_mgr)
        
        # Connect Help menu actions
        self.ui.actionAbout_Tool_Usage.triggered.connect(self.show_tool_usage)
        self.ui.actionLicense.triggered.connect(self.show_license)
        self.ui.actionVersion.triggered.connect(self.show_version)
        
        # Connect buttons
        self.ui.SaveButton_2.clicked.connect(self.file_ops.save_file)
        self.ui.UndoButton_2.clicked.connect(self.ui_helpers.undo_action)
        self.ui.RedoButton_2.clicked.connect(self.ui_helpers.redo_action)
        self.ui.UpdateConfig_2.clicked.connect(self.signal_ops.open_configuration_manager)
        
        # Connect combo boxes
        self.ui.SOCList.currentIndexChanged.connect(self.ui_helpers.soc_selection_changed)
        self.ui.BuildImageType.currentIndexChanged.connect(self.ui_helpers.build_type_changed)
        
        # Connect version fields - update for QLineEdit
        if isinstance(self.ui.VersionNumber, QtWidgets.QLineEdit):
            self.ui.VersionNumber.textChanged.connect(lambda text: self.ui_helpers.update_version_info(False, True))
        else:
            # Fallback for QSpinBox
            self.ui.VersionNumber.valueChanged.connect(lambda val: self.ui_helpers.update_version_info(False, True))
        self.ui.VersionDate.dateChanged.connect(lambda date: self.ui_helpers.update_version_info(False, True))
        self.ui.EditorName.textChanged.connect(lambda: self.ui_helpers.update_version_info(False, True))
        
        # Additional change: Set tab order to improve usability
        self.ui.VersionNumber.setTabOrder(self.ui.VersionNumber, self.ui.VersionDate)
        self.ui.VersionDate.setTabOrder(self.ui.VersionDate, self.ui.EditorName)

    # Help functions
    def show_tool_usage(self):
        help_text = (
            "Signal Manager Tool Usage\n\n"
            "This tool helps you manage signal definitions for embedded systems.\n\n"
            "1. Create or open a signal configuration file\n"
            "2. Add, edit, or delete signals as needed\n"
            "3. Generate code for your target platform\n"
            "4. Save your configuration for future use"
        )
        QMessageBox.information(self, "Tool Usage", help_text)

    def show_license(self):
        license_text = (
            "Signal Manager Tool License\n\n"
            "Copyright (c) 2023\n"
            "All Rights Reserved\n\n"
            "This software is provided 'as-is', without any express or implied warranty."
        )
        QMessageBox.information(self, "License", license_text)

    def show_version(self):
        version_text = "Signal Manager Tool v1.0.0"
        QMessageBox.information(self, "Version", version_text)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SignalMgrApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()