import token
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QMenu, QDialog, QFormLayout, QComboBox, 
    QAbstractItemView
)
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

from Admin_Page.Manage_Employees.Admin_AddEmployee import AddEmployeeDialog
from Admin_Page.Manage_Employees.Admin_OpenEmployee_Record import EmployeeRecordDialog


class BulkEditDialog(QDialog):
    """Dialog to perform bulk editing on selected employees."""
    def __init__(self, db, selected_count, parent=None):
        super().__init__(parent)
        self.db = db
        self.selected_count = selected_count
        self.setWindowTitle(f"Bulk Edit ({self.selected_count} Employees Selected)")
        self.setFixedSize(420, 260)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        info_lbl = QLabel(f"Modifying <b>{self.selected_count}</b> selected employees.<br>"
                          "<small style='color:#7f8c8d;'>Leave options as '-- No Change --' to retain existing values.</small>")
        info_lbl.setWordWrap(True)
        layout.addRow(info_lbl)

        # 1. Department ComboBox
        self.dept_combo = QComboBox()
        self.dept_combo.addItem("-- No Change --", userData="")
        self.populate_departments()

        # 2. Job Title ComboBox
        self.job_combo = QComboBox()
        self.job_combo.addItem("-- No Change --", userData="")
        self.populate_jobs()

        # 3. Supervisor ComboBox (Displays First Name + Last Name)
        self.supervisor_combo = QComboBox()
        self.supervisor_combo.addItem("-- No Change --", userData="")
        self.populate_supervisors()

        # 4. Employment Status ComboBox
        self.status_combo = QComboBox()
        self.status_combo.addItem("-- No Change --", userData="")
        self.populate_employement_status()

        layout.addRow("Department:", self.dept_combo)
        layout.addRow("Job Title:", self.job_combo)
        layout.addRow("Supervisor:", self.supervisor_combo)
        layout.addRow("Employment Status:", self.status_combo)

        # Action Buttons
        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; color: white; padding: 6px 14px; 
                font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6; color: white; padding: 6px 14px; 
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

    def populate_departments(self):
        
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT DISTINCT dept_id, dept_name FROM Departments ORDER BY dept_name")
        depts = cursor.fetchall()
        for dept in depts:
            d_id, d_name = dept[0], dept[1]
            self.dept_combo.addItem(str(d_name), userData=str(d_id))

    def populate_jobs(self):

        cursor = self.db.conn.cursor()
        cursor.execute("SELECT DISTINCT job_title_id, job_title FROM Jobs ORDER BY job_title_id")
        jobs = cursor.fetchall()
        for job in jobs:
            j_id, j_title = job[0], job[1]
            self.job_combo.addItem(str(j_title), userData=str(j_id))
        
    def populate_supervisors(self):

        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT e.employee_id, e.First_Name, e.Last_Name 
            FROM employees e 
            WHERE e.Job_title_Id IN (SELECT j.Job_title_Id FROM Jobs j WHERE j.job_title IN ('Manager','Supervisor')) 
            ORDER BY e.First_Name, e.Last_Name
        """)
        supervisors = cursor.fetchall()
        for sup in supervisors:
            sup_id, f_name, l_name = sup[0], sup[1], sup[2]
            full_name = f"{f_name or ''} {l_name or ''}".strip()
            if full_name:
                self.supervisor_combo.addItem(full_name, userData=str(sup_id))


    def populate_employement_status(self):

        cursor = self.db.conn.cursor()
        cursor.execute("SELECT DISTINCT Employeement_Status FROM employees WHERE Employeement_Status IS NOT NULL AND Employeement_Status != ''")
        statuses = [str(row[0]) for row in cursor.fetchall()]

        if not statuses:
            statuses = ["Active", "Inactive", "Onboarding", "Terminated"]

        for status in statuses:
            self.status_combo.addItem(status, userData=status)

    def get_changes(self):
        """Returns dict containing only fields that were changed."""
        changes = {}

        if self.dept_combo.currentIndex() > 0:
            val = self.dept_combo.currentData() or self.dept_combo.currentText()
            if val:
                changes['dept_id'] = val

        if self.job_combo.currentIndex() > 0:
            val = self.job_combo.currentData() or self.job_combo.currentText()
            if val:
                changes['job_title_id'] = val

        if self.supervisor_combo.currentIndex() > 0:
            val = self.supervisor_combo.currentData()
            if val:
                changes['Supervisor_id'] = val

        if self.status_combo.currentIndex() > 0:
            val = self.status_combo.currentData() or self.status_combo.currentText()
            if val:
                changes['Employeement_Status'] = val

        return changes


class AdminManageEmployees(QWidget):
    def __init__(self, db, current_user, logout_callback):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QHBoxLayout()
        lbl = QLabel("Admin: Manage Employees")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        back = QPushButton("Back to Dashboard"); back.clicked.connect(self.logout_callback)
        header.addWidget(lbl); header.addStretch(); header.addWidget(back)

        btns = QHBoxLayout()
        
        # --- SEARCH BAR SETUP ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search employee data across all fields...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                font-size: 13px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)

        add = QPushButton("Add Employee") 
        add.setFixedWidth(150)  
        add.setFixedHeight(35)  
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
        
        # Place search bar on the left, buttons on the right
        btns.addWidget(self.search_input)
        btns.addWidget(add)
        btns.addWidget(dele)

        self.table = QTableWidget()
        self.table.setColumnCount(14)

        headers = [
            "Username", "First Name", "Last Name", "Display Name", "Email", 
            "Supervisor ID", "Status", "Hired", "Type", "Date Hired", 
            "Created By", "Dept ID", "Job ID", "Action"
        ]
        self.table.setHorizontalHeaderLabels(headers)
       
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # Enable multi-row selection for bulk actions
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addLayout(header); layout.addLayout(btns); layout.addWidget(self.table)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        self.setLayout(layout)

    def filter_table(self):
        """Filters table rows based on text across ALL columns (Case-Insensitive)."""
        search_text = self.search_input.text().strip().lower()

        for row in range(self.table.rowCount()):
            match_found = False
            
            # Check all table columns (excluding column 13 which is the action button)
            for col in range(self.table.columnCount() - 1):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match_found = True
                    break  # Found match in this row, no need to check other columns for this row

            # Show/Hide row based on search match
            self.table.setRowHidden(row, not match_found)

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

        # Re-apply filter in case user was currently searching when reloading
        if hasattr(self, 'search_input') and self.search_input.text():
            self.filter_table()

    def open_add_employee_screen(self):
        dialog = AddEmployeeDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            employee_data = dialog.get_data()

            if not employee_data.get("Username") or not employee_data.get("Email"):
                QMessageBox.warning(self, "Input Error", "Username and Email are required.")
                return

            success = self.db.add_employee_with_requirements(employee_data)

            if success:
                link = dialog.generate_onboarding_token(employee_data["Email"], employee_data["Username"])
                self.load_data()

                self.send_email_trigger(employee_data["Email"], link)

                msg = f"Employee {employee_data['Username']} added!"
                QMessageBox.information(self, "Success", msg)

            else:
                QMessageBox.critical(self, "Error", "Username must be unique or Database error.")

    def del_emp(self):
        selected_rows = list(set(index.row() for index in self.table.selectedIndexes()))
        
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select row(s) to delete.")
            return

        reply = QMessageBox.question(
            self, 'Confirm Delete', 
            f"Are you sure you want to delete {len(selected_rows)} selected employee(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            deleted_count = 0
            for row in selected_rows:
                full_data = self.table.item(row, 0).data(Qt.UserRole)
                if full_data:
                    employee_id = full_data[0]
                    username = full_data[1]
                    if self.db.delete_employee(employee_id):
                        deleted_count += 1
                        self.db.dispatch_alert_event("Employee_Record_Deleted", username, "Admin_User")
            
            self.load_data()
            QMessageBox.information(self, "Success", f"{deleted_count} employee(s) deleted.")

    def send_email_trigger(self, recipient_email, link=None):
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

            body = (
                f"Hello,\n\n"
                f"Welcome to the team! Your onboarding process has officially started.\n"
                f"Please click the link below to set up your account password:\n\n"
                f"{link}\n\n"
                f"Best regards,\n"
                f"Admin Team"
            )
            
            message.attach(MIMEText(body, "plain"))

            # 2. Connect to Server and Send
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(message)
            server.quit()

            QMessageBox.information(self, "Success", f"Email successfully sent to {recipient_email}")
            
            return True
        
        except Exception as e:
            QMessageBox.critical(self, "Email Error", f"Failed to send email: {str(e)}")
            return False
    
    def show_context_menu(self, position):
        selected_rows = list(set(index.row() for index in self.table.selectedIndexes()))
        if not selected_rows:
            return

        menu = QMenu()
        
        # Open Single Record option
        open_record_action = menu.addAction("Open Employee Record") if len(selected_rows) == 1 else None

        # Bulk Edit option ONLY shows when MORE THAN 1 row is selected
        bulk_edit_action = menu.addAction(f"Bulk Edit ({len(selected_rows)} Selected)") if len(selected_rows) > 1 else None

        delete_action = menu.addAction("Delete Selected Employee(s)")
        
        action = menu.exec_(self.table.viewport().mapToGlobal(position))

        if open_record_action and action == open_record_action:
            self.open_employee_record(selected_rows[0])
        elif bulk_edit_action and action == bulk_edit_action:
            self.open_bulk_edit_dialog(selected_rows)
        elif action == delete_action:
            self.del_emp()

    def open_bulk_edit_dialog(self, selected_rows):
        """Opens Bulk Edit dialog and updates selected employees in DB."""
        dialog = BulkEditDialog(self.db, len(selected_rows), parent=self)
        if dialog.exec_() == QDialog.Accepted:
            changes = dialog.get_changes()

            if not changes:
                QMessageBox.information(self, "No Changes", "No attributes were modified.")
                return

            updated_count = 0
            for row in selected_rows:
                full_data = self.table.item(row, 0).data(Qt.UserRole)
                if not full_data:
                    continue
                
                emp_id = full_data[0]
                
                # Execute direct SQL update on selected employee_id
                try:
                    cursor = self.db.conn.cursor()
                    
                    # Construct UPDATE dynamically depending on placeholder format (%s or ?)
                    set_clauses = []
                    values = []
                    for col_name, col_val in changes.items():
                        set_clauses.append(f"{col_name} = %s")
                        values.append(col_val)
                    
                    values.append(emp_id)
                    query = f"UPDATE employees SET {', '.join(set_clauses)} WHERE employee_id = %s"
                    
                    try:
                        cursor.execute(query, values)
                    except Exception:
                        # Fallback for SQLite query format
                        query_sqlite = f"UPDATE employees SET {', '.join([f'{col} = ?' for col in changes.keys()])} WHERE employee_id = ?"
                        cursor.execute(query_sqlite, values)

                    self.db.conn.commit()
                    updated_count += 1
                except Exception as e:
                    print(f"Error updating employee ID {emp_id}: {e}")

            self.load_data()
            QMessageBox.information(self, "Success", f"Successfully updated {updated_count} employee(s).")

    def open_employee_record(self, row):
        admin_name = self.current_user
        # We stored the full database tuple in the first item's UserRole
        full_data = self.table.item(row, 0).data(Qt.UserRole)

        dialog = EmployeeRecordDialog(full_data, self.db, admin_name, self )
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()