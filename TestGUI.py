# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SignalMgrGUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1086, 939)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1051, 891))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.frame_2 = QtWidgets.QFrame(self.tab_2)
        self.frame_2.setGeometry(QtCore.QRect(10, 20, 1021, 241))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.UpdateConfig_2 = QtWidgets.QPushButton(self.frame_2)
        self.UpdateConfig_2.setGeometry(QtCore.QRect(10, 10, 561, 25))
        self.UpdateConfig_2.setObjectName("UpdateConfig_2")
        self.CoreInfo_2 = QtWidgets.QTreeWidget(self.frame_2)
        self.CoreInfo_2.setGeometry(QtCore.QRect(600, 10, 291, 221))
        self.CoreInfo_2.setObjectName("CoreInfo_2")
        self.VersionFrame = QtWidgets.QFrame(self.frame_2)
        self.VersionFrame.setGeometry(QtCore.QRect(10, 50, 411, 101))
        self.VersionFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.VersionFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.VersionFrame.setObjectName("VersionFrame")
        self.label_3 = QtWidgets.QLabel(self.VersionFrame)
        self.label_3.setGeometry(QtCore.QRect(10, 10, 111, 17))
        self.label_3.setObjectName("label_3")
        self.VersionNumber = QtWidgets.QSpinBox(self.VersionFrame)
        self.VersionNumber.setGeometry(QtCore.QRect(140, 30, 44, 26))
        self.VersionNumber.setObjectName("VersionNumber")
        self.VersionDate = QtWidgets.QDateEdit(self.VersionFrame)
        self.VersionDate.setGeometry(QtCore.QRect(290, 20, 110, 26))
        self.VersionDate.setObjectName("VersionDate")
        self.label_5 = QtWidgets.QLabel(self.VersionFrame)
        self.label_5.setGeometry(QtCore.QRect(10, 30, 111, 17))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.VersionFrame)
        self.label_6.setGeometry(QtCore.QRect(10, 60, 121, 17))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.VersionFrame)
        self.label_7.setGeometry(QtCore.QRect(240, 30, 41, 17))
        self.label_7.setObjectName("label_7")
        self.EditorName = QtWidgets.QPlainTextEdit(self.VersionFrame)
        self.EditorName.setGeometry(QtCore.QRect(140, 60, 241, 31))
        self.EditorName.setObjectName("EditorName")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.SignalDetails = QtWidgets.QScrollArea(self.tab)
        self.SignalDetails.setGeometry(QtCore.QRect(0, 30, 591, 751))
        self.SignalDetails.setWidgetResizable(True)
        self.SignalDetails.setObjectName("SignalDetails")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 589, 749))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.SignalDetails.setWidget(self.scrollAreaWidgetContents)
        self.SignalInternalInfo = QtWidgets.QStackedWidget(self.tab)
        self.SignalInternalInfo.setGeometry(QtCore.QRect(630, 30, 361, 731))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SignalInternalInfo.sizePolicy().hasHeightForWidth())
        self.SignalInternalInfo.setSizePolicy(sizePolicy)
        self.SignalInternalInfo.setObjectName("SignalInternalInfo")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.SignalInternalInfo.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.SignalInternalInfo.addWidget(self.page_2)
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(610, 10, 151, 17))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 10, 151, 20))
        self.label.setObjectName("label")
        self.line_2 = QtWidgets.QFrame(self.tab)
        self.line_2.setGeometry(QtCore.QRect(600, 30, 16, 761))
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.tab)
        self.line_3.setGeometry(QtCore.QRect(0, 780, 1031, 20))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.SignalOpFrame = QtWidgets.QFrame(self.tab)
        self.SignalOpFrame.setGeometry(QtCore.QRect(30, 800, 971, 41))
        self.SignalOpFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.SignalOpFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.SignalOpFrame.setObjectName("SignalOpFrame")
        self.UndoButton_2 = QtWidgets.QPushButton(self.SignalOpFrame)
        self.UndoButton_2.setGeometry(QtCore.QRect(270, 10, 88, 27))
        self.UndoButton_2.setObjectName("UndoButton_2")
        self.SaveButton_2 = QtWidgets.QPushButton(self.SignalOpFrame)
        self.SaveButton_2.setGeometry(QtCore.QRect(170, 10, 88, 27))
        self.SaveButton_2.setObjectName("SaveButton_2")
        self.RedoButton_2 = QtWidgets.QPushButton(self.SignalOpFrame)
        self.RedoButton_2.setGeometry(QtCore.QRect(370, 10, 88, 27))
        self.RedoButton_2.setObjectName("RedoButton_2")
        self.SignalCnt = QtWidgets.QSpinBox(self.SignalOpFrame)
        self.SignalCnt.setGeometry(QtCore.QRect(110, 10, 44, 26))
        self.SignalCnt.setObjectName("SignalCnt")
        self.label_4 = QtWidgets.QLabel(self.SignalOpFrame)
        self.label_4.setGeometry(QtCore.QRect(10, 10, 101, 20))
        self.label_4.setObjectName("label_4")
        self.BuildImageType = QtWidgets.QComboBox(self.SignalOpFrame)
        self.BuildImageType.setGeometry(QtCore.QRect(800, 10, 151, 27))
        self.BuildImageType.setObjectName("BuildImageType")
        self.BuildImageType.addItem("")
        self.SOCList = QtWidgets.QComboBox(self.SignalOpFrame)
        self.SOCList.setGeometry(QtCore.QRect(680, 10, 111, 27))
        self.SOCList.setObjectName("SOCList")
        self.SOCList.addItem("")
        self.tabWidget.addTab(self.tab, "")
        
        # Add a new tab for Advanced Settings
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        
        # Add a frame to contain controls
        self.advanced_frame = QtWidgets.QFrame(self.tab_3)
        self.advanced_frame.setGeometry(QtCore.QRect(10, 20, 1021, 241))
        self.advanced_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.advanced_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.advanced_frame.setObjectName("advanced_frame")
        
        # Add a label
        self.label_advanced = QtWidgets.QLabel(self.advanced_frame)
        self.label_advanced.setGeometry(QtCore.QRect(10, 10, 200, 17))
        self.label_advanced.setObjectName("label_advanced")
        
        # Add a treeview for advanced settings
        self.advanced_tree = QtWidgets.QTreeWidget(self.advanced_frame)
        self.advanced_tree.setGeometry(QtCore.QRect(10, 40, 500, 180))
        self.advanced_tree.setObjectName("advanced_tree")
        
        # Add the tab to the tabWidget
        self.tabWidget.addTab(self.tab_3, "")
        
        # Add a new tab for Debug Tools
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        
        # Add a frame to contain debug controls
        self.debug_frame = QtWidgets.QFrame(self.tab_4)
        self.debug_frame.setGeometry(QtCore.QRect(10, 20, 1021, 800))
        self.debug_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.debug_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.debug_frame.setObjectName("debug_frame")
        
        # Add a label
        self.label_debug = QtWidgets.QLabel(self.debug_frame)
        self.label_debug.setGeometry(QtCore.QRect(10, 10, 200, 17))
        self.label_debug.setObjectName("label_debug")
        
        # Add a text area for logs
        self.debug_log = QtWidgets.QPlainTextEdit(self.debug_frame)
        self.debug_log.setGeometry(QtCore.QRect(10, 40, 800, 400))
        self.debug_log.setReadOnly(True)
        self.debug_log.setObjectName("debug_log")
        
        # Add debug control buttons
        self.debug_start_button = QtWidgets.QPushButton(self.debug_frame)
        self.debug_start_button.setGeometry(QtCore.QRect(10, 460, 150, 30))
        self.debug_start_button.setObjectName("debug_start_button")
        
        self.debug_stop_button = QtWidgets.QPushButton(self.debug_frame)
        self.debug_stop_button.setGeometry(QtCore.QRect(170, 460, 150, 30))
        self.debug_stop_button.setObjectName("debug_stop_button")
        
        self.debug_clear_button = QtWidgets.QPushButton(self.debug_frame)
        self.debug_clear_button.setGeometry(QtCore.QRect(330, 460, 150, 30))
        self.debug_clear_button.setObjectName("debug_clear_button")
        
        # Add the tab to the tabWidget
        self.tabWidget.addTab(self.tab_4, "")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1086, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuDataBase = QtWidgets.QMenu(self.menubar)
        self.menuDataBase.setObjectName("menuDataBase")
        self.menuCodeGeneration = QtWidgets.QMenu(self.menubar)
        self.menuCodeGeneration.setObjectName("menuCodeGeneration")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_As = QtWidgets.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionCreate = QtWidgets.QAction(MainWindow)
        self.actionCreate.setObjectName("actionCreate")
        self.actionExport_as_Excel = QtWidgets.QAction(MainWindow)
        self.actionExport_as_Excel.setObjectName("actionExport_as_Excel")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAdd = QtWidgets.QAction(MainWindow)
        self.actionAdd.setObjectName("actionAdd")
        self.actionDelete = QtWidgets.QAction(MainWindow)
        self.actionDelete.setObjectName("actionDelete")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setObjectName("actionPaste")
        self.actionMove = QtWidgets.QAction(MainWindow)
        self.actionMove.setObjectName("actionMove")
        self.actionRename = QtWidgets.QAction(MainWindow)
        self.actionRename.setObjectName("actionRename")
        self.actionAdd_Signal = QtWidgets.QAction(MainWindow)
        self.actionAdd_Signal.setObjectName("actionAdd_Signal")
        self.actionDelete_Signal = QtWidgets.QAction(MainWindow)
        self.actionDelete_Signal.setObjectName("actionDelete_Signal")
        self.actionUpdate_Signal = QtWidgets.QAction(MainWindow)
        self.actionUpdate_Signal.setObjectName("actionUpdate_Signal")
        self.actionRename_Signal = QtWidgets.QAction(MainWindow)
        self.actionRename_Signal.setObjectName("actionRename_Signal")
        self.actionCopy_Signal = QtWidgets.QAction(MainWindow)
        self.actionCopy_Signal.setObjectName("actionCopy_Signal")
        self.actionPaste_Signal = QtWidgets.QAction(MainWindow)
        self.actionPaste_Signal.setObjectName("actionPaste_Signal")
        self.actionSignalMgr = QtWidgets.QAction(MainWindow)
        self.actionSignalMgr.setObjectName("actionSignalMgr")
        self.actionIpcManager = QtWidgets.QAction(MainWindow)
        self.actionIpcManager.setObjectName("actionIpcManager")
        self.actionIpcOvEthMgr = QtWidgets.QAction(MainWindow)
        self.actionIpcOvEthMgr.setObjectName("actionIpcOvEthMgr")
        self.actionAbout_Tool_Usage = QtWidgets.QAction(MainWindow)
        self.actionAbout_Tool_Usage.setObjectName("actionAbout_Tool_Usage")
        self.actionLicense = QtWidgets.QAction(MainWindow)
        self.actionLicense.setObjectName("actionLicense")
        self.actionVersion = QtWidgets.QAction(MainWindow)
        self.actionVersion.setObjectName("actionVersion")
        self.actionImport_From_Excel = QtWidgets.QAction(MainWindow)
        self.actionImport_From_Excel.setObjectName("actionImport_From_Excel")
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.actionExit_2 = QtWidgets.QAction(MainWindow)
        self.actionExit_2.setObjectName("actionExit_2")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionCreate)
        self.menuFile.addAction(self.actionExport_as_Excel)
        self.menuFile.addAction(self.actionImport_From_Excel)
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionExit_2)
        self.menuDataBase.addAction(self.actionAdd_Signal)
        self.menuDataBase.addAction(self.actionDelete_Signal)
        self.menuDataBase.addAction(self.actionUpdate_Signal)
        self.menuDataBase.addAction(self.actionRename_Signal)
        self.menuDataBase.addAction(self.actionCopy_Signal)
        self.menuDataBase.addAction(self.actionPaste_Signal)
        self.menuCodeGeneration.addAction(self.actionSignalMgr)
        self.menuCodeGeneration.addAction(self.actionIpcManager)
        self.menuCodeGeneration.addAction(self.actionIpcOvEthMgr)
        self.menuHelp.addAction(self.actionAbout_Tool_Usage)
        self.menuHelp.addAction(self.actionLicense)
        self.menuHelp.addAction(self.actionVersion)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDataBase.menuAction())
        self.menubar.addAction(self.menuCodeGeneration.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.UpdateConfig_2.setText(_translate("MainWindow", "Update Configuration"))
        self.CoreInfo_2.headerItem().setText(0, _translate("MainWindow", "Core Details"))
        self.label_3.setText(_translate("MainWindow", "Version Details"))
        self.label_5.setText(_translate("MainWindow", "Version Number"))
        self.label_6.setText(_translate("MainWindow", "Last Modified By"))
        self.label_7.setText(_translate("MainWindow", "Date"))
        self.EditorName.setPlainText(_translate("MainWindow", "Enter Your Name"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Core Configuration"))
        self.label_2.setText(_translate("MainWindow", "Signal Details"))
        self.label.setText(_translate("MainWindow", "Signal List"))
        self.UndoButton_2.setText(_translate("MainWindow", "Undo"))
        self.SaveButton_2.setText(_translate("MainWindow", "Save"))
        self.RedoButton_2.setText(_translate("MainWindow", "Redo"))
        self.label_4.setText(_translate("MainWindow", "Signal Count -"))
        self.BuildImageType.setItemText(0, _translate("MainWindow", "Select Build Type"))
        self.SOCList.setItemText(0, _translate("MainWindow", "Select SOC"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Signal Configuration"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Advanced Settings"))
        self.label_advanced.setText(_translate("MainWindow", "Advanced Configuration Options"))
        self.advanced_tree.headerItem().setText(0, _translate("MainWindow", "Settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Debug Tools"))
        self.label_debug.setText(_translate("MainWindow", "Debug & Diagnostics"))
        self.debug_start_button.setText(_translate("MainWindow", "Start Debug"))
        self.debug_stop_button.setText(_translate("MainWindow", "Stop Debug"))
        self.debug_clear_button.setText(_translate("MainWindow", "Clear Logs"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuDataBase.setTitle(_translate("MainWindow", "DataBase"))
        self.menuCodeGeneration.setTitle(_translate("MainWindow", "CodeGeneration"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As"))
        self.actionCreate.setText(_translate("MainWindow", "Create"))
        self.actionExport_as_Excel.setText(_translate("MainWindow", "Export as Excel"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAdd.setText(_translate("MainWindow", "Add"))
        self.actionDelete.setText(_translate("MainWindow", "Delete"))
        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionPaste.setText(_translate("MainWindow", "Paste"))
        self.actionMove.setText(_translate("MainWindow", "Move"))
        self.actionRename.setText(_translate("MainWindow", "Rename"))
        self.actionAdd_Signal.setText(_translate("MainWindow", "Add Signal"))
        self.actionDelete_Signal.setText(_translate("MainWindow", "Delete Signal"))
        self.actionUpdate_Signal.setText(_translate("MainWindow", "Update Signal"))
        self.actionRename_Signal.setText(_translate("MainWindow", "Rename Signal"))
        self.actionCopy_Signal.setText(_translate("MainWindow", "Copy Signal"))
        self.actionPaste_Signal.setText(_translate("MainWindow", "Paste Signal"))
        self.actionSignalMgr.setText(_translate("MainWindow", "SignalMgr"))
        self.actionIpcManager.setText(_translate("MainWindow", "IpcManager"))
        self.actionIpcOvEthMgr.setText(_translate("MainWindow", "IpcOvEthMgr"))
        self.actionAbout_Tool_Usage.setText(_translate("MainWindow", "About Tool Usage"))
        self.actionLicense.setText(_translate("MainWindow", "License"))
        self.actionVersion.setText(_translate("MainWindow", "Version"))
        self.actionImport_From_Excel.setText(_translate("MainWindow", "Import From Excel"))
        self.actionClose.setText(_translate("MainWindow", "Close"))
        self.actionExit_2.setText(_translate("MainWindow", "Exit"))
