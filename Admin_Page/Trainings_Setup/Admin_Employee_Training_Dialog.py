import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
                                QTableWidgetItem, QHeaderView, QMenu, QMessageBox)
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox, QPushButton

class EmployeeTrainingDialog(QDialog):
    print("EmployeeTrainingDialog loaded")
    def __init__(self, parent=None, row_data=None):
        super().__init__(parent)
        self.row_data = row_data if row_data is not None else {}

        self.is_edit = row_data is not None
        # self.setWindowTitle("Edit Training" if self.is_edit else "Create New Training")
        self.setWindowTitle("Setup employee training")
        self.setMinimumWidth(450)
        self.init_ui()

    def init_ui(self):
        print(self.row_data)  # Debug statement to check the data being passed
        self.layout = QFormLayout(self)

        self.employee_id_input = QLineEdit(str(self.row_data.get('employee_id', '') if self.is_edit else ""))
        self.training_id_input = QLineEdit(str(self.row_data.get('training_id', '') if self.is_edit else ""))
        self.required_input = QComboBox()
        self.required_input.addItems(["Yes", "No"])
        self.required_input.setCurrentText(self.row_data.get('required', 'Yes') if self.is_edit else "Yes")
        self.date_input = QLineEdit(datetime.date.today().strftime("%Y-%m-%d"))
        self.date_input.setText(self.row_data.get('required_by_date', self.date_input.text()) if self.is_edit else self.date_input.text())

        self.layout.addRow("Employee ID:", self.employee_id_input)
        self.layout.addRow("Training ID:", self.training_id_input)
        self.layout.addRow("Required:", self.required_input)
        self.layout.addRow("Required By Date:", self.date_input)

        # Buttons
        self.save_btn = QPushButton("Assign")
        self.save_btn.clicked.connect(self.validate_and_accept) # This closes the dialog and returns True
        self.layout.addRow(self.save_btn)
        
    def validate_and_accept(self):
        if not self.employee_id_input.text().strip() or not self.training_id_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Employee ID and Training ID are required!")
            return
        self.accept()

    def get_data(self):
        """Helper to return all field values as a dictionary"""
        return {
            "employee_id": self.employee_id_input.text(),
            "training_id": self.training_id_input.text(),
            "required": self.required_input.currentText(),
            "required_by_date": self.date_input.text()
        }