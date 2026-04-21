from PyQt5.QtWidgets import (QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton, QFileDialog, QMessageBox, QGridLayout, QStackedWidget)
from PyQt5.QtCore import Qt
from Employee_Page.employee_profile_page.profile_page import ProfilePage
from Employee_Page.employee_job_requirements_page.requirements_page import RequirementsPage

class EmployeeDashboard(QWidget):
    def __init__(self, db, logout_callback):
        super().__init__()
        self.db = db
        self.logout_callback = logout_callback
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        # 1. Main Horizontal Layout: [Sidebar] | [Content Container]
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- SIDEBAR SETUP ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #2c3e50; border: none;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 30, 10, 30)

        sidebar_title = QLabel("HR PORTAL")
        sidebar_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        sidebar_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(sidebar_title)

        nav_buttons = [
            (" 🏠 Home", self.show_home),
            ("👤 Profile", self.show_profile),
            ("📋 Job Requirements", self.show_requirements),
            ("🎓 Trainings", self.show_trainings),
            ("📅 Leave Planning", self.show_leave)
        ]

        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #ecf0f1; border-radius: 5px;
                    padding: 12px; text-align: left; font-size: 14px;
                }
                QPushButton:hover { background-color: #34495e; color: #1abc9c; }
            """)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch() 

        logout_btn = QPushButton("Log Out")
        logout_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        logout_btn.clicked.connect(self.logout_callback)
        sidebar_layout.addWidget(logout_btn)

        # Add Sidebar to Main Layout
        self.main_layout.addWidget(self.sidebar)
        
        # --- CONTENT AREA SETUP ---
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # Header Label
        self.header_label = QLabel("Welcome Back!")
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        self.content_layout.addWidget(self.header_label)

        # Setup the StackedWidget
        self.pages = QStackedWidget()
        
        # Initialize the separate page objects
        self.profile_screen = ProfilePage(self.db, self)
        self.req_screen = RequirementsPage(self.db, self.current_user)

        # Add screens to stack
        self.pages.addWidget(QLabel("Home Page Content")) # Index 0
        self.pages.addWidget(self.profile_screen)        # Index 1
        self.pages.addWidget(self.req_screen)            # Index 2

        # Add the StackedWidget to the CONTENT layout
        self.content_layout.addWidget(self.pages)

        # Add the full Content Container to the main layout
        self.main_layout.addWidget(self.content_container)

    # --- NAVIGATION CALLBACKS ---
    def show_home(self):
        self.header_label.setText("Welcome Back!")
        self.pages.setCurrentIndex(0)

    def show_profile(self):
        self.header_label.setText("My Professional Profile")
        self.profile_screen.show_view_mode()
        self.pages.setCurrentWidget(self.profile_screen)

    def show_requirements(self):
        self.header_label.setText("Job Requirements")
        self.pages.setCurrentWidget(self.req_screen)

    def show_trainings(self): 
        self.header_label.setText("Training & Development")
        
    def show_leave(self): 
        self.header_label.setText("Leave Planning & Attendance")

    def load_employee_data(self, username):
        self.current_user = username
        self.profile_screen.refresh_data(username)

        self.req_screen.username = username
        self.req_screen.refresh_table_data()

        self.header_label.setText(f"Welcome Back, {username}!")