#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
from TestGUI import Ui_MainWindow

class SignalMgrApplication(QtWidgets.QMainWindow):
    def __init__(self):
        super(SignalMgrApplication, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Connect signals/slots for functionality
        self.setup_connections()
        
        # Initialize some data
        self.init_data()
        
        self.setWindowTitle("Signal Manager GUI")
        
    def setup_connections(self):
        """Connect UI elements to their functions"""
        # Core Configuration tab connections
        self.ui.UpdateConfig_2.clicked.connect(self.update_config)
        
        # Signal Configuration tab connections
        self.ui.SaveButton_2.clicked.connect(self.save_signals)
        self.ui.UndoButton_2.clicked.connect(self.undo_action)
        self.ui.RedoButton_2.clicked.connect(self.redo_action)
        
        # Debug Tools tab connections
        self.ui.debug_start_button.clicked.connect(self.start_debug)
        self.ui.debug_stop_button.clicked.connect(self.stop_debug)
        self.ui.debug_clear_button.clicked.connect(self.clear_logs)
        
    def init_data(self):
        """Initialize data in the UI"""
        # Add sample data to trees
        self.add_sample_core_info()
        self.add_sample_advanced_settings()
        
        # Set initial values
        self.ui.VersionNumber.setValue(1)
        self.ui.SignalCnt.setValue(0)
    
    def add_sample_core_info(self):
        """Add sample data to core info tree"""
        self.ui.CoreInfo_2.clear()
        
        # Add some sample items
        core_item = QtWidgets.QTreeWidgetItem(["Core Settings"])
        self.ui.CoreInfo_2.addTopLevelItem(core_item)
        
        config_item = QtWidgets.QTreeWidgetItem(["Configuration"])
        core_item.addChild(config_item)
        
        # Expand all items
        self.ui.CoreInfo_2.expandAll()
    
    def add_sample_advanced_settings(self):
        """Add sample data to advanced settings tree"""
        self.ui.advanced_tree.clear()
        
        # Add some sample items
        adv_item = QtWidgets.QTreeWidgetItem(["Advanced Settings"])
        self.ui.advanced_tree.addTopLevelItem(adv_item)
        
        # Add some child items
        log_item = QtWidgets.QTreeWidgetItem(["Logging"])
        adv_item.addChild(log_item)
        
        perf_item = QtWidgets.QTreeWidgetItem(["Performance"])
        adv_item.addChild(perf_item)
        
        # Expand all items
        self.ui.advanced_tree.expandAll()
    
    # Event handlers for Core Configuration tab
    def update_config(self):
        """Handle update configuration button click"""
        print("Updating configuration...")
        
    # Event handlers for Signal Configuration tab
    def save_signals(self):
        """Handle save button click"""
        print("Saving signals...")
        
    def undo_action(self):
        """Handle undo button click"""
        print("Undoing last action...")
        
    def redo_action(self):
        """Handle redo button click"""
        print("Redoing last action...")
    
    # Event handlers for Debug Tools tab
    def start_debug(self):
        """Handle start debug button click"""
        print("Starting debug...")
        self.ui.debug_log.appendPlainText("Debug session started")
        
    def stop_debug(self):
        """Handle stop debug button click"""
        print("Stopping debug...")
        self.ui.debug_log.appendPlainText("Debug session stopped")
        
    def clear_logs(self):
        """Handle clear logs button click"""
        print("Clearing logs...")
        self.ui.debug_log.clear()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SignalMgrApplication()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 