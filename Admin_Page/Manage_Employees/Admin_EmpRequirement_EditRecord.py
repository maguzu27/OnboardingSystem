from PyQt5.QtWidgets import (QDialog, QFormLayout, QComboBox, QDateEdit, 
                             QDialogButtonBox, QLineEdit, QPushButton, QLabel)
from PyQt5.QtCore import QDate
import os

class EditRequirementDialog(QDialog):
    def __init__(self, current_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Requirement Record")
        self.setMinimumWidth(400)
        self.new_file_path = None # To store path if user chooses to replace file
        
        layout = QFormLayout(self)

        # 1. Requirement Item (Text)
        self.item_name_edit = QLineEdit()
        self.item_name_edit.setText(current_data.get('item_name', ""))
        layout.addRow("Requirement Item:", self.item_name_edit)

        # 2. Requirement Type (Text or Dropdown)
        self.type_edit = QLineEdit()
        self.type_edit.setText(current_data.get('type', ""))
        layout.addRow("Type:", self.type_edit)

        # 3. Status Dropdown
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "Received", "Completed", "Rejected", "Expired"])
        self.status_combo.setCurrentText(current_data['status'])
        layout.addRow("Status:", self.status_combo)

        # 4. Due Date Picker
        self.due_date_edit = QDateEdit(calendarPopup=True)
        self.due_date_edit.setDate(QDate.fromString(current_data['due_date'], "yyyy-MM-dd") 
                                   if current_data['due_date'] not in ['None', None] else QDate.currentDate())
        layout.addRow("Due Date:", self.due_date_edit)

        # 5. Completion Date Picker
        self.comp_date_edit = QDateEdit(calendarPopup=True)
        if current_data['comp_date'] and current_data['comp_date'] not in ['None', None]:
            self.comp_date_edit.setDate(QDate.fromString(current_data['comp_date'], "yyyy-MM-dd"))
        else:
            self.comp_date_edit.setDate(QDate.currentDate())
        layout.addRow("Completion Date:", self.comp_date_edit)

        # 6. Replace File Option
        self.file_label = QLabel("Current File: " + os.path.basename(current_data.get('file_path', 'None')))
        self.replace_btn = QPushButton("Replace Attachment 📎")
        self.replace_btn.clicked.connect(self.browse_new_file)
        layout.addRow(self.file_label)
        layout.addRow(self.replace_btn)

        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def browse_new_file(self):
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Select New File", "", "All Files (*)")
        if path:
            self.new_file_path = path
            self.file_label.setText(f"New File Selected: {os.path.basename(path)}")
            self.file_label.setStyleSheet("color: blue; font-weight: bold;")

    def get_data(self):
        return {
            "item_name": self.item_name_edit.text(),
            "type": self.type_edit.text(),
            "status": self.status_combo.currentText(),
            "due_date": self.due_date_edit.date().toString("yyyy-MM-dd"),
            "comp_date": self.comp_date_edit.date().toString("yyyy-MM-dd"),
            "new_file_path": self.new_file_path
        }