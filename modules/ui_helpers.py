import os
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QPushButton, QGroupBox
from PyQt5.QtCore import Qt, QObject

# Make UIHelpers inherit from QObject so it can be used as an event filter
class UIHelpers(QObject):
    def __init__(self, app):
        # Initialize the QObject parent
        super(UIHelpers, self).__init__(app)
        self.app = app
        self.signal_tree = None
        # Store a deep copy of signals data for version comparison
        self.original_signals_data = None
        
    def initialize_version_fields(self):
        """Initialize version fields with default values and add validation"""
        # Initialize metadata if not exists
        if "metadata" not in self.app.signals_data:
            self.app.signals_data["metadata"] = {}
            
        # Try to load from existing metadata
        metadata = self.app.signals_data.get("metadata", {})
        
        # Store a deep copy of the current signals data for future comparison
        import copy
        self.original_signals_data = copy.deepcopy(self.app.signals_data)
        
        # Set version from metadata or default to 1.0
        version_str = metadata.get("version", "1.0")
        try:
            # Try to convert to float for validation
            version_float = float(version_str)
            # Format with one decimal point
            version_str = f"{version_float:.1f}"
        except (ValueError, TypeError):
            version_str = "1.0"
        
        # Set version in UI - assuming VersionNumber has been changed to QLineEdit in the UI
        if isinstance(self.app.ui.VersionNumber, QtWidgets.QLineEdit):
            self.app.ui.VersionNumber.setText(version_str)
        else:
            # Try to extract integer part
            try:
                version_int = int(float(version_str))
                self.app.ui.VersionNumber.setValue(version_int)
            except (ValueError, TypeError):
                self.app.ui.VersionNumber.setValue(1)
        
        # Set date from metadata or current date
        date_str = metadata.get("date", "")
        if date_str:
            try:
                # Parse the date string into a QDate
                date_parts = date_str.split("-")
                if len(date_parts) == 3:
                    year, month, day = map(int, date_parts)
                    qdate = QtCore.QDate(year, month, day)
                    
                    # Only use the date from metadata if it's valid
                    if qdate.isValid():
                        self.app.ui.VersionDate.setDate(qdate)
                    else:
                        self.app.ui.VersionDate.setDate(current_date)
                else:
                    self.app.ui.VersionDate.setDate(QtCore.QDate.currentDate())
            except Exception as e:
                print(f"Error parsing date: {e}")
                self.app.ui.VersionDate.setDate(QtCore.QDate.currentDate())
        else:
            # For new configuration, set to current date
            self.app.ui.VersionDate.setDate(QtCore.QDate.currentDate())
        
        # Set editor name from metadata (previously known as "Last Modified By")
        editor_name = metadata.get("editor", "")
        self.app.ui.EditorName.setPlainText(editor_name)
        
        # Set description from metadata - ensure it's always set regardless of emptiness
        description = metadata.get("description", "")
        if hasattr(self.app.ui, 'VersionDescription'):
            print(f"Setting VersionDescription to: {description}")
            self.app.ui.VersionDescription.setPlainText(description)
        
        # Install event filter for date validation
        self.app.ui.VersionDate.installEventFilter(self)
        
        # Update directly to the metadata fields but don't trigger validation
        if isinstance(self.app.ui.VersionNumber, QtWidgets.QLineEdit):
            version_str = self.app.ui.VersionNumber.text()
        else:
            version_str = str(self.app.ui.VersionNumber.value())
        
        version_date = self.app.ui.VersionDate.date()
        
        # Just store what we have in the metadata without validation
        self.app.signals_data["metadata"]["version"] = version_str
        self.app.signals_data["metadata"]["date"] = version_date.toString("yyyy-MM-dd") 
        self.app.signals_data["metadata"]["editor"] = editor_name
        self.app.signals_data["metadata"]["description"] = description

    def setup_tree_widget(self):
        """Set up a tree widget in the scroll area for signal list with the updated layout"""
        self.signal_tree = QtWidgets.QTreeWidget()
        self.signal_tree.setHeaderLabels(["Signal Name", "Type", "Description"])
        self.signal_tree.setColumnWidth(0, 150)
        self.signal_tree.setColumnWidth(1, 100)
        
        # Change from itemClicked to itemSelectionChanged for more reliable selection handling
        self.signal_tree.itemSelectionChanged.connect(self.on_signal_selection_changed)
        
        # Use the signalDetailsLayout directly instead of creating a new layout
        if hasattr(self.app.ui, 'signalDetailsLayout'):
            self.app.ui.signalDetailsLayout.addWidget(self.signal_tree)
        else:
            # Fallback to old method if the layout doesn't exist
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self.signal_tree)
            self.app.ui.scrollAreaWidgetContents.setLayout(layout)
            
    def populate_soc_list(self):
        # Clear current entries
        self.app.ui.SOCList.clear()
        
        # Get SOC types from configuration or use default if not found
        if self.app.signals_data and "soc_list" in self.app.signals_data:
            soc_types = self.app.signals_data.get("soc_list", [])
        else:
            # Only use Windows as default in new configurations
            soc_types = ["Windows"]
            # Store in signals_data
            self.app.signals_data["soc_list"] = soc_types
        
        # Add configured SOC types to dropdown
        for soc in soc_types:
            self.app.ui.SOCList.addItem(soc)
            
        # Set current SOC if defined
        current_soc = self.app.signals_data.get("soc_type", "Windows")  # Default to Windows
        if current_soc:
            index = self.app.ui.SOCList.findText(current_soc)
            if index >= 0:
                self.app.ui.SOCList.setCurrentIndex(index)
            else:
                # If the current SOC isn't in the list, add it and select it
                self.app.ui.SOCList.addItem(current_soc)
                self.app.ui.SOCList.setCurrentText(current_soc)
                
        # If no SOC type is set yet, set to Windows as default
        if self.app.ui.SOCList.currentText() == "" or self.app.ui.SOCList.count() == 0:
            self.app.ui.SOCList.addItem("Windows")
            self.app.ui.SOCList.setCurrentText("Windows")
            self.app.signals_data["soc_type"] = "Windows"

    def populate_build_types(self):
        # Clear current entries
        self.app.ui.BuildImageType.clear()
        
        # Get build types from configuration or use default if not found
        if self.app.signals_data and "build_list" in self.app.signals_data:
            build_types = self.app.signals_data.get("build_list", [])
        else:
            # Only use SMP as default in new configurations
            build_types = ["SMP"]
            # Store in signals_data
            self.app.signals_data["build_list"] = build_types
        
        # Add configured build types
        for build_type in build_types:
            self.app.ui.BuildImageType.addItem(build_type)
            
        # Set current build type if defined
        current_build = self.app.signals_data.get("build_type", "SMP")  # Default to SMP
        if current_build:
            index = self.app.ui.BuildImageType.findText(current_build)
            if index >= 0:
                self.app.ui.BuildImageType.setCurrentIndex(index)
            else:
                # If the current build type isn't in the list, add it and select it
                self.app.ui.BuildImageType.addItem(current_build)
                self.app.ui.BuildImageType.setCurrentText(current_build)
                
        # If no build type is set yet, set to SMP as default
        if self.app.ui.BuildImageType.currentText() == "" or self.app.ui.BuildImageType.count() == 0:
            self.app.ui.BuildImageType.addItem("SMP")
            self.app.ui.BuildImageType.setCurrentText("SMP")
            self.app.signals_data["build_type"] = "SMP"

    def check_version_and_run(self, func):
        """
        Modified to not check version before editing operations
        Only use for critical operations like save/export
        """
        # Call the original function without version checks
        return func()
    
    def check_version_for_export(self):
        """Check if version information is properly set before export/save operations"""
        metadata = self.app.signals_data.get("metadata", {})
        version_number = metadata.get("version", "")
        version_date_str = metadata.get("date", "")
        editor_name = metadata.get("editor", "")
        
        # Get current editor name from UI
        current_editor = self.app.ui.EditorName.toPlainText().strip()
        
        # Check if editor name is valid
        if not current_editor or current_editor.isspace() or current_editor.lower() == "enter your name":
            QMessageBox.warning(
                self.app,
                "Invalid Editor Name",
                "Please enter your name in the 'Modifier Name' field before saving."
            )
            # Switch to Core Configuration tab
            self.app.ui.tabWidget.setCurrentIndex(0)
            # Focus on editor name field
            self.app.ui.EditorName.setFocus()
            return False
        
        if not version_number or not version_date_str or not editor_name:
            reply = QMessageBox.question(
                self.app, 
                "Missing Version Information", 
                "Version information is incomplete. Would you like to update it now?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Switch to Core Configuration tab
                self.app.ui.tabWidget.setCurrentIndex(0)
                return False
        
        # Validate the date before critical operations
        if not self.validate_version_date():
            # If validation fails, switch to Core Configuration tab
            self.app.ui.tabWidget.setCurrentIndex(0)
            return False
    
        return True

    def is_version_info_filled(self):
        """Check if all version fields are filled"""
        editor_name = self.app.ui.EditorName.toPlainText().strip()
        return (self.app.ui.VersionNumber.value() > 0 and 
               not editor_name.isspace() and 
               not editor_name.lower() == "enter your name" and 
               len(editor_name) > 0)

    def update_version_info(self, initial=False, ui_change=False, skip_validation=False):
        """Update version information with validation
        
        Args:
            initial: True if this is initial setup, no validation needed
            ui_change: True if update was triggered by UI interaction
            skip_validation: True to skip version number validation (used when loading files)
        """
        # Get current values from UI
        if isinstance(self.app.ui.VersionNumber, QtWidgets.QLineEdit):
            version_str = self.app.ui.VersionNumber.text()
        else:
            version_str = str(self.app.ui.VersionNumber.value())
        
        version_date = self.app.ui.VersionDate.date()
        editor_name = self.app.ui.EditorName.toPlainText().strip()
        
        # Validate editor name - only if explicitly requested and not initial setup
        if not initial and ui_change and (not editor_name or editor_name.isspace() or editor_name.lower() == "enter your name"):
            # Don't show warning on startup, only on explicit changes
            if editor_name:  # Only show warning if there's some text (but invalid)
                QMessageBox.warning(
                    self.app,
                    "Invalid Editor Name",
                    "Please enter your name in the 'Modifier Name' field."
                )
            return False
        
        # Get description if field exists
        description = ""
        if hasattr(self.app.ui, 'VersionDescription'):
            description = self.app.ui.VersionDescription.toPlainText().strip()
        
        # Create a new metadata dictionary with current values
        new_metadata = {
            "version": version_str,
            "date": version_date.toString("yyyy-MM-dd"),
            "editor": editor_name,
            "description": description
        }
        
        # Validate version is greater than previous (if not initial and not skip_validation)
        if not initial and not skip_validation and "metadata" in self.app.signals_data:
            old_metadata = self.app.signals_data.get("metadata", {})
            
            # Compare version numbers
            try:
                old_version = float(old_metadata.get("version", "0.0"))
                new_version = float(new_metadata["version"])
                
                if new_version < old_version:
                    QMessageBox.warning(
                        self.app,
                        "Invalid Version",
                        f"New version {new_version} cannot be less than previous version {old_version}"
                    )
                    # Restore previous version in the UI
                    if isinstance(self.app.ui.VersionNumber, QtWidgets.QLineEdit):
                        self.app.ui.VersionNumber.setText(old_metadata.get("version", "1.0"))
                    else:
                        try:
                            old_int = int(float(old_metadata.get("version", "1.0")))
                            self.app.ui.VersionNumber.setValue(old_int)
                        except (ValueError, TypeError):
                            pass
                    return False
            except (ValueError, TypeError):
                # If we can't parse as float, just skip version validation
                pass
        
        # Update metadata in signals_data
        if "metadata" not in self.app.signals_data:
            self.app.signals_data["metadata"] = {}
        
        # Update all metadata fields at once
        self.app.signals_data["metadata"].update(new_metadata)
        
        # Only mark as modified if not initial setup
        if not initial:
            self.app.modified = True
            self.update_window_title()
        
        return True

    def validate_version_date(self):
        """Validate the version date is in future or equal to current date"""
        version_date = self.app.ui.VersionDate.date().toPyDate()
        current_date = datetime.now().date()
        
        # Allow version date to be today or in the future
        if version_date < current_date:
            QMessageBox.warning(
                self.app, 
                "Invalid Date", 
                "Version date must be today or in the future for release planning."
            )
            return False
        return True

    def update_signal_count_display(self):
        """Update the signal count display in the UI"""
        signal_count = len(self.app.signals_data.get("signals", {}))
        # Update the signal count in both locations
        self.app.ui.SignalCnt.setValue(signal_count)
        # Also update in Core Info if it exists
        self.update_core_info()

    def on_signal_selection_changed(self):
        # This handles when the signal selection changes
        selected_items = self.signal_tree.selectedItems()
        if selected_items:
            signal_name = selected_items[0].text(0)
            if "signals" in self.app.signals_data and signal_name in self.app.signals_data["signals"]:
                signal_info = self.app.signals_data["signals"][signal_name]
                self.display_signal_details(signal_name, signal_info)

    def display_signal_details(self, signal_name, signal_info):
        """Display signal details in the SignalInternalInfo widget with the updated layout"""
        # Create a widget to display signal details with all configurable options
        detail_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(detail_widget)

        # Add a scroll area for better handling of many fields
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(scroll_content)

        # Add signal name as a title
        title_label = QtWidgets.QLabel(signal_name)
        title_font = QtGui.QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addRow(QtWidgets.QLabel("Signal Name:"), title_label)

        # Add separator line
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addRow(line)

        # Display key signal properties in a readable format
        for key in ['Variable_Port_Name', 'DataType', 'Memory Region', 'Buffer count_IPC',
                   'Type', 'InitValue', 'Notifiers', 'Source', 'Impl_Approach',
                   'GetObjRef', 'SM_Buff_Count', 'Timeout', 'Periodicity',
                   'ASIL', 'Checksum', 'description']:
            if key in signal_info:
                value = signal_info[key]
                # Format boolean values as Yes/No
                if isinstance(value, bool):
                    value = "Yes" if value else "No"
                # Create a label with the value
                value_label = QtWidgets.QLabel(str(value))
                value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                layout.addRow(f"{key.replace('_', ' ').title()}:", value_label)

        # If it's a structure type, show fields
        if signal_info.get("is_struct", False) and "struct_fields" in signal_info:
            struct_group = QGroupBox("Structure Fields")
            struct_layout = QtWidgets.QVBoxLayout(struct_group)
            
            # Create a tree for structure fields
            field_tree = QtWidgets.QTreeWidget()
            field_tree.setHeaderLabels(["Field Name", "Type", "Description"])
            field_tree.setColumnWidth(0, 150)
            field_tree.setColumnWidth(1, 100)
            
            # Add fields to tree
            for field_name, field_info in signal_info["struct_fields"].items():
                field_item = QtWidgets.QTreeWidgetItem([
                    field_name,
                    field_info.get("type", ""),
                    field_info.get("description", "")
                ])
                field_tree.addTopLevelItem(field_item)
            struct_layout.addWidget(field_tree)
            layout.addRow(struct_group)

        # Show core destinations if available
        core_targets = []
        for key in signal_info:
            if key.startswith("core_") and signal_info[key]:
                core_name = key[5:].replace('_', '.')
                core_targets.append(core_name)
        
        if core_targets:
            dest_label = QtWidgets.QLabel(", ".join(core_targets))
            dest_label.setWordWrap(True)
            layout.addRow("Destination Cores:", dest_label)

        # Complete the scroll area
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Add Edit button at the bottom
        edit_button = QPushButton("Edit Signal")
        edit_button.clicked.connect(lambda: self.app.signal_ops.edit_signal_details(signal_name))
        main_layout.addWidget(edit_button)

        # Set as the current widget in the stacked widget
        if self.app.ui.SignalInternalInfo.count() > 0:
            # Use the page1Layout and page2Layout if they exist
            if hasattr(self.app.ui, 'page1Layout') and hasattr(self.app.ui, 'page2Layout'):
                # Remove any existing widgets from page1Layout
                while self.app.ui.page1Layout.count():
                    item = self.app.ui.page1Layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                # Add to page1Layout instead of creating a new widget
                self.app.ui.page1Layout.addWidget(detail_widget)
                self.app.ui.SignalInternalInfo.setCurrentIndex(0)
            else:
                # Remove any existing custom pages
                while self.app.ui.SignalInternalInfo.count() > 0:
                    widget = self.app.ui.SignalInternalInfo.widget(0)
                    self.app.ui.SignalInternalInfo.removeWidget(widget)
                
                # Add as a new widget
                self.app.ui.SignalInternalInfo.addWidget(detail_widget)
                self.app.ui.SignalInternalInfo.setCurrentWidget(detail_widget)
        else:
            # Add as a new widget
            self.app.ui.SignalInternalInfo.addWidget(detail_widget)
            self.app.ui.SignalInternalInfo.setCurrentWidget(detail_widget)

    def update_core_info(self):
        """Update the Core Info tree widget with configuration data organized by SOC"""
        # Get the tree widget based on UI structure
        if hasattr(self.app.ui, 'CoreInfo_2'):
            if isinstance(self.app.ui.CoreInfo_2, QtWidgets.QScrollArea):
                # For the new UI with scroll area
                if hasattr(self.app.ui, 'coreInfoContents') and hasattr(self.app.ui, 'coreInfoLayout'):
                    # Clear existing content
                    while self.app.ui.coreInfoLayout.count():
                        item = self.app.ui.coreInfoLayout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                    
                    # Create a tree widget to add to the scroll area
                    tree = QtWidgets.QTreeWidget()
                    tree.setHeaderLabels(["Core Information"])
                    self.app.ui.coreInfoLayout.addWidget(tree)
                else:
                    # Fallback for scroll area without layout
                    tree = QtWidgets.QTreeWidget()
                    tree.setHeaderLabels(["Core Information"])
                    old_widget = self.app.ui.CoreInfo_2.takeWidget()
                    if old_widget:
                        old_widget.deleteLater()
                    self.app.ui.CoreInfo_2.setWidget(tree)
            else:
                # For the old UI with direct tree widget
                tree = self.app.ui.CoreInfo_2
                tree.clear()
        else:
            # Couldn't find tree widget, return without doing anything
            return
        
        # Get core info from signals_data
        core_info = self.app.signals_data.get("core_info", {})
        
        if not core_info:
            return
            
        # Add cores to tree widget - grouped by SOC
        for soc_name, cores in core_info.items():
            # Create SOC node as parent
            soc_item = QTreeWidgetItem(tree)
            soc_item.setText(0, f"SOC: {soc_name}")
            soc_item.setExpanded(True)  # Expand SOC by default
            
            # Add cores as children of SOC
            for core_name, core_props in cores.items():
                # Create core item as child of SOC
                core_item = QTreeWidgetItem(soc_item)
                core_item.setText(0, f"Core: {core_name}")
                
                # Create child items for core details
                if isinstance(core_props, dict):
                    # Add core role
                    role_str = "Master" if core_props.get("is_master", False) else "Slave"
                    role_item = QTreeWidgetItem(core_item)
                    role_item.setText(0, f"Role: {role_str}")
                    
                    # OS info
                    os_str = str(core_props.get("os", "Unknown"))
                    os_item = QTreeWidgetItem(core_item)
                    os_item.setText(0, f"OS: {os_str}")
                    
                    # SOC Family
                    family_str = str(core_props.get("soc_family", "Unknown"))
                    if family_str and family_str != "Unknown":
                        family_item = QTreeWidgetItem(core_item)
                        family_item.setText(0, f"SOC Family: {family_str}")
                    
                    # Boolean properties
                    for prop_name, display_name in [
                        ("is_qnx", "QNX Core"),
                        ("is_autosar", "Autosar Compliant"),
                        ("is_sim", "Simulation Core")
                    ]:
                        if core_props.get(prop_name, False):
                            prop_item = QTreeWidgetItem(core_item)
                            prop_item.setText(0, f"{display_name}: Yes")
                else:
                    # For string or other scalar values
                    desc_item = QTreeWidgetItem(core_item)
                    desc_item.setText(0, str(core_props))
        
        # Keep SOCs expanded, but collapse core details by default
        for i in range(tree.topLevelItemCount()):
            soc_item = tree.topLevelItem(i)
            soc_item.setExpanded(True)
            for j in range(soc_item.childCount()):
                core_item = soc_item.child(j)
                core_item.setExpanded(False)

    def refresh_signal_tree(self):
        # Clear and repopulate the signal tree
        self.signal_tree.clear()
        if "signals" in self.app.signals_data:
            for signal_name, signal_info in self.app.signals_data["signals"].items():
                item = QTreeWidgetItem([
                    signal_name,
                    signal_info.get("DataType", ""),  # Changed from "type" to "DataType"
                    signal_info.get("description", "")
                ])
                self.signal_tree.addTopLevelItem(item)

    def soc_selection_changed(self, index):
        if index > 0:  # Not the default "Select SOC" item
            soc_type = self.app.ui.SOCList.currentText()
            self.app.signals_data["soc_type"] = soc_type
            self.app.modified = True
            self.update_window_title()
            self.update_core_info()

    def build_type_changed(self, index):
        if index > 0:  # Not the default "Select Build Type" item
            build_type = self.app.ui.BuildImageType.currentText()
            self.app.signals_data["build_type"] = build_type
            self.app.modified = True
            self.update_window_title()
            self.update_core_info()

    def save_undo_state(self):
        """Save current state to undo stack"""
        import copy
        self.app.undo_stack.append(copy.deepcopy(self.app.signals_data))
        # Clear redo stack after a new action
        self.app.redo_stack.clear()

    def undo_action(self):
        """Restore previous state"""
        if self.app.undo_stack:
            import copy
            # Save current state to redo stack
            self.app.redo_stack.append(copy.deepcopy(self.app.signals_data))
            # Restore previous state
            self.app.signals_data = self.app.undo_stack.pop()
            self.app.modified = True
            self.update_window_title()
            self.refresh_signal_tree()
            self.update_core_info()
            # After undo, update the signal count
            self.update_signal_count_display()

    def redo_action(self):
        """Restore next state"""
        if self.app.redo_stack:
            import copy
            # Save current state to undo stack
            self.app.undo_stack.append(copy.deepcopy(self.app.signals_data))
            # Restore next state
            self.app.signals_data = self.app.redo_stack.pop()
            self.app.modified = True
            self.update_window_title()
            self.refresh_signal_tree()
            self.update_core_info()
            # After redo, update the signal count
            self.update_signal_count_display()

    def get_available_cores(self):
        """Get list of all configured cores in the format 'soc.core'"""
        core_info = self.app.signals_data.get("core_info", {})
        cores = []
        for soc_name, soc_cores in core_info.items():
            for core_name in soc_cores.keys():
                cores.append(f"{soc_name}.{core_name}")
        return cores

    def check_unsaved_changes(self):
        """Check for unsaved changes and prompt user to save if needed"""
        if self.app.modified:
            reply = QMessageBox.question(
                self.app, 
                "Unsaved Changes", 
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.app.file_ops.save_file()
                return True
            elif reply == QMessageBox.Discard:
                return True
            else:
                return False
        return True

    def update_window_title(self):
        """Update window title to show filename and modified status"""
        title = "Signal Manager Tool"
        if self.app.current_file:
            filename = os.path.basename(self.app.current_file)
            title = f"{filename} - {title}"
        if self.app.modified:
            title = f"*{title}"
        self.app.setWindowTitle(title)

    def eventFilter(self, obj, event):
        """Event filter to validate date changes but not block application startup"""
        if obj == self.app.ui.VersionDate and event.type() == QtCore.QEvent.FocusOut:
            # Just show a warning, don't reset the date automatically
            selected_date = obj.date().toPyDate()
            current_date = datetime.now().date()
            if selected_date < current_date:
                QMessageBox.warning(
                    self.app, 
                    "Date Warning", 
                    "Selected date is not in the future. You may need to update it before performing operations."
                )
                # Not forcing a date change here - let the user decide
        
        return super(UIHelpers, self).eventFilter(obj, event)