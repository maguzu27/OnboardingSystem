from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QTextEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt


class RecordEntryScreen(QDialog):
    def __init__(self, db, table_type, admin_name, on_success):
        super().__init__()
        self.db = db
        self.table_type = table_type
        self.admin_name = admin_name
        self.on_success = on_success
        self.setWindowTitle(f"Add New {table_type[:-1]}")
        self.setFixedWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.desc_input.setFixedHeight(100)
        
        if self.table_type == "Jobs":
            form.addRow("Job Title:", self.name_input)
            form.addRow("Description:", self.desc_input)
        else:
            form.addRow("Dept Name:", self.name_input)
            form.addRow("Description:", self.desc_input)
            self.addr_input = QLineEdit()
            form.addRow("Address:", self.addr_input)

        layout.addLayout(form)

        buttons = QHBoxLayout()
        save_btn = QPushButton("Save Record")
        save_btn.setStyleSheet("background-color: #3498db; color: white;")
        save_btn.clicked.connect(self.save_data)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def save_data(self):
        name = self.name_input.text().strip()
        desc = self.desc_input.toPlainText().strip()

        if not name or not desc:
            QMessageBox.warning(self, "Error", "Title/Name and Description are required.")
            return

        if self.table_type == "Jobs":
            data = {'title': name, 'desc': desc, 'admin': self.admin_name}
        else:
            addr = self.addr_input.text().strip()
            data = {'name': name, 'desc': desc, 'address': addr, 'admin': self.admin_name}

        if self.db.upsert_master_data(self.table_type, None, data):
            QMessageBox.information(self, "Success", "Record saved successfully!")
            self.on_success()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Could not save record. Check for duplicate names.")