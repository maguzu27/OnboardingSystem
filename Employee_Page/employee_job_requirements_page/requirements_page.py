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

        title = QLabel("📋 My Onboarding Checklists & Documents")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Requirement Item", "Type", "Status", "Due Date", "Completed Date", "Attachment"
        ])
        
        # Professional Styling
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border-radius: 8px; border: 1px solid #dcdde1; }
            QHeaderView::section { background-color: #34495e; color: white; font-weight: bold; padding: 8px; }
            QTableWidget::item { padding: 10px; color: #2c3e50; }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(45) # Give buttons more height

        # --- FIX FOR STRETCHED/SQUEEZED COLUMNS ---
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive) # Allow manual adjustment
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Requirement Name takes priority
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Due Date
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Completed Date
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Attachment Button
        
        layout.addWidget(self.table)

        # Bottom Action Bar
        actions_layout = QHBoxLayout()
        self.upload_btn = QPushButton(" ⬆  Upload Document for Selected Item")
        self.upload_btn.setFixedWidth(300)
        self.upload_btn.setStyleSheet("""
            QPushButton { background-color: #1abc9c; color: white; padding: 12px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #16a085; }
        """)
        self.upload_btn.clicked.connect(self.handle_general_upload)
        actions_layout.addWidget(self.upload_btn)
        actions_layout.addStretch()
        layout.addLayout(actions_layout)

    def refresh_table_data(self):
        if not self.username: return

        emp_data = self.db.get_employee_by_username(self.username)
        if not emp_data: return
        
        # Using index 0 for ID (standard) - update if your schema differs
        employee_id = emp_data[20] 

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
        self.table.setRowCount(0)
        
        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            self.table.setItem(r_idx, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(r_idx, 1, QTableWidgetItem(str(row[1])))
            self.table.setItem(r_idx, 2, QTableWidgetItem(str(row[2])))
            
            status = str(row[3])
            status_item = QTableWidgetItem(status)
            if status.lower() == "completed":
                status_item.setForeground(Qt.darkGreen)
            self.table.setItem(r_idx, 3, status_item)

            self.table.setItem(r_idx, 4, QTableWidgetItem(str(row[4]) if row[4] else "N/A"))
            self.table.setItem(r_idx, 5, QTableWidgetItem(str(row[5]) if row[5] else "Pending"))

            # Button logic
            req_id = str(row[0])
            file_path = row[7]

            if file_path and os.path.exists(file_path):
                btn = QPushButton("📄 View File")
                btn.setStyleSheet("background-color: #3498db; color: white; border-radius: 4px; padding: 5px;")
                btn.clicked.connect(lambda checked, p=file_path: os.startfile(os.path.abspath(p)))
            else:
                btn = QPushButton("⬆ Upload")
                btn.setStyleSheet("background-color: #1abc9c; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
                btn.clicked.connect(lambda checked, r=req_id: self.process_upload(r))
            
            self.table.setCellWidget(r_idx, 6, btn)

    def handle_general_upload(self):
        """Logic for the large button below the table"""
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            QMessageBox.warning(self, "Selection Missing", "Please select a row first!")
            return
        row = selected_ranges[0].topRow()
        req_id = self.table.item(row, 0).text()
        self.process_upload(req_id)

    def process_upload(self, req_id):
        """Unified upload logic used by both the row buttons and the general button"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Document", "", "PDF Files (*.pdf);;Images (*.png *.jpg)")
        if not file_path: return

        try:
            upload_dir = "uploaded_requirements"
            os.makedirs(upload_dir, exist_ok=True)
            
            original_filename = os.path.basename(file_path)
            unique_filename = f"{self.username}_{req_id}_{original_filename}"
            destination_path = os.path.join(upload_dir, unique_filename)

            shutil.copy(file_path, destination_path)

            success = self.db.add_attachment(
                file_path=destination_path,
                file_name=unique_filename,
                original_name=original_filename,
                username=self.username,
                file_size=os.path.getsize(file_path),
                employee_req_id=req_id
            )

            if success:
                QMessageBox.information(self, "Success", "Document uploaded successfully!")
                self.refresh_table_data()
            else:
                QMessageBox.warning(self, "Error", "Database update failed.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")