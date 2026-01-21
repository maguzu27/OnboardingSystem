from PyQt5.QtWidgets import QDialog, QGridLayout, QLineEdit, QPushButton, QVBoxLayout, QLabel, QScrollArea, QWidget

class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Employee Record")
        self.setMinimumSize(700, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Use a scroll area because 24 fields is a lot for one screen
        scroll = QScrollArea()
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        
        # List of all 24 columns (excluding employee_id as it is autoincrement)
        self.column_names = [
            "Username", "First_Name", "Last_Name", "Display_Name", "Nick_Name",
            "Age", "Gender", "Email", "Address", "Telephone", "Cellphone",
            "Supervisor_id", "Employeement_Status", "Hired", "Employement_Type",
            "Date_Hired", "Birthday", "Date_Created", "Date_Updated", 
            "Created_By", "Updated_By", "Dept_ID", "Job_title_Id"
        ]
        
        self.inputs = {}
        
        # Create 2 columns of inputs
        for i, col in enumerate(self.column_names):
            row = i // 2
            column = (i % 2) * 2
            
            label = QLabel(col.replace("_", " ") + ":")
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Enter {col.replace('_', ' ')}")
            
            grid.addWidget(label, row, column)
            grid.addWidget(line_edit, row, column + 1)
            self.inputs[col] = line_edit

        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        # Style the Add Button to match Login Button
        self.add_btn = QPushButton("Confirm Add Employee")
        self.add_btn.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; color: white; font-weight: bold; 
                height: 40px; border-radius: 5px; margin-top: 10px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.add_btn.clicked.connect(self.accept)
        main_layout.addWidget(self.add_btn)

    def get_data(self):
        # Return a dictionary of all the entered values
        return {col: widget.text() for col, widget in self.inputs.items()}