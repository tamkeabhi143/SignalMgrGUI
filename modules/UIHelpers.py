import os
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QPushButton, QGroupBox
from PyQt5.QtCore import Qt, QObject
import traceback
import copy

# Make UIHelpers inherit from QObject so it can be used as an event filter
class UIHelpers(QObject):
    def __init__(self, app):
        # Initialize the QObject parent
        super(UIHelpers, self).__init__(app)
        self.app = app
        self.signal_tree = None
        # Store a deep copy of signals data for version comparison
        self.original_signals_data = None
        # Default values for version info
        self.default_version_info = {
            "version": "1.0",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "editor": "",
            "description": "Signal Configuration"
        }
        # Flag to track if we're using default values or loaded values
        self.using_default_values = True
        # Flag to track if app just started or file was closed
        self.first_run_or_closed = True

        # Track whether signal handlers have been connected to avoid redundant connections
        self.signal_handlers_connected = False

        # Initialize UI elements if they don't exist
        self.initialize_missing_ui_components()

        self.clear_api_configuration()

    def initialize_version_fields(self, skip_validation=False):
        """Initialize version fields with metadata values or defaults

        Args:
            skip_validation: If True, will not mark file as modified during initialization
        """
        # Remember the original modified state
        original_modified = self.app.modified

        # Reset first_run_or_closed flag after initialization
        # Only reset if not part of the close operation (skip_validation=True)
        if skip_validation:
            self.first_run_or_closed = False

        # Initialize metadata if not exists
        if "metadata" not in self.app.signals_data:
            self.app.signals_data["metadata"] = {}

        # Try to load from existing metadata
        metadata = self.app.signals_data.get("metadata", {})

        # Store a deep copy of the current signals data for future comparison
        import copy
        self.original_signals_data = copy.deepcopy(self.app.signals_data)

        # Check if metadata has values or we should use defaults
        metadata_empty = (
            not metadata.get("version") or
            not metadata.get("date") or
            not metadata.get("editor")
        )

        # Only set using_default_values to True if metadata is empty AND this is first run or file was closed
        # For loaded files or imported data, we should use the values from the file
        if metadata_empty and self.first_run_or_closed:
            self.using_default_values = True
        else:
            # We're using values from a file or imported data
            self.using_default_values = False

        # For loaded or imported data (not first run/closed file), preserve values without validation
        if not self.using_default_values:
            # Get version from metadata as-is without validation
            version_str = metadata.get("version", "")
            if not version_str:  # Only if truly empty, use default
                version_str = self.default_version_info["version"]
        else:
            # Using default values (first run or closed file)
            version_str = self.default_version_info["version"]

        # Set version in UI based on the widget type
        if isinstance(self.app.ui.VersionNumber, QtWidgets.QLineEdit):
            self.app.ui.VersionNumber.setText(version_str)
        elif isinstance(self.app.ui.VersionNumber, QtWidgets.QPlainTextEdit):
            self.app.ui.VersionNumber.setPlainText(version_str)
        elif hasattr(self.app.ui.VersionNumber, "setValue"):
            try:
                version_int = int(float(version_str))
                self.app.ui.VersionNumber.setValue(version_int)
            except (ValueError, TypeError):
                # For non-default values, keep as is to avoid overwriting loaded data
                pass

        # Handle date and time values
        if self.using_default_values:
            # Using default values - set current date and time
            self.app.ui.VersionDate.setDateTime(QtCore.QDateTime.currentDateTime())
        else:
            # Using file/imported values
            date_str = metadata.get("date", "")
            if date_str:
                try:
                    # Check if date string has time component (contains space or T separator)
                    if " " in date_str or "T" in date_str:
                        # Parse ISO format datetime string
                        separator = "T" if "T" in date_str else " "
                        date_part, time_part = date_str.split(separator, 1)

                        # Parse date
                        date_parts = date_part.split("-")
                        year, month, day = map(int, date_parts)

                        # Parse time if present
                        hour, minute, second = 0, 0, 0
                        if ":" in time_part:
                            time_parts = time_part.split(":")
                            hour = int(time_parts[0])
                            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                            # Handle seconds which might have milliseconds
                            if len(time_parts) > 2:
                                second = int(float(time_parts[2]))

                        qdatetime = QtCore.QDateTime(QtCore.QDate(year, month, day),
                                         QtCore.QTime(hour, minute, second))
                    else:
                        # Only date part without time
                        date_parts = date_str.split("-")
                        year, month, day = map(int, date_parts)
                        # Create QDateTime with date and midnight time
                        qdatetime = QtCore.QDateTime(QtCore.QDate(year, month, day),
                                        QtCore.QTime(0, 0, 0))

                        # Only use the datetime from metadata if it's valid
                        if qdatetime.isValid():
                            self.app.ui.VersionDate.setDateTime(qdatetime)
                        else:
                            # Invalid datetime in file, use current datetime
                            self.app.ui.VersionDate.setDateTime(QtCore.QDateTime.currentDateTime())
                except Exception as e:
                    print(f"Error parsing datetime: {e}")
                    # Error parsing datetime, use current datetime
                    self.app.ui.VersionDate.setDateTime(QtCore.QDateTime.currentDateTime())
                else:
                    # No date in metadata, use current datetime
                    self.app.ui.VersionDate.setDateTime(QtCore.QDateTime.currentDateTime())

        # Handle editor name - respect empty string explicitly after closing
        if not self.first_run_or_closed:
            # For loaded files or imported data, use value from metadata
            editor_name = metadata.get("editor", "")
            if hasattr(self.app.ui, 'VersionUpdateName'):
                # Use the placeholder text for the editor name field
                self.app.ui.VersionUpdateName.setPlaceholderText(editor_name)
                self.app.ui.VersionUpdateName.setPlainText(editor_name)
            elif hasattr(self.app.ui, 'EditorName'):
                # Use the placeholder text for the editor name field
                self.app.ui.EditorName.setPlaceholderText(editor_name)
                self.app.ui.EditorName.setPlainText(editor_name)
        else:
            # First run or closed file - use empty string
            self.app.ui.VersionUpdateName.setPlaceholderText("Enter your name")
            self.app.ui.VersionUpdateName.setPlainText("")  # Clear text to show placeholder

        # Handle description - respect empty string explicitly after closing
        # When first_run_or_closed is True, we use empty string (for Close operation)
        # Otherwise we use the value from metadata
        if not self.first_run_or_closed and hasattr(self.app.ui, 'VersionDescription'):
            # For loaded files or imported data, use value from metadata
            description = metadata.get("description", "")
            self.app.ui.VersionDescription.setPlainText(description)
        # Otherwise, leave it as set by close_file (should be empty string)

        # Install event filter for date validation
        self.app.ui.VersionDate.installEventFilter(self)

        # Store the current values back in metadata without changing modified flag
        # This ensures consistency between UI and data model
        if isinstance(self.app.ui.VersionNumber, QtWidgets.QLineEdit):
            curr_version_str = self.app.ui.VersionNumber.text()
        elif isinstance(self.app.ui.VersionNumber, QtWidgets.QPlainTextEdit):
            curr_version_str = self.app.ui.VersionNumber.toPlainText()
        else:
            curr_version_str = str(self.app.ui.VersionNumber.value())

        curr_version_date = self.app.ui.VersionDate.date()
        if hasattr(self.app.ui, 'EditorName'):
            curr_editor_name = self.app.ui.EditorName.toPlainText().strip()
        elif hasattr(self.app.ui, 'VersionUpdateName'):
            curr_editor_name = self.app.ui.VersionUpdateName.toPlainText().strip()

        # Get description from UI if it exists
        curr_description = ""
        if hasattr(self.app.ui, 'VersionDescription'):
            curr_description = self.app.ui.VersionDescription.toPlainText().strip()

        # Update metadata with current UI values
        self.app.signals_data["metadata"]["version"] = curr_version_str
        self.app.signals_data["metadata"]["date"] = curr_version_date.toString("yyyy-MM-dd")
        self.app.signals_data["metadata"]["editor"] = curr_editor_name
        self.app.signals_data["metadata"]["description"] = curr_description

        # If skip_validation is True, restore the original modified state
        # This ensures opening a file doesn't mark it as modified
        if skip_validation:
            self.app.modified = original_modified

    def setup_tree_widget(self):
        """Set up a table widget in the scroll area for signal list with a flat structure"""
        # Check if signal list widget is already set up
        if hasattr(self, 'signal_tree') and self.signal_tree is not None:
            return

        # Use QTableWidget instead of QTreeWidget since signals are flat data
        self.signal_tree = QtWidgets.QTableWidget()
        self.signal_tree.setColumnCount(3)
        self.signal_tree.setHorizontalHeaderLabels(["Signal Name", "Type", "Description"])
        self.signal_tree.setColumnWidth(0, 150)
        self.signal_tree.setColumnWidth(1, 100)
        self.signal_tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.signal_tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Connect signal selection handler only once
        self.signal_tree.itemSelectionChanged.connect(self.handle_signal_selected)

        # Find the scroll area from the UI
        scroll_area = self.app.ui.SignalEntryScrollArea
        if scroll_area:
            # Clear any existing content
            content_widget = QtWidgets.QWidget()
            scroll_area.setWidget(content_widget)

            # Create layout for content widget
            layout = QtWidgets.QVBoxLayout(content_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            # Add table widget to layout
            layout.addWidget(self.signal_tree)
            print("Signal table successfully set up in SignalEntryScrollArea")
        else:
            print("ERROR: SignalEntryScrollArea not found in UI")

    # We also need to update refresh_signal_tree to work with QTableWidget
    def refresh_signal_tree(self):
        # Clear and repopulate the signal table
        self.signal_tree.setRowCount(0)
        if "signals" in self.app.signals_data:
            signals = self.app.signals_data["signals"]
            self.signal_tree.setRowCount(len(signals))

            for row, (signal_name, signal_info) in enumerate(signals.items()):
                # Create items for each column
                name_item = QtWidgets.QTableWidgetItem(signal_name)
                type_item = QtWidgets.QTableWidgetItem(signal_info.get("DataType", ""))
                desc_item = QtWidgets.QTableWidgetItem(signal_info.get("description", ""))

                # Set items in table
                self.signal_tree.setItem(row, 0, name_item)
                self.signal_tree.setItem(row, 1, type_item)
                self.signal_tree.setItem(row, 2, desc_item)

    def populate_soc_list(self):
        # Clear current entries
        self.app.ui.SOCListComboBox.clear()

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
            self.app.ui.SOCListComboBox.addItem(soc)

        # Set current SOC if defined
        current_soc = self.app.signals_data.get("soc_type", "Windows")  # Default to Windows
        if current_soc:
            index = self.app.ui.SOCListComboBox.findText(current_soc)
            if index >= 0:
                self.app.ui.SOCListComboBox.setCurrentIndex(index)
            else:
                # If the current SOC isn't in the list, add it and select it
                self.app.ui.SOCListComboBox.addItem(current_soc)
                self.app.ui.SOCListComboBox.setCurrentText(current_soc)

        # If no SOC type is set yet, set to Windows as default
        if self.app.ui.SOCListComboBox.currentText() == "" or self.app.ui.SOCListComboBox.count() == 0:
            self.app.ui.SOCListComboBox.addItem("Windows")
            self.app.ui.SOCListComboBox.setCurrentText("Windows")
            self.app.signals_data["soc_type"] = "Windows"

    def populate_build_types(self):
        # Clear current entries
        self.app.ui.BuildImageComboBox.clear()

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
            self.app.ui.BuildImageComboBox.addItem(build_type)

        # Set current build type if defined
        current_build = self.app.signals_data.get("build_type", "SMP")  # Default to SMP
        if current_build:
            index = self.app.ui.BuildImageComboBox.findText(current_build)
            if index >= 0:
                self.app.ui.BuildImageComboBox.setCurrentIndex(index)
            else:
                # If the current build type isn't in the list, add it and select it
                self.app.ui.BuildImageComboBox.addItem(current_build)
                self.app.ui.BuildImageComboBox.setCurrentText(current_build)

        # If no build type is set yet, set to SMP as default
        if self.app.ui.BuildImageComboBox.currentText() == "" or self.app.ui.BuildImageComboBox.count() == 0:
            self.app.ui.BuildImageComboBox.addItem("SMP")
            self.app.ui.BuildImageComboBox.setCurrentText("SMP")
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
        # Accept loaded or imported data as-is if not modified
        if not self.app.modified and self.app.current_file is not None:
            return True

        # Skip validation when using default values for new files
        if self.using_default_values and self.app.current_file is None:
            return True

        # Only validate if there's an already opened file/imported data and it has changes
        if self.app.modified:
            metadata = self.app.signals_data.get("metadata", {})
            version_number = metadata.get("version", "")
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

            if not version_number or not editor_name:
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

            # For modified files, validate the date
            if not self.validate_version_date():
                # If validation fails, switch to Core Configuration tab
                self.app.ui.tabWidget.setCurrentIndex(0)
                return False

        return True

    def is_version_info_filled(self):
        """Check if all version fields are filled"""
        editor_name = self.app.ui.EditorName.toPlainText().strip()

        # Get version based on widget type
        if isinstance(self.app.ui.VersionNumber, QtWidgets.QLineEdit):
            version_filled = bool(self.app.ui.VersionNumber.text().strip())
        elif isinstance(self.app.ui.VersionNumber, QtWidgets.QPlainTextEdit):
            version_filled = bool(self.app.ui.VersionNumber.toPlainText().strip())
        elif hasattr(self.app.ui.VersionNumber, "value"):
            version_filled = self.app.ui.VersionNumber.value() > 0
        else:
            version_filled = False

        return (version_filled and
               not editor_name.isspace() and
               not editor_name.lower() == "enter your name" and
               len(editor_name) > 0)

    def update_version_info(self, initial=False, ui_change=False, skip_validation=False):
        """Update version information without validation during UI interaction

        Args:
            initial: True if this is initial setup
            ui_change: True if update was triggered by UI interaction
            skip_validation: True to skip version number validation
        """
        # Get current values from UI based on widget type
        if isinstance(self.app.ui.VersionNumber, QtWidgets.QLineEdit):
            version_str = self.app.ui.VersionNumber.text()
        elif isinstance(self.app.ui.VersionNumber, QtWidgets.QPlainTextEdit):
            version_str = self.app.ui.VersionNumber.toPlainText()
        elif hasattr(self.app.ui.VersionNumber, "value"):
            version_str = str(self.app.ui.VersionNumber.value())
        else:
            version_str = "1.0"  # Default fallback

        version_date = self.app.ui.VersionDate.date()
        # Get editor name - check which UI element exists
        if hasattr(self.app.ui, 'EditorName') and self.app.ui.EditorName is not None:
            editor_name = self.app.ui.EditorName.toPlainText().strip()
        elif hasattr(self.app.ui, 'VersionUpdateName') and self.app.ui.VersionUpdateName is not None:
            editor_name = self.app.ui.VersionUpdateName.toPlainText().strip()
        else:
            # Default value if neither field exists
            editor_name = ""
            print("Warning: Neither EditorName nor VersionUpdateName found in UI")

        # For UI changes, always skip validation - only validate during save/export operations
        if ui_change:
            skip_validation = True

        # Skip validation if:
        # 1. Initial setup (initial=True)
        # 2. Explicitly requested (skip_validation=True)
        # 3. Using default values for specific actions:
        #    - Creating a new file (app.current_file is None)
        #    - Opening an existing file/importing data (not app.modified)
        # 4. First run or closed file (self.first_run_or_closed)
        # 5. UI changes (ui_change=True) - per user requirement to validate only at save/export
        should_skip_validation = (
            initial
            or skip_validation
            or ui_change  # Always skip validation for UI changes
            or self.first_run_or_closed
            or (self.using_default_values and (self.app.current_file is None or not self.app.modified))
        )

        # Get description if field exists
        description = ""
        if hasattr(self.app.ui, 'VersionDescription'):
            description = self.app.ui.VersionDescription.toPlainText().strip()
        else:
            description = self.default_version_info["description"]

        # Create a new metadata dictionary with current values
        new_metadata = {
            "version": version_str,
            "date": version_date.toString("yyyy-MM-dd"),
            "editor": editor_name,
            "description": description
        }

        # Validate version is greater than previous (unless validation is skipped)
        if not should_skip_validation and "metadata" in self.app.signals_data:
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
                    elif isinstance(self.app.ui.VersionNumber, QtWidgets.QPlainTextEdit):
                        self.app.ui.VersionNumber.setPlainText(old_metadata.get("version", "1.0"))
                    elif hasattr(self.app.ui.VersionNumber, "setValue"):
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

        # Only mark as modified if not initial setup and data was actually changed
        if not initial:
            # Check if any values actually changed before marking as modified
            old_metadata = self.original_signals_data.get("metadata", {}) if self.original_signals_data else {}
            # Don't mark as modified if editor name is just the placeholder text
            is_placeholder = lambda name: not name or name.isspace() or name.lower() in ["please enter your name", "enter your name"]

            editor_changed = (editor_name != old_metadata.get("editor", "") and
                             not (is_placeholder(editor_name) and is_placeholder(old_metadata.get("editor", ""))))

            if (version_str != old_metadata.get("version", "") or
                editor_changed or
                description != old_metadata.get("description", "")):
                self.app.modified = True
                self.update_window_title()

        # If values match defaults, set the flag
        self.using_default_values = (
            version_str == self.default_version_info["version"] and
            editor_name == self.default_version_info["editor"] and
            description == self.default_version_info["description"]
        )

        return True

    def validate_version_date(self):
        """Validate the version date is today or in the future

        Returns:
            bool: True if date is valid or validation should be skipped
        """
        # Accept loaded or imported data as-is if not modified
        if not self.app.modified and self.app.current_file is not None:
            return True

        # Skip validation when using default values for new files
        if self.using_default_values and self.app.current_file is None:
            return True

        # Validate only for user edits during save/export operations
        # Get datetime from QDateTimeEdit widget
        version_datetime = self.app.ui.VersionDate.dateTime().toPyDateTime()
        version_date = version_datetime.date()
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
        try:
            # Process events before updating to keep UI responsive
            QtWidgets.QApplication.processEvents()

            # Initialize components if they don't exist
            if not hasattr(self.app.ui, 'SignalCnt'):
                self._create_signal_count_widgets()
                # Process events after widget creation
                QtWidgets.QApplication.processEvents()

            # Safety check for signal_data
            if not hasattr(self.app, 'signals_data') or self.app.signals_data is None:
                print("Warning: signals_data not initialized, skipping count update")
                return

            # Update the count safely
            signal_count = len(self.app.signals_data.get("signals", {}))

            # Check if SignalCnt still exists and is valid before accessing
            if hasattr(self.app.ui, 'SignalCnt') and self.app.ui.SignalCnt is not None:
                self.app.ui.SignalCnt.setValue(signal_count)
                # Process events after updating
                QtWidgets.QApplication.processEvents()
            else:
                print("Warning: SignalCnt widget not available, skipping update")
        except Exception as e:
            print(f"Error updating signal count: {e}")
            import traceback
            traceback.print_exc()
            # Ensure UI remains responsive even after error
            QtWidgets.QApplication.processEvents()

    def on_signal_selection_changed(self):
        # This handles when the signal selection changes
        selected_items = self.signal_tree.selectedItems()
        if selected_items:
            signal_name = selected_items[0].text(0)
            if "signals" in self.app.signals_data and signal_name in self.app.signals_data["signals"]:
                signal_info = self.app.signals_data["signals"][signal_name]
                self.display_signal_details(signal_name, signal_info)

    def display_signal_details(self, signal_name, signal_info):
        """Display signal details in the SiganlDetailsFrame with the new SignalAttributeSection scrollArea"""
        try:
            print(f"Displaying details for signal: {signal_name}")

            # Get the SiganlDetailsFrame
            details_frame = self.app.ui.SiganlDetailsFrame
            if not details_frame:
                print("ERROR: SiganlDetailsFrame not found")
                return

            # Check if we already created the scroll area
            attr_scroll = None
            if hasattr(self.app.ui, "SignalAttributeSection"):
                attr_scroll = self.app.ui.SignalAttributeSection
            else:
                attr_scroll = details_frame.findChild(QtWidgets.QScrollArea, "SignalAttributeSection")

            # If not found or not valid, create the scroll area
            if not attr_scroll or not isinstance(attr_scroll, QtWidgets.QScrollArea):
                attr_scroll = self.setup_signal_attribute_section(details_frame)
                if not attr_scroll:
                    print("ERROR: Failed to create SignalAttributeSection")
                    return

                # Store direct reference to the scroll area in the UI
                self.app.ui.SignalAttributeSection = attr_scroll
                print("Created SignalAttributeSection during signal display")

            # Create content for the scroll area
            content_widget = QtWidgets.QWidget()
            attr_scroll.setWidget(content_widget)

            # Use form layout for signal attributes
            form_layout = QtWidgets.QFormLayout(content_widget)
            content_widget.setLayout(form_layout)  # Explicitly set layout to content widget
            form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

            # Add signal name as a title
            title_label = QtWidgets.QLabel(signal_name)
            title_font = QtGui.QFont()
            title_font.setBold(True)
            title_font.setPointSize(12)
            title_label.setFont(title_font)
            form_layout.addRow(QtWidgets.QLabel("Signal Name:"), title_label)

            # Add separator line
            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.HLine)
            line.setFrameShadow(QtWidgets.QFrame.Sunken)
            form_layout.addRow(line)

            # Display SignalInternalInfo first if it exists (with special formatting)
            if "SignalInternalInfo" in signal_info:
                internal_value = str(signal_info["SignalInternalInfo"])
                internal_label = QtWidgets.QLabel(internal_value)
                internal_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                internal_font = QtGui.QFont()
                internal_font.setBold(True)
                internal_label.setFont(internal_font)
                form_layout.addRow("SignalInternalInfo:", internal_label)
                print(f"Added SignalInternalInfo: {internal_value}")

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
                    form_layout.addRow(f"{key.replace('_', ' ').title()}:", value_label)

            # If it's a structure type, show fields
            if signal_info.get("is_struct", False) and "struct_fields" in signal_info:
                struct_group = QGroupBox("Structure Fields")
                struct_layout = QtWidgets.QVBoxLayout(struct_group)
                struct_group.setLayout(struct_layout)

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
                form_layout.addRow(struct_group)

            # Show core destinations if available
            core_targets = []
            for key in signal_info:
                if key.startswith("core_") and signal_info[key]:
                    core_name = key[5:].replace('_', '.')
                    core_targets.append(core_name)

            if core_targets:
                dest_label = QtWidgets.QLabel(", ".join(core_targets))
                dest_label.setWordWrap(True)
                form_layout.addRow("Destination Cores:", dest_label)

            # Add Edit button at the bottom of the form
            edit_button = QPushButton("Edit Signal")
            edit_button.clicked.connect(lambda: self.app.signal_ops.edit_signal_details(signal_name))
            form_layout.addRow("", edit_button)

            print(f"Signal details displayed for {signal_name}")

            # Make sure the form is visible
            content_widget.show()
            attr_scroll.show()
            details_frame.show()

        except Exception as e:
            print(f"Error displaying signal details: {e}")
            traceback.print_exc()

    def update_core_info(self):
        """Update the Core Info tree widget with configuration data organized by SOC"""
        try:
            # Find the correct tree widget regardless of UI version
            tree = self._get_core_tree_widget()
            if not tree:
                print("ERROR: Could not find or create core info tree widget")
                return

            # Clear the tree widget
            tree.clear()

            # Get core info from signals_data
            core_info = self.app.signals_data.get("core_info", {})

            if not core_info:
                tree.addTopLevelItem(QTreeWidgetItem(["No core information available"]))
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

        except Exception as e:
            print(f"ERROR in update_core_info: {e}")
            import traceback
            traceback.print_exc()

    def _get_core_tree_widget(self):
        """Get the core tree widget, creating it if necessary"""

        # First try to find the correct scroll area based on the new UI structure
        soc_area = getattr(self.app.ui, 'Soc_CoreInfo', None)
        if soc_area:
            scroll_area = soc_area
        else:
            scroll_area = self.app.findChild(QtWidgets.QScrollArea, "Soc_CoreInfo")
            if not scroll_area:
                print("ERROR: Neither APIscrollArea nor Soc_CoreInfo found in UI")
                return None

        # Get or create a content widget
        content_widget = scroll_area.widget()
        if not content_widget:
            content_widget = QtWidgets.QWidget()
            scroll_area.setWidget(content_widget)
            print("DEBUG: Created new content widget for scroll area")

        # Set up a layout if needed
        layout = content_widget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout(content_widget)
            print("DEBUG: Created new layout for content widget")

        # Check if there's already a tree widget in this layout
        tree_widget = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QtWidgets.QTreeWidget):
                tree_widget = widget
                print("DEBUG: Found existing tree widget in layout")
                break

        # Create a tree widget if we didn't find one
        if not tree_widget:
            # Create a tree widget
            tree_widget = QtWidgets.QTreeWidget()
            tree_widget.setHeaderLabels(["Core Information"])
            tree_widget.setColumnWidth(0, 300)
            layout.addWidget(tree_widget)
            print("DEBUG: Created new tree widget")

        # Store references in the app
        self.app.ui.core_info_tree = tree_widget

        # Update the reference to use the new scroll area
        self.app.ui.scrollArea_core_specific = scroll_area  # For backwards compatibility
        self.app.ui.api_scroll_area = scroll_area  # New reference with consistent naming

        print("DEBUG: Successfully created/found core tree widget")
        return tree_widget

    def _ensure_core_info_components(self):
        """Ensure all core info components are properly set up"""
        # Just call _get_core_tree_widget which will create everything if needed
        tree = self._get_core_tree_widget()
        if tree:
            print("Core info components successfully set up")
            return True
        else:
            print("ERROR: Failed to set up core info components")
            return False

    """ def refresh_signal_tree(self):
        # Clear and repopulate the signal tree
        self.signal_tree.clear()
        if "signals" in self.app.signals_data:
            for signal_name, signal_info in self.app.signals_data["signals"].items():
                item = QTreeWidgetItem([
                    signal_name,
                    signal_info.get("DataType", ""),  # Changed from "type" to "DataType"
                    signal_info.get("description", "")
                ])
                self.signal_tree.addTopLevelItem(item) """

    def soc_selection_changed(self, index):
        if index > 0:  # Not the default "Select SOC" item
            soc_type = self.app.ui.SOCListComboBox.currentText()
            self.app.signals_data["soc_type"] = soc_type
            self.app.modified = True
            self.update_window_title()
            self.update_core_info()

    def build_type_changed(self, index):
        if index > 0:  # Not the default "Select Build Type" item
            build_type = self.app.ui.BuildImageComboBox.currentText()

            # Save current API configuration first
            self.save_api_configuration()

            self.app.signals_data["build_type"] = build_type
            self.app.modified = True
            self.update_window_title()

            # Update API configuration UI
            self.update_api_configuration()

            # Update other UI components that depend on build type
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
        """Event filter that no longer validates date changes in real-time"""
        # Per user requirement, the date validation should only happen
        # during Save/Save As/Export as Excel operations, not during UI interaction
        #
        # if obj == self.app.ui.VersionDate and event.type() == QtCore.QEvent.FocusOut:
        #     selected_date = obj.date().toPyDate()
        #     current_date = datetime.now().date()
        #     if selected_date < current_date:
        #         QMessageBox.warning(
        #             self.app,
        #             "Date Warning",
        #             "Selected date is not in the future. You may need to update it before performing operations."
        #         )

        return super(UIHelpers, self).eventFilter(obj, event)

    def initialize_missing_ui_components(self):
        """Initialize UI components that might be missing in the UI"""
        # Add SignalCnt if it doesn't exist
        if not hasattr(self.app.ui, 'SignalCnt'):
            self._create_signal_count_widgets()

        # Ensure core info components are initialized
        self._ensure_core_info_components()

        # Set up the signal tree in SignalEntryScrollArea
        # Only set up if it doesn't exist yet
        if not hasattr(self, 'signal_tree') or self.signal_tree is None:
            self.setup_tree_widget()

        # Set up toolbar icons
        self.setup_toolbar_icons()

        # Ensure widget connections are set up - only once
        self.ensure_widget_connections()

        print("All UI components initialized")

    def _create_signal_count_widgets(self):
        """Create SignalCnt label and spinner in the Signal Data Base tab"""
        try:
            # Check if widgets already exist to avoid duplication
            if hasattr(self.app.ui, 'SignalCnt') and self.app.ui.SignalCnt is not None:
                print("SignalCnt widgets already exist, skipping creation")
                return

            # Process events before creating widgets
            QtWidgets.QApplication.processEvents()

            # Find the Signal Data Base tab
            tab_widget = self.app.ui.tabWidget
            signal_tab = None

            for i in range(tab_widget.count()):
                if tab_widget.tabText(i) == "Signal Data Base":
                    signal_tab = tab_widget.widget(i)
                    break

            if not signal_tab:
                print("ERROR: Signal Data Base tab not found")
                return

            # Find the layout containing BoardListComboBox
            if not hasattr(self.app.ui, 'BoardListComboBox') or self.app.ui.BoardListComboBox is None:
                print("ERROR: BoardListComboBox not found")
                return

            board_list = self.app.ui.BoardListComboBox
            parent_widget = board_list.parentWidget()

            if not parent_widget:
                print("ERROR: Parent widget of BoardListComboBox not found")
                return

            # Find the horizontal layout containing BoardListComboBox
            board_layout = None
            for layout in parent_widget.findChildren(QtWidgets.QHBoxLayout):
                try:
                    for i in range(layout.count()):
                        if layout.itemAt(i) and layout.itemAt(i).widget() == board_list:
                            board_layout = layout
                            break
                    if board_layout:
                        break
                except Exception as e:
                    print(f"Error checking layout items: {e}")
                    continue

            if not board_layout:
                print("WARNING: Could not find layout for BoardListComboBox, trying alternative method")
                # Alternative: look for SignalOpFrame which contains the signal count in some UI versions
                signal_op_frame = self.app.findChild(QtWidgets.QFrame, "SignalOpFrame")
                if signal_op_frame:
                    # Look for existing SignalCnt in SignalOpFrame
                    signal_cnt = signal_op_frame.findChild(QtWidgets.QSpinBox, "SignalCnt")
                    if signal_cnt:
                        print("Found existing SignalCnt in SignalOpFrame")
                        self.app.ui.SignalCnt = signal_cnt
                        # Try to find the label as well
                        signal_cnt_label = signal_op_frame.findChild(QtWidgets.QLabel, "label_4")
                        if signal_cnt_label:
                            self.app.ui.SignalCntLabel = signal_cnt_label
                        return
                    else:
                        print("ERROR: Could not find SignalCnt in SignalOpFrame")
                        return
                else:
                    print("ERROR: Could not find layout or SignalOpFrame")
                    return

            # Create SignalCnt label and spin box
            signal_cnt_label = QtWidgets.QLabel("Signal Count:", self.app)
            signal_cnt_spin = QtWidgets.QSpinBox(self.app)
            signal_cnt_spin.setReadOnly(True)
            signal_cnt_spin.setEnabled(False)
            signal_cnt_spin.setMaximum(99999)
            signal_cnt_spin.setObjectName("SignalCnt")  # Set object name for easier finding

            # Calculate current signal count safely
            signal_count = 0
            if hasattr(self.app, 'signals_data') and self.app.signals_data:
                signal_count = len(self.app.signals_data.get("signals", {}))
            signal_cnt_spin.setValue(signal_count)

            # Store reference in UI
            self.app.ui.SignalCntLabel = signal_cnt_label
            self.app.ui.SignalCnt = signal_cnt_spin

            # Add to layout (at the beginning, before BoardListComboBox)
            board_layout.insertWidget(0, signal_cnt_label)
            board_layout.insertWidget(1, signal_cnt_spin)

            # Process events after widget creation
            QtWidgets.QApplication.processEvents()

            print("SignalCnt widgets added successfully")
        except Exception as e:
            print(f"Error creating SignalCnt widgets: {e}")
            import traceback
            traceback.print_exc()
            # Make UI responsive even after error
            QtWidgets.QApplication.processEvents()

    def ensure_widget_connections(self):
        """Ensure all widget connections are properly set up"""
        # Connect SOC and Build type change events if not already connected
        try:
            # Only set up connections if not already done
            if not hasattr(self, '_widget_connections_setup') or not self._widget_connections_setup:
                # Disconnect first to avoid multiple connections
                try:
                    self.app.ui.SOCListComboBox.currentIndexChanged.disconnect(self.soc_selection_changed)
                except:
                    pass
                # Reconnect
                self.app.ui.SOCListComboBox.currentIndexChanged.connect(self.soc_selection_changed)

                # Do the same for build type
                try:
                    self.app.ui.BuildImageComboBox.currentIndexChanged.disconnect(self.build_type_changed)
                except:
                    pass
                self.app.ui.BuildImageComboBox.currentIndexChanged.connect(self.build_type_changed)

                # Mark connections as set up
                self._widget_connections_setup = True
        except Exception as e:
            print(f"Error setting up widget connections: {e}")
            import traceback
            traceback.print_exc()

    def print_ui_diagnostics(self):
        """Print diagnostic information about UI components for troubleshooting"""
        try:
            print("\n=== UI COMPONENT DIAGNOSTICS ===")

            # Check if tab_2 (Project Specific Config tab) exists
            tab_widget = getattr(self.app.ui, 'tabWidget', None)
            if (tab_widget):
                tab_2 = None
                for i in range(tab_widget.count()):
                    if tab_widget.tabText(i) == "Project Specific Config":
                        tab_2 = tab_widget.widget(i)
                        break
                print(f"  Project Specific Config Tab: {'✅ Found' if tab_2 else '❌ Missing'}")
            else:
                print("  tabWidget: ❌ Missing")

            # Check for APIFrame and APIscrollArea
            api_frame = self.app.findChild(QtWidgets.QFrame, "APIFrame")
            print(f"  APIFrame: {'✅ Found' if api_frame else '❌ Missing'}")

            api_scroll_area = self.app.findChild(QtWidgets.QScrollArea, "APIscrollArea")
            print(f"  APIscrollArea: {'✅ Found' if api_scroll_area else '❌ Missing'}")

            # Check for old and new reference to scroll area
            scroll_specific = getattr(self.app.ui, 'scrollArea_core_specific', None)
            print(f"  scrollArea_core_specific reference: {'✅ Found' if scroll_specific else '❌ Missing'}")

            api_scroll = getattr(self.app.ui, 'api_scroll_area', None)
            print(f"  api_scroll_area reference: {'✅ Found' if api_scroll else '❌ Missing'}")

            # Core info components
            soc_core_info = getattr(self.app.ui, 'Soc_CoreInfo', None)
            print(f"  Soc_CoreInfo: {'✅ Found' if soc_core_info else '❌ Missing'}")

            core_tree = getattr(self.app.ui, 'core_info_tree', None)
            print(f"  core_info_tree: {'✅ Found' if core_tree else '❌ Missing'}")

            # Check for container and layout in main app
            core_details_container = getattr(self.app, 'core_details_container', None)
            print(f"  app.core_details_container: {'✅ Found' if core_details_container else '❌ Missing'}")

            # Rest of diagnostic info (unchanged)
            # ...existing diagnostic code...

            print("\n===============================\n")

        except Exception as e:
            print(f"Error in diagnostics: {e}")
            import traceback
            traceback.print_exc()

    def fix_ui_integration(self):
        """Fix integration between old UI references and new UI structure"""
        try:
            # First, locate the APIscrollArea which is part of the new UI
            api_scroll_area = self.app.findChild(QtWidgets.QScrollArea, "APIscrollArea")

            if api_scroll_area:
                # If we found the new scroll area, ensure our references are updated
                self.app.ui.api_scroll_area = api_scroll_area
                self.app.ui.scrollArea_core_specific = api_scroll_area  # Legacy reference

                # Ensure the tree widget is properly set up in the APIscrollArea
                self._get_core_tree_widget()

                print("Successfully integrated with new UI structure (APIscrollArea)")
                return True
            else:
                print("WARNING: Could not find APIscrollArea in the UI")
                return False

        except Exception as e:
            print(f"Error fixing UI integration: {e}")
            import traceback
            traceback.print_exc()
            return False

    def setup_toolbar_icons(self):
        """Set up toolbar icons and connect them to their respective actions"""
        try:
            # Get reference to toolbar
            toolbar = self.app.ui.mainToolBar
            if not toolbar:
                print("Toolbar not found!")
                return

            # Clear any existing actions
            toolbar.clear()

            # Define the actions to add to toolbar with their icons
            toolbar_actions = [
                ("actionNew", "NewFile.png"),
                ("actionOpen", "OpenFile.png"),
                None,  # Separator
                ("actionSave", "Save.png"),
                ("actionSave_As", "SaveAs.png"),
                None,  # Separator
                ("actionExport_To_Excel", "ExportToExcel.png"),
                ("actionImport_From_Excel", "Import.png"),
                None,  # Separator
                ("actionAdd_Entry", "AddEntry.png"),
                ("actionDelete_Entry", "RemoveEntry.png"),
                ("actionUpdate_Entry", "UpdateEntry.png"),
                None,  # Separator
                ("actionUndo", "Undo.png"),
                ("actionRedo", "Redo.png")
            ]

            # Add actions to toolbar
            for item in toolbar_actions:
                if item is None:
                    # Add separator
                    toolbar.addSeparator()
                    continue

                action_name, icon_file = item

                # Skip if action doesn't exist
                if not hasattr(self.app.ui, action_name):
                    print(f"Action {action_name} not found!")
                    continue

                # Get action from UI
                action = getattr(self.app.ui, action_name)

                # Set icon if in cache
                if hasattr(self.app, "_icon_cache") and icon_file in self.app._icon_cache:
                    action.setIcon(self.app._icon_cache[icon_file])

                # Add to toolbar
                toolbar.addAction(action)

            print("Toolbar icons set up successfully")

        except Exception as e:
            print(f"Error setting up toolbar icons: {e}")
            import traceback
            traceback.print_exc()

    def handle_signal_selected(self):
        """Handle signal selection with improved error handling to prevent crashes"""
        try:
            # For QTableWidget, we need to use selectedIndexes() or currentRow()
            selected_rows = self.signal_tree.selectionModel().selectedRows()
            if not selected_rows:
                print("No row selected")
                return

            # Get the row index of the first selected row
            row_index = selected_rows[0].row()

            # Get signal name from first column (index 0)
            name_item = self.signal_tree.item(row_index, 0)
            if not name_item:
                print("Invalid selected row item")
                return

            signal_name = name_item.text()
            if not signal_name:
                print("Empty signal name")
                return

            print(f"Signal selected: {signal_name}")

            # Get signal data from signals_data dictionary
            signals = self.app.signals_data.get("signals", {})
            if not signals:
                print("No signals data available")
                return

            # Find selected signal
            signal_data = signals.get(signal_name)
            if not signal_data:
                print(f"No data found for signal: {signal_name}")
                return

            # Display signal details in the SiganlDetailsFrame
            self.display_signal_details(signal_name, signal_data)

        except Exception as e:
            print(f"Error handling signal selection: {e}")
            import traceback
            traceback.print_exc()
            # Show error message to user
            QMessageBox.warning(self.app, "Error",
                              f"An error occurred while loading signal details.\n{str(e)}")

    def setup_signal_attribute_section(self, parent_frame):
        """
        Set up the Signal Attribute section in the provided frame
        without creating unnecessary 'Signal Attribute' label

        Args:
            parent_frame: The parent frame to add the section to
        """
        try:
            # Clear any existing content in the frame
            for child in parent_frame.findChildren(QtWidgets.QWidget):
                if child.objectName() != "label_2":  # Keep the label_2 widget to avoid crashes
                    child.setParent(None)

            # Create a new vertical layout for the frame
            if parent_frame.layout():
                # Clear existing layout
                while parent_frame.layout().count():
                    item = parent_frame.layout().takeAt(0)
                    widget = item.widget()
                    if widget and widget.objectName() != "label_2":  # Keep the label_2 widget
                        widget.setParent(None)
                # Delete old layout
                QtWidgets.QWidget().setLayout(parent_frame.layout())

            # Create fresh layout
            layout = QtWidgets.QVBoxLayout(parent_frame)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)

            # Create the attribute section - skip creating the redundant label
            attribute_section = QtWidgets.QScrollArea(parent_frame)
            attribute_section.setWidgetResizable(True)
            attribute_section.setObjectName("SignalAttributeSection")

            # Store reference
            self.app.ui.SignalAttributeSection = attribute_section

            # Add to main layout
            layout.addWidget(attribute_section)

            # Hide label_2 if it exists
            label_2 = parent_frame.findChild(QtWidgets.QLabel, "label_2")
            if label_2:
                label_2.setVisible(False)

            print("Signal Attribute section set up successfully")
            return attribute_section

        except Exception as e:
            print(f"Error setting up Signal Attribute section: {e}")
            import traceback
            traceback.print_exc()
            return None

    def add_attribute_field(self, layout, label_text, object_name):
        """
        Add a field to the attribute section

        Args:
            layout: The layout to add the field to
            label_text: Text for the label
            object_name: Object name for the input field
        """
        # Create label
        label = QtWidgets.QLabel(label_text)

        # Create input field
        input_field = QtWidgets.QLineEdit()
        input_field.setObjectName(object_name)

        # Add to layout
        layout.addRow(label, input_field)

    def display_signal_details_internal(self, signal_name, signal_info):
        """Display signal details in the SiganlDetailsFrame with the new SignalAttributeSection scrollArea"""
        try:
            print(f"Displaying details for signal: {signal_name}")

            # Make UI responsive before processing
            QtWidgets.QApplication.processEvents()

            # Get the SiganlDetailsFrame - note the spelling matches your UI structure
            details_frame = self.app.ui.SiganlDetailsFrame
            if not details_frame:
                print("ERROR: SiganlDetailsFrame not found")
                return

            # Check if we already created the scroll area
            attr_scroll = details_frame.findChild(QtWidgets.QScrollArea, "SignalAttributeSection")

            # If not found, create the scroll area without the redundant label
            if not attr_scroll:
                attr_scroll = self.setup_signal_attribute_section(details_frame)
                if not attr_scroll:
                    print("ERROR: Failed to create SignalAttributeSection")
                    return
                # Process events after creating scroll area
                QtWidgets.QApplication.processEvents()

            # Create content for the scroll area
            content_widget = QtWidgets.QWidget()
            attr_scroll.setWidget(content_widget)

            # Use form layout for signal attributes
            form_layout = QtWidgets.QFormLayout(content_widget)
            content_widget.setLayout(form_layout)  # Explicitly set layout to content widget
            form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

            # Add signal name as a title
            title_label = QtWidgets.QLabel(signal_name)
            title_font = QtGui.QFont()
            title_font.setBold(True)
            title_font.setPointSize(12)
            title_label.setFont(title_font)
            form_layout.addRow(QtWidgets.QLabel("Signal Name:"), title_label)

            # Process events after adding title
            QtWidgets.QApplication.processEvents()

            # Add separator line
            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.HLine)
            line.setFrameShadow(QtWidgets.QFrame.Sunken)
            form_layout.addRow(line)

            # Safety check for signal_info
            if signal_info is None:
                print(f"Warning: Signal info is None for {signal_name}")
                error_label = QtWidgets.QLabel("Signal information not available")
                form_layout.addRow(error_label)
                return

            # Display SignalInternalInfo first if it exists (with special formatting)
            if "SignalInternalInfo" in signal_info:
                try:
                    internal_value = str(signal_info["SignalInternalInfo"])
                    internal_label = QtWidgets.QLabel(internal_value)
                    internal_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    internal_font = QtGui.QFont()
                    internal_font.setBold(True)
                    internal_label.setFont(internal_font)
                    form_layout.addRow("SignalInternalInfo:", internal_label)
                    print(f"Added SignalInternalInfo: {internal_value}")
                except Exception as e:
                    print(f"Error displaying SignalInternalInfo: {e}")

            # Process events periodically
            QtWidgets.QApplication.processEvents()

            # Display key signal properties in a readable format
            for key in ['Variable_Port_Name', 'DataType', 'Memory Region', 'Buffer count_IPC',
                    'Type', 'InitValue', 'Notifiers', 'Source', 'Impl_Approach',
                    'GetObjRef', 'SM_Buff_Count', 'Timeout', 'Periodicity',
                    'ASIL', 'Checksum', 'description']:
                try:
                    if key in signal_info:
                        value = signal_info[key]
                        # Format boolean values as Yes/No
                        if isinstance(value, bool):
                            value = "Yes" if value else "No"
                        # Create a label with the value
                        value_label = QtWidgets.QLabel(str(value))
                        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                        form_layout.addRow(f"{key.replace('_', ' ').title()}:", value_label)
                except Exception as e:
                    print(f"Error displaying property {key}: {e}")

                # Process events every few items
                if key in ['DataType', 'Source', 'description']:
                    QtWidgets.QApplication.processEvents()

            # If it's a structure type, show fields
            if signal_info.get("is_struct", False) and "struct_fields" in signal_info:
                try:
                    struct_group = QGroupBox("Structure Fields")
                    struct_layout = QtWidgets.QVBoxLayout(struct_group)
                    struct_group.setLayout(struct_layout)

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
                    form_layout.addRow(struct_group)

                    # Process events after adding structure fields
                    QtWidgets.QApplication.processEvents()
                except Exception as e:
                    print(f"Error displaying structure fields: {e}")

            # Show core destinations if available
            try:
                core_targets = []
                for key in signal_info:
                    if key.startswith("core_") and signal_info[key]:
                        core_name = key[5:].replace('_', '.')
                        core_targets.append(core_name)

                if core_targets:
                    dest_label = QtWidgets.QLabel(", ".join(core_targets))
                    dest_label.setWordWrap(True)
                    form_layout.addRow("Destination Cores:", dest_label)
            except Exception as e:
                print(f"Error displaying core destinations: {e}")

            # Process events before adding edit button
            QtWidgets.QApplication.processEvents()

            # Add Edit button at the bottom of the form
            try:
                edit_button = QPushButton("Edit Signal")
                edit_button.clicked.connect(lambda: self.app.signal_ops.edit_signal_details(signal_name))
                form_layout.addRow("", edit_button)
            except Exception as e:
                print(f"Error adding edit button: {e}")

            print(f"Signal details displayed for {signal_name}")

            # Make sure the form is visible
            content_widget.show()
            attr_scroll.show()
            details_frame.show()

            # Final processEvents to ensure UI is fully updated
            QtWidgets.QApplication.processEvents()

        except Exception as e:
            print(f"Error displaying signal details: {e}")
            traceback.print_exc()
            # Ensure UI remains responsive even after error
            QtWidgets.QApplication.processEvents()

    def _reconnect_ui_signals(self):
        """Reconnect UI signals after file loading"""
        try:
            print("Starting UI signal reconnection SAFELY...")

            # Process events before reconnecting
            QtWidgets.QApplication.processEvents()

            # Initialize signal connection state dictionary if not exists
            if not hasattr(self, '_signal_connections_state'):
                print("Creating new signal_connections_state dictionary")
                self._signal_connections_state = {
                    'signal_tree': False,
                    'soc_list': False,
                    'build_list': False
                }

            # Reconnect signal tree if it exists and should be reconnected
            print("Checking signal tree reconnection...")
            if hasattr(self, 'signal_tree') and self.signal_tree:
                try:
                    reconnect_tree = self._signal_connections_state.get('signal_tree', False)
                    print(f"Signal tree reconnection state: {reconnect_tree}")

                    # Make sure the function exists before connecting
                    if reconnect_tree and hasattr(self, 'handle_signal_selected'):
                        # Create a safe reference to the function
                        handle_func = self.handle_signal_selected
                        if handle_func:
                            # First check if there are existing connections and disconnect
                            try:
                                self.signal_tree.itemSelectionChanged.disconnect()
                                print("Disconnected existing signal tree connections")
                            except Exception as e:
                                print(f"No existing signal tree connections to disconnect: {e}")

                            # Now reconnect safely
                            try:
                                self.signal_tree.itemSelectionChanged.connect(handle_func)
                                print("Reconnected signal tree selection signal")
                            except Exception as e:
                                print(f"Failed to connect signal tree signal: {e}")
                except Exception as e:
                    print(f"Error safely reconnecting signal tree: {e}")

            # Process events after reconnecting signal tree
            QtWidgets.QApplication.processEvents()

            # Connect SOC combobox only if it exists and should be reconnected
            print("Checking SOC combobox reconnection...")
            if hasattr(self.app.ui, 'SOCListComboBox') and self.app.ui.SOCListComboBox:
                try:
                    reconnect_soc = self._signal_connections_state.get('soc_list', False)
                    print(f"SOC list reconnection state: {reconnect_soc}")

                    if reconnect_soc and hasattr(self, 'soc_selection_changed'):
                        # Create a safe reference to the function
                        soc_func = self.soc_selection_changed
                        if soc_func:
                            # First disconnect any existing connections
                            try:
                                self.app.ui.SOCListComboBox.currentIndexChanged.disconnect()
                                print("Disconnected existing SOC list connections")
                            except Exception as e:
                                print(f"No existing SOC list connections to disconnect: {e}")

                            # Now reconnect safely
                            try:
                                self.app.ui.SOCListComboBox.currentIndexChanged.connect(soc_func)
                                print("Reconnected SOC list signal")
                            except Exception as e:
                                print(f"Failed to connect SOC list signal: {e}")
                except Exception as e:
                    print(f"Error safely reconnecting SOC list: {e}")

            # Process events after SOC combobox reconnection
            QtWidgets.QApplication.processEvents()

            # Connect Build type combobox only if it exists and should be reconnected
            print("Checking Build type combobox reconnection...")
            if hasattr(self.app.ui, 'BuildImageComboBox') and self.app.ui.BuildImageComboBox:
                try:
                    reconnect_build = self._signal_connections_state.get('build_list', False)
                    print(f"Build list reconnection state: {reconnect_build}")

                    if reconnect_build and hasattr(self, 'build_type_changed'):
                        # Create a safe reference to the function
                        build_func = self.build_type_changed
                        if build_func:
                            # First disconnect any existing connections
                            try:
                                self.app.ui.BuildImageComboBox.currentIndexChanged.disconnect()
                                print("Disconnected existing Build list connections")
                            except Exception as e:
                                print(f"No existing Build list connections to disconnect: {e}")

                            # Now reconnect safely
                            try:
                                self.app.ui.BuildImageComboBox.currentIndexChanged.connect(build_func)
                                print("Reconnected Build list signal")
                            except Exception as e:
                                print(f"Failed to connect Build list signal: {e}")
                except Exception as e:
                    print(f"Error safely reconnecting Build list: {e}")

            # Process events after reconnecting combos
            QtWidgets.QApplication.processEvents()

            print("SKIPPING toolbar icon reconnection to avoid crashes...")

            # Mark as set up - this should be done only if successful
            self._widget_connections_setup = True

            print("UI signals successfully reconnected")

            # Final process events after reconnecting
            QtWidgets.QApplication.processEvents()
        except Exception as e:
            print(f"Error reconnecting UI signals: {e}")
            import traceback
            traceback.print_exc()
            # Make UI responsive even after failure
            QtWidgets.QApplication.processEvents()

    def _disconnect_ui_signals(self):
        """Temporarily disconnect UI signals to prevent crashes during file loading"""
        try:
            # Store connection state
            self._signal_connections_state = {}

            # Disconnect signal tree selection if connected
            if hasattr(self, 'signal_tree') and self.signal_tree:
                try:
                    self.signal_tree.itemSelectionChanged.disconnect()
                    self._signal_connections_state['signal_tree'] = True
                    print("Disconnected signal tree selection signal")
                except:
                    self._signal_connections_state['signal_tree'] = False
                    print("Signal tree selection was not connected")

            # Disconnect SOC combobox
            if hasattr(self.app.ui, 'SOCListComboBox'):
                try:
                    self.app.ui.SOCListComboBox.currentIndexChanged.disconnect()
                    self._signal_connections_state['soc_list'] = True
                    print("Disconnected SOC list signal")
                except:
                    self._signal_connections_state['soc_list'] = False
                    print("SOC list was not connected")

            # Disconnect Build type combobox
            if hasattr(self.app.ui, 'BuildImageComboBox'):
                try:
                    self.app.ui.BuildImageComboBox.currentIndexChanged.disconnect()
                    self._signal_connections_state['build_list'] = True
                    print("Disconnected Build list signal")
                except:
                    self._signal_connections_state['build_list'] = False
                    print("Build list was not connected")

            # Reset the widget_connections_setup flag
            self._widget_connections_setup = False

            print("UI signals successfully disconnected")
        except Exception as e:
            print(f"Error disconnecting UI signals: {e}")
            import traceback
            traceback.print_exc()

    def clear_signal_attribute_section(self):
        """
        Safely clear the signal attribute section to prevent segmentation faults.
        This creates a completely new widget and properly handles existing references.
        """
        try:
            print("Safely clearing SignalAttributeSection...")

            # Get the SiganlDetailsFrame - note the spelling matches the UI structure
            if hasattr(self.app.ui, 'SiganlDetailsFrame') and self.app.ui.SiganlDetailsFrame is not None:
                details_frame = self.app.ui.SiganlDetailsFrame

                # Process events to ensure UI is responsive
                QtWidgets.QApplication.processEvents()

                # Find existing SignalAttributeSection or create it if it doesn't exist
                attr_scroll = details_frame.findChild(QtWidgets.QScrollArea, "SignalAttributeSection")

                # If no scroll area exists, create a new one from scratch
                if not attr_scroll or not isinstance(attr_scroll, QtWidgets.QScrollArea):
                    # Create a new layout for the frame if needed
                    if details_frame.layout() is None:
                        layout = QtWidgets.QVBoxLayout(details_frame)
                        layout.setContentsMargins(5, 5, 5, 5)
                    else:
                        layout = details_frame.layout()

                    # Create a new scroll area
                    attr_scroll = QtWidgets.QScrollArea(details_frame)
                    attr_scroll.setWidgetResizable(True)
                    attr_scroll.setObjectName("SignalAttributeSection")

                    # Add it to layout if not already there
                    layout.addWidget(attr_scroll)

                    # Store reference to ensure access
                    self.app.ui.SignalAttributeSection = attr_scroll
                    print("Created new SignalAttributeSection")

                # Create empty content for the scroll area
                empty_widget = QtWidgets.QWidget()
                empty_layout = QtWidgets.QVBoxLayout(empty_widget)

                # Create "No signal selected" message
                empty_label = QtWidgets.QLabel("No signal selected")
                empty_label.setAlignment(QtCore.Qt.AlignCenter)
                empty_layout.addWidget(empty_label)

                # Set the empty widget as scroll area content
                # Save the previous widget for proper cleanup
                previous_widget = attr_scroll.takeWidget()

                # Process events before setting the new widget
                QtWidgets.QApplication.processEvents()

                # Set the new empty widget
                attr_scroll.setWidget(empty_widget)

                # Process events after widget change
                QtWidgets.QApplication.processEvents()

                # Properly clean up the previous widget if it exists
                if previous_widget:
                    previous_widget.setParent(None)
                    del previous_widget

                print("SignalAttributeSection successfully cleared")
        except Exception as e:
            print(f"Error clearing signal attribute section: {e}")
            import traceback
            traceback.print_exc()
            # Ensure UI remains responsive
            QtWidgets.QApplication.processEvents()

    def _create_smp_api_config(self, parent_layout):
        """Create SMP API configuration layout"""
        # Create group box for better organization
        group_box = QtWidgets.QGroupBox("SMP API Configuration")
        form_layout = QtWidgets.QFormLayout(group_box)

        # SpinLock API settings
        spinlock_section = QtWidgets.QGroupBox("SpinLock/Unlock API")
        spinlock_layout = QtWidgets.QFormLayout(spinlock_section)

        # SpinLock API
        self.app.lineEdit_SpinLockAPI = QtWidgets.QLineEdit()
        spinlock_layout.addRow("SpinLock API:", self.app.lineEdit_SpinLockAPI)

        # SpinUnlock API
        self.app.lineEdit_SpinUnLockAPI = QtWidgets.QLineEdit()
        spinlock_layout.addRow("SpinUnlock API:", self.app.lineEdit_SpinUnLockAPI)

        # SpinLock Header
        self.app.lineEdit_SpinLockHeaderFile = QtWidgets.QLineEdit()
        spinlock_layout.addRow("Header File:", self.app.lineEdit_SpinLockHeaderFile)

        # Add spinlock section to parent
        form_layout.addRow(spinlock_section)

        # Semaphore API settings
        semaphore_section = QtWidgets.QGroupBox("Semaphore API")
        semaphore_layout = QtWidgets.QFormLayout(semaphore_section)

        # SemaphoreLock API
        self.app.lineEdit_SemaphoreLockAPI = QtWidgets.QLineEdit()
        semaphore_layout.addRow("SemaphoreLock API:", self.app.lineEdit_SemaphoreLockAPI)

        # SemaphoreUnlock API
        self.app.lineEdit_SemaphoreUnLockAPI = QtWidgets.QLineEdit()
        semaphore_layout.addRow("SemaphoreUnlock API:", self.app.lineEdit_SemaphoreUnLockAPI)

        # Semaphore Header
        self.app.lineEdit_SemaphoreHeaderFile = QtWidgets.QLineEdit()
        semaphore_layout.addRow("Header File:", self.app.lineEdit_SemaphoreHeaderFile)

        # Add semaphore section to parent
        form_layout.addRow(semaphore_section)

        # GetCoreId API settings
        coreid_section = QtWidgets.QGroupBox("GetCoreId API")
        coreid_layout = QtWidgets.QFormLayout(coreid_section)

        # GetCoreId API
        self.app.lineEdit_GetCoreID = QtWidgets.QLineEdit()
        coreid_layout.addRow("GetCoreId API:", self.app.lineEdit_GetCoreID)

        # GetCoreId Header
        self.app.lineEdit_GetCoreIDHeaderFile = QtWidgets.QLineEdit()
        coreid_layout.addRow("Header File:", self.app.lineEdit_GetCoreIDHeaderFile)

        # Add coreid section to parent
        form_layout.addRow(coreid_section)

        # Add group box to parent layout
        parent_layout.addWidget(group_box)

        # Load values if they exist
        self._load_smp_api_values()

    def _create_multicore_api_config(self, parent_layout):
        """Create multi-core API configuration layout with expandable sections"""
        # Create group box
        group_box = QtWidgets.QGroupBox("Multi-core API Configuration")
        group_layout = QtWidgets.QVBoxLayout(group_box)

        # Get cores from configuration
        core_info = self.app.signals_data.get("core_info", {})
        if not core_info:
            no_cores_label = QtWidgets.QLabel("No cores configured. Please configure cores first.")
            group_layout.addWidget(no_cores_label)
        else:
            # Create a tree widget for hierarchical organization
            tree_widget = QtWidgets.QTreeWidget()
            tree_widget.setHeaderLabels(["Configuration", "Value"])
            tree_widget.setColumnCount(2)  # Two columns: one for name, one for value
            tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            tree_widget.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            tree_widget.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            group_layout.addWidget(tree_widget)

            # Create items for each SOC and its cores
            for soc_name, cores in core_info.items():
                # Create SOC level item
                soc_item = QtWidgets.QTreeWidgetItem(tree_widget, [f"SOC: {soc_name}", ""])
                soc_item.setExpanded(True)  # Expanded by default

                # Create core items under this SOC
                for core_name, core_data in cores.items():
                    # Create core level item
                    core_item = QtWidgets.QTreeWidgetItem(soc_item, [f"Core: {core_name}", ""])
                    core_item.setExpanded(True)  # Start expanded

                    # Create SpinLock section as a child item of the core
                    spinlock_item = QtWidgets.QTreeWidgetItem(core_item, ["SpinLock/Unlock API", ""])
                    spinlock_item.setExpanded(False)  # Collapsed by default

                    # Create SpinLock API widgets as children of the spinlock item
                    spinlock_api_item = QtWidgets.QTreeWidgetItem(spinlock_item, ["SpinLock API", ""])
                    spinlock_api = QtWidgets.QLineEdit()
                    spinlock_api.setObjectName(f"lineEdit_SpinLockAPI_{soc_name}_{core_name}")
                    tree_widget.setItemWidget(spinlock_api_item, 1, spinlock_api)

                    spinunlock_api_item = QtWidgets.QTreeWidgetItem(spinlock_item, ["SpinUnlock API", ""])
                    spinunlock_api = QtWidgets.QLineEdit()
                    spinunlock_api.setObjectName(f"lineEdit_SpinUnLockAPI_{soc_name}_{core_name}")
                    tree_widget.setItemWidget(spinunlock_api_item, 1, spinunlock_api)

                    spinlock_header_item = QtWidgets.QTreeWidgetItem(spinlock_item, ["Header File", ""])
                    spinlock_header = QtWidgets.QLineEdit()
                    spinlock_header.setObjectName(f"lineEdit_SpinLockHeaderFile_{soc_name}_{core_name}")
                    tree_widget.setItemWidget(spinlock_header_item, 1, spinlock_header)

                    # Create Semaphore section as a child item of the core
                    semaphore_item = QtWidgets.QTreeWidgetItem(core_item, ["Semaphore API", ""])
                    semaphore_item.setExpanded(False)  # Collapsed by default

                    # Create Semaphore API widgets as children of the semaphore item
                    semaphore_lock_item = QtWidgets.QTreeWidgetItem(semaphore_item, ["SemaphoreLock API", ""])
                    semaphore_lock = QtWidgets.QLineEdit()
                    semaphore_lock.setObjectName(f"lineEdit_SemaphoreLockAPI_{soc_name}_{core_name}")
                    tree_widget.setItemWidget(semaphore_lock_item, 1, semaphore_lock)

                    semaphore_unlock_item = QtWidgets.QTreeWidgetItem(semaphore_item, ["SemaphoreUnlock API", ""])
                    semaphore_unlock = QtWidgets.QLineEdit()
                    semaphore_unlock.setObjectName(f"lineEdit_SemaphoreUnLockAPI_{soc_name}_{core_name}")
                    tree_widget.setItemWidget(semaphore_unlock_item, 1, semaphore_unlock)

                    semaphore_header_item = QtWidgets.QTreeWidgetItem(semaphore_item, ["Header File", ""])
                    semaphore_header = QtWidgets.QLineEdit()
                    semaphore_header.setObjectName(f"lineEdit_SemaphoreHeaderFile_{soc_name}_{core_name}")
                    tree_widget.setItemWidget(semaphore_header_item, 1, semaphore_header)

                    # Store widgets in app for later access
                    setattr(self.app, f"spinlock_api_{soc_name}_{core_name}", spinlock_api)
                    setattr(self.app, f"spinunlock_api_{soc_name}_{core_name}", spinunlock_api)
                    setattr(self.app, f"spinlock_header_{soc_name}_{core_name}", spinlock_header)
                    setattr(self.app, f"semaphore_lock_{soc_name}_{core_name}", semaphore_lock)
                    setattr(self.app, f"semaphore_unlock_{soc_name}_{core_name}", semaphore_unlock)
                    setattr(self.app, f"semaphore_header_{soc_name}_{core_name}", semaphore_header)

                    # Load values if they exist
                    self._load_core_api_values(soc_name, core_name)

        # Add group box to parent layout
        parent_layout.addWidget(group_box)

    def update_api_configuration(self):
        """Update API configuration UI based on build type"""
        try:
            # Find the API Frame
            api_frame = self.app.findChild(QtWidgets.QFrame, "APIFrame")
            if not api_frame:
                print("APIFrame not found in UI")
                return

            # Get the API scroll area
            api_scroll_area = self.app.findChild(QtWidgets.QScrollArea, "APIscrollArea")
            if not api_scroll_area:
                print("APIscrollArea not found in UI")
                return

            # Create fresh content widget
            contents_widget = QtWidgets.QWidget()
            api_scroll_area.setWidget(contents_widget)

            # Create layout
            main_layout = QtWidgets.QVBoxLayout(contents_widget)
            main_layout.setContentsMargins(10, 10, 10, 10)

            # Get current build type
            build_type = self.app.signals_data.get("build_type", "SMP")

            # Different UI based on build type
            if build_type == "SMP":
                self._create_smp_api_config(main_layout)
            else:
                self._create_multicore_api_config(main_layout)

            # Store references for access
            self.app.api_scroll_contents = contents_widget
            self.app.api_main_layout = main_layout

            return True
        except Exception as e:
            print(f"Error updating API configuration: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _load_smp_api_values(self):
        """Load SMP API values from configuration"""
        # Get API settings from configuration
        if "project_specific" in self.app.signals_data and "api_config" in self.app.signals_data["project_specific"]:
            api_config = self.app.signals_data["project_specific"]["api_config"]

            # Set values if they exist
            if "smp" in api_config:
                smp_config = api_config["smp"]

                # SpinLock APIs
                if "spinlock_api" in smp_config:
                    self.app.lineEdit_SpinLockAPI.setText(smp_config["spinlock_api"])
                if "spinunlock_api" in smp_config:
                    self.app.lineEdit_SpinUnLockAPI.setText(smp_config["spinunlock_api"])
                if "spinlock_header" in smp_config:
                    self.app.lineEdit_SpinLockHeaderFile.setText(smp_config["spinlock_header"])

                # Semaphore APIs
                if "semaphore_lock_api" in smp_config:
                    self.app.lineEdit_SemaphoreLockAPI.setText(smp_config["semaphore_lock_api"])
                if "semaphore_unlock_api" in smp_config:
                    self.app.lineEdit_SemaphoreUnLockAPI.setText(smp_config["semaphore_unlock_api"])
                if "semaphore_header" in smp_config:
                    self.app.lineEdit_SemaphoreHeaderFile.setText(smp_config["semaphore_header"])

                # GetCoreId API
                if "get_core_id_api" in smp_config:
                    self.app.lineEdit_GetCoreID.setText(smp_config["get_core_id_api"])
                if "get_core_id_header" in smp_config:
                    self.app.lineEdit_GetCoreIDHeaderFile.setText(smp_config["get_core_id_header"])

    def _load_core_api_values(self, soc_name, core_name):
        """Load API values for a specific core"""
        # Get API settings from configuration
        if "project_specific" in self.app.signals_data and "api_config" in self.app.signals_data["project_specific"]:
            api_config = self.app.signals_data["project_specific"]["api_config"]

            # Check if multicore config exists
            if "multicore" in api_config:
                multicore_config = api_config["multicore"]

                # Find this core's config
                core_key = f"{soc_name}_{core_name}"
                if core_key in multicore_config:
                    core_config = multicore_config[core_key]

                    # Get widgets for this core
                    spinlock_api = getattr(self.app, f"spinlock_api_{soc_name}_{core_name}", None)
                    spinunlock_api = getattr(self.app, f"spinunlock_api_{soc_name}_{core_name}", None)
                    spinlock_header = getattr(self.app, f"spinlock_header_{soc_name}_{core_name}", None)
                    semaphore_lock = getattr(self.app, f"semaphore_lock_{soc_name}_{core_name}", None)
                    semaphore_unlock = getattr(self.app, f"semaphore_unlock_{soc_name}_{core_name}", None)
                    semaphore_header = getattr(self.app, f"semaphore_header_{soc_name}_{core_name}", None)

                    # Set values if widgets and data exist
                    if spinlock_api and "spinlock_api" in core_config:
                        spinlock_api.setText(core_config["spinlock_api"])
                    if spinunlock_api and "spinunlock_api" in core_config:
                        spinunlock_api.setText(core_config["spinunlock_api"])
                    if spinlock_header and "spinlock_header" in core_config:
                        spinlock_header.setText(core_config["spinlock_header"])
                    if semaphore_lock and "semaphore_lock_api" in core_config:
                        semaphore_lock.setText(core_config["semaphore_lock_api"])
                    if semaphore_unlock and "semaphore_unlock_api" in core_config:
                        semaphore_unlock.setText(core_config["semaphore_unlock_api"])
                    if semaphore_header and "semaphore_header" in core_config:
                        semaphore_header.setText(core_config["semaphore_header"])

    def save_api_configuration(self):
        """Save API configuration to the signals data structure"""
        try:
            # Initialize project_specific if it doesn't exist
            if "project_specific" not in self.app.signals_data:
                self.app.signals_data["project_specific"] = {}

            # Initialize api_config if it doesn't exist
            if "api_config" not in self.app.signals_data["project_specific"]:
                self.app.signals_data["project_specific"]["api_config"] = {}

            # Get current build type
            build_type = self.app.signals_data.get("build_type", "SMP")

            # Get API form data according to the current build type
            if build_type == "SMP":
                # Save SMP API configuration
                self.app.signals_data["project_specific"]["api_config"]["smp"] = {
                    "spinlock_api": self.app.lineEdit_SpinLockAPI.text(),
                    "spinunlock_api": self.app.lineEdit_SpinUnLockAPI.text(),
                    "spinlock_header": self.app.lineEdit_SpinLockHeaderFile.text(),
                    "semaphore_lock_api": self.app.lineEdit_SemaphoreLockAPI.text(),
                    "semaphore_unlock_api": self.app.lineEdit_SemaphoreUnLockAPI.text(),
                    "semaphore_header": self.app.lineEdit_SemaphoreHeaderFile.text(),
                    "get_core_id_api": self.app.lineEdit_GetCoreID.text(),
                    "get_core_id_header": self.app.lineEdit_GetCoreIDHeaderFile.text()
                }
            else:
                # Save multicore API configuration
                if "multicore" not in self.app.signals_data["project_specific"]["api_config"]:
                    self.app.signals_data["project_specific"]["api_config"]["multicore"] = {}

                # Get all configured cores
                core_info = self.app.signals_data.get("core_info", {})
                for soc_name, cores in core_info.items():
                    for core_name in cores:
                        core_key = f"{soc_name}_{core_name}"

                        # Get the widget references for this core
                        spinlock_api = getattr(self.app, f"spinlock_api_{core_key}", None)
                        if not spinlock_api:
                            continue  # Skip if widgets don't exist for this core

                        # Save this core's API configuration
                        self.app.signals_data["project_specific"]["api_config"]["multicore"][core_key] = {
                            "spinlock_api": getattr(self.app, f"spinlock_api_{core_key}").text(),
                            "spinunlock_api": getattr(self.app, f"spinunlock_api_{core_key}").text(),
                            "spinlock_header": getattr(self.app, f"spinlock_header_{core_key}").text(),
                            "semaphore_lock_api": getattr(self.app, f"semaphore_lock_{core_key}").text(),
                            "semaphore_unlock_api": getattr(self.app, f"semaphore_unlock_{core_key}").text(),
                            "semaphore_header": getattr(self.app, f"semaphore_header_{core_key}").text()
                        }

            # Mark as modified
            self.app.modified = True

            return True
        except Exception as e:
            print(f"Error saving API configuration: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_paths(self):
        """Save output and script paths to the data structure"""
        try:
            # Initialize project_specific if it doesn't exist
            if "project_specific" not in self.app.signals_data:
                self.app.signals_data["project_specific"] = {}

            # Initialize paths if it doesn't exist
            if "paths" not in self.app.signals_data["project_specific"]:
                self.app.signals_data["project_specific"]["paths"] = {}

            # Save output path
            output_path = ""
            if hasattr(self.app.ui, 'lineEdit_output_dir'):
                output_path = self.app.ui.lineEdit_output_dir.text()
            elif hasattr(self.app.ui, 'OutputPathLineEdit'):
                output_path = self.app.ui.OutputPathLineEdit.text()

            # Save script path
            script_path = ""
            if hasattr(self.app.ui, 'lineEdit_scripts_dir'):
                script_path = self.app.ui.lineEdit_scripts_dir.text()
            elif hasattr(self.app.ui, 'ScriptPathLineEdit'):
                script_path = self.app.ui.ScriptPathLineEdit.text()

            # Update data structure
            self.app.signals_data["project_specific"]["paths"]["output_path"] = output_path
            self.app.signals_data["project_specific"]["paths"]["script_path"] = script_path

            # Mark as modified
            self.app.modified = True

            return True
        except Exception as e:
            print(f"Error saving paths: {e}")
            import traceback
            traceback.print_exc()
            return False

    def clear_api_configuration(self):
        """Clear all API configuration fields"""
        try:
            print("Clearing API configuration fields...")

            # Clear SMP mode fields if they exist
            smp_fields = [
                "lineEdit_SpinLockAPI",
                "lineEdit_SpinUnLockAPI",
                "lineEdit_SpinLockHeaderFile",
                "lineEdit_SemaphoreLockAPI",
                "lineEdit_SemaphoreUnLockAPI",
                "lineEdit_SemaphoreHeaderFile",
                "lineEdit_GetCoreID",
                "lineEdit_GetCoreIDHeaderFile"
            ]

            for field_name in smp_fields:
                field = getattr(self.app, field_name, None)
                if field and hasattr(field, 'setText'):
                    field.setText("")

            # Clear MultiCore mode fields if they exist
            # Find all attributes that match our naming pattern
            for attr_name in dir(self.app):
                # Look for the spinlock and semaphore widgets for each core
                if any(attr_name.startswith(prefix) for prefix in
                      ["spinlock_api_", "spinunlock_api_", "spinlock_header_",
                       "semaphore_lock_", "semaphore_unlock_", "semaphore_header_"]):
                    field = getattr(self.app, attr_name)
                    if field and hasattr(field, 'setText'):
                        field.setText("")

            # Also clear the data structure
            if "project_specific" in self.app.signals_data:
                if "api_config" in self.app.signals_data["project_specific"]:
                    self.app.signals_data["project_specific"]["api_config"] = {}

            print("API configuration fields cleared successfully")
            return True
        except Exception as e:
            print(f"Error clearing API configuration: {e}")
            import traceback
            traceback.print_exc()
            return False
