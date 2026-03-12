from PyQt5.QtWidgets import (QDialog,QWidget, QVBoxLayout, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QComboBox, QHBoxLayout, 
                             QPushButton, QMessageBox, QLabel, QHeaderView, QInputDialog, QMenu, QFrame, QFormLayout, QLineEdit)
from PyQt5.QtCore import Qt
from Admin_Page.Master_Tables_Setup.Admin_MasterTable_New_Record import RecordEntryScreen
from Admin_Page.Setup_Alerts.Admin_Upsert_Alert import AlertEntryDialog
from Admin_Page.Job_Requirements.Admin_JobReq_Items import RequirementItemsEditor

class AlertItemsManager(QDialog):
    def __init__(self, db, current_user=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_user = current_user

        screen = self.screen().availableGeometry()
        self.resize(int(screen.width() * 0.5), int(screen.height() * 0.5))
        self.setWindowTitle("Alert Items Management")

        # self.resize(1200, 800)
        # self.setMinimumSize(800, 600)
        # self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>Alert Items Manager</h2>"))

        back_btn = QPushButton("Close")
        back_btn.clicked.connect(self.reject)

        header.addStretch()
        header.addWidget(back_btn)
        layout.addLayout(header)

        # Actions
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Create New Alerts")
        self.add_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 5px 15px;")
        self.add_btn.clicked.connect(self.add_record)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Alert Name", "Date Created", "Created By", "Updated By", "Date Updated",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        data = self.db.get_all_alert_setup_items() 
        
        if not data:
            return

        for r_idx, row in enumerate(data):
            self.table.insertRow(r_idx)
            
            # Explicit mapping based on your Alert_Dashboard_Items table structure:
            # row[0]: ID, row[1]: Alert_Name, row[2]: Alert_Code, 
            # row[3]: Alert_Type, row[4]: Alert_Description, row[5]: Alert_Status,
            # row[6]: Alert_Trigger_Date, row[7]: Alert_Acknowledged_By, row[8]: Alert_Acknowledged_Date
            
            self.table.setItem(r_idx, 0, QTableWidgetItem(str(row[0]))) # ID
            self.table.setItem(r_idx, 1, QTableWidgetItem(str(row[1]))) # Alert Name
            self.table.setItem(r_idx, 2, QTableWidgetItem(str(row[2]))) # Date Created
            self.table.setItem(r_idx, 3, QTableWidgetItem(str(row[3]))) # Created By
            self.table.setItem(r_idx, 4, QTableWidgetItem(str(row[4] or ""))) # Updated By
            self.table.setItem(r_idx, 5, QTableWidgetItem(str(row[5] or ""))) # Date Updated

    def add_record(self):
        dialog = AlertEntryDialog(self.db, self.current_user, self, title="Add New Alert")
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()
            
            # data = dialog.get_data()
            # if not data['name']:
            #     QMessageBox.warning(self, "Missing Info", "Please provide a name and select a job.")
            #     return

            # if self.db.add_alert_item(data['name'], self.current_user):
            #     self.load_data()
            #     QMessageBox.information(self, "Success", "Alert saved successfully.")

    def show_context_menu(self, pos):
        row = self.table.currentRow()
        if row < 0: return

        menu = QMenu()
        # setup_items_action = menu.addAction("Setup Items") # New Option
        # menu.addSeparator()
        edit_action = menu.addAction("Edit Record")
        delete_action = menu.addAction("Delete Record")
        
        action = menu.exec_(self.table.viewport().mapToGlobal(pos))
        
        # if action == setup_items_action:
        #     self.open_setup_items(row)
        if action == edit_action:
            self.edit_record(row)
        elif action == delete_action:
            self.confirm_delete(row)


    def edit_record(self, row):
        # 1. Get the ID from the selected row
        row_id = self.table.item(row, 0).text()
        
        # 2. Fetch the full record from the DB using the ID
        full_data = self.db.get_alert_by_id(row_id) 
        
        if not full_data:
            QMessageBox.warning(self, "Error", "Could not retrieve alert data.")
            return
        # 3. Open the SAME dialog, but pass the data and a different title
        dialog = AlertEntryDialog(self.db, self.current_user, self, title="Edit Alert", data=full_data)
        
        if dialog.exec_() == QDialog.Accepted:
            # updated_data = dialog.get_data()
            
            # 4. Call an UPDATE method in your DB class instead of add
            # if self.db.update_alert_item(row_id, updated_data):
            self.load_data()
            QMessageBox.information(self, "Success", "Alert updated successfully!")

    # def edit_record(self, row):
    #     # breakpoint()
    #     row_id = self.table.item(row, 0).text()
    #     # name = self.table.item(row, 1).text()
    #     # job_id = int(self.table.item(row, 2).text())

    #     # Open the integrated Master-Detail editor
    #     dialog = EditAlertFullDialog(self.db, row_id, self)
        
    #     if dialog.exec_() == QDialog.Accepted:
    #         header, items = dialog.get_all_data()
            
    #         # Save both header and items in one transaction
    #         if self.db.update_alert_full(req_id, header['name'], header['job_id'], self.current_user, items):
    #             self.load_data()
    #             QMessageBox.information(self, "Success", "All changes have been saved.")

    def confirm_delete(self, row):
        row_id = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(self, 'Confirm Delete', f"Delete {name}?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_alert_item(row_id):
                self.load_data()

    # def open_setup_items(self, row):
    #     req_id = self.table.item(row, 0).text()
    #     group_name = self.table.item(row, 1).text()
    #     # Open the new screen
    #     self.item_editor = RequirementItemsEditor(self.db, req_id, group_name)
    #     self.item_editor.exec_()

class EditAlertFullDialog(QDialog):
    def __init__(self, db, req_id, name, job_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.req_id = req_id
        self.setWindowTitle(f"Edit Requirement: {name}")
        self.resize(1000, 700)
        self.init_ui(name, job_id)

    def init_ui(self, name, job_id):
        layout = QVBoxLayout(self)

        # --- HEADER SECTION (Requirements_Setup) ---
        header_frame = QFrame()
        header_frame.setStyleSheet("background: #f1f2f6; border-radius: 8px; border: 1px solid #dcdde1;")
        form = QFormLayout(header_frame)
        
        self.name_input = QLineEdit(name)
        self.job_combo = QComboBox()
        # Populate Job Combo (Assuming get_master_data logic)
        jobs = self.db.get_master_data("Jobs")
        for j_id, title, desc, *args in jobs:
            self.job_combo.addItem(f"{title} ({desc})", j_id)
        self.job_combo.setCurrentIndex(self.job_combo.findData(job_id))

        form.addRow("Group Name:", self.name_input)
        form.addRow("Linked Job:", self.job_combo)
        layout.addWidget(header_frame)

        # --- ITEMS SECTION (Requirements_Setup_Items) ---
        layout.addWidget(QLabel("<b>Associated Requirement Items:</b>"))
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Line ID", "Name", "Code", "Type", "Description"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.items_table)

        item_btn_layout = QHBoxLayout()

        # Add Line Button for convenience
        add_line_btn = QPushButton("+ Add New Row")
        add_line_btn.setFixedWidth(120)
        add_line_btn.clicked.connect(self.add_blank_row)
        layout.addWidget(add_line_btn)


        duplicate_btn = QPushButton("📋 Duplicate Existing")
        duplicate_btn.setFixedWidth(150)
        duplicate_btn.setStyleSheet("""
            QPushButton { 
                background-color: #f39c12; 
                color: white; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        duplicate_btn.clicked.connect(self.open_duplicate_search)
        
        item_btn_layout.addWidget(add_line_btn)
        item_btn_layout.addWidget(duplicate_btn)
        item_btn_layout.addStretch() # Pushes buttons to the left
        layout.addLayout(item_btn_layout)

        # --- FOOTER ---
        btns = QHBoxLayout()
        self.save_btn = QPushButton("Save All Changes")
        self.save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 10px 20px;")
        self.save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(cancel_btn)
        btns.addWidget(self.save_btn)
        layout.addLayout(btns)

        self.load_items_to_table()

    def open_duplicate_search(self):
        # Local import to prevent circular dependency
        from Admin_Page.Job_Requirements.Admin_DuplicateJobReq_Items_Dialog import DuplicateSearchDialog
        
        search_dlg = DuplicateSearchDialog(self.db, self)
        if search_dlg.exec_() == QDialog.Accepted:
            data = search_dlg.selected_data
            if data:
                # Add to UI table so user can see/edit it before saving
                row_pos = self.items_table.rowCount()
                self.items_table.insertRow(row_pos)
                
                self.items_table.setItem(row_pos, 0, QTableWidgetItem(str(row_pos + 1)))
                self.items_table.setItem(row_pos, 1, QTableWidgetItem(str(data.get('name', ''))))
                self.items_table.setItem(row_pos, 2, QTableWidgetItem(str(data.get('code', ''))))
                self.items_table.setItem(row_pos, 3, QTableWidgetItem(str(data.get('type', ''))))
                self.items_table.setItem(row_pos, 4, QTableWidgetItem(str(data.get('desc', ''))))

    def load_items_to_table(self):
        items = self.db.get_items_by_requirement(self.req_id)
        self.items_table.setRowCount(0)
        for r_idx, row in enumerate(items):
            self.add_blank_row()
            # Mapping database columns to table (Skipping Req_id index 0)
            for c_idx in range(1, 6):
                self.items_table.setItem(r_idx, c_idx-1, QTableWidgetItem(str(row[c_idx])))

    def add_blank_row(self):
        row_pos = self.items_table.rowCount()
        self.items_table.insertRow(row_pos)
        next_line_id = row_pos + 1
        self.items_table.setItem(row_pos, 0, QTableWidgetItem(str(next_line_id)))

    def get_all_data(self):
        # Extract Header
        header_data = {
            "name": self.name_input.text(),
            "job_id": self.job_combo.currentData()
        }
        # Extract Items Table
        items_list = []
        for r in range(self.items_table.rowCount()):
            line_data = []
            for c in range(5):
                item = self.items_table.item(r, c)
                line_data.append(item.text() if item else "")
            if line_data[1]: # Only add if Name is not empty
                items_list.append(line_data)
        
        return header_data, items_list