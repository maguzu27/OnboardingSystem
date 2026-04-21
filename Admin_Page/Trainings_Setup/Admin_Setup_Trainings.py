from PyQt5.QtWidgets import (QMenu, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QPushButton, QLabel, QHeaderView, QTableWidgetItem, 
                             QComboBox, QLineEdit, QDialog, QFormLayout, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer

from Admin_Page.Trainings_Setup.Admin_Training_Dialog import TrainingDialog
from Admin_Page.Trainings_Setup.Admin_Setup_Employee_Trainings import AdminTrainingAssignment

class AdminTrainingManagement(QWidget):
    def __init__(self, db,current_user, back_callback):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.back_callback = back_callback
        self.init_ui()
        

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header & Add Button
        header_layout = QHBoxLayout()

        # --- NEW BACK BUTTON ---
        back_btn = QPushButton("⬅ Back")
        back_btn.setFixedWidth(80)
        back_btn.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold; padding: 5px;")
        back_btn.clicked.connect(self.back_callback) # Uses the callback passed in __init__
        header_layout.addWidget(back_btn)

        title = QLabel("📚 Global Training Registry")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        add_btn = QPushButton("+ Create New Training")
        add_btn.clicked.connect(lambda: self.open_training_dialog(row_data=None)) # Pass None for new record
        add_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px;")

        add_emp_training_btn = QPushButton("+ Setup Employee Trainings")
        add_emp_training_btn.clicked.connect(lambda: self.open_employee_training_dialog()) # Pass None for new record
        add_emp_training_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        header_layout.addWidget(add_emp_training_btn)
        layout.addLayout(header_layout)

        # Training Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Training Name", "Training Description", "Type", "Duration", 
            "In Charge", "Requirement Group", "Link", "Created By", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.refresh_data()

    def refresh_data(self):
        self.table.setRowCount(0)
        data = self.db.get_all_training_items() 
        
        if not data:
            return

        for r_idx, row in enumerate(data):
            self.table.insertRow(r_idx)
           
            self.table.setItem(r_idx, 0, QTableWidgetItem(str(row[1]))) # Name
            self.table.setItem(r_idx, 1, QTableWidgetItem(str(row[2]))) # Description
            self.table.setItem(r_idx, 2, QTableWidgetItem(str(row[3]))) # Type
            self.table.setItem(r_idx, 3, QTableWidgetItem(str(row[4]))) # Duration
            self.table.setItem(r_idx, 4, QTableWidgetItem(str(row[5]))) # Provider/In Charge
            self.table.setItem(r_idx, 5, QTableWidgetItem(str(row[6]))) # Group Requirement
            self.table.setItem(r_idx, 6, QTableWidgetItem(str(row[7]))) # Resources/Link
            self.table.setItem(r_idx, 7, QTableWidgetItem(str(row[8]))) # Created By
            self.table.setItem(r_idx, 8, QTableWidgetItem(str(row[0]))) # Training ID
            self.table.setItem(r_idx, 9 , QTableWidgetItem(str(row[9]))) # Contact Name
            self.table.setItem(r_idx, 10 , QTableWidgetItem(str(row[10]))) # Contact Email
            
            # Action Column (Edit/Delete)
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            self.table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self.show_context_menu)
            self.table.setCellWidget(r_idx, 8, btn_container)

    def open_employee_training_dialog(self):
        # Create a dialog wrapper
        dialog = QDialog(self)
        dialog.setWindowTitle("Assign Employee Trainings")
        dialog.setMinimumSize(900, 600) # Give it some space for table data
        
        # Create a layout for the dialog
        dialog_layout = QVBoxLayout(dialog)

        assignment_widget = AdminTrainingAssignment(
            db=self.db, 
            current_user=self.current_user, 
            back_callback=dialog.accept 
        )
        
        dialog_layout.addWidget(assignment_widget)
        
        # Execute the dialog
        dialog.exec_()

    def open_training_dialog(self, row_data=None):
        
        dialog = TrainingDialog(self, row_data)
        if dialog.exec_():
            new_data = dialog.get_data()

            if row_data is not None:
                success = self.db.update_training(
                    t_id=new_data['id'],
                    name=new_data['training_name'], # You can change to new_values['training_name'] if you want to allow editing the name
                    desc=new_data['training_description'], # You can change to new_values['training_description'] if you want to allow editing the description
                    t_type=new_data['training_type'], # You can change to new_values['training_type'] if you want to allow editing the type
                    duration=new_data['training_duration'], # You can change to new_values['training_duration'] if you want to allow editing the duration
                    provider=new_data['training_provider'], # You can change to new_values['training_provider'] if you want to allow editing the provider
                    resources=new_data['training_resources'], # You can change to new_values['training_resources'] if you want to allow editing the resources
                    group=new_data['group_requirement'], # You can change to new_values['group_requirement'] if you want to allow editing the group requirement
                    updated_by=self.current_user, # You can change to self.current_user if you want to update the 'updated_by' field to the current user
                    contact_name=new_data['training_contact_name'], # You can change to new_values['training_contact_name'] if you want to allow editing the contact name
                    contact_email=new_data['training_contact_email'], # You can change to new_values['training_contact_email'] if you want to allow editing the contact email
            )
            else:
                success = self.db.add_training(
                    name=new_data['training_name'], # You can change to new_values['training_name'] if you want to allow editing the name
                    desc=new_data['training_description'], # You can change to new_values['training_description'] if you want to allow editing the description
                    t_type=new_data['training_type'], # You can change to new_values['training_type'] if you want to allow editing the type
                    duration=new_data['training_duration'], # You can change to new_values['training_duration'] if you want to allow editing the duration
                    provider=new_data['training_provider'], # You can change to new_values['training_provider'] if you want to allow editing the provider
                    contact_name=new_data['training_contact_name'], # You can change to new_values['training_contact_name'] if you want to allow editing the contact name
                    contact_email=new_data['training_contact_email'], # You can change to new_values['training_contact_email'] if you want to allow editing the contact email
                    resources=new_data['training_resources'], # You can change to new_values['training_resources'] if you want to allow editing the resources
                    group=new_data['group_requirement'], # You can change to new_values['group_requirement'] if you want to allow editing the group requirement
                    created_by=self.current_user # Passed from constructor
                )

            if success:
                QMessageBox.information(self, "Success", "Training saved successfully!")
                self.refresh_data()

    def show_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        
        row = index.row()
        self.table.selectRow(row)

        if row < 0: return

        menu = QMenu(self.table)
        edit_action = menu.addAction("Edit Record")
        delete_action = menu.addAction("Delete Record")
        
        action = menu.exec_(self.table.viewport().mapToGlobal(pos))

        if action == edit_action:
            QTimer.singleShot(10, lambda: self.edit_record(row))
        elif action == delete_action:
            QTimer.singleShot(10, lambda: self.confirm_delete(row))

    def edit_record(self, row):
        def get_text(r, c):
            item = self.table.item(r, c)
            return item.text() if item else ""

        data = {
            'id': get_text(row, 8),
            'training_name': get_text(row, 0),
            'training_description': get_text(row, 1),
            'training_type': get_text(row, 2),
            'training_duration': get_text(row, 3),
            'training_provider': get_text(row, 4),
            'group_requirement': get_text(row, 5),
            'training_resources': get_text(row, 6),
            'training_contact_name': get_text(row, 9), 
            'training_contact_email': get_text(row, 10)
        }

        self.open_training_dialog(row_data=data)

    def confirm_delete(self, row):
        training_id = self.table.item(row, 8).text()
        name = self.table.item(row, 0).text()
        
        reply = QMessageBox.question(self, 'Confirm Delete', f"Delete {name}?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_master_data("Trainings", training_id):
                self.refresh_data()