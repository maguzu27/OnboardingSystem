
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QComboBox, QHBoxLayout, 
                             QPushButton, QMessageBox, QLabel, QHeaderView, QInputDialog, QMenu, QDialog)

from PyQt5.QtCore import Qt
from admin_JobReq_Item_Entry import AddRequirementItemDialog

class RequirementItemsEditor(QDialog):
    def __init__(self, db, req_id, group_name, parent=None):
        # Pass parent to super() to ensure proper window centering and modality
        super().__init__(parent) 
        self.db = db
        self.req_id = req_id
        self.setWindowTitle(f"Setup Items: {group_name}")
        self.resize(900, 600)
        
        # Set window modality explicitly (extra safety)
        self.setWindowModality(Qt.ApplicationModal)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # --- HEADER WITH BACK BUTTON ---
        header_layout = QHBoxLayout()
        title_lbl = QLabel(f"<h2>Requirement Items</h2>")
        
        back_btn = QPushButton("Back")
        back_btn.setFixedWidth(80)
        # self.reject() closes the dialog and returns 0 (Cancel)
        back_btn.clicked.connect(self.reject) 
        
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(back_btn)
        layout.addLayout(header_layout)

        # --- TABLE ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Line ID", "Requirement Name", "Code", "Type", "Description"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # --- ACTIONS ---
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add New Item Line")
        self.add_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.add_btn.clicked.connect(self.add_line)
        btn_layout.addWidget(self.add_btn)
        layout.addLayout(btn_layout)

        self.load_items()

    def load_items(self):
        self.table.setRowCount(0)
        items = self.db.get_items_by_requirement(self.req_id)
        for r_idx, row in enumerate(items):
            self.table.insertRow(r_idx)
            # row[0] is Req_id, row[1] is Req_line_id
            for c_idx in range(1, 6): 
                self.table.setItem(r_idx, c_idx-1, QTableWidgetItem(str(row[c_idx])))

    def add_line(self):
        # 1. Open the new professional dialog
        dialog = AddRequirementItemDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Validation: Ensure Name and Code aren't empty
            if not data['name'] or not data['code']:
                QMessageBox.warning(self, "Input Error", "Name and Code are required.")
                return

            # 2. Auto-calculate next Line ID based on current table rows
            next_line = self.table.rowCount() + 1
            
            # 3. Save to database
            success = self.db.add_requirement_item(
                self.req_id, 
                next_line, 
                data['name'], 
                data['code'], 
                data['type'], 
                data['desc']
            )
            
            if success:
                self.load_items()
            else:
                QMessageBox.critical(self, "Database Error", "Could not save the requirement item.")