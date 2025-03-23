#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import json
import time
import traceback
from pathlib import Path

# Add the parent directory to the path so modules can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def get_platform_path(path_components):
    """
    Create platform-specific paths from components.
    This ensures paths work correctly on both Windows and Linux.

    Args:
        path_components (list): List of path components to join

    Returns:
        str: Platform-specific path
    """
    return os.path.join(*path_components)

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QAction, QMenu, QGroupBox
from PyQt5.QtGui import QIcon
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

        # Explicitly initialize SignalAttributeSection to None
        self.ui.SignalAttributeSection = None

        # Performance optimization: Preload menu resources to avoid delays
        self._preload_menu_resources()

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

        # Initialize modules
        self.file_ops = FileOperations(self)
        self.signal_ops = SignalOperations(self)
        self.code_gen = CodeGeneration(self)
        self.ui_helpers = UIHelpers(self)

        # Clear default "Enter Your Name" text before setting up connections
        if hasattr(self.ui, "EditorName"):
            self.ui.EditorName.setPlaceholderText("Enter your name")
            self.ui.EditorName.setPlainText("")  # Clear text to show placeholder
        elif hasattr(self.ui, "VersionUpdateName"):
            self.ui.VersionUpdateName.setPlaceholderText("Enter your name")
            self.ui.VersionUpdateName.setPlainText("")  # Clear text to show placeholder

        # Connect UI elements to their respective functions
        self.setup_connections()

        # Setup tree widget for signal display
        self.ui_helpers.setup_tree_widget()

        # By Default make API Configuration empty
        self.ui_helpers.clear_api_configuration()

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

    def _preload_menu_resources(self):
        """Preload menu resources for better performance with cross-platform support"""
        try:
            # Get the base icon directory path using platform-agnostic path handling
            icon_dir = get_platform_path([os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Cfg", "Icons"])
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

                # First try loading directly from file path
                if os.path.exists(icon_path):
                    # Create icon directly from file
                    icon = QtGui.QIcon(icon_path)
                    if not icon.isNull():
                        self._icon_cache[action_name] = icon
                        self._icon_cache[icon_file] = icon  # Also store by filename
                        print(f"Successfully loaded icon: {action_name} from {icon_path}")
                    else:
                        print(f"Warning: Failed to create icon from {icon_path}")
                        # Try using resource path as fallback
                        resource_path = f":/icons/{icon_file}"
                        icon = QtGui.QIcon(resource_path)
                        if not icon.isNull():
                            self._icon_cache[action_name] = icon
                            self._icon_cache[icon_file] = icon
                            print(f"Successfully loaded icon: {action_name} from resource {resource_path}")
                else:
                    print(f"Warning: Icon file not found: {icon_path}")
                    # Try using resource path as fallback
                    resource_path = f":/icons/{icon_file}"
                    icon = QtGui.QIcon(resource_path)
                    if not icon.isNull():
                        self._icon_cache[action_name] = icon
                        self._icon_cache[icon_file] = icon
                        print(f"Successfully loaded icon: {action_name} from resource {resource_path}")

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
        icon_dir = get_platform_path([os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Cfg", "Icons"])

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
            "actionCut_Entry": "Cut.png",
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
        """if not hasattr(self.ui, "SignalOpFrame"):
            # Create a placeholder frame if needed for compatibility
            self.ui.SignalOpFrame = QtWidgets.QFrame(self) """

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
            #self._setup_toolbar_icons()

            # Disconnect any existing connections to prevent duplicate triggers
            #self._disconnect_existing_actions()

            # Print menu debug info
            #self._debug_menu_structure()

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
            cut_signal_func = self.signal_ops.cut_signal
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
                ("actionCut_Entry", cut_signal_func),
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
            #self._setup_signal_tracing()

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
                            connections = len(action.receivers(action.triggered))
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
            # Get the action by name
            if hasattr(self.ui, action_name):
                action = getattr(self.ui, action_name)
            else:
                # Look for alternate names with underscore variations
                alternate_names = [
                    action_name,
                    action_name.replace('_', ''),
                    'action' + action_name,
                    'action' + action_name.replace('_', ''),
                    'action' + action_name[0].upper() + action_name[1:].replace('_', ''),
                    'action' + action_name[0].upper() + action_name[1:],
                    'action' + ''.join(word.capitalize() for word in action_name.split('_'))
                ]

                # Try to find the action with any of the name variations
                for name in alternate_names:
                    if hasattr(self.ui, name):
                        action = getattr(self.ui, name)
                        action_name = name  # Use the actual name that was found
                        break
                else:
                    print(f"Could not find action {action_name} with any naming variation")
                    return False

            # Make sure the object is a QAction
            if not isinstance(action, QAction):
                print(f"{action_name} is not a QAction")
                return False

            try:
                # Disconnect any existing signals to prevent duplicates
                try:
                    action.triggered.disconnect()
                except:
                    pass

                # Connect the function directly to the triggered signal
                action.triggered.connect(func)

                # Make sure the action is visible
                action.setVisible(True)

                # Check if this is a paste action - if so, disable it by default
                if 'paste' in action_name.lower():
                    action.setEnabled(False)
                    print(f"Paste action {action_name} set to disabled by default")
                else:
                    if 'cut' in action_name.lower():
                        action.setEnabled(False)
                        print(f"Cut action {action_name} set to disabled by default for this version")
                    else:
                        action.setEnabled(True)

                # Make sure the action has an icon if available
                # Check if we have an icon for this action type
                action_type = action_name.lower().replace('action', '').replace('_', '')
                for key in ["new", "open", "save", "save_as", "export", "import", "close",
                           "add", "delete", "update", "copy", "paste", "undo", "redo",
                           "about", "license", "exit"]:
                    if key in action_type:
                        # Try to set an icon if we have one cached
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
                            "redo": "Redo.png",
                            "about": "About.png",
                            "license": "License.png",
                            "exit": "Exit.png"
                        }
                        if key in icon_mapping and hasattr(self, "_icon_cache"):
                            icon_file = icon_mapping[key]
                            if icon_file in self._icon_cache:
                                action.setIcon(self._icon_cache[icon_file])
                        break

                return True
            except Exception as e:
                print(f"Error connecting action {action_name}: {e}")
                return False
        except Exception as e:
            print(f"Error in _connect_action for {action_name}: {e}")
            return False

    def _connect_remaining_ui_elements(self):
        """Connect non-menu UI elements like buttons, combo boxes, etc."""
        try:
            # Connect buttons
            if hasattr(self.ui, "SaveButton_2"):
                self.ui.SaveButton_2.clicked.connect(self.file_ops.save_file)
            elif hasattr(self.ui, "Soc_CoreInfoUpdatedButton"):
                self.ui.Soc_CoreInfoUpdatedButton.clicked.connect(self.signal_ops.open_configuration_manager)

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

            # Fix the SignalDetailsFrame - handle the typo in the name "SiganlDetailsFrame"
            if hasattr(self.ui, "SiganlDetailsFrame"):  # Note the typo in original code "Siganl"
                # Hide the redundant label but leave it in place to avoid core dumps
                label = self.ui.SiganlDetailsFrame.findChild(QtWidgets.QLabel, "label_2")
                if label:
                    label.setVisible(False)
                    print("Hidden unnecessary Signal Attribute label")

                # Ensure the SignalAttributeSection is created during initialization
                if hasattr(self.ui_helpers, "setup_signal_attribute_section"):
                    scroll_area = self.ui_helpers.setup_signal_attribute_section(self.ui.SiganlDetailsFrame)
                    # Store direct reference to ensure it's accessible
                    if scroll_area:
                        self.ui.SignalAttributeSection = scroll_area
                        print("Set up Signal Attribute Section successfully")
                else:
                    print("Warning: setup_signal_attribute_section not found in ui_helpers")

            print("Connected remaining UI elements")

        except Exception as e:
            print(f"Error connecting remaining UI elements: {e}")
            import traceback
            traceback.print_exc()

    def build_type_changed(self, index):
        """Handle build type change and update core details view"""
        try:
            # First let the UIHelpers handle the basic build type changed event
            self.ui_helpers.build_type_changed(index)

            # No longer updating core_details_view since we're removing that functionality
            # Previous code:
            # if hasattr(self, 'core_details_layout') and self.core_details_layout:
            #     self.update_core_details_view()
            # else:
            #     print("Note: core_details_layout not available yet - skipping update")
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
        try:
            print("Open file operation starting")
            # Ensure SiganlDetailsFrame and SignalAttributeSection are initialized
            """ if hasattr(self.ui, "SiganlDetailsFrame"):
                # Set up AttributeSection before opening the file to ensure it exists
                if not hasattr(self.ui, "SignalAttributeSection") or self.ui.SignalAttributeSection is None:
                    if hasattr(self.ui_helpers, "setup_signal_attribute_section"):
                        print("Creating SignalAttributeSection before file open")
                        scroll_area = self.ui_helpers.setup_signal_attribute_section(self.ui.SiganlDetailsFrame)
                        if scroll_area:
                            self.ui.SignalAttributeSection = scroll_area
                            print("SignalAttributeSection successfully created") """

            # Process UI events before opening file to ensure UI is ready
            QtWidgets.QApplication.processEvents()

            # Now open the file
            result = self.file_ops.open_file()

            if result:
                try:
                    # Initialize Project Specific Config after successful file open
                    self.initialize_project_specific_config()
                    print("Project specific config initialization completed")
                except Exception as e:
                    print(f"Warning: Error in project config initialization: {e}")
                    traceback.print_exc()

            return result
        except Exception as e:
            print(f"Error in open_file_wrapper: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
            return False

    def create_file_wrapper(self):
        """Wrapper for create_new_file to handle the menu action"""
        try:
            print("Starting create new file operation")
            # Ensure SiganlDetailsFrame and SignalAttributeSection are initialized
            """ if hasattr(self.ui, "SiganlDetailsFrame"):
                # Set up AttributeSection before creating the file to ensure it exists
                if not hasattr(self.ui, "SignalAttributeSection") or self.ui.SignalAttributeSection is None:
                    if hasattr(self.ui_helpers, "setup_signal_attribute_section"):
                        print("Creating SignalAttributeSection before file creation")
                        scroll_area = self.ui_helpers.setup_signal_attribute_section(self.ui.SiganlDetailsFrame)
                        if scroll_area:
                            self.ui.SignalAttributeSection = scroll_area
                            print("SignalAttributeSection successfully created") """

            # Process UI events before file creation
            QtWidgets.QApplication.processEvents()

            # Create the new file
            result = self.file_ops.create_new_file()

            if result:
                # Initialize Project Specific Config after file creation
                self.initialize_project_specific_config()
                print("Project specific config initialized after file creation")

            return result
        except Exception as e:
            print(f"Error in create_file_wrapper: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to create new file: {str(e)}")
            return False

    def import_excel_wrapper(self):
        """Wrapper for import_from_excel to handle the menu action"""
        try:
            print("Starting import from Excel operation")
            # Ensure SiganlDetailsFrame and SignalAttributeSection are initialized
            if hasattr(self.ui, "SiganlDetailsFrame"):
                # Set up AttributeSection before importing to ensure it exists
                if not hasattr(self.ui, "SignalAttributeSection") or self.ui.SignalAttributeSection is None:
                    if hasattr(self.ui_helpers, "setup_signal_attribute_section"):
                        print("Creating SignalAttributeSection before Excel import")
                        scroll_area = self.ui_helpers.setup_signal_attribute_section(self.ui.SiganlDetailsFrame)
                        if scroll_area:
                            self.ui.SignalAttributeSection = scroll_area
                            print("SignalAttributeSection successfully created")

            # Process UI events before importing
            QtWidgets.QApplication.processEvents()

            # Import from Excel
            result = self.file_ops.import_from_excel()

            if result:
                # Initialize Project Specific Config after import
                self.initialize_project_specific_config()
                print("Project specific config initialized after Excel import")

            return result
        except Exception as e:
            print(f"Error in import_excel_wrapper: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to import from Excel: {str(e)}")
            return False

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
            #self.set_project_specific_config_enabled(False)

            # Instead, ensure just the path fields are enabled:
            self.ensure_path_fields_enabled()

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

            # Removed references to core_details_container
            if hasattr(self, 'core_details_container'):
                self.core_details_container.setEnabled(enabled)

        except Exception as e:
            print(f"Error setting Project Specific Config enabled state: {e}")

    def add_expand_collapse_buttons(self):
        """Set up the core specific details section"""
        try:
            # Removed call to setup_core_details_section
            pass
        except Exception as e:
            print(f"Error setting up core specific details: {e}")

    def setup_core_details_section(self):
        """Create a dynamic core details section that updates based on BuildImageType"""
        # This entire method is no longer needed - leaving as stub for compatibility
        try:
            print("WARNING: setup_core_details_section called, but this functionality has been removed")
            return
        except Exception as e:
            print(f"Error in setup_core_details_section: {e}")

    def update_core_details_view(self):
        """Update the core details view based on current BuildImageType"""
        # This entire method is no longer needed - leaving as stub for compatibility
        try:
            print("WARNING: update_core_details_view called, but this functionality has been removed")
            return
        except Exception as e:
            print(f"Error in update_core_details_view: {e}")

    def create_smp_mode_view(self):
        """Create a form view for SMP mode configuration"""
        # This entire method is no longer needed - leaving as stub for compatibility
        try:
            print("WARNING: create_smp_mode_view called, but this functionality has been removed")
            return
        except Exception as e:
            print(f"Error in create_smp_mode_view: {e}")

    def save_smp_config(self):
        """Save SMP configuration from input fields"""
        try:
            # Only keep core data structure initialization and skip UI operations
            # Initialize project_specific if it doesn't exist
            if "project_specific" not in self.signals_data:
                self.signals_data["project_specific"] = {}

            # Get or create smp_config
            if "smp_config" not in self.signals_data["project_specific"]:
                self.signals_data["project_specific"]["smp_config"] = {}

            # Initialize core_specific_config if it doesn't exist
            if "core_specific_config" not in self.signals_data:
                self.signals_data["core_specific_config"] = {}

            # Get or create Global section
            if "Global" not in self.signals_data["core_specific_config"]:
                self.signals_data["core_specific_config"]["Global"] = {}

        except Exception as e:
            print(f"Error saving SMP configuration: {e}")

    def create_multiimage_mode_view(self):
        """Create the MultiImage mode view with cores and collapsible sections"""
        # This entire method is no longer needed - leaving as stub for compatibility
        try:
            print("WARNING: create_multiimage_mode_view called, but this functionality has been removed")
            return
        except Exception as e:
            print(f"Error in create_multiimage_mode_view: {e}")

    def update_multicore_sections(self):
        """Update the multicore sections based on the core count"""
        # This entire method is no longer needed - leaving as stub for compatibility
        try:
            print("WARNING: update_multicore_sections called, but this functionality has been removed")

            # Only keep the core data sync functionality, without UI operations
            self.sync_core_info_with_multi_image()

        except Exception as e:
            print(f"Error in update_multicore_sections: {e}")

    def sync_core_info_with_multi_image(self):
        """Sync CoreInfo with MultiImage core sections"""
        try:
            # Check if we have a signal_tree from UIHelpers
            if not hasattr(self.ui_helpers, 'signal_tree'):
                return

            # Get current cores - if we have spinBox_core_count
            num_cores = 0
            if hasattr(self.ui, 'spinBox_core_count'):
                num_cores = self.ui.spinBox_core_count.value()
            else:
                # Default to 2 cores if no UI element
                num_cores = 2

            cores = [f"Core{i}" for i in range(num_cores)]

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

            # Update CoreInfo tree widget if available - keep this part
            # ...existing code...

        except Exception as e:
            print(f"Error syncing CoreInfo with MultiImage: {e}")

    def toggle_core_section(self, core_section):
        """Toggle visibility of a specific core section's content"""
        # This entire method is no longer needed - leaving as stub for compatibility
        try:
            print("WARNING: toggle_core_section called, but this functionality has been removed")
            return
        except Exception as e:
            print(f"Error in toggle_core_section: {e}")

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

                # Save paths to data structure
                self.ui_helpers.save_paths()

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

                # Save paths to data structure
                self.ui_helpers.save_paths()

                # Mark as modified
                self.modified = True
                self.ui_helpers.update_window_title()

        except Exception as e:
            print(f"Error browsing scripts directory: {e}")

    def create_collapsible_sections(self):
        """Create collapsible sections for input groups (legacy method for compatibility)"""
        # For backward compatibility, just return without doing anything
        return

    def update_multicore_inputs(self):
        """Update multicore inputs (legacy method for compatibility)"""
        # For backward compatibility, just return without doing anything
        return

    def initialize_project_specific_config(self):
        """Initialize the complete project specific configuration tab (called after file operations)"""
        try:
            print("Initializing Project Specific Config after file operation...")

            # Load paths if available
            if "project_specific" in self.signals_data and "paths" in self.signals_data["project_specific"]:
                paths = self.signals_data["project_specific"]["paths"]

                # Set output path
                if "output_path" in paths:
                    if hasattr(self.ui, 'lineEdit_output_dir'):
                        self.ui.lineEdit_output_dir.setText(paths["output_path"])
                    elif hasattr(self.ui, 'OutputPathLineEdit'):
                        self.ui.OutputPathLineEdit.setText(paths["output_path"])

                # Set script path
                if "script_path" in paths:
                    if hasattr(self.ui, 'lineEdit_scripts_dir'):
                        self.ui.lineEdit_scripts_dir.setText(paths["script_path"])
                    elif hasattr(self.ui, 'ScriptPathLineEdit'):
                        self.ui.ScriptPathLineEdit.setText(paths["script_path"])

            # Update API configuration
            self.ui_helpers.update_api_configuration()

            # Ensure path fields are enabled
            self.ensure_path_fields_enabled()

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
            # Process events before icon setup
            QtWidgets.QApplication.processEvents()

            # Get the base icon directory path
            icon_dir = get_platform_path([os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Cfg", "Icons"])

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

            # Create an icon cache if it doesn't exist
            if not hasattr(self, "_icon_cache"):
                self._icon_cache = {}

            # Preload all icons into the cache
            for icon_name, icon_file in icon_mapping.items():
                try:
                    icon_path = os.path.join(icon_dir, icon_file)
                    if os.path.exists(icon_path):
                        icon = QtGui.QIcon(icon_path)
                        if not icon.isNull():
                            self._icon_cache[icon_file] = icon
                            print(f"Cached icon {icon_file}")
                        else:
                            print(f"Warning: Failed to create icon from {icon_path}")
                    else:
                        print(f"Warning: Icon file not found: {icon_path}")
                except Exception as e:
                    print(f"Error caching icon {icon_file}: {e}")

            # Process events after caching icons
            QtWidgets.QApplication.processEvents()

            # Check for main toolbar
            try:
                main_toolbar = self.findChild(QtWidgets.QToolBar, "mainToolBar")

                # If mainToolBar exists, set up icons for each action on it
                if main_toolbar:
                    print("Setting up main toolbar icons")

                    # Apply icons to each toolbar action
                    action_count = 0
                    for action in main_toolbar.actions():
                        try:
                            action_name = action.objectName().lower()

                            # Skip separators
                            if not action_name:
                                continue

                            # Find matching icon in our mapping
                            for key, icon_file in icon_mapping.items():
                                if key in action_name:
                                    # Use cached icon if available
                                    if icon_file in self._icon_cache:
                                        action.setIcon(self._icon_cache[icon_file])
                                        print(f"Set icon for toolbar action {action_name} from cache")

                                        # Try to connect the action to its method
                                        method_name = f"{key}_action"
                                        if hasattr(self, method_name):
                                            try:
                                                method = getattr(self, method_name)
                                                # Disconnect first to avoid multiple connections
                                                try:
                                                    action.triggered.disconnect()
                                                except:
                                                    pass
                                                # Connect and enable
                                                action.triggered.connect(method)
                                                action.setEnabled(True)
                                                action_count += 1
                                            except Exception as e:
                                                print(f"Error connecting {action_name} to {method_name}: {e}")
                                    else:
                                        # Load from file
                                        try:
                                            icon_path = os.path.join(icon_dir, icon_file)
                                            if os.path.exists(icon_path):
                                                icon = QtGui.QIcon(icon_path)
                                                if not icon.isNull():
                                                    action.setIcon(icon)
                                                    # Cache the icon for future use
                                                    self._icon_cache[icon_file] = icon
                                                    print(f"Set icon for toolbar action {action_name} from {icon_path}")
                                                else:
                                                    print(f"Warning: Failed to create icon from {icon_path}")
                                            else:
                                                print(f"Warning: Icon file not found: {icon_path}")
                                        except Exception as e:
                                            print(f"Error setting icon for {action_name}: {e}")
                                    break
                        except Exception as e:
                            print(f"Error processing toolbar action: {e}")
                            continue

                    print(f"Connected {action_count} toolbar actions")

                    # Process events after toolbar processing
                    QtWidgets.QApplication.processEvents()
            except Exception as e:
                print(f"Error finding or processing main toolbar: {e}")

            # Safely process toolbuttons
            try:
                # Find all toolboxes/toolbars in the UI
                all_toolbars = self.findChildren(QtWidgets.QToolBar)
                all_toolbuttons = self.findChildren(QtWidgets.QToolButton)

                print(f"Found {len(all_toolbars)} toolbars and {len(all_toolbuttons)} toolbuttons")

                # Process events after finding buttons
                QtWidgets.QApplication.processEvents()

                # Apply icons to all toolbuttons
                button_count = 0
                for button in all_toolbuttons:
                    try:
                        button_name = button.objectName().lower()

                        # Skip special buttons
                        if "toggle_button" in button_name:
                            continue

                        # Try to match button name to an icon
                        for key, icon_file in icon_mapping.items():
                            if key in button_name:
                                # Use cached icon if available
                                if icon_file in self._icon_cache:
                                    button.setIcon(self._icon_cache[icon_file])
                                    print(f"Set icon for button {button_name} from cache")

                                    # Try to connect the button to its method
                                    method_name = f"{key}_action"
                                    if hasattr(self, method_name):
                                        try:
                                            method = getattr(self, method_name)
                                            # Disconnect first to avoid multiple connections
                                            try:
                                                button.clicked.disconnect()
                                            except:
                                                pass
                                            # Connect
                                            button.clicked.connect(method)
                                            button_count += 1
                                            print(f"Connected button {button_name} to {method_name}")
                                        except Exception as e:
                                            print(f"Error connecting button {button_name}: {e}")
                                else:
                                    # Load from file
                                    try:
                                        icon_path = os.path.join(icon_dir, icon_file)
                                        if os.path.exists(icon_path):
                                            icon = QtGui.QIcon(icon_path)
                                            if not icon.isNull():
                                                button.setIcon(icon)
                                                # Cache the icon for future use
                                                self._icon_cache[icon_file] = icon
                                                print(f"Set icon for button {button_name} from {icon_path}")
                                            else:
                                                print(f"Warning: Failed to create icon from {icon_path}")
                                        else:
                                            print(f"Warning: Icon file not found: {icon_path}")
                                    except Exception as e:
                                        print(f"Error setting icon for {button_name}: {e}")
                                break
                    except Exception as e:
                        print(f"Error processing toolbutton: {e}")
                        continue

                print(f"Connected {button_count} toolbar buttons")

                # Process events after processing toolbuttons
                QtWidgets.QApplication.processEvents()
            except Exception as e:
                print(f"Error processing toolbuttons: {e}")

            # Safely process signal operation frame
            try:
                # Also check for buttons in SignalOpFrame
                if hasattr(self.ui, "SignalOpFrame"):
                    # Signal operation buttons with correct icon mapping
                    button_mappings = {
                        "SaveButton": "Save.png",
                        "UndoButton": "Undo.png",
                        "RedoButton": "Redo.png",
                        "UpdateConfig": "UpdateEntry.png"
                    }

                    frame_button_count = 0
                    for button_name, icon_file in button_mappings.items():
                        # Try both with and without _2 suffix
                        for btn_variant in [button_name, f"{button_name}_2"]:
                            try:
                                if hasattr(self.ui, btn_variant):
                                    button = getattr(self.ui, btn_variant)

                                    # Use cached icon if available
                                    if icon_file in self._icon_cache:
                                        button.setIcon(self._icon_cache[icon_file])
                                        print(f"Set icon for {btn_variant} from cache")

                                        # Try to connect the button to its method
                                        action_type = button_name.lower().replace("button", "")
                                        method_name = f"{action_type}_action"
                                        if hasattr(self, method_name):
                                            try:
                                                method = getattr(self, method_name)
                                                # Disconnect first to avoid multiple connections
                                                try:
                                                    button.clicked.disconnect()
                                                except:
                                                    pass
                                                # Connect
                                                button.clicked.connect(method)
                                                frame_button_count += 1
                                                print(f"Connected {btn_variant} to {method_name}")
                                            except Exception as e:
                                                print(f"Error connecting {btn_variant}: {e}")
                                    else:
                                        # Load from file
                                        try:
                                            icon_path = os.path.join(icon_dir, icon_file)
                                            if os.path.exists(icon_path):
                                                icon = QtGui.QIcon(icon_path)
                                                if not icon.isNull():
                                                    button.setIcon(icon)
                                                    # Cache the icon for future use
                                                    self._icon_cache[icon_file] = icon
                                                    print(f"Set icon for {btn_variant} from {icon_path}")
                                                else:
                                                    print(f"Warning: Failed to create icon from {icon_path}")
                                            else:
                                                print(f"Warning: Icon file not found: {icon_path}")
                                        except Exception as e:
                                            print(f"Error setting icon for {btn_variant}: {e}")
                            except Exception as e:
                                print(f"Error processing button {btn_variant}: {e}")

                    print(f"Connected {frame_button_count} frame buttons")

                    # Process events after connecting frame buttons
                    QtWidgets.QApplication.processEvents()
            except Exception as e:
                print(f"Error processing signal operation frame: {e}")

            print("Toolbar setup completed successfully")

            # Final process events after toolbar setup
            QtWidgets.QApplication.processEvents()
            return True
        except Exception as e:
            print(f"Error setting up toolbar icons: {e}")
            import traceback
            traceback.print_exc()

            # Ensure UI remains responsive even after error
            QtWidgets.QApplication.processEvents()
            return False

    def ensure_path_fields_enabled(self):
        """Ensure path fields are enabled regardless of other settings"""
        try:
            # Check for the new UI elements
            if hasattr(self.ui, "OutputPathLineEdit") and hasattr(self.ui, "ScriptPathLineEdit"):
                # New UI structure
                if hasattr(self.ui, "OutputPathLineEdit"):
                    self.ui.OutputPathLineEdit.setEnabled(True)
                if hasattr(self.ui, "OutputPathButton"):
                    self.ui.OutputPathButton.setEnabled(True)
                if hasattr(self.ui, "ScriptPathLineEdit"):
                    self.ui.ScriptPathLineEdit.setEnabled(True)
                if hasattr(self.ui, "ScriptPathButton"):
                    self.ui.ScriptPathButton.setEnabled(True)
            elif hasattr(self.ui, "lineEdit_output_dir") and hasattr(self.ui, "lineEdit_scripts_dir"):
                # Old UI structure
                path_widgets = [
                    self.ui.lineEdit_output_dir,
                    self.ui.lineEdit_scripts_dir,
                    self.ui.pushButton_browse_output,
                    self.ui.pushButton_browse_scripts
                ]

                for widget in path_widgets:
                    widget.setEnabled(True)

            print("Path fields enabled successfully")
        except Exception as e:
            print(f"Error ensuring path fields are enabled: {e}")

def main():
    """
    Main entry point for the application.
    Initializes and runs the SignalMgrApp.
    """
    app = QtWidgets.QApplication(sys.argv)

    # Force-reload resources
    import importlib
    try:
        import Cfg.signalmgrapp_rc
        importlib.reload(Cfg.signalmgrapp_rc)
        print("Successfully loaded resource module")
    except Exception as e:
        print(f"Error loading resources: {e}")

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__ + '\\..')), "Cfg", "Icons", "AppIcon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Warning: Application icon not found at {icon_path}")

    # Optimize performance for menus
    app.setAttribute(QtCore.Qt.AA_DontUseNativeMenuBar, True)

    # Set application style for better performance
    app.setStyle("Fusion")  # Use Fusion style for consistent cross-platform appearance and better performance

    # Pre-load and cache QPixmap instances (shared between icons)
    QtGui.QPixmapCache.setCacheLimit(10240)  # Increase cache size (in KB)

    # Additional settings for improved menu performance
    app.processEvents()  # Process any pending events before showing window

    """# Disable effects that can slow down menu display
    if hasattr(QtWidgets.QApplication, 'setEffectEnabled'):
        for effect in [QtCore.Qt.UI_AnimateMenu, QtCore.Qt.UI_FadeMenu,
                      QtCore.Qt.UI_AnimateCombo, QtCore.Qt.UI_AnimateTooltip]:
            app.setEffectEnabled(effect, False) """

    # Print platform information for debugging
    import platform
    print(f"Running on: {platform.system()} {platform.release()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Qt path: {QtWidgets.__file__}")

    window = SignalMgrApp()
    window.show()

    # Process events again after show to ensure UI is fully loaded
    app.processEvents()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
