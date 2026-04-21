from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QStyle, 
                             QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize
import webbrowser
from PyQt5.QtWidgets import QDialog, QFormLayout
from Admin_Page.Master_Tables_Setup.admin_master_table_manager import MasterTableManager
from Admin_Page.Job_Requirements.admin_requirements_setup_manager import RequirementsSetupManager
from Admin_Page.Setup_Alerts.Admin_Setup_Alerts_Manager import AlertsSetupManager
from Admin_Page.Trainings_Setup.Admin_Setup_Trainings import AdminTrainingManagement

class AdminHome(QWidget):
    def __init__(self, admin_name, nav_to_manage, logout_callback):
        super().__init__()
        self.admin_name = admin_name
        self.nav_to_manage = nav_to_manage
        self.logout_callback = logout_callback
        self.init_ui()
        
        # Timer for the Real-time Clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        # --- TOP HEADER ---
        header = QHBoxLayout()
        self.admin_label = QLabel(f"Welcome, {self.admin_name}")
        self.admin_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        self.update_time()

        header.addWidget(self.admin_label)
        header.addStretch()
        header.addWidget(self.time_label)
        
        # --- MIDDLE GRID BUTTONS ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # 1. Define the 'buttons' list inside this method
        buttons = [
            ("Manage Employees", QStyle.SP_FileDialogContentsView, lambda: self.nav_to_manage()),
            ("Setup Master Tables", QStyle.SP_DirHomeIcon, lambda: self.nav_to_manage(MasterTableManager)),
            ("Job Requirements", QStyle.SP_FileDialogDetailedView, lambda: self.nav_to_manage(RequirementsSetupManager)),
            ("Alerts", QStyle.SP_MessageBoxWarning, lambda: self.nav_to_manage(AlertsSetupManager)),
            ("Trainings", QStyle.SP_MessageBoxInformation, lambda: self.nav_to_manage(AdminTrainingManagement)),
            # ("Alerts", QStyle.SP_MessageBoxWarning, lambda: self.msg("Alerts"))
        ]

        # 2. Loop through the list to create the UI
        row, col = 0, 0
        for text, icon_style, callback in buttons:
            btn = QPushButton(text)
            btn.setIcon(self.style().standardIcon(icon_style))
            btn.setIconSize(QSize(40, 40)) # Fixed from Qt.Size to QSize
            btn.setFixedSize(220, 160)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 2px solid #ecf0f1;
                    border-radius: 15px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #34495e;
                }
                QPushButton:hover {
                    background-color: #3498db;
                    color: white;
                    border: 2px solid #2980b9;
                }
            """)
            btn.clicked.connect(callback)
            grid_layout.addWidget(btn, row, col)
            col += 1
            if col > 1: # 2 buttons per row
                col = 0
                row += 1

        # Logout at bottom
        logout_btn = QPushButton("Sign Out")
        logout_btn.setFixedWidth(100)
        logout_btn.clicked.connect(self.logout_callback)

        layout.addLayout(header)
        layout.addSpacing(40)
        layout.addLayout(grid_layout, stretch=1)
        layout.addWidget(logout_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

    def update_time(self):
        current = QDateTime.currentDateTime().toString("MMMM d, yyyy - hh:mm:ss AP")
        self.time_label.setText(current)

    def msg(self, feature):
        QMessageBox.information(self, "Coming Soon", f"The {feature} management feature is under development.")

    def nav_to_master_data(self):
        self.nav_to_manage(MasterTableManager)