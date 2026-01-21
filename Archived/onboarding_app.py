import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QStackedWidget, 
                             QHeaderView, QFrame, QAction, QStyle, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize



# --- DATABASE MANAGER ---
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("onboarding.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                email TEXT,
                education TEXT,
                job_title TEXT,
                supervisor TEXT
            )
        """)
        # If the table exists but lacks the email column, this handles it:
        try:
            self.cursor.execute("ALTER TABLE employees ADD COLUMN email TEXT")
        except sqlite3.OperationalError:
            pass # Column already exists
        self.conn.commit()

    def add_employee(self, name, email, edu, title, sup):
        try:
            self.cursor.execute("INSERT INTO employees (name, email, education, job_title, supervisor) VALUES (?, ?, ?, ?, ?)",
                                (name, email, edu, title, sup))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_employee(self, emp_id):
        self.cursor.execute("DELETE FROM employees WHERE id=?", (emp_id,))
        self.conn.commit()

    def get_all_employees(self):
        self.cursor.execute("SELECT id, name, email, education, job_title, supervisor FROM employees")
        return self.cursor.fetchall()

    def get_employee_by_name(self, name):
        self.cursor.execute("SELECT * FROM employees WHERE name=?", (name,))
        return self.cursor.fetchone()

# --- LOGIN SCREEN ---
class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

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
        self.password.setEchoMode(QLineEdit.Password)

        # Connect text change to check admin credentials in real-time
        self.username.textChanged.connect(self.check_admin_creds)
        self.password.textChanged.connect(self.check_admin_creds)

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
        """Toggle button visibility based on input"""
        if self.username.text() == "admin" and self.password.text() == "admin123":
            self.admin_settings_btn.show()
        else:
            self.admin_settings_btn.hide()

    def open_db_settings(self):
        """This function runs when the Advanced Settings button is clicked"""
        QMessageBox.information(self, "Advanced Settings", 
                                "Current Database: onboarding.db\nConnection Status: Local SQLite3")

    def handle_login(self):
        # ... (Your existing handle_login code) ...
        user = self.username.text()
        pw = self.password.text()
        if user == "admin" and pw == "admin123":
            self.on_login_success("admin", user)
        elif user != "" and pw == "123":
            self.on_login_success("employee", user)
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials!")
# --- ADMIN HOME (DASHBOARD) ---
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
            ("Manage Employees", QStyle.SP_FileDialogContentsView, self.nav_to_manage),
            ("Job Roles", QStyle.SP_DirHomeIcon, lambda: self.msg("Job Roles")),
            ("Job Requirements", QStyle.SP_FileDialogDetailedView, lambda: self.msg("Requirements")),
            ("Alerts", QStyle.SP_MessageBoxWarning, lambda: self.msg("Alerts"))
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
            
# --- ADMIN MANAGEMENT SCREEN ---
class AdminDashboard(QWidget):
    def __init__(self, db, logout_callback):
        super().__init__()
        self.db = db
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QHBoxLayout()
        lbl = QLabel("Admin: Manage Employees")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        back = QPushButton("Back to Dashboard"); back.clicked.connect(self.logout_callback)
        header.addWidget(lbl); header.addStretch(); header.addWidget(back)

        form = QHBoxLayout()
        self.n_in = QLineEdit(); self.n_in.setPlaceholderText("Name")
        self.m_in = QLineEdit(); self.m_in.setPlaceholderText("Email")
        self.e_in = QLineEdit(); self.e_in.setPlaceholderText("Education")
        self.j_in = QLineEdit(); self.j_in.setPlaceholderText("Job Title")
        self.s_in = QLineEdit(); self.s_in.setPlaceholderText("Supervisor")
        form.addWidget(self.n_in); form.addWidget(self.m_in); form.addWidget(self.e_in); form.addWidget(self.j_in); form.addWidget(self.s_in)

        btns = QHBoxLayout()
        add = QPushButton("Add Employee"); add.clicked.connect(self.add_emp)
        dele = QPushButton("Delete Selected"); dele.clicked.connect(self.del_emp)
        btns.addWidget(add); btns.addWidget(dele)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Education", "Job Title", "Supervisor", "Action"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addLayout(header); layout.addLayout(form); layout.addLayout(btns); layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        self.table.setRowCount(0)
        employees = self.db.get_all_employees()
        
        for r_idx, r_data in enumerate(employees):
            self.table.insertRow(r_idx)
            
            # Use range(6) to only fill the text columns (0 to 5)
            for c_idx in range(6):
                val = r_data[c_idx] if r_data[c_idx] is not None else ""
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
                
            # Add Send Email Button in Column index 6 (the 7th column)
            send_btn = QPushButton("Send Email")
            send_btn.setStyleSheet("""
                QPushButton { background-color: #2ecc71; color: white; border-radius: 3px; padding: 2px; }
                QPushButton:hover { background-color: #27ae60; }
            """)   
            
            # Since we forced the SQL order, index 2 is now definitely the email
            email_address = str(r_data[2]) 
            send_btn.clicked.connect(lambda ch, em=email_address: self.send_email_trigger(em))
            
            self.table.setCellWidget(r_idx, 6, send_btn) 

    def add_emp(self):
        if self.db.add_employee(self.n_in.text(), self.m_in.text(), self.e_in.text(), self.j_in.text(), self.s_in.text()):
            self.load_data()
            self.n_in.clear(); self.m_in.clear(); self.e_in.clear(); self.j_in.clear(); self.s_in.clear()
        else:
            QMessageBox.critical(self, "Error", "Employee name must be unique.")

    def del_emp(self):
        row = self.table.currentRow()
        if row >= 0:
            self.db.delete_employee(self.table.item(row, 0).text())
            self.load_data()
            
    def send_email_trigger(self, email):
        if email and "@" in email:
            QMessageBox.information(self, "Email System", f"Opening mail client for: {email}")
            # This opens the default system mail app (Outlook/Gmail)
            import webbrowser
            webbrowser.open(f"mailto:{email}?subject=Company Onboarding")
        else:
            QMessageBox.warning(self, "Error", "Invalid email address.")

# --- EMPLOYEE SCREEN ---
class EmployeeDashboard(QWidget):
    def __init__(self, db, logout_callback):
        super().__init__()
        self.db = db
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("My Employee Profile")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        self.info_card = QFrame()
        self.info_card.setFrameShape(QFrame.StyledPanel)
        self.info_card.setStyleSheet("background-color: #f9f9f9; padding: 20px; border-radius: 10px;")
        card_layout = QVBoxLayout(self.info_card)
        
        self.details = QLabel("Loading details...")
        self.details.setStyleSheet("font-size: 16px; line-height: 150%;")
        card_layout.addWidget(self.details)

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout_callback)

        layout.addWidget(title, alignment=Qt.AlignCenter)
        layout.addWidget(self.info_card)
        layout.addWidget(logout_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def load_employee_data(self, name):
        data = self.db.get_employee_by_name(name)
        if data:
            self.details.setText(f"<b>Name:</b> {data[1]}<br>"
                                 f"<b>Email:</b> {data[2]}<br>"
                                 f"<b>Education:</b> {data[3]}<br>"
                                 f"<b>Job Title:</b> {data[4]}<br>"
                                 f"<b>Supervisor:</b> {data[5]}")
        else:
            self.details.setText("No information found for this account.<br>Contact Admin to add your details.")

# --- MAIN APP ---
class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setStyleSheet("""
            QPushButton { border-radius: 5px; padding: 5px; }
            QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 3px; }
        """)

        self.login_page = LoginWindow(self.handle_routing)
        self.admin_home = AdminHome("Admin User", self.go_to_manage_employees, self.show_login)
        self.admin_manage_page = AdminDashboard(self.db, self.go_to_admin_home)
        self.employee_page = EmployeeDashboard(self.db, self.show_login)
        
        self.addWidget(self.login_page)       # 0
        self.addWidget(self.admin_home)       # 1
        self.addWidget(self.admin_manage_page) # 2
        self.addWidget(self.employee_page)    # 3
        
        self.setWindowTitle("Corporate Onboarding System")
        self.resize(1000, 700)
        self.setCurrentIndex(0)

    def handle_routing(self, role, username):
        if role == "admin":
            self.admin_home.admin_label.setText(f"Welcome, {username}")
            self.setCurrentIndex(1)
        else:
            self.employee_page.load_employee_data(username)
            self.setCurrentIndex(3)

    def go_to_manage_employees(self):
        self.admin_manage_page.load_data()
        self.setCurrentIndex(2)

    def go_to_admin_home(self):
        self.setCurrentIndex(1)

    def show_login(self):
        self.login_page.username.clear()
        self.login_page.password.clear()
        self.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())