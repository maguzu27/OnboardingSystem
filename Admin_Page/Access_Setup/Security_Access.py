from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, 
                             QDialog, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt

class UserAccessDialog(QDialog):
    """Dialog to Add or Edit User Access & Permissions."""
    def __init__(self, db, user_data=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_data = user_data  # None if adding new, else tuple/dict of existing user
        self.setWindowTitle("Edit User Access" if user_data else "Grant User Access")
        self.setFixedSize(380, 260)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["employee", "admin"])

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive", "Pending"])

        # If editing existing record, pre-fill values
        if self.user_data:
            # Assumes user_data format: (id, username, role, status, ...)
            self.username_input.setText(str(self.user_data[1]))
            self.username_input.setReadOnly(True)  # Don't allow username change on edit
            
            curr_role = str(self.user_data[2]).lower() if len(self.user_data) > 2 else "employee"
            role_idx = self.role_combo.findText(curr_role, Qt.MatchFixedString)
            if role_idx >= 0:
                self.role_combo.setCurrentIndex(role_idx)

            curr_status = str(self.user_data[3]) if len(self.user_data) > 3 else "Active"
            status_idx = self.status_combo.findText(curr_status, Qt.MatchFixedString)
            if status_idx >= 0:
                self.status_combo.setCurrentIndex(status_idx)

        layout.addRow("Username:", self.username_input)
        layout.addRow("Access Role:", self.role_combo)
        layout.addRow("Account Status:", self.status_combo)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 6px; font-weight: bold; border-radius: 4px;")
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #7f8c8d; color: white; padding: 6px; border-radius: 4px;")
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

    def get_data(self):
        return {
            "username": self.username_input.text().strip(),
            "role": self.role_combo.currentText(),
            "status": self.status_combo.currentText()
        }


class SecurityAccessManager(QWidget):
    """Main Screen for Managing User Access Levels and Permissions."""
    def __init__(self, db, admin_name, back_callback):
        super().__init__()
        self.db = db
        self.admin_name = admin_name
        self.back_callback = back_callback
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        header_label = QLabel("Security & Access Control")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setStyleSheet("background-color: #7f8c8d; color: white; padding: 6px 12px; border-radius: 4px;")
        back_btn.clicked.connect(self.back_callback)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(back_btn)

        # --- CONTROLS BAR (Search & Action Buttons) ---
        controls_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search user, role, or status...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                font-size: 13px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus { border: 1px solid #3498db; }
        """)
        self.search_input.textChanged.connect(self.filter_table)

        grant_access_btn = QPushButton("➕ Modify / Grant Access")
        grant_access_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white; font-weight: bold; 
                padding: 8px 14px; border-radius: 5px;
            }
            QPushButton:hover { background-color: #219150; }
        """)
        grant_access_btn.clicked.connect(self.open_edit_dialog)

        revoke_btn = QPushButton("🗑️ Revoke / Delete Access")
        revoke_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white; font-weight: bold; 
                padding: 8px 14px; border-radius: 5px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        revoke_btn.clicked.connect(self.delete_user_access)

        controls_layout.addWidget(self.search_input)
        controls_layout.addWidget(grant_access_btn)
        controls_layout.addWidget(revoke_btn)

        # --- USER ACCESS TABLE ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "User ID", "Username", "Access Level (Role)", "Status", "Actions"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add to Layout
        main_layout.addLayout(header_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.table)

    def load_data(self):
        """Fetches user accounts and fills table."""
        self.table.setRowCount(0)
        
        # Calls database method to get users (fallback to get_all_employees if method missing)
        if hasattr(self.db, 'get_all_users_access'):
            users = self.db.get_all_users_access()
        elif hasattr(self.db, 'get_all_employees'):
            users = self.db.get_all_employees()
        else:
            users = []

        for row_idx, user in enumerate(users):
            self.table.insertRow(row_idx)

            # Safely handle database indices
            user_id = str(user[0]) if len(user) > 0 else ""
            username = str(user[1]) if len(user) > 1 else ""
            role = str(user[15]) if len(user) > 15 else (str(user[2]) if len(user) > 2 else "employee")
            status = str(user[13]) if len(user) > 13 else (str(user[3]) if len(user) > 3 else "Active")

            # Fill columns
            item_id = QTableWidgetItem(user_id)
            item_id.setData(Qt.UserRole, user)  # Attach full raw user record
            
            self.table.setItem(row_idx, 0, item_id)
            self.table.setItem(row_idx, 1, QTableWidgetItem(username))
            self.table.setItem(row_idx, 2, QTableWidgetItem(role.upper()))
            self.table.setItem(row_idx, 3, QTableWidgetItem(status))

            # Action Edit Button inside row
            edit_btn = QPushButton("Edit Role")
            edit_btn.setStyleSheet("background-color: #3498db; color: white; border-radius: 3px; padding: 3px;")
            edit_btn.clicked.connect(lambda ch, r=row_idx: self.open_edit_dialog(r))
            self.table.setCellWidget(row_idx, 4, edit_btn)

        if self.search_input.text():
            self.filter_table()

    def filter_table(self):
        """Case-insensitive search filter."""
        query = self.search_input.text().strip().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount() - 1):
                item = self.table.item(row, col)
                if item and query in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def open_edit_dialog(self, row=None):
        """Opens modal dialog to edit selected row or current selection."""
        target_row = row if row is not None else self.table.currentRow()
        user_data = None

        if target_row >= 0:
            user_data = self.table.item(target_row, 0).data(Qt.UserRole)

        dialog = UserAccessDialog(self.db, user_data=user_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["username"]:
                QMessageBox.warning(self, "Input Error", "Username is required.")
                return

            # Update DB (uses helper or custom db update method)
            if hasattr(self.db, 'update_user_access_role'):
                success = self.db.update_user_access_role(data["username"], data["role"], data["status"])
            else:
                # Basic fallback DB execution if specific method isn't in DatabaseManager yet
                try:
                    cursor = self.db.conn.cursor()
                    cursor.execute(
                        "UPDATE employees SET role = %s, status = %s WHERE username = %s",
                        (data["role"], data["status"], data["username"])
                    )
                    self.db.conn.commit()
                    success = True
                except Exception as e:
                    QMessageBox.critical(self, "Database Error", str(e))
                    success = False

            if success:
                QMessageBox.information(self, "Success", f"Access permissions updated for {data['username']}.")
                self.load_data()

    def delete_user_access(self):
        """Revokes access or removes user record."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a user to revoke access.")
            return

        user_data = self.table.item(row, 0).data(Qt.UserRole)
        username = self.table.item(row, 1).text() if self.table.item(row, 1) else "selected user"

        reply = QMessageBox.question(
            self, 'Confirm Revoke Access',
            f"Are you sure you want to revoke access/delete user '{username}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if hasattr(self.db, 'delete_user_access'):
                success = self.db.delete_user_access(username)
            elif hasattr(self.db, 'delete_employee') and user_data:
                user_id = user_data[0]
                success = self.db.delete_employee(user_id)
            else:
                success = False

            if success:
                QMessageBox.information(self, "Success", f"Access for {username} has been revoked.")
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Could not revoke user access.")