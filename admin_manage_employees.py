from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import QMenu, QDialog, QFormLayout, QScrollArea
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from Admin_AddEmployee import AddEmployeeDialog
import os

class EmployeeRecordDialog(QDialog):
    def __init__(self, employee_data, db, parent=None):
        super().__init__(parent)
        self.db = db

        # Database index 1 is Username
        self.username = employee_data[1]
        self.setWindowTitle(f"Employee Record: {self.username}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        # Get path from DB
        self.file_path = self.db.get_employee_attachment(self.username)
        self.init_ui(employee_data)

    def init_ui(self, data):
        # 1. Main layout for the entire Dialog
        main_layout = QVBoxLayout(self)

        # 2. Scroll Area for the 24 Data Fields
        scroll = QScrollArea()
        scroll_content = QWidget()
        form_layout = QFormLayout(scroll_content)

        labels = [
            "ID", "Username", "First Name", "Last Name", "Display Name", "Nick Name",
            "Age", "Gender", "Email", "Address", "Telephone", "Cellphone",
            "Supervisor ID", "Status", "Hired", "Type", "Date Hired", 
            "Birthday", "Created", "Updated", "Created By", "Updated By",
            "Dept ID", "Job ID"
        ]

        for i, label_text in enumerate(labels):
            val = data[i] if i < len(data) else ""
            form_layout.addRow(f"<b>{label_text}:</b>", QLabel(str(val)))

        # --- FILE STATUS LOGIC ---
        has_file = False
        if self.file_path and os.path.exists(self.file_path):
            has_file = True

        status_text = "Exists" if has_file else "Not Found"
        form_layout.addRow("<b>File Status:</b>", QLabel(status_text))
        # -------------------------

        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll) # Add scroll area to main layout

        # 3. Permanent Button Container at the Bottom
        button_container = QVBoxLayout()
        button_container.setContentsMargins(10, 10, 10, 10)

        self.view_file_btn = QPushButton("View Attached Document")
        self.view_file_btn.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; padding: 10px; font-weight: bold; border-radius: 4px;}
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }
        """)
        
        # Enable/Disable based on file existence
        if not has_file:
            self.view_file_btn.setEnabled(False)
            self.view_file_btn.setText("No Document Attached")
        else:
            self.view_file_btn.setEnabled(True)

        self.view_file_btn.clicked.connect(self.open_file)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(35)
        close_btn.clicked.connect(self.accept)

        button_container.addWidget(self.view_file_btn)
        button_container.addWidget(close_btn)
        
        # Add the button container to the bottom of the main layout
        main_layout.addLayout(button_container)

    def open_file(self):
        if self.file_path:
            try:
                # On Windows, this opens the file with the default app (PDF reader, etc.)
                os.startfile(os.path.abspath(self.file_path))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

class AdminManageEmployees(QWidget):
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

        # form = QHBoxLayout()
        # self.n_in = QLineEdit(); self.n_in.setPlaceholderText("Name")
        # self.m_in = QLineEdit(); self.m_in.setPlaceholderText("Email")
        # self.e_in = QLineEdit(); self.e_in.setPlaceholderText("Education")
        # self.j_in = QLineEdit(); self.j_in.setPlaceholderText("Job Title")
        # self.s_in = QLineEdit(); self.s_in.setPlaceholderText("Supervisor")
        # form.addWidget(self.n_in); form.addWidget(self.m_in); form.addWidget(self.e_in); form.addWidget(self.j_in); form.addWidget(self.s_in)

        btns = QHBoxLayout()
        add = QPushButton("Add Employee"); 
        add.setFixedWidth(150)  # Optional: sets a consistent width
        add.setFixedHeight(35)  # Optional: sets a consistent height
        add.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        add.clicked.connect(self.open_add_employee_screen)
        dele = QPushButton("Delete Selected"); dele.clicked.connect(self.del_emp)
        btns.addWidget(add); btns.addWidget(dele)

        self.table = QTableWidget()
        self.table.setColumnCount(14)

        headers = [
            "Username", "First Name", "Last Name", "Display Name", "Email", 
            "Supervisor ID", "Status", "Hired", "Type", "Date Hired", 
            "Created By", "Dept ID", "Job ID", "Action"
        ]
        self.table.setHorizontalHeaderLabels(headers)

        # self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Education", "Job Title", "Supervisor", "Action"])
       
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addLayout(header); layout.addLayout(btns); layout.addWidget(self.table)

     
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        self.setLayout(layout)

    def load_data(self):
        self.table.setRowCount(0)
        employees = self.db.get_all_employees()

        mapping = [1, 2, 3, 4, 8, 12, 13, 14, 15, 16, 20, 22, 23]

        for r_idx, r_data in enumerate(employees):
            self.table.insertRow(r_idx)

            for table_col, db_idx in enumerate(mapping):
                val = r_data[db_idx] if r_data[db_idx] is not None else ""
                item = QTableWidgetItem(str(val))

                if table_col == 0:
                    item.setData(Qt.UserRole, r_data)

                self.table.setItem(r_idx, table_col, item)

            # Add Send Email Button in Column 13
            send_btn = QPushButton("Send Email")
            send_btn.setStyleSheet("background-color: #2ecc71; color: white; border-radius: 3px;")
            
            # Email is at index 8 in the database result
            email_address = str(r_data[8]) 
            send_btn.clicked.connect(lambda ch, em=email_address: self.send_email_trigger(em))
            
            self.table.setCellWidget(r_idx, 13, send_btn) 
  

    # def add_emp(self):
    #     if self.db.add_employee(self.n_in.text(), self.m_in.text(), self.e_in.text(), self.j_in.text(), self.s_in.text()):
    #         self.load_data()
    #         self.n_in.clear(); self.m_in.clear(); self.e_in.clear(); self.j_in.clear(); self.s_in.clear()
    #     else:
    #         QMessageBox.critical(self, "Error", "Employee name must be unique.")

    def open_add_employee_screen(self):
        dialog = AddEmployeeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # name, email, edu, job, superv = dialog.get_data()
            employee_data = dialog.get_data()

            # Check if fields are empty
            if not employee_data.get("Username") or not employee_data.get("Email"):
                QMessageBox.warning(self, "Input Error", "Username and Email are required.")
                return

            # Add to Database
            if self.db.add_employee(employee_data):
                self.load_data()
                QMessageBox.information(self, "Success", f"Employee {employee_data['Username']} added!")
            else:
                QMessageBox.critical(self, "Error", "Username must be unique or Database error.")

    def del_emp(self):
        row = self.table.currentRow()
        if row >= 0:
            # 1. Get the full tuple from the hidden data in the first cell
            full_data = self.table.item(row, 0).data(Qt.UserRole)
            
            if full_data:
                employee_id = full_data[0] # The ID is index 0 in your database table
                username = full_data[1]    # The Username for the confirmation message
                
                # 2. Ask for confirmation (Safety first!)
                reply = QMessageBox.question(self, 'Confirm Delete', 
                                           f"Are you sure you want to delete {username}?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    # 3. Call delete using the ID
                    if self.db.delete_employee(employee_id):
                        self.load_data()
                        QMessageBox.information(self, "Success", "Employee deleted.")
                    else:
                        QMessageBox.critical(self, "Error", "Could not delete from database.")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a row to delete.")
            
    def send_email_trigger(self, recipient_email):
        if not recipient_email or "@" not in recipient_email:
            QMessageBox.warning(self, "Error", "Invalid email address.")
            return

        # --- EMAIL CONFIGURATION ---
        sender_email = "magatjohnpaul27@gmail.com"  # Your email
        sender_password = "wker vixy miag fvas" # Your App Password
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        try:
            # 1. Create the Message
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = "Welcome to the Company - Onboarding"

            body = f"Hello,\n\nWelcome to the team! Your onboarding process has officially started. Please check your portal for details.\n\nBest regards,\nAdmin Team"
            message.attach(MIMEText(body, "plain"))

            # 2. Connect to Server and Send
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(message)
            server.quit()

            QMessageBox.information(self, "Success", f"Email successfully sent to {recipient_email}")

        except Exception as e:
            QMessageBox.critical(self, "Email Error", f"Failed to send email: {str(e)}")


            

    def show_context_menu(self, position):
        # Get the row index where the user clicked
        row = self.table.currentRow()
        if row == -1:
            return

        # Create the menu
        menu = QMenu()
        open_record_action = menu.addAction("Open Employee Records")
        delete_action = menu.addAction("Delete Employee") # Bonus: Add delete here too
        
        # Show the menu at the cursor position
        action = menu.exec_(self.table.viewport().mapToGlobal(position))

        if action == open_record_action:
            self.open_employee_record(row)
        elif action == delete_action:
            self.del_emp()

    def open_employee_record(self, row):
        # We stored the full database tuple (all 24 cols) in the first item's UserRole
        full_data = self.table.item(row, 0).data(Qt.UserRole)

        if full_data:
            dialog = EmployeeRecordDialog(full_data, self.db, self)
            dialog.exec_()
        else:
            QMessageBox.critical(self, "Error", "Could not retrieve full employee data.")

# class AddEmployeeDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Add New Employee")
#         self.setMinimumWidth(350)
#         self.init_ui()

#     def init_ui(self):
#         layout = QVBoxLayout()
#         form = QFormLayout()

#         # Create input fields
#         self.n_in = QLineEdit(); self.n_in.setPlaceholderText("Full Name")
#         self.m_in = QLineEdit(); self.m_in.setPlaceholderText("Email Address")
#         self.e_in = QLineEdit(); self.e_in.setPlaceholderText("Education/Degree")
#         self.j_in = QLineEdit(); self.j_in.setPlaceholderText("Job Title")
#         self.s_in = QLineEdit(); self.s_in.setPlaceholderText("Supervisor Name")

#         # Styling inputs to match your theme
#         input_style = "padding: 8px; border: 1px solid #ccc; border-radius: 4px;"
#         for widget in [self.n_in, self.m_in, self.e_in, self.j_in, self.s_in]:
#             widget.setStyleSheet(input_style)

#         form.addRow("Name:", self.n_in)
#         form.addRow("Email:", self.m_in)
#         form.addRow("Education:", self.e_in)
#         form.addRow("Job Title:", self.j_in)
#         form.addRow("Supervisor:", self.s_in)

#         # Buttons
#         self.submit_btn = QPushButton("Confirm Add")
#         self.submit_btn.setStyleSheet("""
#             QPushButton { background-color: #3498db; color: white; font-weight: bold; padding: 10px; border-radius: 5px; }
#             QPushButton:hover { background-color: #2980b9; }
#         """)
#         self.submit_btn.clicked.connect(self.accept) # Closes dialog and returns "Accepted"

#         layout.addLayout(form)
#         layout.addSpacing(10)
#         layout.addWidget(self.submit_btn)
#         self.setLayout(layout)

#     def get_data(self):
#         """Returns the data entered in the fields"""
#         return (self.n_in.text(), self.m_in.text(), self.e_in.text(), 
#                 self.j_in.text(), self.s_in.text())


