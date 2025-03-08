import sys
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='excel_import_debug.log',
    filemode='w'
)
logger = logging.getLogger('excel_import_debug')

def test_file_dialog():
    """Test if file dialog works properly in the current environment"""
    logger.info("Testing file dialog functionality")
    
    try:
        # Try to detect the GUI toolkit being used
        if 'PyQt5' in sys.modules or 'PySide2' in sys.modules:
            logger.info("Detected Qt framework")
            if 'PyQt5' in sys.modules:
                from PyQt5.QtWidgets import QApplication, QFileDialog
            else:
                from PySide2.QtWidgets import QApplication, QFileDialog
                
            app = QApplication.instance() or QApplication([])
            file_path, _ = QFileDialog.getOpenFileName(None, "Test File Dialog", "", "Excel Files (*.xlsx *.xls)")
            
        elif 'tkinter' in sys.modules:
            logger.info("Detected Tkinter framework")
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            file_path = filedialog.askopenfilename(title="Test File Dialog", 
                                                  filetypes=[("Excel files", "*.xlsx *.xls")])
            
        else:
            logger.warning("Could not detect GUI framework. Testing with Qt.")
            # Try with Qt as fallback
            try:
                from PyQt5.QtWidgets import QApplication, QFileDialog
                app = QApplication.instance() or QApplication([])
                file_path, _ = QFileDialog.getOpenFileName(None, "Test File Dialog", "", "Excel Files (*.xlsx *.xls)")
            except ImportError:
                logger.error("Failed to import PyQt5")
                return False
        
        logger.info(f"Dialog result: {'Selected: ' + file_path if file_path else 'No file selected'}")
        return bool(file_path)
        
    except Exception as e:
        logger.error(f"Error testing file dialog: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    result = test_file_dialog()
    print(f"File dialog test {'PASSED' if result else 'FAILED'}")
    print(f"Check {os.path.abspath('excel_import_debug.log')} for details")
