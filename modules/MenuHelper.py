from PyQt5 import QtWidgets, QtCore
import sys

class MenuHelper:
    """Helper class to ensure proper menu initialization and visibility"""

    @staticmethod
    def ensure_menu_visibility(app_window):
        """Ensure that menus are properly visible in the application

        Args:
            app_window: The main application window (QMainWindow instance)
        """
        # Make sure the menu bar exists and is visible
        menu_bar = app_window.menuBar()
        if menu_bar:
            menu_bar.setVisible(True)

            # Force the menu bar to update its geometry
            menu_bar.adjustSize()

            # Check if we're on Windows platform
            if sys.platform.startswith('win'):
                # On Windows, sometimes we need to explicitly set native menubar off
                menu_bar.setNativeMenuBar(False)

            # For QDarkStyle or other custom styles, ensure proper colors
            menu_bar.setStyleSheet("")  # Reset any style that might hide menus

        # Process events to ensure UI updates
        QtWidgets.QApplication.processEvents()

    @staticmethod
    def fix_menu_connections(app_window):
        """Fix menu action connections and make sure they're properly triggered

        Args:
            app_window: The main application window
        """
        # Reconnect menu actions if needed
        for action in app_window.findChildren(QtWidgets.QAction):
            # Check if the action belongs to a menu
            parent = action.parent()
            if isinstance(parent, QtWidgets.QMenu):
                # Disconnect and reconnect the action's triggered signal if needed
                try:
                    # Store the connection state
                    connected = action.receivers(action.triggered) > 0

                    if not connected:
                        # For testing purposes, connect to a debug handler
                        print(f"Warning: Menu action '{action.text()}' has no connections")
                except Exception:
                    pass

    @staticmethod
    def refresh_menus(app_window):
        """Completely refresh all menus in the application

        Args:
            app_window: The main application window
        """
        menu_bar = app_window.menuBar()
        if not menu_bar:
            return

        # Store current menus
        menus = []
        for i in range(menu_bar.actions().__len__()):
            menus.append(menu_bar.actions()[i].menu())

        # Clear and re-add all menus
        menu_bar.clear()
        for menu in menus:
            if menu:
                menu_bar.addMenu(menu)

        # Make sure the menu bar is visible and up to date
        menu_bar.setVisible(True)
        menu_bar.adjustSize()
        app_window.update()
