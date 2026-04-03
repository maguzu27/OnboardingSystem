from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QFileDialog, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt
import os
import shutil

class RequirementsPage(QWidget):
    def __init__(self, db, username):
        super().__init__()
        self.db = db
        self.username = username
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)

        # Title
        title = QLabel("📋 My Onboarding Checklists & Documents")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        # --- THE PROFESSIONAL TABLE ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Requirement Item", "Type", "Status", "Due Date", "Completed Date"
        ])
        
        # Table Styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dcdde1;
                gridline-color: #f1f2f6;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                padding: 10px;
                color: #2c3e50;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Read-only for employees
        
        # Stretch columns gracefully
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID column small
        
        layout.addWidget(self.table)

        # --- ACTIONS SECTION ---
        actions_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton(" ⬆  Upload Document for Selected Item")
        self.upload_btn.setFixedWidth(300)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c; color: white; padding: 12px; 
                border-radius: 6px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #16a085; }
        """)
        self.upload_btn.clicked.connect(self.handle_upload)

        actions_layout.addWidget(self.upload_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)

    def refresh_table_data(self):
        """Fetches requirements for the current username and populates the table."""
        if not self.username:
            return

        # 1. Get Employee ID from Username (since query filters by Employee_id)
        emp_data = self.db.get_employee_by_username(self.username)
        if not emp_data:
            return
        
        employee_id = emp_data[20]
        print (f"Refreshing requirements table for employee ID: {employee_id} (username: {self.username})")  # Debug statement

        # 2. Query data
        query = """
            SELECT 
                er.Employee_Req_ID, 
                rsi.Req_Name, 
                rsi.Req_Item_Type, 
                er.Requirement_Status,
                er.Requirement_Due_Date,
                er.Requirement_Completion_Date,
                ra.attachment_id,
                ra.file_path
            FROM Employee_Requirements er
                JOIN Requirements_Setup_Items rsi ON er.Req_id = rsi.Req_id AND er.Req_line_id = rsi.Req_line_id
                LEFT JOIN Requirement_Attachments ra ON er.Employee_Req_ID = ra.Employee_Req_ID
            WHERE er.Employee_id = ?
        """
        rows = self.db.execute_query(query, (employee_id,))
        print(f"Loaded using employee_id: {employee_id}")  # Debug statement to check what data is being returned
        print(f"Loaded {len(rows)} requirement records for employee ID {employee_id}")  # Debug statement

        self.table.setRowCount(0)
        
        if not rows:
            return

        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            
            # Map selected SQL columns to UI cells
            self.table.setItem(r_idx, 0, QTableWidgetItem(str(row[0]))) # ID
            self.table.setItem(r_idx, 1, QTableWidgetItem(str(row[1]))) # Name
            self.table.setItem(r_idx, 2, QTableWidgetItem(str(row[2]))) # Type
            self.table.setItem(r_idx, 3, QTableWidgetItem(str(row[3]))) # Status
            self.table.setItem(r_idx, 4, QTableWidgetItem(str(row[4]) if row[4] else "N/A")) # Due Date
            self.table.setItem(r_idx, 5, QTableWidgetItem(str(row[5]) if row[5] else "Pending")) # Comp Date

    def handle_upload(self):
        # Determine which row is selected
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            QMessageBox.warning(self, "Selection Missing", "Please select a requirement from the table first!")
            return

        row = selected_ranges[0].topRow()
        req_id = self.table.item(row, 0).text()

        file_path, _ = QFileDialog.getOpenFileName(self, "Open Document", "", "PDF Files (*.pdf);;Images (*.png *.jpg)")
        
        if file_path:
            try:
                # Setup destination
                upload_dir = "uploaded_requirements"
                os.makedirs(upload_dir, exist_ok=True)

                original_filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                unique_filename = f"{self.username}_{req_id}_{original_filename}"
                destination_path = os.path.join(upload_dir, unique_filename)

                shutil.copy(file_path, destination_path)

                # Save to DB
                success = self.db.add_attachment(
                    file_path=destination_path,
                    file_name=unique_filename,
                    original_name=original_filename,
                    username=self.username,
                    file_size=file_size,
                    employee_req_id=req_id
                )

                if success:
                    QMessageBox.information(self, "Success", "Requirement document uploaded successfully!")
                    self.refresh_table_data() # Update the table view
                else:
                    QMessageBox.warning(self, "Error", "Attachment failed to save to database.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")