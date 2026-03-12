from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QLabel, QHeaderView, 
                             QMenu, QAction, QMessageBox, QDialog, QFileDialog)
from PyQt5.QtCore import Qt
from database_manager import DatabaseManager
import os
import shutil
from Admin_Page.Manage_Employees.Admin_EmpRequirement_EditRecord import EditRequirementDialog

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
        query = """
            SELECT 
                er.Employee_Req_ID, 
                rsi.Req_Name, 
                rsi.Req_Item_Type, 
                er.Requirement_Status,
                er.Date_Created,
                er.Requirement_Due_Date,
                er.Requirement_Completion_Date,
                ra.attachment_id,
                ra.file_path

            FROM Employee_Requirements er
            JOIN Requirements_Setup_Items rsi ON er.Req_id = rsi.Req_id AND er.Req_line_id = rsi.Req_line_id
            LEFT JOIN Requirement_Attachments ra ON er.Employee_Req_ID = ra.Employee_Req_ID and er.Employee_id = ra.Employee_Name
            WHERE er.Employee_id = ?
        """
        rows = self.db.execute_query(query, (self.employee_id,))
        
        self.table.setRowCount(0)
        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
           
            for c_idx, value in enumerate(row):
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(value)))

            # Add Actions Button
            actions_btn = QPushButton("Actions ▾")
            actions_btn.setStyleSheet("background-color: #f1f2f6; border: 1px solid #dcdde1; padding: 5px;")
            
            # Create Menu for the button
            menu = QMenu()
            edit_act = QAction("Edit Record", self)
            del_act = QAction("Delete Record", self)
            # upload_act = QAction("Attach File", self)
            
            # Connect actions (passing the ID via a lambda)
            req_id = row[0]
            file_path = row[8]
            
            if file_path and os.path.exists(file_path):
                file_action = QAction("View File 👁️", self)
                file_action.triggered.connect(lambda checked, p=file_path: self.view_file(p))
            else:
                file_action = QAction("Attach File 📎", self)
                file_action.triggered.connect(lambda checked, r=req_id: self.upload_requirement(r, self.employee_id))



            edit_act.triggered.connect(lambda checked, r=req_id, f=file_path: self.edit_record(r, f))
            del_act.triggered.connect(lambda checked, r=req_id: self.delete_record(r))
            # upload_act.triggered.connect(lambda checked, r=req_id: self.upload_requirement(r, self.employee_id))
            
            menu.addActions([edit_act, del_act, file_action])
            actions_btn.setMenu(menu)
            
            self.table.setCellWidget(r_idx, 7, actions_btn)

    def delete_record(self, record_id):
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to remove this requirement from the employee?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_employee_requirement(record_id):
                self.load_data()

    def upload_requirement(self, req_id, employee_name):
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
                    employee_req_id=req_id
                )

                if success:
                    QMessageBox.information(self, "Success", "File uploaded and recorded successfully!")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Database Error", "File copied but failed to save to database.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            
    def view_file(self, path):
        """Opens the file using the default system application."""
        try:
            if os.path.exists(path):
                # For Windows:
                os.startfile(os.path.abspath(path))
                # For macOS: os.system(f"open '{path}'")
                # For Linux: os.system(f"xdg-open '{path}'")
            else:
                QMessageBox.warning(self, "Error", "The file could not be found on the server.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")


    def edit_record(self, record_id, file_path=None):
        target_row = -1
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == str(record_id):
                target_row = row
                # break
        
        if target_row == -1: return

        def get_text(r, c):
            item = self.table.item(r, c)
            return item.text() if item and item.text() != "None" else ""

        # Gather current values from table
        current_data = {
            "item_name": get_text(target_row, 1),
            "type": get_text(target_row, 2),
            "status": get_text(target_row, 3),
            "due_date": get_text(target_row, 5),
            "comp_date": get_text(target_row, 6),
            "file_path": file_path if file_path else "None"
        }

        dialog = EditRequirementDialog(current_data, self)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()

            # 1. Update Database (Employee_Requirements)
            query = """
                UPDATE Employee_Requirements 
                SET Requirement_Status = ?, 
                    Requirement_Due_Date = ?, 
                    Requirement_Completion_Date = ?
                WHERE Employee_Req_ID = ?
            """
            self.db.execute_non_query(query, (new_data['status'], new_data['due_date'], new_data['comp_date'], record_id))

            # 2. Handle File Replacement if needed
            if new_data['new_file_path']:
                # Logic to delete old file from disk could be added here
                self.process_replacement_file(record_id, new_data['new_file_path'])

            QMessageBox.information(self, "Success", "Record and Attachment updated!")
            self.load_data()

    def process_replacement_file(self, req_id, file_path):
        # Reuses your logic to copy file and update attachment DB
        upload_dir = "uploaded_requirements"
        os.makedirs(upload_dir, exist_ok=True)
        unique_filename = f"Updated_{req_id}_{os.path.basename(file_path)}"
        dest_path = os.path.join(upload_dir, unique_filename)
        shutil.copy(file_path, dest_path)
        
        # Update the attachment table for this specific requirement ID
        # Note: Depending on your DB, you might need an UPDATE instead of add_attachment
        self.db.update_attachment(req_id, dest_path, unique_filename)
