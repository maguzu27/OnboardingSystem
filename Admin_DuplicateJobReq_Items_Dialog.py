from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt

class DuplicateSearchDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.selected_data = None
        self.setWindowTitle("Search Item to Duplicate")
        self.resize(700, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Name or Code...")
        self.search_input.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Code", "Type", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.select_item)
        layout.addWidget(self.table)

        # Buttons
        btns = QHBoxLayout()
        select_btn = QPushButton("Select & Copy")
        select_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        select_btn.clicked.connect(self.select_item)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btns.addStretch()
        btns.addWidget(cancel_btn)
        btns.addWidget(select_btn)
        layout.addLayout(btns)

        self.load_data()

    def load_data(self):
        # Fetching unique items to avoid duplicating the exact same thing multiple times in list
        query = "SELECT DISTINCT Req_Name, Req_code, Req_Item_Type, Req_Description FROM Requirements_Setup_Items"
        self.db.cursor.execute(query)
        data = self.db.cursor.fetchall()
        
        self.table.setRowCount(0)
        for r_idx, row in enumerate(data):
            self.table.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))

    def filter_table(self):
        search_text = self.search_input.text().lower()
        for i in range(self.table.rowCount()):
            match = any(search_text in (self.table.item(i, j).text().lower() if self.table.item(i, j) else "") for j in range(self.table.columnCount()))
            self.table.setRowHidden(i, not match)

    def select_item(self):
        row = self.table.currentRow()
        if row >= 0:
            self.selected_data = {
                "name": self.table.item(row, 0).text(),
                "code": self.table.item(row, 1).text(),
                "type": self.table.item(row, 2).text(),
                "desc": self.table.item(row, 3).text()
            }
            self.accept()