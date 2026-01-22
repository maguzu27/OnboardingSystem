from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QWidget, QFormLayout, 
                             QTabWidget, QFrame)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import os

class EmployeeRecordDialog(QDialog):
    def __init__(self, employee_data, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.username = employee_data[1]  # Username at index 1
        self.file_path = self.db.get_employee_attachment(self.username)
        
        self.setWindowTitle("Employee Management Profile")
        self.resize(600, 750)
        self.setStyleSheet("""
            QDialog { background-color: #f8f9fa; }
            QLabel { color: #2c3e50; font-size: 13px; }
            QTabWidget::pane { border: 1px solid #dee2e6; background: white; border-radius: 5px; }
            QTabBar::tab { background: #e9ecef; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: white; border-bottom: 2px solid #3498db; font-weight: bold; }
        """)
        
        self.init_ui(employee_data)

    def init_ui(self, data):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- MODERN HEADER ---
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #dee2e6;")
        header_layout = QHBoxLayout(header)
        
        info_layout = QVBoxLayout()
        name_lbl = QLabel(f"{data[2]} {data[3]}") # First + Last Name
        name_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; border: none;")
        user_lbl = QLabel(f"@{data[1]} | ID: {data[0]}")
        user_lbl.setStyleSheet("color: #7f8c8d; border: none;")
        info_layout.addWidget(name_lbl)
        info_layout.addWidget(user_lbl)
        
        status_badge = QLabel(str(data[13]).upper()) # Status
        status_badge.setFixedSize(90, 30)
        status_badge.setAlignment(Qt.AlignCenter)
        color = "#27ae60" if "active" in str(data[13]).lower() else "#e67e22"
        status_badge.setStyleSheet(f"background-color: {color}; color: white; border-radius: 15px; font-weight: bold;")
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        header_layout.addWidget(status_badge)
        main_layout.addWidget(header)

        # --- CATEGORIZED TABS ---
        self.tabs = QTabWidget()
        
        # Tab 1: Personal Info
        personal_tab = self.create_form_tab([
            ("Nickname", data[5]), ("Age", data[6]), ("Gender", data[7]), 
            ("Birthday", data[17]), ("Email", data[8]), ("Cellphone", data[11]),
            ("Telephone", data[10]), ("Address", data[9])
        ])
        
        # Tab 2: Employment Details
        work_tab = self.create_form_tab([
            ("Department ID", data[22]), ("Job ID", data[23]), ("Type", data[15]),
            ("Date Hired", data[16]), ("Supervisor ID", data[12]), ("Hired Status", data[14])
        ])

        # Tab 3: System Logs
        logs_tab = self.create_form_tab([
            ("Created By", data[20]), ("Created Date", data[18]),
            ("Updated By", data[21]), ("Updated Date", data[19])
        ])

        self.tabs.addTab(personal_tab, "Personal")
        self.tabs.addTab(work_tab, "Employment")
        self.tabs.addTab(logs_tab, "Record Details")
        main_layout.addWidget(self.tabs)

        # --- FOOTER / ACTIONS ---
        footer_layout = QHBoxLayout()
        
        has_file = bool(self.file_path and os.path.exists(self.file_path))
        self.view_file_btn = QPushButton(" View Document")
        self.view_file_btn.setFixedHeight(40)
        btn_style = "background-color: #3498db; color: white; font-weight: bold; border-radius: 5px; padding: 0 15px;"
        if not has_file:
            btn_style = "background-color: #bdc3c7; color: #ffffff; border-radius: 5px;"
            self.view_file_btn.setEnabled(False)
            self.view_file_btn.setText("No Attachment")
            
        self.view_file_btn.setStyleSheet(btn_style)
        self.view_file_btn.clicked.connect(self.open_file)

        close_btn = QPushButton("Dismiss")
        close_btn.setFixedHeight(40)
        close_btn.setFixedWidth(100)
        close_btn.setStyleSheet("background-color: #ffffff; border: 1px solid #dcdde1; border-radius: 5px;")
        close_btn.clicked.connect(self.accept)

        footer_layout.addWidget(self.view_file_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(close_btn)
        main_layout.addLayout(footer_layout)

    def create_form_tab(self, fields):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        for label, value in fields:
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("font-weight: bold; color: #7f8c8d;")
            val = QLabel(str(value) if value else "N/A")
            val.setStyleSheet("font-size: 14px; color: #2c3e50;")
            layout.addRow(lbl, val)
            
            # Add a thin separator line
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet("color: #f1f2f6;")
            layout.addRow(line)
            
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll.setStyleSheet("border: none; background: white;")
        return scroll

    def open_file(self):
        if self.file_path:
            try:
                os.startfile(os.path.abspath(self.file_path))
            except Exception as e:
                print(f"Error: {e}")