from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QStyle, 
                             QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize
import webbrowser


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
            
# class AdminDashboard(QWidget):
#     def __init__(self, db, logout_callback):
#         super().__init__()
#         self.db = db
#         self.logout_callback = logout_callback
#         self.init_ui()

#     def init_ui(self):
#         layout = QVBoxLayout()
#         header = QHBoxLayout()
#         lbl = QLabel("Admin: Manage Employees")
#         lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
#         back = QPushButton("Back to Dashboard"); back.clicked.connect(self.logout_callback)
#         header.addWidget(lbl); header.addStretch(); header.addWidget(back)

#         form = QHBoxLayout()
#         self.n_in = QLineEdit(); self.n_in.setPlaceholderText("Name")
#         self.m_in = QLineEdit(); self.m_in.setPlaceholderText("Email")
#         self.e_in = QLineEdit(); self.e_in.setPlaceholderText("Education")
#         self.j_in = QLineEdit(); self.j_in.setPlaceholderText("Job Title")
#         self.s_in = QLineEdit(); self.s_in.setPlaceholderText("Supervisor")
#         form.addWidget(self.n_in); form.addWidget(self.m_in); form.addWidget(self.e_in); form.addWidget(self.j_in); form.addWidget(self.s_in)

#         btns = QHBoxLayout()
#         add = QPushButton("Add Employee"); add.clicked.connect(self.add_emp)
#         dele = QPushButton("Delete Selected"); dele.clicked.connect(self.del_emp)
#         btns.addWidget(add); btns.addWidget(dele)

#         self.table = QTableWidget()
#         self.table.setColumnCount(7)
#         self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Education", "Job Title", "Supervisor", "Action"])
#         self.table.setEditTriggers(QTableWidget.NoEditTriggers)
#         self.table.setSelectionBehavior(QTableWidget.SelectRows)
#         self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

#         layout.addLayout(header); layout.addLayout(form); layout.addLayout(btns); layout.addWidget(self.table)
#         self.setLayout(layout)

#     def load_data(self):
#         self.table.setRowCount(0)
#         employees = self.db.get_all_employees()
        
#         for r_idx, r_data in enumerate(employees):
#             self.table.insertRow(r_idx)
            
#             # Use range(6) to only fill the text columns (0 to 5)
#             for c_idx in range(6):
#                 val = r_data[c_idx] if r_data[c_idx] is not None else ""
#                 self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
                
#             # Add Send Email Button in Column index 6 (the 7th column)
#             send_btn = QPushButton("Send Email")
#             send_btn.setStyleSheet("""
#                 QPushButton { background-color: #2ecc71; color: white; border-radius: 3px; padding: 2px; }
#                 QPushButton:hover { background-color: #27ae60; }
#             """)   
            
#             # Since we forced the SQL order, index 2 is now definitely the email
#             email_address = str(r_data[2]) 
#             send_btn.clicked.connect(lambda ch, em=email_address: self.send_email_trigger(em))
            
#             self.table.setCellWidget(r_idx, 6, send_btn) 

#     def add_emp(self):
#         if self.db.add_employee(self.n_in.text(), self.m_in.text(), self.e_in.text(), self.j_in.text(), self.s_in.text()):
#             self.load_data()
#             self.n_in.clear(); self.m_in.clear(); self.e_in.clear(); self.j_in.clear(); self.s_in.clear()
#         else:
#             QMessageBox.critical(self, "Error", "Employee name must be unique.")

#     def del_emp(self):
#         row = self.table.currentRow()
#         if row >= 0:
#             self.db.delete_employee(self.table.item(row, 0).text())
#             self.load_data()
            
#     def send_email_trigger(self, email):
#         if email and "@" in email:
#             QMessageBox.information(self, "Email System", f"Opening mail client for: {email}")
#             # This opens the default system mail app (Outlook/Gmail)
#             import webbrowser
#             webbrowser.open(f"mailto:{email}?subject=Company Onboarding")
#         else:
#             QMessageBox.warning(self, "Error", "Invalid email address.")