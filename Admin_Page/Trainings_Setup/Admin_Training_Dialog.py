import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
                                QTableWidgetItem, QHeaderView, QMenu, QMessageBox)
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox, QPushButton

class TrainingDialog(QDialog):
    def __init__(self, parent=None, row_data=None):
        super().__init__(parent)
        self.row_data = row_data
        self.is_edit = row_data is not None
        self.setWindowTitle("Edit Training" if self.is_edit else "Create New Training")
        self.setMinimumWidth(450)
        self.init_ui()

    def init_ui(self):
        self.layout = QFormLayout(self)

        # Create Inputs
        self.name_input = QLineEdit(self.row_data.get('training_name', '') if self.is_edit else "")
        self.desc_input = QTextEdit(self.row_data.get('training_description', '') if self.is_edit else "")
        
        self.type_input = QComboBox()
        self.type_input.addItems(["Online", "Classroom", "Workshop", "External"])
        if self.is_edit:
            self.type_input.setCurrentText(self.row_data.get('training_type', 'Online'))

        self.duration_input = QLineEdit(self.row_data.get('training_duration', '') if self.is_edit else "")
        self.provider_input = QLineEdit(self.row_data.get('training_provider', '') if self.is_edit else "")
        self.contact_name_input = QLineEdit(self.row_data.get('training_contact_name', '') if self.is_edit else "")
        self.contact_email_input = QLineEdit(self.row_data.get('training_contact_email', '') if self.is_edit else "")
        self.resources_input = QLineEdit(self.row_data.get('training_resources', '') if self.is_edit else "")
        self.group_input = QLineEdit(self.row_data.get('group_requirement', '') if self.is_edit else "")

        # Add to Form
        self.layout.addRow("Training Name:", self.name_input)
        self.layout.addRow("Details:", self.desc_input)
        self.layout.addRow("Type:", self.type_input)
        self.layout.addRow("Duration:", self.duration_input)
        self.layout.addRow("Provider:", self.provider_input)
        self.layout.addRow("Contact Name:", self.contact_name_input)
        self.layout.addRow("Contact Email:", self.contact_email_input)
        self.layout.addRow("Link:", self.resources_input)
        self.layout.addRow("Required For:", self.group_input)

        # Buttons
        self.button_box = QHBoxLayout()
        self.save_btn = QPushButton("💾 Update" if self.is_edit else "💾 Save")
        self.save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 8px;")
        self.cancel_btn = QPushButton("Cancel")
        
        self.button_box.addWidget(self.save_btn)
        self.button_box.addWidget(self.cancel_btn)
        self.layout.addRow(self.button_box)

        # Signal Connections
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

    def validate_and_accept(self):
        if not self.name_input.text().strip() or not self.desc_input.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Name and Description are required!")
            return
        self.accept()

    def get_data(self):
        """Helper to return all field values as a dictionary"""
        return {
            "id": self.row_data.get('id') if self.is_edit else None,
            "training_name": self.name_input.text(),
            "training_description": self.desc_input.toPlainText(),
            "training_type": self.type_input.currentText(),
            "training_duration": self.duration_input.text(),
            "training_provider": self.provider_input.text(),
            "training_contact_name": self.contact_name_input.text(),
            "training_contact_email": self.contact_email_input.text(),
            "training_resources": self.resources_input.text(),
            "group_requirement": self.group_input.text()
        }