import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QLineEdit, QAction

from Settings_Screen import AdvancedSettingsDialog
from forgot_password import ForgotPasswordDialog

class LoginWindow(QWidget):
    def __init__(self, db, on_login_success):
        super().__init__()
        self.db = db
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        self.basedir = os.path.dirname(__file__)
        self.eye_icon_path = os.path.join(self.basedir, "icons", "eye.png")
        self.hidden_icon_path = os.path.join(self.basedir, "icons", "hidden.png")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)  # Slightly reduced spacing for better visual grouping

        self.label = QLabel("Company Portal Login")
        self.label.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 20px;")
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setFixedWidth(250)
        self.username.setFixedHeight(35)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setFixedWidth(250)
        self.password.setFixedHeight(35)
        self.toggle_action = self.password.addAction(
            QIcon(self.eye_icon_path), 
            QLineEdit.TrailingPosition
        )
        self.toggle_action.setVisible(False)

        self.password.setEchoMode(QLineEdit.Password)

        self.toggle_action.triggered.connect(self.toggle_password_visibility)
        self.password.textChanged.connect(self.manage_icon_visibility)

        # Connect text change to check admin credentials in real-time
        self.username.editingFinished.connect(self.check_admin_creds)
        self.password.editingFinished.connect(self.check_admin_creds)

        # --- FORGOT PASSWORD BUTTON ---
        self.forgot_btn = QPushButton("Forgot Password?")
        self.forgot_btn.setFixedWidth(250)
        self.forgot_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #3498db;
                text-align: right;
                font-size: 11px;
                text-decoration: underline;
                padding-right: 2px;
            }
            QPushButton:hover {
                color: #1d6fa5;
                cursor: pointer;
            }
        """)
        self.forgot_btn.clicked.connect(self.open_forgot_password_dialog)
        self.forgot_btn.setAutoDefault(False)
        self.forgot_btn.setDefault(False)

        # Login Button
        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedWidth(250); self.login_btn.setFixedHeight(40)
        self.login_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; border-radius: 5px;")
        self.login_btn.clicked.connect(self.handle_login)

        # --- ADVANCED SETTINGS BUTTON (Hidden initially) ---
        self.admin_settings_btn = QPushButton("Advanced Settings")
        self.admin_settings_btn.setFixedWidth(250); self.admin_settings_btn.setFixedHeight(35)
        self.admin_settings_btn.setStyleSheet("""
            QPushButton {
                color: #e67e22; 
                background-color: transparent; 
                border: 1px solid #e67e22; 
                border-radius: 5px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fdf2e9;
            }
        """)
        # This line was causing your SyntaxError - fixed now:
        self.admin_settings_btn.clicked.connect(self.open_db_settings)
        self.admin_settings_btn.hide() 

        # Add everything to layout
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.username, alignment=Qt.AlignCenter)
        layout.addWidget(self.password, alignment=Qt.AlignCenter)
        layout.addWidget(self.forgot_btn, alignment=Qt.AlignCenter)  # Added right below password field
        layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.admin_settings_btn, alignment=Qt.AlignCenter)
        
        
        # 1. Force the login button to be the 'Default' button for the window
        self.login_btn.setDefault(True)
        self.login_btn.setAutoDefault(True)

        # 2. Ensure returnPressed is connected correctly
        self.username.returnPressed.connect(self.handle_login)
        self.password.returnPressed.connect(self.handle_login)
        
        # 3. Prevent the Advanced Settings button from 'stealing' the Enter key
        self.admin_settings_btn.setAutoDefault(False)
        self.admin_settings_btn.setDefault(False)
        
        self.setLayout(layout)
        self.username.setFocus()

    def check_admin_creds(self):

        user = self.username.text()
        pw = self.password.text()

        result = self.db.verify_login(user, pw)

        if result and result[0] == "Admin":
            self.admin_settings_btn.show()
        else:
            self.admin_settings_btn.hide()

    def open_db_settings(self):
        dialog = AdvancedSettingsDialog(self)
        dialog.exec_()

    def handle_login(self):
        user = self.username.text()
        pw = self.password.text()

        result = self.db.verify_login(user, pw)

        if result:
            role = result[0]      # e.g., 'admin' or 'employee'
            username = result[1]  # e.g., 'JohnDoe'

            self.on_login_success(role.lower(), username)
        else:
            QMessageBox.warning(self, "Error", "Invalid Credentials")

    def toggle_password_visibility(self):
        if self.password.echoMode() == QLineEdit.Password:
            self.password.setEchoMode(QLineEdit.Normal)
            self.toggle_action.setIcon(QIcon(self.hidden_icon_path))
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.toggle_action.setIcon(QIcon(self.eye_icon_path))

    def manage_icon_visibility(self):
        if not self.username.text() or not self.password.text():
            self.admin_settings_btn.hide()

        # Only show the eye icon if there is text in the box
        if len(self.password.text()) > 0:
            self.toggle_action.setVisible(True)
        else:
            self.toggle_action.setVisible(False)
            # Optional: Reset to password mode if they clear the text
            self.password.setEchoMode(QLineEdit.Password)
            self.toggle_action.setIcon(QIcon(self.eye_icon_path))
    
    # In login_window.py
    def showEvent(self, event):
        """Resets the UI state every time the window is shown."""
        super().showEvent(event)
        if hasattr(self, 'admin_settings_btn'):
            self.admin_settings_btn.hide()

    def open_forgot_password_dialog(self):
        dialog = ForgotPasswordDialog(self)
        dialog.exec_()