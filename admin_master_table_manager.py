from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QComboBox, QHBoxLayout, 
                             QPushButton, QMessageBox, QLabel, QHeaderView)
from PyQt5.QtCore import Qt
from Admin_MasterTable_New_Record import RecordEntryScreen

class MasterTableManager(QWidget):
    def __init__(self, db, admin_name, back_callback):
        super().__init__()
        self.db = db
        self.admin_name = admin_name
        self.back_callback = back_callback
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # --- HEADER ---
        header = QHBoxLayout()
        title = QLabel("System Master Data Management")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setFixedWidth(150)
        back_btn.clicked.connect(self.back_callback)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(back_btn)
        self.layout.addLayout(header)

        # --- TABS ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { background: #e9ecef; padding: 10px 20px; border-top-left-radius: 4px; }
            QTabBar::tab:selected { background: white; border-bottom: 2px solid #3498db; font-weight: bold; }
        """)
        
        self.tabs.addTab(self.create_table_tab("Jobs"), "Job Titles")
        self.tabs.addTab(self.create_table_tab("Departments"), "Departments")
        self.layout.addWidget(self.tabs)

    def create_table_tab(self, table_type):
        page = QWidget()
        layout = QVBoxLayout(page)

        # Action Bar
        action_bar = QHBoxLayout()
        
        # New "Add" Button
        add_btn = QPushButton(f"Add New {table_type[:-1]}") # e.g., Add New Job
        add_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 5px 15px;")
        add_btn.clicked.connect(lambda: self.open_add_screen(table_type))
        
        actions = QComboBox()
        actions.addItems(["--- Actions ---", "Enable Edit Mode", "Save Changes", "Delete Selected"])
        actions.setFixedWidth(180)
        actions.currentIndexChanged.connect(lambda idx, t=table_type: self.handle_action(idx, t))
        
        action_bar.addWidget(add_btn) # Added button to the left
        action_bar.addStretch()
        action_bar.addWidget(actions)
        layout.addLayout(action_bar)

        # Table Setup
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        if table_type == "Jobs":
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["ID", "Job Title", "Description"])
        else:
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["ID", "Dept Name", "Description", "Address"])

        layout.addWidget(table)
        self.load_table_data(table, table_type)
        
        setattr(self, f"{table_type.lower()}_table", table)
        return page

    def open_add_screen(self, table_type):
        """Opens the dedicated popup window for a new record."""
        self.entry_window = RecordEntryScreen(self.db, table_type, self.admin_name, 
                                              on_success=lambda: self.refresh_after_add(table_type))
        self.entry_window.show()

    def refresh_after_add(self, table_type):
        """Callback to refresh table once the popup saves."""
        table = getattr(self, f"{table_type.lower()}_table")
        self.load_table_data(table, table_type)

    # def create_table_tab(self, table_type):
    #     page = QWidget()
    #     layout = QVBoxLayout(page)

    #     # Action Bar
    #     action_bar = QHBoxLayout()
    #     actions = QComboBox()
    #     actions.addItems(["--- Actions ---", "Enable Edit Mode", "Add New Record","Save Changes", "Delete Selected"])
    #     actions.setFixedWidth(200)
    #     actions.currentIndexChanged.connect(lambda idx, t=table_type: self.handle_action(idx, t))
        
    #     action_bar.addStretch()
    #     action_bar.addWidget(actions)
    #     layout.addLayout(action_bar)

    #     # Table Setup
    #     table = QTableWidget()
    #     table.setAlternatingRowColors(True)
    #     table.setSelectionBehavior(QTableWidget.SelectRows)
    #     table.setEditTriggers(QTableWidget.NoEditTriggers)
    #     table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    #     # Click empty row feature
    #     # table.itemClicked.connect(self.check_for_new_entry)

    #     if table_type == "Jobs":
    #         table.setColumnCount(3)
    #         table.setHorizontalHeaderLabels(["ID", "Job Title", "Description"])
    #     else:
    #         table.setColumnCount(4)
    #         table.setHorizontalHeaderLabels(["ID", "Dept Name", "Description", "Address"])

    #     layout.addWidget(table)
    #     self.load_table_data(table, table_type)
        
    #     # Store dynamic reference (e.g., self.jobs_table)
    #     setattr(self, f"{table_type.lower()}_table", table)
    #     return page

    def load_table_data(self, table, table_type):
        table.setRowCount(0)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Fetch data from your DatabaseManager
        data = self.db.get_master_data(table_type) 
        
        for r_idx, r_data in enumerate(data):
            table.insertRow(r_idx)
            for c_idx, val in enumerate(r_data):
                table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
        

    def check_for_new_entry(self, item):
        """Automatically enables editing when the placeholder row is clicked"""
        table = item.tableWidget()
        if item.row() == table.rowCount() - 1:
            table.setEditTriggers(QTableWidget.AllEditTriggers)
            if item.text() == "(Click here to add new record)":
                item.setText("")
                item.setForeground(Qt.black)
            table.editItem(item)

    # def handle_action(self, index, table_type):
    #     table = getattr(self, f"{table_type.lower()}_table")
        
    #     if index == 1: # Enable Edit
    #         table.setEditTriggers(QTableWidget.AllEditTriggers)
    #         # Re-enable the flags for existing items
    #         for r in range(table.rowCount()):
    #             for c in range(1, table.columnCount()): # Skip ID column
    #                 item = table.item(r, c)
    #                 if item: item.setFlags(item.flags() | Qt.ItemIsEditable)
    #         QMessageBox.information(self, "Edit Mode", "Table is now editable. Click 'Save Changes' to commit.")

    #     elif index == 2: # "Add New Record"
    #         self.prepare_add_row(table)

    #     elif index == 3: # Save Changes
    #         self.save_logic(table, table_type)
            
    #     elif index == 4: # Delete
    #         self.delete_logic(table, table_type)


        # self.sender().setCurrentIndex(0) # Reset dropdown

    def handle_action(self, index, table_type):
        table = getattr(self, f"{table_type.lower()}_table")
        
        if index == 1: # Enable Edit
            table.setEditTriggers(QTableWidget.AllEditTriggers)
            # Unlock items
            for r in range(table.rowCount()):
                for c in range(1, table.columnCount()):
                    item = table.item(r, c)
                    if item: item.setFlags(item.flags() | Qt.ItemIsEditable)
            QMessageBox.information(self, "Edit Mode", "Table is now editable. Edit cells and click 'Save Changes'.")

        elif index == 2: # Save Changes
            self.save_logic(table, table_type)
            
        elif index == 3: # Delete
            self.delete_logic(table, table_type)

        self.sender().setCurrentIndex(0)


    def prepare_add_row(self, table):
        """Adds a blank row and focuses the user on it."""
        # Disable editing on existing rows first
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        new_row_idx = table.rowCount()
        table.insertRow(new_row_idx)
        
        # Initialize items as editable
        for col in range(table.columnCount()):
            item = QTableWidgetItem("")
            if col == 0: # ID column remains read-only
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setText("AUTO")
            else:
                item.setFlags(item.flags() | Qt.ItemIsEditable)
            table.setItem(new_row_idx, col, item)
            
        table.selectRow(new_row_idx)
        table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        
        # Focus on the first data column
        table.editItem(table.item(new_row_idx, 1))

    def save_logic(self, table, table_type):
        table.clearFocus() 
        rows = table.rowCount()
        
        rows = table.rowCount()
        for row in range(rows):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                val = item.text().strip() if item else ""
                row_data.append(val)

            # Skip truly empty rows
            if not row_data[1] or row_data[1] == "AUTO":
                continue

            # Determine if New (ID is "AUTO" or empty) or Update (ID is numeric)
            record_id = row_data[0] if row_data[0].isdigit() else None
            
            if table_type == "Jobs":
                data = {'title': row_data[1], 'desc': row_data[2], 'admin': self.admin_name}
            else:
                data = {'name': row_data[1], 'desc': row_data[2], 'address': row_data[3], 'admin': self.admin_name}

            # Send to DB
            self.db.upsert_master_data(table_type, record_id, data)

        QMessageBox.information(self, "Success", f"{table_type} data saved/updated.")
        self.load_table_data(table, table_type)

    def delete_logic(self, table, table_type):
        """Deletes the selected row from the database."""
        current_row = table.currentRow()
        if current_row < 0 or current_row == table.rowCount() - 1:
            QMessageBox.warning(self, "Selection Error", "Please select a valid record to delete.")
            return

        id_item = table.item(current_row, 0)
        if not id_item:
            return

        record_id = id_item.text()
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                     f"Are you sure you want to delete ID {record_id}?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            if self.db.delete_master_data(table_type, record_id):
                QMessageBox.information(self, "Deleted", "Record removed successfully.")
                self.load_table_data(table, table_type)