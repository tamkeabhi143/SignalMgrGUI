#!/usr/bin/env python3
"""
Test script to view only the Signal Manager GUI layout without functionality.
"""

import sys
import os

# Add the TestQT5 directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "TestQT5"))

try:
    from PyQt5 import QtWidgets
    from SignalMgrGUI import Ui_MainWindow
except ImportError:
    print("Error: PyQt5 is not installed. Please install it with:")
    print("pip install PyQt5")
    sys.exit(1)

class TestWindow(QtWidgets.QMainWindow):
    """Test window that only displays the UI without functionality"""
    def __init__(self):
        super(TestWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Signal Manager GUI Test")

def main():
    """Run the test UI"""
    app = QtWidgets.QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    print("Starting Signal Manager UI Test...")
    main()
