from PyQt5.QtWidgets import (QMenu, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QPushButton, QLabel, QHeaderView, QTableWidgetItem, 
                             QComboBox, QLineEdit, QDialog, QFormLayout, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from Admin_Page.Trainings_Setup.Admin_Employee_Training_Dialog import EmployeeTrainingDialog


class AdminTrainingAssignment(QWidget):
    def __init__(self, db, current_user, back_callback):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.back_callback = back_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Selection Area
        selection_group = QHBoxLayout()
        
        self.training_selector = QComboBox()
        print("Loading trainings into selector...")  # Debug statement
        self.load_trainings()
        print("Trainings loaded into selector.")  # Debug statement
        self.training_selector.insertItem(0, "All Trainings", None)
        self.training_selector.setCurrentIndex(0)

        self.training_selector.currentIndexChanged.connect(self.refresh_data)
        
        self.target_selector = QComboBox()
        self.target_selector.addItems(["All Categories","Individual User", "By Department", "By Job Title"])
        self.target_selector.currentIndexChanged.connect(self.refresh_data)
        
        assign_btn = QPushButton("Assign Training")
        assign_btn.setStyleSheet("background-color: #3498db; color: white;")
        assign_btn.clicked.connect(lambda: self.handle_assignment(row_data=None))
        # assign_btn.clicked.connect(self.handle_assignment)

        selection_group.addWidget(QLabel("Select Training:"))
        selection_group.addWidget(self.training_selector)
        selection_group.addWidget(QLabel("Target:"))
        selection_group.addWidget(self.target_selector)
        selection_group.addWidget(assign_btn)
        
        layout.addLayout(selection_group)
        
        # Recent Assignments Table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Employee", "Training", "Training Description", "Assigned Date", "Status"])
        layout.addWidget(self.log_table)
        self.refresh_data()

    def load_trainings(self):
        """Fetch all trainings from the database and populate the combobox."""
        try:
            # Clear existing items first
            self.training_selector.clear()

            trainings = self.db.get_all_training_items()
            
            if not trainings:
                self.training_selector.addItem("No trainings found", None)
                return
            
            seen_trainings = set()

            for row in trainings:
                t_id = row[0]   # The Primary Key ID
                t_name = row[1] # The Training Name
                
              
                if t_id not in seen_trainings:
                    self.training_selector.addItem(f"Training ID: {t_id} -  {t_name}", t_id)
                    seen_trainings.add(t_id)
                
        except Exception as e:
            print(f"Error loading trainings: {e}")
            QMessageBox.critical(self, "Database Error", "Could not load training list.")

    def handle_assignment(self, row_data=None):
        
        dialog = EmployeeTrainingDialog(self, row_data)
        if dialog.exec_():
            new_data = dialog.get_data()
            print(f"Received data from dialog: {new_data}")  # Debug statement

            if row_data is not None:
                success = self.db.update_employee_training(
                    employee_id=new_data['employee_id'],
                    training_id=new_data['training_id'],
                    required=new_data['required'],
                    required_by_date=new_data['required_by_date'],
                    assigned_by=self.current_user
                )
            else:
                success = self.db.add_employee_training(
                    employee_id=new_data['employee_id'],
                    training_id=new_data['training_id'],
                    required=new_data['required'],
                    required_by_date=new_data['required_by_date'],
                    assigned_by=self.current_user
                )
           
            if success:
                QMessageBox.information(self, "Success", "Training saved successfully!")
                self.refresh_data()



    def refresh_data(self):
        self.log_table.setRowCount(0)  # Clear existing data

        selected_training_id = self.training_selector.currentData()
        selected_category = self.target_selector.currentText()
        print(f"Selected training ID for refresh: {selected_training_id}")  # Debug statement
        print(f"Selected category for refresh: {selected_category}")  # Debug statement

        if selected_training_id is None and selected_category == "All Categories":
            data = self.db.get_employee_training_items()
        else:
            data = self.db.get_employee_trainings_by_id(selected_training_id)

        if not data: return

        self.log_table.setContextMenuPolicy(Qt.CustomContextMenu)

        try:
            self.log_table.customContextMenuRequested.disconnect() # Clear old connections
        except:
            pass
        self.log_table.customContextMenuRequested.connect(self.show_context_menu)


        for r_idx, row in enumerate(data):
            self.log_table.insertRow(r_idx)
            for c_idx in range(min(len(row), self.log_table.columnCount())):
                self.log_table.setItem(r_idx, c_idx, QTableWidgetItem(str(row[c_idx])))

                if c_idx < self.log_table.columnCount():

                    self.log_table.setItem(r_idx, 0, QTableWidgetItem(str(row[0]))) # employee_id
                    self.log_table.setItem(r_idx, 1, QTableWidgetItem(str(row[10]))) # training_name
                    self.log_table.setItem(r_idx, 2, QTableWidgetItem(str(row[9]))) # training_description
                    self.log_table.setItem(r_idx, 3, QTableWidgetItem(str(row[3]))) # required_by_date
                    self.log_table.setItem(r_idx, 4, QTableWidgetItem(str(row[4]))) # completion_status

                    # Action Column (Edit/Delete)
                    btn_container = QWidget()
                    btn_layout = QHBoxLayout(btn_container)
                    btn_layout.setContentsMargins(2, 2, 2, 2)

                    self.log_table.setContextMenuPolicy(Qt.CustomContextMenu)
                    self.log_table.customContextMenuRequested.connect(self.show_context_menu)
                    self.log_table.setCellWidget(r_idx, 15, btn_container)

    def show_context_menu(self, pos):
        index = self.log_table.indexAt(pos)
        if not index.isValid():
            return
        
        row = index.row()
        self.log_table.selectRow(row)

        if row < 0: return

        menu = QMenu(self.log_table)
        edit_action = menu.addAction("Edit Record")
        delete_action = menu.addAction("Delete Record")
        
        action = menu.exec_(self.log_table.viewport().mapToGlobal(pos))

        if action == edit_action:
            QTimer.singleShot(10, lambda: self.edit_record(row))
        elif action == delete_action:
            QTimer.singleShot(10, lambda: self.confirm_delete(row))

    def edit_record(self, row):
        def get_text(r, c):
            item = self.log_table.item(r, c)
            return item.text() if item else ""

        data = {
            'employee_id': get_text(row, 0),
            'training_id': get_text(row, 1),
            'required': get_text(row, 2),
            'required_by_date': get_text(row, 3),
            'completion_status': get_text(row, 4),
            'completion_date': get_text(row, 5)
        }

        self.handle_assignment(row_data=data)

    def confirm_delete(self, row):
        training_id = self.log_table.item(row, 8).text()
        name = self.log_table.item(row, 0).text()
        
        reply = QMessageBox.question(self, 'Confirm Delete', f"Delete {name}?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_master_data("Trainings", training_id):
                self.refresh_data()