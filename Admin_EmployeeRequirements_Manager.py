from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QLabel, QHeaderView, 
                             QMenu, QAction, QMessageBox, QDialog, QFileDialog)
from PyQt5.QtCore import Qt
from database_manager import DatabaseManager
import os
import shutil

class EmployeeRequirementsScreen(QDialog):
    def __init__(self, db, employee_id, employee_name, parent=None):
        super().__init__(parent)
        self.db = db
        self.employee_id = employee_id
        self.setWindowTitle(f"Requirements for {employee_name}")
        self.resize(900, 500)
        self.init_ui(employee_name)

    def init_ui(self, employee_name):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(f"Requirement Checklist: {employee_name}")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px 0;")
        layout.addWidget(header)

        # Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Requirement Item", "Type", "Status", "Date Created", "Due Date", "Completed Date", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        """
        Joins Employee_Requirements with Requirements_Setup_Items 
        to show friendly names.
        """
        query = """
            SELECT 
                er.Employee_Req_ID, 
                rsi.Req_Name, 
                rsi.Req_Item_Type, 
                er.Requirement_Status,
                er.Date_Created,
                er.Requirement_Due_Date,
                er.Requirement_Completion_Date
            FROM Employee_Requirements er
            JOIN Requirements_Setup_Items rsi ON er.Req_id = rsi.Req_id AND er.Req_line_id = rsi.Req_line_id
            WHERE er.Employee_id = ?
        """
        rows = self.db.execute_query(query, (self.employee_id,))
        
        self.table.setRowCount(0)
        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            for c_idx, value in enumerate(row):
                # breakpoint()
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(value)))

            # Add Actions Button
            actions_btn = QPushButton("Actions ▾")
            actions_btn.setStyleSheet("background-color: #f1f2f6; border: 1px solid #dcdde1; padding: 5px;")
            
            # Create Menu for the button
            menu = QMenu()
            edit_act = QAction("Edit Status", self)
            del_act = QAction("Delete Record", self)
            upload_act = QAction("Attach File", self)
            
            # Connect actions (passing the ID via a lambda)
            req_id = row[0]
            edit_act.triggered.connect(lambda checked, r=req_id: self.edit_record(r))
            del_act.triggered.connect(lambda checked, r=req_id: self.delete_record(r))
            upload_act.triggered.connect(lambda checked, r=req_id: self.upload_requirement(r, self.employee_id))
            
            menu.addActions([edit_act, del_act, upload_act])
            actions_btn.setMenu(menu)
            
            self.table.setCellWidget(r_idx, 7, actions_btn)

    def edit_record(self, record_id):
        # Here you would open a small dialog to change 'Ask_Employee' status
        print(f"Edit Requirement ID: {record_id}")

    def delete_record(self, record_id):
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to remove this requirement from the employee?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_employee_requirement(record_id):
                self.load_data()

    def upload_requirement(self, req_id, employee_name):

        # # 1. Open File Dialog
        # options = QFileDialog.Options()
        # file_path, _ = QFileDialog.getOpenFileName(
        #     self, "Select File to Upload", "", 
        #     "All Files (*);;PDF Files (*.pdf);;Images (*.png *.jpg)", options=options
        # )

        # if file_path:
        #     try:
        #         # 2. Setup Destination
        #         upload_dir = "uploaded_requirements"
        #         if not os.path.exists(upload_dir):
        #             os.makedirs(upload_dir)

        #         original_filename = os.path.basename(file_path)
        #         file_size = os.path.getsize(file_path)
                
        #         # Use timestamp + req_id to ensure absolute uniqueness
        #         from datetime import datetime
        #         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #         unique_filename = f"{req_id}_{timestamp}_{original_filename}"
        #         destination_path = os.path.join(upload_dir, unique_filename)

        #         # 3. Copy file to project folder
        #         shutil.copy(file_path, destination_path)

        #         # 4. Save metadata to Database (including the req_id)
        #         success = self.db.add_attachment(
        #             req_id=req_id,
        #             file_path=destination_path,
        #             file_name=unique_filename,
        #             original_name=original_filename,
        #             username=employee_name,
        #             file_size=file_size
        #         )

        #         if success:
        #             # OPTIONAL: Automatically update status to 'Submitted' or 'Received'
        #             # self.db.update_req_status(req_id, "Received") 
        #             QMessageBox.information(self, "Success", "File attached successfully!")
        #             self.load_data() # Refresh table
        #         else:
        #             QMessageBox.warning(self, "Database Error", "File copied but failed to link in database.")

        #     except Exception as e:
        #         QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")




    # def upload_requirement(self, employee_name):
        # 1. Open File Dialog
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Upload", "", 
            "All Files (*);;PDF Files (*.pdf);;Images (*.png *.jpg)", options=options
        )

        if file_path:
            try:
                # 2. Setup Destination
                upload_dir = "uploaded_requirements"
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                original_filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                # Create a unique filename to prevent overwriting
                unique_filename = f"{employee_name}_{original_filename}"
                destination_path = os.path.join(upload_dir, unique_filename)

                # 3. Copy file to project folder
                shutil.copy(file_path, destination_path)

                # 4. Save metadata to Database
                success = self.db.add_attachment(
                    file_path=destination_path,
                    file_name=unique_filename,
                    original_name=original_filename,
                    username=employee_name,
                    file_size=file_size,
                    employee_req_id=req_id  # Pass the employee requirement ID
                )

                if success:
                    QMessageBox.information(self, "Success", "File uploaded and recorded successfully!")
                else:
                    QMessageBox.warning(self, "Database Error", "File copied but failed to save to database.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            