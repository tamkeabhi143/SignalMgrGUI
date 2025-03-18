#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Add the parent directory to the path so modules can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from Cfg.SignalMgrGUI import Ui_SignalMgrApp
import Cfg.signalmgrapp_rc

# Import the new modules
from Modules.FileOperations import FileOperations
from Modules.SignalOperations import SignalOperations
from Modules.CodeGeneration import CodeGeneration
from Modules.UIHelpers import UIHelpers

class SignalMgrApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(SignalMgrApp, self).__init__()
        self.ui = Ui_SignalMgrApp()
        self.ui.setupUi(self)
        
        # Performance optimization: Preload menu actions to avoid delays
        self._preload_menu_resources()
        
        # Completely replace menu setup with direct creation to fix menu issues
        self._setup_menus_directly()
        
        # Initialize flags to prevent recursion
        self._initializing_core_details = False
        self._updating_core_details = False
        
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
        
        # Map old UI element names to new ones
        # We'll check if the new UI elements exist and use them, otherwise fall back to old ones
        self._map_ui_elements()
        
        # Add BoardSelect dropdown to the UI
        self.create_board_select_dropdown()
        
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
        if hasattr(self.ui, "EditorName"):
            self.ui.EditorName.setPlainText("")
        elif hasattr(self.ui, "VersionUpdateName"):
            self.ui.VersionUpdateName.setPlainText("")
        
        # Connect UI elements to their respective functions
        self.setup_connections()
        
        # Setup tree widget for signal display
        self.ui_helpers.setup_tree_widget()
        
        # Initialize SOC list and build types
        self.ui_helpers.populate_soc_list()
        self.ui_helpers.populate_build_types()
        self.populate_board_select()
        
        # Initialize version fields
        self.ui_helpers.initialize_version_fields()
        
        # Disable SignalCnt field if it exists
        if hasattr(self.ui, "SignalCnt"):
            self.ui.SignalCnt.setReadOnly(True)
            self.ui.SignalCnt.setEnabled(False)
            self.ui_helpers.update_signal_count_display()
        
        # Initialize basic parts of Project Specific Config tab, but not the core details
        self.initialize_basic_project_config()
        
        # Set window title
        self.setWindowTitle("Signal Manager Tool")
        
        # DON'T set up delayed initialization - per user request
        # We'll initialize the core details only when a file is opened/created/imported

    def _preload_menu_resources(self):
        """Preload menu resources for better performance"""
        try:
            # Get the base icon directory path
            icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Cfg", "Icons")
            print(f"Icon directory: {icon_dir}")
            
            # Fixed mapping of action names to correct icon file names
            icon_mapping = {
                "new": "NewFile.png",
                "open": "OpenFile.png",
                "save": "Save.png",
                "save_as": "SaveAs.png",
                "export_to_excel": "ExportToExcel.png",
                "import_from_excel": "Import.png",
                "close": "Close.png",
                "add_entry": "AddEntry.png",
                "delete_entry": "RemoveEntry.png",
                "update_entry": "UpdateEntry.png",
                "copy_entry": "Copy.png",
                "paste_entry": "Paste.png",
                "undo": "Undo.png",
                "redo": "Redo.png",
                "about_tool": "About.png",
                "license": "License.png",
                "exit": "Exit.png"
            }
            
            # Cache to store loaded icons
            self._icon_cache = {}
            
            # Preload all icons using direct file paths instead of resources
            for action_name, icon_file in icon_mapping.items():
                icon_path = os.path.join(icon_dir, icon_file)
                if os.path.exists(icon_path):
                    # Create icon directly from file
                    icon = QtGui.QIcon(icon_path)
                    if not icon.isNull():
                        self._icon_cache[action_name] = icon
                        self._icon_cache[icon_file] = icon  # Also store by filename
                        print(f"Successfully loaded icon: {action_name} from {icon_path}")
                    else:
                        print(f"Warning: Failed to create icon from {icon_path}")
                else:
                    print(f"Warning: Icon file not found: {icon_path}")
                        
        except Exception as e:
            print(f"Warning: Error preloading menu resources: {e}")
            import traceback
            traceback.print_exc()

    def _setup_menus_directly(self):
        """Setup menus directly to fix menu rendering issues"""
        try:
            # Get original menu bar and make it visible
            menu_bar = self.menuBar()
            menu_bar.clear()  # Clear any existing menus
            menu_bar.setVisible(True)
            menu_bar.setEnabled(True)
            
            # Cache all original actions from UI for retrieval later
            self._cache_original_actions()
            
            # Create the main menus directly on the menubar
            file_menu = menu_bar.addMenu("&File")
            edit_menu = menu_bar.addMenu("&Edit")
            code_gen_menu = menu_bar.addMenu("&Code Generator")
            help_menu = menu_bar.addMenu("&Help")
            
            # ------- File Menu -------
            # Add actions directly to new menu rather than using existing UI menu
            self._add_to_menu(file_menu, [
                ("actionNew", "New", "Ctrl+N"),
                ("actionOpen", "Open", "Ctrl+O"),
                None,  # Separator
                ("actionSave", "Save", "Ctrl+S"),
                ("actionSave_As", "Save As", "Ctrl+Shift+S"),
                None,  # Separator
                ("actionExport_To_Excel", "Export to Excel"),
                ("actionImport_From_Excel", "Import from Excel"),
                None,  # Separator
                ("actionClose", "Close"),
                None,  # Separator
                ("actionExit", "Exit", "Alt+F4")
            ])
            
            # ------- Edit Menu -------
            self._add_to_menu(edit_menu, [
                ("actionAdd_Entry", "Add Entry", "Ctrl+A"),
                ("actionDelete_Entry", "Delete Entry", "Del"),
                None,  # Separator
                ("actionUpdate_Entry", "Update Entry", "Ctrl+U"),
                ("actionCopy_Entry", "Copy Entry", "Ctrl+C"),
                ("actionPaste_Entry", "Paste Entry", "Ctrl+V"),
                None,  # Separator
                ("actionUndo", "Undo", "Ctrl+Z"),
                ("actionRedo", "Redo", "Ctrl+Y")
            ])
            
            # ------- Code Generator Menu -------
            self._add_to_menu(code_gen_menu, [
                ("actionSignalMgr", "Signal Manager"),
                ("actionIpcManager", "IPC Manager"),
                ("actionIpcOvEthMgr", "IPC Over Ethernet Manager"),
                None  # Add Generate Header File later in setup_connections
            ])
            
            # ------- Help Menu -------
            self._add_to_menu(help_menu, [
                ("actionAbout_Tool", "About Tool"),
                ("actionLicense", "License")
            ])
            
            # Store menus for later access
            self.ui.menuFile = file_menu
            self.ui.menuEdit = edit_menu
            self.ui.menuCode_Generator = code_gen_menu
            self.ui.menuHelp = help_menu
            
            # Print a confirmation message
            print("Menu system rebuilt directly in the code")
            
            # Set the menu bar explicitly
            self.setMenuBar(menu_bar)
            
        except Exception as e:
            print(f"Error setting up menus directly: {e}")
            import traceback
            traceback.print_exc()
    
    def _cache_original_actions(self):
        """Cache all original actions from UI for retrieval later"""
        self._original_actions = {}
        
        # Get all actions from original UI
        if hasattr(self.ui, "menuFile"):
            for action in self.ui.menuFile.actions():
                if action.objectName():
                    self._original_actions[action.objectName()] = action
        
        if hasattr(self.ui, "menuEdit"):
            for action in self.ui.menuEdit.actions():
                if action.objectName():
                    self._original_actions[action.objectName()] = action
        
        if hasattr(self.ui, "menuCode_Generator"):
            for action in self.ui.menuCode_Generator.actions():
                if action.objectName():
                    self._original_actions[action.objectName()] = action
        
        if hasattr(self.ui, "menuHelp"):
            for action in self.ui.menuHelp.actions():
                if action.objectName():
                    self._original_actions[action.objectName()] = action
    
    def _add_to_menu(self, menu, items):
        """Add items to menu, handling separators and existing actions"""
        # Get the base icon directory path
        icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Cfg", "Icons")
        
        # Fixed mapping of action names to correct icon file names
        icon_mapping = {
            "actionNew": "NewFile.png",
            "actionOpen": "OpenFile.png", 
            "actionSave": "Save.png",
            "actionSave_As": "SaveAs.png",
            "actionExport_To_Excel": "ExportToExcel.png",
            "actionImport_From_Excel": "Import.png",
            "actionClose": "Close.png",
            "actionAdd_Entry": "AddEntry.png",
            "actionDelete_Entry": "RemoveEntry.png",
            "actionUpdate_Entry": "UpdateEntry.png",
            "actionCopy_Entry": "Copy.png",
            "actionPaste_Entry": "Paste.png",
            "actionUndo": "Undo.png",
            "actionRedo": "Redo.png",
            "actionAbout_Tool": "About.png",
            "actionLicense": "License.png",
            "actionExit": "Exit.png",
            "actionSignalMgr": "Save.png",  # Use generic icons for these
            "actionIpcManager": "Save.png",
            "actionIpcOvEthMgr": "Save.png",
            "actionGenerateHeader": "Save.png"
        }
        
        for item in items:
            if item is None:
                # Add separator
                menu.addSeparator()
                continue
                
            action_name, action_text, shortcut = (item + (None,))[:3]
            
            # Create a brand new QAction for each menu item
            action = QtWidgets.QAction(action_text, self)
            action.setObjectName(action_name)
            
            # Set shortcut if provided
            if shortcut:
                action.setShortcut(shortcut)
                
            # Set icon directly from file path
            if action_name in icon_mapping:
                icon_file = icon_mapping[action_name]
                
                # Use cached icon if available
                if hasattr(self, "_icon_cache") and icon_file in self._icon_cache:
                    action.setIcon(self._icon_cache[icon_file])
                    print(f"Set icon for {action_name} from cache ({icon_file})")
                else:
                    # Create icon from file
                    icon_path = os.path.join(icon_dir, icon_file)
                    if os.path.exists(icon_path):
                        icon = QtGui.QIcon(icon_path)
                        if not icon.isNull():
                            action.setIcon(icon)
                            print(f"Set icon for {action_name} from {icon_path}")
                        else:
                            print(f"Warning: Failed to create icon from {icon_path}")
                    else:
                        print(f"Warning: Icon file not found: {icon_path}")
            
            # Store reference in ui object for later access
            setattr(self.ui, action_name, action)
            
            # Add to menu
            menu.addAction(action)
            
            # Print confirmation
            print(f"Added menu item: {action_text} ({action_name})")

    def _map_ui_elements(self):
        """Map old UI element names to new ones for compatibility"""
        # Version information mapping
        if not hasattr(self.ui, "EditorName") and hasattr(self.ui, "VersionUpdateName"):
            self.ui.EditorName = self.ui.VersionUpdateName
        
        # SOC and Build Type mapping
        if not hasattr(self.ui, "SOCList") and hasattr(self.ui, "SOCListComboBox"):
            self.ui.SOCList = self.ui.SOCListComboBox
            
        if not hasattr(self.ui, "BuildImageType") and hasattr(self.ui, "BuildImageComboBox"):
            self.ui.BuildImageType = self.ui.BuildImageComboBox
            
        # Menu action mapping - ensure compatibility between old and new action names
        # File menu
        if hasattr(self.ui, "actionNew") and not hasattr(self.ui, "actionCreate"):
            self.ui.actionCreate = self.ui.actionNew
            
        if hasattr(self.ui, "actionExport_To_Excel") and not hasattr(self.ui, "actionExport_as_Excel"):
            self.ui.actionExport_as_Excel = self.ui.actionExport_To_Excel
            
        # Edit menu
        if hasattr(self.ui, "actionAdd_Entry") and not hasattr(self.ui, "actionAdd_Signal"):
            self.ui.actionAdd_Signal = self.ui.actionAdd_Entry
            
        if hasattr(self.ui, "actionDelete_Entry") and not hasattr(self.ui, "actionDelete_Signal"):
            self.ui.actionDelete_Signal = self.ui.actionDelete_Entry
            
        if hasattr(self.ui, "actionUpdate_Entry") and not hasattr(self.ui, "actionUpdate_Signal"):
            self.ui.actionUpdate_Signal = self.ui.actionUpdate_Entry
            
        if hasattr(self.ui, "actionCopy_Entry") and not hasattr(self.ui, "actionCopy_Signal"):
            self.ui.actionCopy_Signal = self.ui.actionCopy_Entry
            
        # Paste action
        if hasattr(self.ui, "actionPaste_Entry") and not hasattr(self.ui, "actionPaste_Signal"):
            self.ui.actionPaste_Signal = self.ui.actionPaste_Entry
        elif not hasattr(self.ui, "actionPaste_Signal") and not hasattr(self.ui, "actionPaste_Entry"):
            # Create a Paste action if it doesn't exist
            self.ui.actionPaste_Signal = QtWidgets.QAction(self)
            self.ui.actionPaste_Signal.setText("Paste Signal")
            if hasattr(self.ui, "menuEdit"):
                self.ui.menuEdit.addAction(self.ui.actionPaste_Signal)
                
        # Help menu
        if hasattr(self.ui, "actionAbout_Tool") and not hasattr(self.ui, "actionAbout_Tool_Usage"):
            self.ui.actionAbout_Tool_Usage = self.ui.actionAbout_Tool
            
        # Frame mappings
        if not hasattr(self.ui, "SignalOpFrame"):
            # Create a placeholder frame if needed for compatibility
            self.ui.SignalOpFrame = QtWidgets.QFrame(self)

    def create_board_select_dropdown(self):
        """Create and add the BoardSelect dropdown to the UI"""
        try:
            # If BoardListComboBox exists, use it instead of creating a new one
            if hasattr(self.ui, "BoardListComboBox"):
                self.ui.BoardSelect = self.ui.BoardListComboBox
                print("Using existing BoardListComboBox")
                return
                
            # Check if we need to create a new dropdown
            if hasattr(self.ui, "BoardSelect"):
                print("BoardSelect already exists")
                return
                
            # Create the BoardSelect dropdown
            self.ui.BoardSelect = QtWidgets.QComboBox(self.ui.SignalOpFrame)
            self.ui.BoardSelect.setObjectName("BoardSelect")
            
            # Get the horizontal layout of the SignalOpFrame
            horizontal_layout = self.ui.SignalOpFrame.layout()
            
            # Insert the BoardSelect dropdown before the SOCList
            # Find the index of SOCList in the layout
            for i in range(horizontal_layout.count()):
                if horizontal_layout.itemAt(i).widget() == self.ui.SOCList:
                    # Create a label for the BoardSelect dropdown
                    self.ui.BoardSelectLabel = QtWidgets.QLabel(self.ui.SignalOpFrame)
                    self.ui.BoardSelectLabel.setObjectName("BoardSelectLabel")
                    self.ui.BoardSelectLabel.setText("BoardSelect")
                    
                    # Insert the label and dropdown before SOCList
                    horizontal_layout.insertWidget(i - 1, self.ui.BoardSelectLabel)
                    horizontal_layout.insertWidget(i, self.ui.BoardSelect)
                    break
        except Exception as e:
            print(f"Error creating BoardSelect dropdown: {e}")

    def populate_board_select(self):
        """Populate the BoardSelect dropdown with default board options"""
        try:
            # Clear the dropdown first
            self.ui.BoardSelect.clear()
            
            # Add the default board options
            board_options = ["j721e_hyd", "j721s2_hyd", "j721s2_hyd3", "TC4", "GM_VIP", "DCU_A1H", "DCU_A1L"]
            for board in board_options:
                self.ui.BoardSelect.addItem(board)
            
            # Set the first option as default
            self.ui.BoardSelect.setCurrentIndex(0)
            
            # Store the board options in signals_data for persistence
            if "board_options" not in self.signals_data:
                self.signals_data["board_options"] = board_options
                self.signals_data["selected_board"] = board_options[0]
        except Exception as e:
            print(f"Error populating BoardSelect dropdown: {e}")

    def setup_connections(self):
        """Connect all UI elements to their respective functions"""
        try:
            # Fix toolbar icons first
            self._setup_toolbar_icons()
            
            # Disconnect any existing connections to prevent duplicate triggers
            self._disconnect_existing_actions()
            
            # Print menu debug info
            self._debug_menu_structure()
            
            # Cache function references to avoid repeated lookups
            # File menu functions
            open_func = self.open_file_wrapper
            save_func = self.file_ops.save_file
            save_as_func = self.file_ops.save_file_as
            create_func = self.create_file_wrapper
            export_excel_func = self.file_ops.export_to_excel
            import_excel_func = self.import_excel_wrapper
            close_file_func = self.file_ops.close_file
            exit_func = self.file_ops.close_application
            
            # Edit menu functions
            add_signal_func = self.signal_ops.add_signal
            delete_signal_func = self.signal_ops.delete_signal
            update_signal_func = self.signal_ops.update_signal
            copy_signal_func = self.signal_ops.copy_signal
            paste_signal_func = self.signal_ops.paste_signal
            undo_func = self.ui_helpers.undo_action
            redo_func = self.ui_helpers.redo_action
            
            # Code Generation menu functions
            gen_signal_mgr_func = self.code_gen.generate_signal_mgr
            gen_ipc_mgr_func = self.code_gen.generate_ipc_manager
            gen_ipc_eth_func = self.code_gen.generate_ipc_eth_mgr
            gen_header_func = self.code_gen.generate_header_file
            
            # Help menu functions
            about_func = self.show_tool_usage
            license_func = self.show_license
            
            # Connect file menu actions
            file_menu_connections = [
                ("actionNew", create_func),
                ("actionOpen", open_func),
                ("actionSave", save_func),
                ("actionSave_As", save_as_func),
                ("actionExport_To_Excel", export_excel_func),
                ("actionImport_From_Excel", import_excel_func),
                ("actionClose", close_file_func),
                ("actionExit", exit_func)
            ]
            
            # Connect edit menu actions
            edit_menu_connections = [
                ("actionAdd_Entry", add_signal_func),
                ("actionDelete_Entry", delete_signal_func),
                ("actionUpdate_Entry", update_signal_func),
                ("actionCopy_Entry", copy_signal_func),
                ("actionPaste_Entry", paste_signal_func),
                ("actionUndo", undo_func),
                ("actionRedo", redo_func)
            ]
            
            # Connect code generator menu actions
            code_gen_connections = [
                ("actionSignalMgr", gen_signal_mgr_func),
                ("actionIpcManager", gen_ipc_mgr_func),
                ("actionIpcOvEthMgr", gen_ipc_eth_func)
            ]
            
            # Connect help menu actions
            help_menu_connections = [
                ("actionAbout_Tool", about_func),
                ("actionLicense", license_func)
            ]
            
            # Connect all actions in a batch
            all_connections = file_menu_connections + edit_menu_connections + code_gen_connections + help_menu_connections
            
            for action_name, func in all_connections:
                if self._connect_action(action_name, func):
                    print(f"Successfully connected {action_name} to function")
                else:
                    print(f"Failed to connect {action_name}")
            
            # Add Generate Header File action to the Code Generator menu
            try:
                # Create action for Generate Header File
                action_gen_header = QtWidgets.QAction("Generate Header File", self)
                action_gen_header.setObjectName("actionGenerateHeader")
                action_gen_header.triggered.connect(gen_header_func)
                
                # Add to Code Generator menu
                if hasattr(self.ui, "menuCode_Generator"):
                    self.ui.menuCode_Generator.addAction(action_gen_header)
                    print("Added Generate Header File action to menu")
            except Exception as e:
                print(f"Could not add header generation menu item: {e}")
            
            # Connect remaining UI elements (buttons, combo boxes, etc.)
            self._connect_remaining_ui_elements()
            
            # Process events to ensure menu connections are established
            QtWidgets.QApplication.processEvents()
            
            # Set up signal tracing for debugging if needed
            self._setup_signal_tracing()
            
            print("All menu connections established successfully")
            
        except Exception as e:
            print(f"Error in setup_connections: {e}")
            import traceback
            traceback.print_exc()
    
    def _debug_menu_structure(self):
        """Print debug information about the menu structure"""
        try:
            print("\n--- MENU STRUCTURE DEBUG ---")
            
            # Check if menuBar exists
            menu_bar = self.menuBar()
            if not menu_bar:
                print("No menu bar found!")
                return
                
            print(f"Menu bar exists with {len(menu_bar.actions())} top-level menus")
            
            # Check each menu
            for menu_name in ["menuFile", "menuEdit", "menuCode_Generator", "menuHelp"]:
                if hasattr(self.ui, menu_name):
                    menu = getattr(self.ui, menu_name)
                    actions = menu.actions()
                    print(f"Menu '{menu_name}' has {len(actions)} actions")
                    
                    # Print each action
                    for i, action in enumerate(actions):
                        connections = 'Unknown'
                        try:
                            connections = action.receivers(QtCore.SIGNAL('triggered()'))
                        except:
                            try:
                                connections = action.receivers(action.triggered)
                            except:
                                pass
                        
                        print(f"  {i+1}. {action.text()} (visible: {action.isVisible()}, enabled: {action.isEnabled()}, connections: {connections})")
                else:
                    print(f"Menu '{menu_name}' not found")
            
            print("--- END MENU DEBUG ---\n")
            
        except Exception as e:
            print(f"Error in menu debug: {e}")
    
    def _setup_signal_tracing(self):
        """Set up signal tracing for debugging menu actions"""
        try:
            # Only do this in debug mode
            debug_mode = True
            if not debug_mode:
                return
                
            print("Setting up signal tracing for menu actions...")
            
            # Define a trace function
            def trace_action(action_name):
                def _trace():
                    print(f"ACTION TRIGGERED: {action_name}")
                return _trace
            
            # List of all major actions to trace
            action_names = [
                "actionNew", "actionOpen", "actionSave", "actionSave_As",
                "actionExport_To_Excel", "actionImport_From_Excel", "actionClose", "actionExit",
                "actionAdd_Entry", "actionDelete_Entry", "actionUpdate_Entry",
                "actionCopy_Entry", "actionPaste_Entry", "actionUndo", "actionRedo",
                "actionSignalMgr", "actionIpcManager", "actionIpcOvEthMgr",
                "actionAbout_Tool", "actionLicense", "actionGenerateHeader"
            ]
            
            # Connect trace function to each action
            for action_name in action_names:
                if hasattr(self.ui, action_name):
                    action = getattr(self.ui, action_name)
                    
                    # Connect the trace function AFTER the main function
                    # This way we can see when the action is triggered without interfering
                    action.triggered.connect(trace_action(action_name))
                    
            print("Signal tracing set up for all menu actions")
            
        except Exception as e:
            print(f"Error setting up signal tracing: {e}")

    def _disconnect_existing_actions(self):
        """Disconnect all existing menu action connections to prevent duplication"""
        try:
            # List of all action names to disconnect
            action_names = [
                "actionNew", "actionOpen", "actionSave", "actionSave_As",
                "actionExport_To_Excel", "actionImport_From_Excel", "actionClose", "actionExit",
                "actionAdd_Entry", "actionDelete_Entry", "actionUpdate_Entry",
                "actionCopy_Entry", "actionPaste_Entry", "actionUndo", "actionRedo",
                "actionSignalMgr", "actionIpcManager", "actionIpcOvEthMgr",
                "actionAbout_Tool", "actionLicense", "actionGenerateHeader"
            ]
            
            # Also check for alternate names
            alt_action_names = [
                "actionCreate", "actionExport_as_Excel", 
                "actionAdd_Signal", "actionDelete_Signal", "actionUpdate_Signal",
                "actionCopy_Signal", "actionPaste_Signal", 
                "actionAbout_Tool_Usage"
            ]
            
            # Combine all action names
            all_action_names = action_names + alt_action_names
            
            # Try to disconnect all actions
            for action_name in all_action_names:
                if hasattr(self.ui, action_name):
                    action = getattr(self.ui, action_name)
                    try:
                        # Block signals temporarily to avoid unexpected triggers
                        action.blockSignals(True)
                        # Disconnect all signals
                        action.triggered.disconnect()
                        action.blockSignals(False)
                    except:
                        # Ignore if the action doesn't have connections
                        action.blockSignals(False)
                        pass
        
        except Exception as e:
            print(f"Error disconnecting existing actions: {e}")

    def _connect_action(self, action_name, func):
        """Connect a menu action to its function, handling different action name variations"""
        try:
            # First try to find the action in the UI
            action = None
            
            # Try to find in UI directly
            if hasattr(self.ui, action_name):
                action = getattr(self.ui, action_name)
            else:
                # Try alternative names
                alt_names = []
                if action_name.startswith("action"):
                    # Generate alternative names
                    if "Entry" in action_name:
                        alt_names.append(action_name.replace("Entry", "Signal"))
                    elif "Signal" in action_name:
                        alt_names.append(action_name.replace("Signal", "Entry"))
                        
                    # Try actionExport/Import variations
                    if action_name == "actionExport_To_Excel":
                        alt_names.append("actionExport_as_Excel")
                    elif action_name == "actionExport_as_Excel":
                        alt_names.append("actionExport_To_Excel")
                        
                    # Try New/Create variations
                    if action_name == "actionNew":
                        alt_names.append("actionCreate")
                    elif action_name == "actionCreate":
                        alt_names.append("actionNew")
                        
                    # Try Tool/Tool_Usage variations
                    if action_name == "actionAbout_Tool":
                        alt_names.append("actionAbout_Tool_Usage")
                    elif action_name == "actionAbout_Tool_Usage":
                        alt_names.append("actionAbout_Tool")
                
                # Try all alternative names
                for alt_name in alt_names:
                    if hasattr(self.ui, alt_name):
                        action = getattr(self.ui, alt_name)
                        break
            
            # If we couldn't find an existing action, check if it was created in _add_to_menu
            if not action and hasattr(self.ui, action_name):
                action = getattr(self.ui, action_name)
                
            # If we still don't have an action, log an error and return
            if not action:
                print(f"Error: Could not find action {action_name} in UI")
                return False
            
            # Make sure the action is a QAction
            if not isinstance(action, QtWidgets.QAction):
                print(f"Error: {action_name} is not a QAction")
                return False
                
            # Now connect the action
            try:
                # Disconnect any existing connections first
                try:
                    action.triggered.disconnect()
                except:
                    pass
                
                # Connect the function directly to the triggered signal
                action.triggered.connect(func)
                
                # Add a direct triggered signal connection for PyQt5 compatibility
                try:
                    # This is a fallback for PyQt5 and older Qt versions
                    action.connect(action, QtCore.SIGNAL('triggered()'), func)
                except:
                    pass
                
                # Make sure the action is visible and enabled
                action.setVisible(True)
                action.setEnabled(True)
                
                return True
            except Exception as e:
                print(f"Error connecting action {action_name}: {e}")
                return False
                
        except Exception as e:
            print(f"Error in _connect_action for {action_name}: {e}")
            return False

    def _connect_remaining_ui_elements(self):
        """Connect non-menu UI elements like buttons, combo boxes, etc."""
        # Connect buttons
        if hasattr(self.ui, "SaveButton_2"):
            self.ui.SaveButton_2.clicked.connect(self.file_ops.save_file)
        elif hasattr(self.ui, "Soc_CoreInfoUpdatedButton"):
            self.ui.Soc_CoreInfoUpdatedButton.clicked.connect(self.file_ops.save_file)
            
        if hasattr(self.ui, "UndoButton_2"):
            self.ui.UndoButton_2.clicked.connect(self.ui_helpers.undo_action)
            
        if hasattr(self.ui, "RedoButton_2"):
            self.ui.RedoButton_2.clicked.connect(self.ui_helpers.redo_action)
            
        if hasattr(self.ui, "UpdateConfig_2"):
            self.ui.UpdateConfig_2.clicked.connect(self.signal_ops.open_configuration_manager)
        
        # Connect combo boxes
        if hasattr(self.ui, "SOCList"):
            self.ui.SOCList.currentIndexChanged.connect(self.ui_helpers.soc_selection_changed)
        elif hasattr(self.ui, "SOCListComboBox"):
            self.ui.SOCList = self.ui.SOCListComboBox
            self.ui.SOCList.currentIndexChanged.connect(self.ui_helpers.soc_selection_changed)
            
        if hasattr(self.ui, "BuildImageType"):
            self.ui.BuildImageType.currentIndexChanged.connect(self.build_type_changed)
        elif hasattr(self.ui, "BuildImageComboBox"):
            self.ui.BuildImageType = self.ui.BuildImageComboBox
            self.ui.BuildImageType.currentIndexChanged.connect(self.build_type_changed)
            
        if hasattr(self.ui, "BoardSelect"):
            self.ui.BoardSelect.currentIndexChanged.connect(self.board_selection_changed)
        elif hasattr(self.ui, "BoardListComboBox"):
            self.ui.BoardSelect = self.ui.BoardListComboBox
            self.ui.BoardSelect.currentIndexChanged.connect(self.board_selection_changed)
        
        # Connect version fields
        if hasattr(self.ui, "VersionNumber"):
            self.ui.VersionNumber.textChanged.connect(lambda: self.ui_helpers.update_version_info(True, False))
        if hasattr(self.ui, "VersionDate"):
            self.ui.VersionDate.dateChanged.connect(lambda: self.ui_helpers.update_version_info(False, False))
        if hasattr(self.ui, "EditorName"):
            self.ui.EditorName.textChanged.connect(lambda: self.ui_helpers.update_version_info(False, True))
        elif hasattr(self.ui, "VersionUpdateName"):
            self.ui.VersionUpdateName.textChanged.connect(lambda: self.ui_helpers.update_version_info(False, True))
        
        # Set up tab widget traversal
        if hasattr(self.ui, "VersionNumber") and hasattr(self.ui, "VersionDate"):
            self.ui.VersionNumber.setTabOrder(self.ui.VersionNumber, self.ui.VersionDate)
            
        if hasattr(self.ui, "VersionDate") and hasattr(self.ui, "EditorName"):
            self.ui.VersionDate.setTabOrder(self.ui.VersionDate, self.ui.EditorName)
        elif hasattr(self.ui, "VersionDate") and hasattr(self.ui, "VersionUpdateName"):
            self.ui.VersionDate.setTabOrder(self.ui.VersionDate, self.ui.VersionUpdateName)

    def build_type_changed(self, index):
        """Handle build type change and update core details view"""
        try:
            # First let the UIHelpers handle the basic build type changed event
            self.ui_helpers.build_type_changed(index)
            
            # Check if the UI is fully initialized 
            if hasattr(self, 'core_details_layout') and self.core_details_layout:
                # Then update our dynamic core details view
                self.update_core_details_view()
            else:
                print("Note: core_details_layout not available yet - skipping update")
        except Exception as e:
            print(f"Error handling build type change: {e}")

    def board_selection_changed(self, index):
        """Handle board selection change"""
        try:
            selected_board = self.ui.BoardSelect.currentText()
            self.signals_data["selected_board"] = selected_board
            self.modified = True
        except Exception as e:
            print(f"Error handling board selection change: {e}")

    # Add wrapper methods to handle menu actions that need special parameter handling
    def open_file_wrapper(self):
        """Wrapper for open_file to handle the menu action"""
        result = self.file_ops.open_file()
        if result:
            # Initialize Project Specific Config after successful file open
            self.initialize_project_specific_config()
            
    def create_file_wrapper(self):
        """Wrapper for create_new_file to handle the menu action"""
        result = self.file_ops.create_new_file()
        if result:
            # Initialize Project Specific Config after file creation
            self.initialize_project_specific_config()
            
    def import_excel_wrapper(self):
        """Wrapper for import_from_excel to handle the menu action"""
        result = self.file_ops.import_from_excel()
        if result:
            # Initialize Project Specific Config after Excel import
            self.initialize_project_specific_config()

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

    def initialize_basic_project_config(self):
        """Initialize only the basic parts of the project specific configuration tab"""
        try:
            # Set up the directory browse buttons
            self.connect_project_specific_buttons()
            
            # Initialize build type controls visibility
            self.set_project_specific_config_enabled(False)
            
        except Exception as e:
            print(f"Error initializing basic project config: {e}")

    def set_project_specific_config_enabled(self, enabled):
        """Enable or disable all inputs in Project Specific Config tab"""
        try:
            # Get current build type
            build_type = self.signals_data.get("build_type", "")
            
            # Check for the new UI elements
            if hasattr(self.ui, "OutputPathLineEdit") and hasattr(self.ui, "ScriptPathLineEdit"):
                # New UI structure
                if hasattr(self.ui, "OutputPathLineEdit"):
                    self.ui.OutputPathLineEdit.setEnabled(enabled)
                if hasattr(self.ui, "OutputPathButton"):
                    self.ui.OutputPathButton.setEnabled(enabled)
                if hasattr(self.ui, "ScriptPathLineEdit"):
                    self.ui.ScriptPathLineEdit.setEnabled(enabled)
                if hasattr(self.ui, "ScriptPathButton"):
                    self.ui.ScriptPathButton.setEnabled(enabled)
            elif hasattr(self.ui, "lineEdit_output_dir") and hasattr(self.ui, "lineEdit_scripts_dir"):
                # Old UI structure
                dir_widgets = [
                    self.ui.lineEdit_output_dir,
                    self.ui.lineEdit_scripts_dir,
                    self.ui.pushButton_browse_output,
                    self.ui.pushButton_browse_scripts
                ]
                
                for widget in dir_widgets:
                    widget.setEnabled(enabled)
            
            if enabled:
                # Update the core details view based on build type
                self.update_core_details_view()
            else:
                # If disabled, make sure all core-specific widgets are disabled too
                if hasattr(self, 'core_details_container'):
                    self.core_details_container.setEnabled(False)
                
        except Exception as e:
            print(f"Error setting Project Specific Config enabled state: {e}")

    def add_expand_collapse_buttons(self):
        """Set up the core specific details section"""
        try:
            # Set up the core details section directly without checking for UI widgets
            # that might not exist yet
            self.setup_core_details_section()
            
        except Exception as e:
            print(f"Error setting up core specific details: {e}")

    def setup_core_details_section(self):
        """Create a dynamic core details section that updates based on BuildImageType"""
        try:
            # This method shouldn't be used during initialization anymore
            # Instead, delayed_ui_setup handles this directly
            print("WARNING: setup_core_details_section called, but this method is deprecated")
            print("The core details will be set up by delayed_ui_setup")
            return
            
            # The rest of this method is kept for reference but not executed
            # Flag to prevent recursion
            self._initializing_core_details = True
            
            # Find the actual widget directly from the UI object
            scroll_widget = self.findChild(QtWidgets.QScrollArea, "scrollArea_core_specific")
            if not scroll_widget:
                print("DEBUG: scrollArea_core_specific not found on the window object")
                # Try to find it from the UI
                if hasattr(self.ui, 'scrollArea_core_specific'):
                    scroll_widget = self.ui.scrollArea_core_specific
                    print("DEBUG: Found scrollArea_core_specific on self.ui")
                else:
                    print("ERROR: scrollArea_core_specific not found on self.ui either")
                    self._initializing_core_details = False
                    return
            
            # Find the contents widget
            contents_widget = scroll_widget.widget()
            if not contents_widget:
                print("DEBUG: scrollArea_core_specific has no widget")
                # Create a new widget for the scroll area
                contents_widget = QtWidgets.QWidget()
                scroll_widget.setWidget(contents_widget)
                print("DEBUG: Created new widget for scrollArea_core_specific")
            
            # If the contents widget already has a layout, use it instead of creating a new one
            layout = contents_widget.layout()
            if not layout:
                print("DEBUG: Contents widget has no layout, creating one")
                layout = QtWidgets.QVBoxLayout(contents_widget)
            else:
                print("DEBUG: Using existing layout from contents widget")
            
            # Clear any existing content in the layout
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
            
            # Create container for core details if it doesn't exist
            if not hasattr(self, 'core_details_container') or not self.core_details_container:
                self.core_details_container = QtWidgets.QWidget(contents_widget)
                print("DEBUG: Created new core_details_container")
                
                # Only create a new layout if we created a new container
                self.core_details_layout = QtWidgets.QVBoxLayout(self.core_details_container)
                self.core_details_layout.setContentsMargins(5, 5, 5, 5)
                print("DEBUG: Created new core_details_layout")
            
            # Add the container to the layout if it's not already there
            if self.core_details_container.parent() != contents_widget:
                layout.addWidget(self.core_details_container)
                print("DEBUG: Added core_details_container to layout")
            
            # Store reference to contents_widget and layout
            self.ui.scrollAreaWidgetContents_core = contents_widget
            self.ui.verticalLayout_cores = layout
            
            # Initial update based on current build type - BUT ONLY IF THIS IS NOT 
            # BEING CALLED FROM update_core_details_view
            if not hasattr(self, '_updating_core_details') or not self._updating_core_details:
                # Get current build type
                build_type = self.signals_data.get("build_type", "SMP")
                
                # Clear existing content
                for i in reversed(range(self.core_details_layout.count())):
                    item = self.core_details_layout.itemAt(i)
                    if item.widget():
                        item.widget().setParent(None)
                
                if build_type == "SMP":
                    self.create_smp_mode_view()
                else:  # MultiImage mode
                    self.create_multiimage_mode_view()
            
            self._initializing_core_details = False
            
        except Exception as e:
            print(f"Error setting up core details section: {e}")
            import traceback
            traceback.print_exc()
            self._initializing_core_details = False

    def update_core_details_view(self):
        """Update the core details view based on current BuildImageType"""
        try:
            # Check if we're recursively calling between setup and update
            if hasattr(self, '_initializing_core_details') and self._initializing_core_details:
                print("DEBUG: Avoiding recursive call to update_core_details_view")
                return
                
            # Set recursion prevention flag
            self._updating_core_details = True
            
            # Check if the core_details_layout exists
            if not hasattr(self, 'core_details_layout') or not self.core_details_layout:
                print("Error: core_details_layout not found or is None - cannot update core details view")
                self._updating_core_details = False
                return
                
            # Get current build type
            build_type = self.signals_data.get("build_type", "SMP")
            
            # Clear existing content
            for i in reversed(range(self.core_details_layout.count())):
                item = self.core_details_layout.itemAt(i)
                if item.widget():
                    item.widget().setParent(None)
            
            if build_type == "SMP":
                self.create_smp_mode_view()
            else:  # MultiImage mode
                self.create_multiimage_mode_view()
            
            self._updating_core_details = False
                
        except Exception as e:
            print(f"Error updating core details view: {e}")
            import traceback
            traceback.print_exc()
            self._updating_core_details = False

    def create_smp_mode_view(self):
        """Create a form view for SMP mode configuration"""
        try:
            # Use the generated SMPSection UI class instead of creating widgets manually
            from Cfg.SMPSection import Ui_SMPSection
            
            # Create a container widget for SMP section
            form_widget = QtWidgets.QWidget()
            
            # Set up UI from the generated class
            self.smp_ui = Ui_SMPSection()
            self.smp_ui.setupUi(form_widget)
            
            # Connect collapse button
            self.smp_ui.collapse_button.clicked.connect(lambda: self.toggle_core_section(form_widget))
            
            # Load existing values into the UI elements
            # Try to get the value from various possible sources in priority order
            
            # Initialize data sources
            project_data = self.signals_data.get("project_specific", {})
            smp_config = project_data.get("smp_config", {})
            
            core_specific_config = {}
            if "core_specific_config" in self.signals_data:
                core_specific_config = self.signals_data["core_specific_config"]
            elif hasattr(self.signals_data, "core_specific_config"):
                core_specific_config = self.signals_data.core_specific_config
            
            # If we don't have any core_specific_config yet, initialize it
            if not core_specific_config and "core_specific_config" not in self.signals_data:
                self.signals_data["core_specific_config"] = {"Global": {}}
                core_specific_config = self.signals_data["core_specific_config"]
            
            # Field mappings
            field_names = {
                "SpinLockAPI": self.smp_ui.lineEdit_SpinLockAPI,
                "SpinUnLockAPI": self.smp_ui.lineEdit_SpinUnLockAPI,
                "SpinLockHeaderFile": self.smp_ui.lineEdit_SpinLockHeaderFile,
                "SemaphoreLockAPI": self.smp_ui.lineEdit_SemaphoreLockAPI,
                "SemaphoreUnLockAPI": self.smp_ui.lineEdit_SemaphoreUnLockAPI,
                "SemaphoreHeaderFile": self.smp_ui.lineEdit_SemaphoreHeaderFile,
                "GetCoreID": self.smp_ui.lineEdit_GetCoreID,
                "GetCoreIDHeaderFile": self.smp_ui.lineEdit_GetCoreIDHeaderFile
            }
            
            # Populate UI fields with values from configs
            for field_name, widget in field_names.items():
                # Try to get value from different sources in order of priority
                value = ""
                
                # 1. Check smp_config in project_specific
                if field_name in smp_config:
                    value = smp_config[field_name]
                
                # 2. Check core_specific_config -> Global
                if not value and "Global" in core_specific_config and field_name in core_specific_config["Global"]:
                    value = core_specific_config["Global"][field_name]
                
                # 3. Check core_specific_config -> SMP 
                if not value and "SMP" in core_specific_config and field_name in core_specific_config["SMP"]:
                    value = core_specific_config["SMP"][field_name]
                
                # Set value to UI field
                if value:
                    widget.setText(value)
                
                # Connect signals
                widget.textChanged.connect(self.save_smp_config)
                
                # Store reference to the new widget in UI (for compatibility)
                setattr(self.ui, f"lineEdit_{field_name}", widget)
            
            # Add the form widget to the container
            self.core_details_layout.addWidget(form_widget)
            
            # Save initial config if we have values
            self.save_smp_config()
            
        except Exception as e:
            print(f"Error creating SMP mode view: {e}")
            import traceback
            traceback.print_exc()
    
    def save_smp_config(self):
        """Save SMP configuration from input fields"""
        try:
            # Check if we have the SMP UI set up
            if not hasattr(self, 'smp_ui'):
                print("SMP UI not initialized, skipping save")
                return
            
            # Define the field names to save
            field_names = {
                "SpinLockAPI": self.smp_ui.lineEdit_SpinLockAPI,
                "SpinUnLockAPI": self.smp_ui.lineEdit_SpinUnLockAPI,
                "SpinLockHeaderFile": self.smp_ui.lineEdit_SpinLockHeaderFile,
                "SemaphoreLockAPI": self.smp_ui.lineEdit_SemaphoreLockAPI,
                "SemaphoreUnLockAPI": self.smp_ui.lineEdit_SemaphoreUnLockAPI,
                "SemaphoreHeaderFile": self.smp_ui.lineEdit_SemaphoreHeaderFile,
                "GetCoreID": self.smp_ui.lineEdit_GetCoreID,
                "GetCoreIDHeaderFile": self.smp_ui.lineEdit_GetCoreIDHeaderFile
            }
            
            # Initialize project_specific if it doesn't exist
            if "project_specific" not in self.signals_data:
                self.signals_data["project_specific"] = {}
            
            # Get or create smp_config
            if "smp_config" not in self.signals_data["project_specific"]:
                self.signals_data["project_specific"]["smp_config"] = {}
            
            smp_config = self.signals_data["project_specific"]["smp_config"]
            
            # Initialize core_specific_config if it doesn't exist
            if "core_specific_config" not in self.signals_data:
                self.signals_data["core_specific_config"] = {}
            
            # Get or create Global section
            if "Global" not in self.signals_data["core_specific_config"]:
                self.signals_data["core_specific_config"]["Global"] = {}
            
            global_config = self.signals_data["core_specific_config"]["Global"]
            
            # Collect values and save to both locations
            has_content = False
            for data_field, widget in field_names.items():
                try:
                    value = widget.text()
                    
                    # Save to smp_config
                    smp_config[data_field] = value
                    
                    # Save to Global section in core_specific_config
                    global_config[data_field] = value
                    
                    # Check if this field has content
                    if value:
                        has_content = True
                        
                except RuntimeError:
                    # Widget has been deleted, skip it
                    print(f"Widget for {data_field} has been deleted, skipping")
            
            # Mark as modified if any field has content
            if has_content:
                self.modified = True
                self.ui_helpers.update_window_title()
            
        except Exception as e:
            print(f"Error saving SMP configuration: {e}")
            import traceback
            traceback.print_exc()

    def create_multiimage_mode_view(self):
        """Create the MultiImage mode view with cores and collapsible sections"""
        try:
            # Create core count controls section
            core_controls = QtWidgets.QWidget(self.core_details_container)
            core_controls_layout = QtWidgets.QHBoxLayout(core_controls)
            core_controls_layout.setContentsMargins(0, 0, 0, 0)
            
            label_core_count = QtWidgets.QLabel("Number of Cores:", core_controls)
            core_controls_layout.addWidget(label_core_count)
            
            # Get existing core count from saved data if available
            default_core_count = 2
            existing_core_info = self.signals_data.get("core_info", {})
            
            # Check if we have nested core data (like "Aurix": {"Core0": {...}, ...})
            if existing_core_info:
                # Find first key that might contain nested cores
                for key, value in existing_core_info.items():
                    if isinstance(value, dict) and any(core.startswith("Core") for core in value.keys()):
                        # We found nested cores
                        nested_cores = value
                        existing_core_count = len(nested_cores)
                        if existing_core_count > 0:
                            default_core_count = existing_core_count
                            print(f"Using existing core count from nested structure: {default_core_count}")
                        break
                else:
                    # No nested structure found, use direct count
                    existing_core_count = len(existing_core_info.keys())
                    if existing_core_count > 0:
                        default_core_count = existing_core_count
                        print(f"Using existing core count: {default_core_count}")
            
            self.ui.spinBox_core_count = QtWidgets.QSpinBox(core_controls)
            self.ui.spinBox_core_count.setMinimum(1)
            self.ui.spinBox_core_count.setMaximum(32)
            self.ui.spinBox_core_count.setValue(default_core_count)
            core_controls_layout.addWidget(self.ui.spinBox_core_count)
            
            # Add button to update cores
            self.ui.update_cores_button = QtWidgets.QPushButton("Update Cores", core_controls)
            self.ui.update_cores_button.clicked.connect(self.update_multicore_sections)
            core_controls_layout.addWidget(self.ui.update_cores_button)
            
            core_controls_layout.addStretch()
            
            # Add core controls to the container
            self.core_details_layout.addWidget(core_controls)
            
            # Create multicore container
            self.multicore_container = QtWidgets.QWidget(self.core_details_container)
            self.verticalLayout_multicore = QtWidgets.QVBoxLayout(self.multicore_container)
            self.verticalLayout_multicore.setContentsMargins(5, 5, 5, 5)
            
            # Store references to these widgets
            self.ui.multicore_container = self.multicore_container
            
            # Add multicore container to the layout
            self.core_details_layout.addWidget(self.multicore_container)
            
            # Reset flag to ensure saved data is used first time
            self._user_changed_core_count = False
            
            # Create initial core sections
            self.update_multicore_sections()
            
            # Update CoreInfo to match if it exists
            self.sync_core_info_with_multi_image()
            
        except Exception as e:
            print(f"Error creating MultiImage mode view: {e}")

    def update_multicore_sections(self):
        """Update the multicore sections based on the core count"""
        try:
            # Check if multicore container exists
            if not hasattr(self, "multicore_container"):
                print("Error: multicore_container not found")
                return
                
            # Clear previous widgets
            for i in reversed(range(self.verticalLayout_multicore.count())):
                item = self.verticalLayout_multicore.itemAt(i)
                if item.widget():
                    item.widget().setParent(None)
            
            # Get the number of cores
            num_cores = self.ui.spinBox_core_count.value()
            cores = [f"Core{i}" for i in range(num_cores)]  # Changed to match Core0 format
            
            # Before creating the UI, check if there's existing core data and adjust UI accordingly
            existing_core_info = self.signals_data.get("core_info", {})
            
            # Check if we have nested core data structure
            is_nested = False
            parent_key = None
            nested_cores = {}
            
            if existing_core_info:
                for key, value in existing_core_info.items():
                    if isinstance(value, dict) and any(core_name.startswith("Core") for core_name in value.keys()):
                        is_nested = True
                        parent_key = key
                        nested_cores = value
                        print(f"Found nested core structure under '{parent_key}' in update_multicore_sections")
                        break
                
                # Only update spinBox_core_count if this is the initial load
                # (Only when we're updating from file load, not from user spinbox change)
                if not hasattr(self, "_user_changed_core_count") or not self._user_changed_core_count:
                    # Get number of cores from the existing data
                    if is_nested:
                        saved_cores = len(nested_cores.keys())
                    else:
                        saved_cores = len(existing_core_info.keys())
                        
                    if saved_cores > num_cores:
                        # Update the UI to reflect the actual saved cores
                        print(f"Adjusting core count from {num_cores} to {saved_cores} based on saved data")
                        self.ui.spinBox_core_count.setValue(saved_cores)
                        num_cores = saved_cores
                        cores = [f"Core{i}" for i in range(num_cores)]  # Changed to match Core0 format
            
            # Set flag for future updates
            self._user_changed_core_count = True
            
            # Create a collapsible section for each core
            for core_name in cores:
                # Create the core section widget
                core_section = QtWidgets.QWidget(self.multicore_container)
                core_section.setObjectName(f"core_section_{core_name}")
                
                # Create main layout for the core section
                core_layout = QtWidgets.QVBoxLayout(core_section)
                core_layout.setContentsMargins(0, 0, 0, 0)
                core_layout.setSpacing(0)
                
                # Create header with expand/collapse button
                header = QtWidgets.QWidget(core_section)
                header.setObjectName(f"header_{core_name}")
                header.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc;")
                
                header_layout = QtWidgets.QHBoxLayout(header)
                header_layout.setContentsMargins(5, 2, 5, 2)  # Reduced margins
                
                # Add toggle button
                toggle_button = QtWidgets.QToolButton(header)
                toggle_button.setObjectName("toggle_button")
                toggle_button.setArrowType(QtCore.Qt.DownArrow)
                toggle_button.setAutoRaise(True)
                header_layout.addWidget(toggle_button)
                
                # Add header label
                label = QtWidgets.QLabel(f"Configuration for {core_name}", header)
                font = label.font()
                font.setBold(True)
                label.setFont(font)
                header_layout.addWidget(label)
                
                # Add spacer
                header_layout.addStretch()
                
                # Create content widget with collapsible content
                content = QtWidgets.QWidget(core_section)
                content.setObjectName("core_content")
                
                # Create form layout for the content
                form_layout = QtWidgets.QFormLayout(content)
                form_layout.setContentsMargins(10, 5, 5, 5)  # Reduced margins
                
                # Add the input fields for each core
                field_pairs = [
                    ("SpinLockAPI", f"spinLockAPI_{core_name}"),
                    ("SpinUnLockAPI", f"spinUnLockAPI_{core_name}"),
                    ("SpinLockHeaderFile", f"spinLockHeaderFile_{core_name}"),
                    ("SemaphoreLockAPI", f"semaphoreLockAPI_{core_name}"),
                    ("SemaphoreUnLockAPI", f"semaphoreUnLockAPI_{core_name}"),
                    ("SemaphoreHeaderFile", f"semaphoreHeaderFile_{core_name}"),
                    ("GetCoreID", f"getCoreID_{core_name}"),
                    ("GetCoreIDHeaderFile", f"getCoreIDHeaderFile_{core_name}")
                ]
                
                for label_text, object_name in field_pairs:
                    # Create label
                    field_label = QtWidgets.QLabel(content)
                    field_label.setText(label_text)
                    
                    # Create line edit
                    line_edit = QtWidgets.QLineEdit(content)
                    line_edit.setObjectName(object_name)
                    
                    # Check for saved values based on structure type
                    if is_nested and parent_key in existing_core_info:
                        # Handle nested structure
                        if core_name in nested_cores and hasattr(nested_cores[core_name], "core_specific_config"):
                            if label_text in nested_cores[core_name].core_specific_config:
                                line_edit.setText(nested_cores[core_name].core_specific_config[label_text])
                    else:
                        # Handle flat structure
                        if hasattr(self.signals_data, "core_specific_config") and core_name in self.signals_data.core_specific_config:
                            if label_text in self.signals_data.core_specific_config[core_name]:
                                line_edit.setText(self.signals_data.core_specific_config[core_name][label_text])
                    
                    # Add to form layout
                    form_layout.addRow(field_label, line_edit)
                
                # Add header and content to the core section
                core_layout.addWidget(header)
                core_layout.addWidget(content)
                
                # Connect toggle button
                toggle_button.clicked.connect(lambda checked, section=core_section: self.toggle_core_section(section))
                
                # Add the core section to the multicore container
                self.verticalLayout_multicore.addWidget(core_section)
            
            # Update CoreInfo to match
            self.sync_core_info_with_multi_image()
                
        except Exception as e:
            print(f"Error updating multicore sections: {e}")
            import traceback
            traceback.print_exc()

    def sync_core_info_with_multi_image(self):
        """Sync CoreInfo with MultiImage core sections"""
        try:
            # Check if we have a signal_tree from UIHelpers
            if not hasattr(self.ui_helpers, 'signal_tree'):
                return
                
            # Get current cores from MultiImage
            num_cores = self.ui.spinBox_core_count.value()
            cores = [f"Core{i}" for i in range(num_cores)]  # Changed to match "Core0" format instead of "Core 0"
            
            # PRESERVE existing core_info data instead of overwriting it
            existing_core_info = self.signals_data.get("core_info", {})
            
            # Check if we have nested core data structure (like "Aurix": {"Core0": {...}, ...})
            is_nested = False
            parent_key = None
            nested_cores = {}
            
            for key, value in existing_core_info.items():
                if isinstance(value, dict) and any(core_name.startswith("Core") for core_name in value.keys()):
                    is_nested = True
                    parent_key = key
                    nested_cores = value
                    print(f"Found nested core structure under '{parent_key}'")
                    break
            
            # Handle based on structure
            if is_nested:
                # If we have a nested structure, keep it and update only the cores
                for core in cores:
                    if core not in nested_cores:
                        nested_cores[core] = {}
            else:
                # For non-nested structure, decide if we need to update
                if not existing_core_info:
                    # If empty, create new structure
                    self.signals_data["core_info"] = {core: {} for core in cores}
                else:
                    # Add any missing cores
                    for core in cores:
                        if core not in existing_core_info:
                            existing_core_info[core] = {}
            
            # Update CoreInfo tree widget if available
            if hasattr(self.ui, 'CoreInfo_2') and isinstance(self.ui.CoreInfo_2, QtWidgets.QScrollArea):
                # Check if there's an existing tree widget
                tree = None
                if self.ui.CoreInfo_2.widget() and isinstance(self.ui.CoreInfo_2.widget(), QtWidgets.QTreeWidget):
                    tree = self.ui.CoreInfo_2.widget()
                else:
                    # Create a new tree widget
                    tree = QtWidgets.QTreeWidget()
                    tree.setHeaderHidden(True)
                    self.ui.CoreInfo_2.setWidget(tree)
                
                # Clear the tree
                tree.clear()
                
                # For nested structure, create a parent node first
                if is_nested:
                    parent_item = QtWidgets.QTreeWidgetItem([parent_key])
                    tree.addTopLevelItem(parent_item)
                    
                    # Add cores under the parent
                    for core in cores:
                        core_data = nested_cores.get(core, {})
                        core_item = QtWidgets.QTreeWidgetItem([core])
                        parent_item.addChild(core_item)
                        
                        # Add properties to the core
                        if core_data:
                            # Default properties if not present in saved data
                            properties = {
                                "OS": core_data.get("os", "Unknown"),
                                "SOC Family": core_data.get("soc_family", "Unknown"),
                                "Master/Slave": "Master" if core_data.get("is_master", False) else "Slave",
                                "Autosar Compatible": "Yes" if core_data.get("is_autosar", False) else "No",
                                "QNX Core": "Yes" if core_data.get("is_qnx", False) else "No",
                                "Simulation Core": "Yes" if core_data.get("is_sim", False) else "No"
                            }
                            
                            # Add each property to the tree
                            for prop_name, prop_value in properties.items():
                                prop_item = QtWidgets.QTreeWidgetItem([f"{prop_name}: {prop_value}"])
                                core_item.addChild(prop_item)
                else:
                    # For flat structure, add cores directly to the tree
                    for core in cores:
                        core_item = QtWidgets.QTreeWidgetItem([core])
                        tree.addTopLevelItem(core_item)
                        
                        # Get core properties from the core_info data
                        core_data = existing_core_info.get(core, {})
                        
                        # If the core has detailed properties (from file), use those
                        if core_data:
                            # Default properties if not present in saved data
                            properties = {
                                "OS": core_data.get("os", "Unknown"),
                                "SOC Family": core_data.get("soc_family", "Unknown"),
                                "Master/Slave": "Master" if core_data.get("is_master", False) else "Slave",
                                "Autosar Compatible": "Yes" if core_data.get("is_autosar", False) else "No",
                                "QNX Core": "Yes" if core_data.get("is_qnx", False) else "No",
                                "Simulation Core": "Yes" if core_data.get("is_sim", False) else "No"
                            }
                            
                            # Add each property to the tree
                            for prop_name, prop_value in properties.items():
                                prop_item = QtWidgets.QTreeWidgetItem([f"{prop_name}: {prop_value}"])
                                core_item.addChild(prop_item)
                                
                # Expand the tree for better visibility
                tree.expandAll()
            
        except Exception as e:
            print(f"Error syncing CoreInfo with MultiImage: {e}")

    def toggle_core_section(self, core_section):
        """Toggle visibility of a specific core section's content"""
        try:
            # Get content widget and toggle button
            content = core_section.findChild(QtWidgets.QWidget, "core_content")
            toggle_button = core_section.findChild(QtWidgets.QToolButton, "toggle_button")
            
            if not content or not toggle_button:
                return
                
            # Toggle visibility
            is_visible = content.isVisible()
            content.setVisible(not is_visible)
            
            # Update button arrow
            toggle_button.setArrowType(
                QtCore.Qt.RightArrow if is_visible else QtCore.Qt.DownArrow
            )
            
        except Exception as e:
            print(f"Error toggling core section: {e}")

    def connect_project_specific_buttons(self):
        """Connect Project Specific Config tab related buttons"""
        try:
            # Connect directory browse buttons
            if hasattr(self.ui, 'pushButton_browse_output'):
                self.ui.pushButton_browse_output.clicked.connect(self.browse_output_dir)
            elif hasattr(self.ui, 'OutputPathButton'):
                self.ui.OutputPathButton.clicked.connect(self.browse_output_dir)
                
            if hasattr(self.ui, 'pushButton_browse_scripts'):
                self.ui.pushButton_browse_scripts.clicked.connect(self.browse_scripts_dir)
            elif hasattr(self.ui, 'ScriptPathButton'):
                self.ui.ScriptPathButton.clicked.connect(self.browse_scripts_dir)
            
        except Exception as e:
            print(f"Error connecting Project Specific Config buttons: {e}")

    def browse_output_dir(self):
        """Handle browse output directory button click"""
        try:
            directory = QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select Output Directory", os.path.expanduser("~"),
                QtWidgets.QFileDialog.ShowDirsOnly
            )
            
            if directory:
                if hasattr(self.ui, 'lineEdit_output_dir'):
                    self.ui.lineEdit_output_dir.setText(directory)
                elif hasattr(self.ui, 'OutputPathLineEdit'):
                    self.ui.OutputPathLineEdit.setText(directory)
                
                # Mark as modified
                self.modified = True
                self.ui_helpers.update_window_title()
                
        except Exception as e:
            print(f"Error browsing output directory: {e}")

    def browse_scripts_dir(self):
        """Handle browse scripts directory button click"""
        try:
            directory = QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select Scripts Directory", os.path.expanduser("~"),
                QtWidgets.QFileDialog.ShowDirsOnly
            )
            
            if directory:
                if hasattr(self.ui, 'lineEdit_scripts_dir'):
                    self.ui.lineEdit_scripts_dir.setText(directory)
                elif hasattr(self.ui, 'ScriptPathLineEdit'):
                    self.ui.ScriptPathLineEdit.setText(directory)
                
                # Mark as modified
                self.modified = True
                self.ui_helpers.update_window_title()
                
        except Exception as e:
            print(f"Error browsing scripts directory: {e}")

    def create_collapsible_sections(self):
        """Create collapsible sections for input groups (legacy method for compatibility)"""
        # For backward compatibility, this now calls update_core_details_view
        self.update_core_details_view()

    def update_multicore_inputs(self):
        """Update multicore inputs (legacy method for compatibility)"""
        # For backward compatibility, this now calls update_multicore_sections
        self.update_multicore_sections()

    def initialize_project_specific_config(self):
        """Initialize the complete project specific configuration tab (called after file operations)"""
        try:
            print("Initializing Project Specific Config after file operation...")
            
            # Reset the user_changed_core_count flag before initialization
            self._user_changed_core_count = False
            
            # First make sure basic config is initialized
            self.initialize_basic_project_config()
            
            # Enable the config inputs if we have a file open
            self.set_project_specific_config_enabled(self.current_file is not None)
            
            # Find the scroll area
            scroll_widget = self.findChild(QtWidgets.QScrollArea, "scrollArea_core_specific")
            if not scroll_widget:
                print("ERROR: scrollArea_core_specific not found")
                return
                
            # Create a fresh widget for the scroll area
            contents_widget = QtWidgets.QWidget()
            scroll_widget.setWidget(contents_widget)
            
            # Create a fresh layout
            main_layout = QtWidgets.QVBoxLayout(contents_widget)
            
            # Create container widget
            self.core_details_container = QtWidgets.QWidget(contents_widget)
            self.core_details_layout = QtWidgets.QVBoxLayout(self.core_details_container)
            self.core_details_layout.setContentsMargins(5, 5, 5, 5)
            
            # Add container to the main layout
            main_layout.addWidget(self.core_details_container)
            
            # Store references
            self.ui.scrollAreaWidgetContents_core = contents_widget
            self.ui.verticalLayout_cores = main_layout
            
            # Now update with the appropriate view based on build type
            build_type = self.signals_data.get("build_type", "SMP")
            
            # Log existing core data for debugging
            core_info = self.signals_data.get("core_info", {})
            if core_info:
                # Check if we have a nested structure
                for key, value in core_info.items():
                    if isinstance(value, dict) and any(core_name.startswith("Core") for core_name in value.keys()):
                        print(f"Found existing NESTED core data under '{key}' with {len(value)} cores")
                        for core_name, core_data in value.items():
                            print(f"  - {core_name}: {core_data}")
                        break
                else:
                    # No nested structure
                    print(f"Found existing FLAT core data with {len(core_info)} cores")
                    for core_name, core_data in core_info.items():
                        print(f"  - {core_name}: {core_data}")
            
            # Clear any existing UI element references that might be stale
            # This is important to prevent accessing deleted Qt objects
            for field_name in [
                "lineEdit_SpinLockAPI", "lineEdit_SpinUnLockAPI", "lineEdit_SpinLockHeaderFile",
                "lineEdit_SemaphoreLockAPI", "lineEdit_SemaphoreUnLockAPI", "lineEdit_SemaphoreHeaderFile",
                "lineEdit_GetCoreID", "lineEdit_GetCoreIDHeaderFile"
            ]:
                if hasattr(self.ui, field_name):
                    delattr(self.ui, field_name)
            
            # Create the appropriate view
            try:
                if build_type == "SMP":
                    self.create_smp_mode_view()
                else:
                    # Make sure we use saved core count by resetting the flag
                    self._user_changed_core_count = False
                    self.create_multiimage_mode_view()
            except Exception as view_error:
                # If we fail to create the view, create a fallback view with a message
                print(f"Error creating {build_type} view: {view_error}")
                fallback_widget = QtWidgets.QLabel(self.core_details_container)
                fallback_widget.setText(f"Error loading {build_type} configuration. Please check the console for details.")
                fallback_widget.setStyleSheet("color: red;")
                self.core_details_layout.addWidget(fallback_widget)
                
                # Make sure to clear the layout first
                for i in reversed(range(self.core_details_layout.count())):
                    item = self.core_details_layout.itemAt(i)
                    if item.widget() != fallback_widget:  # Don't remove our fallback widget
                        widget = item.widget()
                        if widget:
                            widget.setParent(None)
                
                import traceback
                traceback.print_exc()
                
            print("Project Specific Config initialization completed successfully")
                
        except Exception as e:
            print(f"Error initializing project specific config: {e}")
            import traceback
            traceback.print_exc()

    def ensure_menu_actions_enabled(self):
        """Ensure all menu actions are visible and enabled"""
        try:
            # Set menu bar properties once
            menu_bar = self.menuBar()
            menu_bar.setVisible(True)
            menu_bar.setEnabled(True)
            
            # Process all menus at once rather than individual checks
            menu_actions = {
                "menuFile": "File",
                "menuEdit": "Edit",
                "menuCode_Generator": "Code Generator",
                "menuHelp": "Help"
            }
            
            # Pre-check which menus exist to avoid hasattr calls in loops
            existing_menus = {}
            for menu_name in menu_actions:
                if hasattr(self.ui, menu_name):
                    existing_menus[menu_name] = getattr(self.ui, menu_name)
            
            # Set properties for existing menus
            for menu_name, menu in existing_menus.items():
                menu.setTitle(menu_actions[menu_name])
                menu.setVisible(True)
                menu.setEnabled(True)
                menu_action = menu.menuAction()
                menu_action.setVisible(True)
                menu_action.setEnabled(True)
                
                # Enable all actions in this menu
                for action in menu.actions():
                    action.setVisible(True)
                    action.setEnabled(True)
            
        except Exception as e:
            print(f"Error enabling menu actions: {e}")

    def _setup_toolbar_icons(self):
        """Fix and set up toolbox/toolbar button icons"""
        try:
            # Get the base icon directory path
            icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Cfg", "Icons")
            
            # Fixed mapping of action/button types to correct icon file names
            icon_mapping = {
                "new": "NewFile.png",
                "open": "OpenFile.png", 
                "save": "Save.png",
                "save_as": "SaveAs.png",
                "export": "ExportToExcel.png",
                "import": "Import.png",
                "close": "Close.png",
                "add": "AddEntry.png",
                "delete": "RemoveEntry.png",
                "update": "UpdateEntry.png",
                "copy": "Copy.png",
                "paste": "Paste.png",
                "undo": "Undo.png",
                "redo": "Redo.png"
            }
            
            # Check for main toolbar
            main_toolbar = self.findChild(QtWidgets.QToolBar, "mainToolBar")
            
            # If mainToolBar exists, set up icons for each action on it
            if main_toolbar:
                print("Setting up main toolbar icons")
                
                # Apply icons to each toolbar action
                for action in main_toolbar.actions():
                    action_name = action.objectName().lower()
                    
                    # Skip separators
                    if not action_name:
                        continue
                        
                    # Find matching icon in our mapping
                    for key, icon_file in icon_mapping.items():
                        if key in action_name:
                            # Use cached icon if available
                            if hasattr(self, "_icon_cache") and icon_file in self._icon_cache:
                                action.setIcon(self._icon_cache[icon_file])
                                print(f"Set icon for toolbar action {action_name} from cache")
                            else:
                                # Load from file
                                icon_path = os.path.join(icon_dir, icon_file)
                                if os.path.exists(icon_path):
                                    icon = QtGui.QIcon(icon_path)
                                    if not icon.isNull():
                                        action.setIcon(icon)
                                        print(f"Set icon for toolbar action {action_name} from {icon_path}")
                                    else:
                                        print(f"Warning: Failed to create icon from {icon_path}")
                                else:
                                    print(f"Warning: Icon file not found: {icon_path}")
                            break
            
            # Find all toolboxes/toolbars in the UI
            all_toolbars = self.findChildren(QtWidgets.QToolBar)
            all_toolbuttons = self.findChildren(QtWidgets.QToolButton)
            
            print(f"Found {len(all_toolbars)} toolbars and {len(all_toolbuttons)} toolbuttons")
            
            # Apply icons to all toolbuttons
            for button in all_toolbuttons:
                button_name = button.objectName().lower()
                
                # Skip special buttons
                if "toggle_button" in button_name:
                    continue
                    
                # Try to match button name to an icon
                for key, icon_file in icon_mapping.items():
                    if key in button_name:
                        # Use cached icon if available
                        if hasattr(self, "_icon_cache") and icon_file in self._icon_cache:
                            button.setIcon(self._icon_cache[icon_file])
                            print(f"Set icon for button {button_name} from cache")
                        else:
                            # Load from file
                            icon_path = os.path.join(icon_dir, icon_file)
                            if os.path.exists(icon_path):
                                icon = QtGui.QIcon(icon_path)
                                if not icon.isNull():
                                    button.setIcon(icon)
                                    print(f"Set icon for button {button_name} from {icon_path}")
                                else:
                                    print(f"Warning: Failed to create icon from {icon_path}")
                            else:
                                print(f"Warning: Icon file not found: {icon_path}")
                        break
                        
            # Also check for buttons in SignalOpFrame
            if hasattr(self.ui, "SignalOpFrame"):
                # Signal operation buttons with correct icon mapping
                button_mappings = {
                    "SaveButton": "Save.png",
                    "UndoButton": "Undo.png",
                    "RedoButton": "Redo.png",
                    "UpdateConfig": "UpdateEntry.png"
                }
                
                for button_name, icon_file in button_mappings.items():
                    # Try both with and without _2 suffix
                    for btn_variant in [button_name, f"{button_name}_2"]:
                        if hasattr(self.ui, btn_variant):
                            button = getattr(self.ui, btn_variant)
                            
                            # Use cached icon if available
                            if hasattr(self, "_icon_cache") and icon_file in self._icon_cache:
                                button.setIcon(self._icon_cache[icon_file])
                                print(f"Set icon for {btn_variant} from cache")
                            else:
                                # Load from file
                                icon_path = os.path.join(icon_dir, icon_file)
                                if os.path.exists(icon_path):
                                    icon = QtGui.QIcon(icon_path)
                                    if not icon.isNull():
                                        button.setIcon(icon)
                                        print(f"Set icon for {btn_variant} from {icon_path}")
                                    else:
                                        print(f"Warning: Failed to create icon from {icon_path}")
                                else:
                                    print(f"Warning: Icon file not found: {icon_path}")
                                    
        except Exception as e:
            print(f"Error setting up toolbar icons: {e}")
            import traceback
            traceback.print_exc()

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Force-reload resources
    import importlib
    try:
        import Cfg.signalmgrapp_rc
        importlib.reload(Cfg.signalmgrapp_rc)
        print("Successfully loaded resource module")
    except Exception as e:
        print(f"Error loading resources: {e}")
    
    # Optimize performance for menus
    app.setAttribute(QtCore.Qt.AA_DontUseNativeMenuBar, True)
    
    # Set application style for better performance
    app.setStyle("Fusion")  # Use Fusion style for consistent cross-platform appearance and better performance
    
    # Pre-load and cache QPixmap instances (shared between icons)
    QtGui.QPixmapCache.setCacheLimit(10240)  # Increase cache size (in KB)
    
    # Additional settings for improved menu performance
    app.processEvents()  # Process any pending events before showing window
    
    # Disable effects that can slow down menu display
    if hasattr(QtWidgets.QApplication, 'setEffectEnabled'):
        for effect in [QtCore.Qt.UI_AnimateMenu, QtCore.Qt.UI_FadeMenu, 
                      QtCore.Qt.UI_AnimateCombo, QtCore.Qt.UI_AnimateTooltip]:
            app.setEffectEnabled(effect, False)
    
    window = SignalMgrApp()
    window.show()
    
    # Process events again after show to ensure UI is fully loaded
    app.processEvents()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()