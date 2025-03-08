import sys
import os
import logging

logger = logging.getLogger(__name__)

class ExcelImporter:
    def __init__(self, parent=None):
        self.parent = parent
        
    def import_excel(self):
        """Import data from an Excel file"""
        logger.info("Starting Excel import process")
        
        try:
            file_path = self._get_excel_file_path()
            if not file_path:
                logger.warning("No file selected or dialog canceled")
                return False
                
            logger.info(f"Selected file: {file_path}")
            # Process the Excel file here
            return self._process_excel_file(file_path)
            
        except Exception as e:
            logger.error(f"Error during Excel import: {str(e)}", exc_info=True)
            return False
    
    def _get_excel_file_path(self):
        """Show a file dialog to select an Excel file"""
        logger.debug("Opening file dialog for Excel selection")
        
        # Force the dialog to be shown in the foreground
        try:
            # Try to detect the GUI toolkit being used
            if 'PyQt5' in sys.modules:
                from PyQt5.QtWidgets import QFileDialog, QApplication
                
                # Ensure we have an application instance
                app = QApplication.instance() or QApplication([])
                
                # Use native dialog if possible
                options = QFileDialog.Options()
                
                file_path, _ = QFileDialog.getOpenFileName(
                    self.parent,
                    "Select Excel File",
                    "",
                    "Excel Files (*.xlsx *.xls);;All Files (*)",
                    options=options
                )
                
            elif 'PySide2' in sys.modules:
                from PySide2.QtWidgets import QFileDialog, QApplication
                
                app = QApplication.instance() or QApplication([])
                options = QFileDialog.Options()
                
                file_path, _ = QFileDialog.getOpenFileName(
                    self.parent,
                    "Select Excel File",
                    "",
                    "Excel Files (*.xlsx *.xls);;All Files (*)",
                    options=options
                )
                
            elif 'tkinter' in sys.modules:
                import tkinter as tk
                from tkinter import filedialog
                
                # Ensure we have a root window
                root = tk.Tk() if not tk._default_root else tk._default_root
                root.withdraw()  # Hide the root window
                root.attributes('-topmost', True)  # Bring dialog to front
                
                file_path = filedialog.askopenfilename(
                    title="Select Excel File",
                    filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
                )
                
                if hasattr(root, 'destroy') and root != tk._default_root:
                    root.destroy()
                    
            else:
                logger.warning("Could not detect GUI framework. Trying PyQt as fallback.")
                # Try with PyQt as fallback
                try:
                    from PyQt5.QtWidgets import QFileDialog, QApplication
                    app = QApplication.instance() or QApplication([])
                    file_path, _ = QFileDialog.getOpenFileName(
                        None,
                        "Select Excel File",
                        "",
                        "Excel Files (*.xlsx *.xls);;All Files (*)"
                    )
                except ImportError:
                    logger.error("Failed to import PyQt5 for file dialog")
                    return None
                    
            return file_path
            
        except Exception as e:
            logger.error(f"Error showing file dialog: {str(e)}", exc_info=True)
            return None
            
    def _process_excel_file(self, file_path):
        """Process the selected Excel file"""
        # Implementation depends on your application's needs
        logger.info(f"Processing Excel file: {file_path}")
        # Your Excel processing code here
        return True
