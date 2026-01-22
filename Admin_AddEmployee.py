from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QWidget, QFormLayout, 
                             QTabWidget, QFrame, QScrollArea, QComboBox, QGridLayout, QDateEdit)
from PyQt5.QtCore import Qt, QDate

class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New Employee")
        self.resize(600, 700)
        
        # Professional Styling consistent with the Profile View
        self.setStyleSheet("""
            QDialog { background-color: #f8f9fa; }
            QLineEdit { 
                padding: 10px; 
                border: 1px solid #dee2e6; 
                border-radius: 5px; 
                background: white;
                selection-background-color: #3498db;
            }
            QLineEdit:focus { border: 1px solid #3498db; }
            QTabWidget::pane { border: 1px solid #dee2e6; background: white; border-radius: 5px; }
            QTabBar::tab { background: #e9ecef; padding: 12px 25px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: white; border-bottom: 2px solid #3498db; font-weight: bold; }
        """)
        
        self.inputs = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # --- HEADER ---
        header_lbl = QLabel("Create Employee Profile")
        header_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(header_lbl)

        # --- TABBED FORM ---
        self.tabs = QTabWidget()
        
        # Tab 1: Identity & Contact
        self.tabs.addTab(self.create_input_tab([
            ("Username", "Username", "Required (Unique)"),
            ("Display_Name", "Display Name", ""),
            ("First_Name", "First Name", ""),
            ("Last_Name", "Last Name", ""),
            ("Email", "Email Address", "Required"),
            ("Nick_Name", "Nickname", ""),
            ("Cellphone", "Cellphone", ""),
            ("Telephone", "Telephone", ""),
            ("Address", "Home Address", "")
        ]), "Personal Info")

        # Tab 2: Employment Details
        self.tabs.addTab(self.create_input_tab([
            ("Supervisor_ID", "Supervisor ID", ""),
            ("Dept_ID", "Department ID", ""),
            ("Job_title_Id", "Job ID", ""),
            ("Employement_Type", "Employment Type", "e.g. Full-time, Contract"),
            ("Date_Hired", "Date Hired", "YYYY-MM-DD"),
            ("Employeement_Status", "Employment Status", "e.g. Active, Probation")
        ]), "Job Details")

        # Tab 3: Additional Data
        self.tabs.addTab(self.create_input_tab([
            ("Age", "Age", ""),
            ("Gender", "Gender", ""),
            ("Birthday", "Birthday", "YYYY-MM-DD"),
            ("Created_By", "Admin Name", "")
        ]), "Additional")

        main_layout.addWidget(self.tabs)

        # --- FOOTER BUTTONS ---
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 15, 0, 0)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.setStyleSheet("background-color: white; border: 1px solid #dcdde1; border-radius: 5px;")
        cancel_btn.clicked.connect(self.reject)

        self.submit_btn = QPushButton("Save Employee")
        self.submit_btn.setFixedSize(160, 40)
        self.submit_btn.setStyleSheet("""
            QPushButton { background-color: #2ecc71; color: white; font-weight: bold; border-radius: 5px; }
            QPushButton:hover { background-color: #27ae60; }
        """)
        self.submit_btn.clicked.connect(self.accept)

        footer_layout.addStretch()
        footer_layout.addWidget(cancel_btn)
        footer_layout.addWidget(self.submit_btn)
        main_layout.addLayout(footer_layout)

    def create_input_tab(self, field_list):
        container = QWidget()
        layout = QGridLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.setColumnStretch(1, 1)

        # Professional style for both LineEdits and ComboBoxes
        widget_style = """
            QLineEdit, QComboBox, QDateEdit {
                padding: 8px 12px;
                border: 1px solid #dcdde1;
                border-radius: 6px;
                background-color: #ffffff;
                color: #2f3640;
                font-size: 14px;
            }
            QLineEdit:hover, QComboBox:hover {
                border: 1px solid #3498db;
                background-color: #f5faff;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """

        for i, (key, label_text, hint) in enumerate(field_list):
            lbl = QLabel(label_text)
            lbl.setMinimumWidth(140)
            lbl.setStyleSheet("font-weight: bold; color: #34495e; font-size: 13px;")
            layout.addWidget(lbl, i, 0)

            # Logic to create a Dropdown for Employment Type
            if key == "Employement_Type":
                input_field = QComboBox()
                input_field.addItems(["Salary", "Hourly", "Contractual", "Seasonal", "Student"])
                input_field.setStyleSheet(widget_style)
                input_field.setFixedHeight(40)
                self.inputs[key] = input_field
            elif key == "Employeement_Status":
                input_field = QComboBox()
                input_field.addItems(["Hired", "Initial Interview", "Job Offer Sent", "For Review", "Hiring Team Interview", "Offer Declined", "Active", "Probation", "Separated"])
                input_field.setStyleSheet(widget_style)
                input_field.setFixedHeight(40)
                self.inputs[key] = input_field
            elif key == "Gender":
                input_field = QComboBox()
                input_field.addItems(["Male", "Female", "Non-Binary", "Prefer not to say"])
                input_field.setStyleSheet(widget_style)
                input_field.setFixedHeight(40)
                self.inputs[key] = input_field
            elif key == "Birthday" or key == "Date_Hired":
                input_field = QDateEdit()
                input_field.setCalendarPopup(True) # This enables the clickable calendar
                input_field.setDisplayFormat("yyyy-MM-dd") # Standard database format
                input_field.setDate(QDate.currentDate()) # Default to today
            else:
                input_field = QLineEdit()
                input_field.setPlaceholderText(hint)
                input_field.setStyleSheet(widget_style)
                input_field.setFixedHeight(40)
                self.inputs[key] = input_field
            
            layout.addWidget(input_field, i, 1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        scroll.setStyleSheet("border: none; background: white;")
        return scroll

    def get_data(self):
        user_input = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QComboBox):
                user_input[key] = widget.currentText()
            elif isinstance(widget, QDateEdit):
                # Formats the date as a string for SQLite
                user_input[key] = widget.date().toString("yyyy-MM-dd")
            else:
                user_input[key] = widget.text()

        full_employee_data = {
            "Username": "", "First_Name": "", "Last_Name": "", 
            "Display_Name": "", "Nick_name": "", "Age": "", "Gender": "", 
            "Email": "", "Address": "", "Telephone": "", "Cellphone": "",
            "Supervisor_ID": "", "Employeement_Status": None, "Hired": None, 
            "Employement_Type": "", "Date_Hired": "", "Birthday": "", 
            "Date_Created": "", "Date_Updated": "", "Created_By": "", "Updated_By": "",
            "Dept_ID": "", "Job_title_Id": ""
        }
        full_employee_data.update(user_input)
        return full_employee_data