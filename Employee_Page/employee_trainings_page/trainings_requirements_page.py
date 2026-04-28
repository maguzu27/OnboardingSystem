from PyQt5.QtWidgets import (QMenu, QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QFileDialog, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import QTimer, Qt
import os
import shutil
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

class TrainingRequirementsPage(QWidget):
    def __init__(self, db, username):
        super().__init__()
        self.db = db
        self.username = username
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)

        title = QLabel("📋 My Training Requirements")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Training Name", "Description ", "Due Date", "Completion Status", "Completion Date", "Assigned By", "Training Link" 
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
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Training Name
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Description takes priority
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Due Date
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Completion Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Completion Date
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Assigned By
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Training Link
        
        layout.addWidget(self.table)

    def refresh_table_data(self):
        if not self.username: return

        emp_data = self.db.get_employee_by_username(self.username)
        if not emp_data: return

        self.employee_id = emp_data[20]

        rows = self.db.get_employee_training_items(self.employee_id)
        self.table.setRowCount(0)
        

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)

        try: self.table.customContextMenuRequested.disconnect()
        except: pass

        self.table.customContextMenuRequested.connect(self.show_context_menu)

        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            self.table.setItem(r_idx, 0, QTableWidgetItem(str(row[10]))) # Training Name
            self.table.setItem(r_idx, 1, QTableWidgetItem(str(row[9]))) # Description
            self.table.setItem(r_idx, 2, QTableWidgetItem(str(row[3]))) # Due Date
            self.table.setItem(r_idx, 3, QTableWidgetItem(str(row[4]))) # Completion Status
            self.table.setItem(r_idx, 4, QTableWidgetItem(str(row[5]))) # Completion Date
            self.table.setItem(r_idx, 5, QTableWidgetItem(str(row[7]))) # Assigned By
            self.table.setItem(r_idx, 6, QTableWidgetItem(str(row[11]))) # Training Link (resources)



    def show_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        
        row = index.row()
        self.table.selectRow(row)

        # print( employee_id, training_id)

        if row < 0: return

        menu = QMenu(self.table)
        update_status_action = menu.addAction("Update Training Status")
        open_training_action = menu.addAction("Open Training Link")
        
        action = menu.exec_(self.table.viewport().mapToGlobal(pos))
        
        if action == update_status_action:
            QTimer.singleShot(10, lambda: self.update_record(row))
        elif action == open_training_action:
            QTimer.singleShot(10, lambda: self.open_training_link(row))


    def update_record(self, row):
        print("Update logic for row:", row)

        rows = self.db.get_employee_training_items(self.employee_id)

        training_id = rows[row][1] 
    

        # 2. Create a simple update dialog
        from PyQt5.QtWidgets import QDialog, QFormLayout, QComboBox, QDateEdit
        from PyQt5.QtCore import QDate

        dialog = QDialog(self)
        dialog.setWindowTitle("Update Training Status")
        dialog.setMinimumWidth(300)
        form = QFormLayout(dialog)

        # Status Dropdown
        status_input = QComboBox()
        status_input.addItems(["Pending", "In Progress", "Completed"])
        current_status = self.table.item(row, 3).text()
        status_input.setCurrentText(current_status)

        # Completion Date Input
        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        current_date_str = self.table.item(row, 4).text()
        
        if current_date_str and current_date_str != "None" and current_date_str != "N/A":
            date_input.setDate(QDate.fromString(current_date_str, "yyyy-MM-dd"))
        else:
            date_input.setDate(QDate.currentDate())

        form.addRow("Status:", status_input)
        form.addRow("Date Completed:", date_input)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Update")
        save_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(save_btn)
        form.addRow(btn_layout)

        # 3. If user clicks Update, save to DB
        if dialog.exec_():
            new_status = status_input.currentText()
            new_date = date_input.date().toString("yyyy-MM-dd")

            # Call your DB update method
            # You might need to add this method to your database class if it doesn't exist
            success = self.db.update_employee_training_status(
                employee_id = self.employee_id,
                training_id=training_id,
                status=new_status,
                completion_date=new_date
            )

            if success:
                QMessageBox.information(self, "Success", "Record updated successfully!")
                self.refresh_table_data()
            else:
                QMessageBox.warning(self, "Error", "Failed to update record.")

    def open_training_link(self, row):
        """
        Retrieves the link from the table and opens it in the default web browser.
        """
        # Column 6 is "Training Link" based on your init_ui setup
        link_item = self.table.item(row, 6)
        
        if not link_item:
            QMessageBox.warning(self, "No Link", "There is no link associated with this training.")
            return

        link_text = link_item.text().strip()

        # Check if the link exists and isn't just a placeholder string
        if not link_text or link_text.lower() in ["none", "n/a", "pending"]:
            QMessageBox.warning(self, "No Link", "No valid training link or resource path found.")
            return

        # Create a QUrl object. 
        # QUrl.fromUserInput is smart: it handles adding 'http://' if missing 
        # and also handles local file paths correctly.
        url = QUrl.fromUserInput(link_text)

        if url.isValid():
            success = QDesktopServices.openUrl(url)
            if not success:
                QMessageBox.critical(self, "Error", f"Failed to open the link: {link_text}")
        else:
            QMessageBox.warning(self, "Invalid Link", f"The link provided is not valid: {link_text}")
            
    # def update_record(self, row):
        # def get_text(r, c):
        #     item = self.table.item(r, c)
        #     return item.text() if item else ""

        # data = {
        #     'id': get_text(row, 8),
        #     'training_name': get_text(row, 0),
        #     'training_description': get_text(row, 1),
        #     'training_type': get_text(row, 2),
        #     'training_duration': get_text(row, 3),
        #     'training_provider': get_text(row, 4),
        #     'group_requirement': get_text(row, 5),
        #     'training_resources': get_text(row, 6),
        #     'training_contact_name': get_text(row, 9), 
        #     'training_contact_email': get_text(row, 10)
        # }

        # self.open_training_dialog(row_data=data)

    # def handle_general_upload(self):
    #     """Logic for the large button below the table"""
    #     selected_ranges = self.table.selectedRanges()
    #     if not selected_ranges:
    #         QMessageBox.warning(self, "Selection Missing", "Please select a row first!")
    #         return
    #     row = selected_ranges[0].topRow()
    #     req_id = self.table.item(row, 0).text()
    #     self.process_upload(req_id)

    # def process_upload(self, req_id):
    #     """Unified upload logic used by both the row buttons and the general button"""
    #     file_path, _ = QFileDialog.getOpenFileName(self, "Open Document", "", "PDF Files (*.pdf);;Images (*.png *.jpg)")
    #     if not file_path: return

    #     try:
    #         upload_dir = "uploaded_requirements"
    #         os.makedirs(upload_dir, exist_ok=True)
            
    #         original_filename = os.path.basename(file_path)
    #         unique_filename = f"{self.username}_{req_id}_{original_filename}"
    #         destination_path = os.path.join(upload_dir, unique_filename)

    #         shutil.copy(file_path, destination_path)

    #         success = self.db.add_attachment(
    #             file_path=destination_path,
    #             file_name=unique_filename,
    #             original_name=original_filename,
    #             username=self.username,
    #             file_size=os.path.getsize(file_path),
    #             employee_req_id=req_id
    #         )

    #         if success:
    #             QMessageBox.information(self, "Success", "Document uploaded successfully!")
    #             self.refresh_table_data()
    #         else:
    #             QMessageBox.warning(self, "Error", "Database update failed.")

    #     except Exception as e:
    #         QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")
    #         QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

