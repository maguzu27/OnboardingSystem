from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QWidget, QFormLayout, 
                             QTabWidget, QFrame, QMessageBox, QComboBox, QLineEdit, QDateEdit)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QDate
import os
from database_manager import DatabaseManager

class EmployeeRecordDialog(QDialog):
    def __init__(self, employee_data, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.inputs = {}
        self.employee_id = employee_data[0]   # Employee ID at index 0
        self.username = employee_data[1]  # Username at index 1
        self.file_path = self.db.get_employee_attachment(self.username)
        
        self.setWindowTitle("Employee Management Profile")
        self.resize(600, 750)
        self.setStyleSheet("""
            QDialog { background-color: #f8f9fa; }
            QLabel { color: #2c3e50; font-size: 13px; }
            QTabWidget::pane { border: 1px solid #dee2e6; background: white; border-radius: 5px; }
            QTabBar::tab { background: #e9ecef; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: white; border-bottom: 2px solid #3498db; font-weight: bold; }
        """)
        
        self.init_ui(employee_data)
        self.set_edit_mode(False)

    def init_ui(self, data):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- NEW ACTION BAR ---
        action_bar = QHBoxLayout()
        self.action_dropdown = QComboBox() # <--- FIXED: Create the dropdown
        self.action_dropdown.addItems(["--- Actions ---", "Edit Record", "Delete Record"])
        self.action_dropdown.currentIndexChanged.connect(self.handle_action)
        action_bar.addStretch()
        action_bar.addWidget(self.action_dropdown)
        main_layout.addLayout(action_bar)

        # --- MODERN HEADER ---
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #dee2e6;")
        header_layout = QHBoxLayout(header)
        
        info_layout = QVBoxLayout()
        self.name_lbl = QLabel(f"{data[2]} {data[3]}") # First + Last Name
        self.name_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; border: none;")
        user_lbl = QLabel(f"@{data[1]} | ID: {data[0]}")
        user_lbl.setStyleSheet("color: #7f8c8d; border: none;")
        info_layout.addWidget(self.name_lbl)
        info_layout.addWidget(user_lbl)
        
        status_badge = QLabel(str(data[13]).upper()) # Status
        status_badge.setFixedSize(90, 30)
        status_badge.setAlignment(Qt.AlignCenter)
        color = "#27ae60" if "active" in str(data[13]).lower() else "#e67e22"
        status_badge.setStyleSheet(f"background-color: {color}; color: white; border-radius: 15px; font-weight: bold;")
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        header_layout.addWidget(status_badge)
        main_layout.addWidget(header)

        # --- CATEGORIZED TABS ---
        self.tabs = QTabWidget()
        
        # Tab 1: Personal Info
        personal_tab = self.create_form_tab([
            ("Nickname", data[5]), ("Age", data[6]), ("Gender", data[7]), 
            ("Birthday", data[17]), ("Email", data[8]), ("Cellphone", data[11]),
            ("Telephone", data[10]), ("Address", data[9])
        ])
        
        # Tab 2: Employment Details
        work_tab = self.create_form_tab([
            ("Department ID", data[22]), ("Job ID", data[23]), ("Type", data[15]),
            ("Date Hired", data[16]), ("Supervisor ID", data[12]), ("Hired Status", data[14])
        ])

        # Tab 3: System Logs
        logs_tab = self.create_form_tab([
            ("Created By", data[20]), ("Created Date", data[18]),
            ("Updated By", data[21]), ("Updated Date", data[19])
        ])

        self.tabs.addTab(personal_tab, "Personal")
        self.tabs.addTab(work_tab, "Employment")
        self.tabs.addTab(logs_tab, "Record Details")
        main_layout.addWidget(self.tabs)

        # --- BOTTOM SAVE BUTTON (Hidden by default) ---
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setFixedHeight(45)
        self.save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; border-radius: 5px;")
        self.save_btn.setVisible(False)
        self.save_btn.clicked.connect(self.save_edits)
        main_layout.addWidget(self.save_btn)

        # --- FOOTER / ACTIONS ---
        footer_layout = QHBoxLayout()
        
        has_file = bool(self.file_path and os.path.exists(self.file_path))
        self.view_file_btn = QPushButton(" View Document")
        self.view_file_btn.setFixedHeight(40)
        btn_style = "background-color: #3498db; color: white; font-weight: bold; border-radius: 5px; padding: 0 15px;"
        if not has_file:
            btn_style = "background-color: #bdc3c7; color: #ffffff; border-radius: 5px;"
            self.view_file_btn.setEnabled(False)
            self.view_file_btn.setText("No Attachment")

            
            
        self.view_file_btn.setStyleSheet(btn_style)
        self.view_file_btn.clicked.connect(self.open_file)

        close_btn = QPushButton("Dismiss")
        close_btn.setFixedHeight(40)
        close_btn.setFixedWidth(100)
        close_btn.setStyleSheet("background-color: #ffffff; border: 1px solid #dcdde1; border-radius: 5px;")
        close_btn.clicked.connect(self.accept)

        footer_layout.addWidget(self.view_file_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(close_btn)
        main_layout.addLayout(footer_layout)

    def create_form_tab(self, fields):
        widget = QWidget()
        layout = QFormLayout(widget)

        view_style = "border: none; background: transparent; color: #2c3e50; font-weight: bold;"
        # layout.setContentsMargins(20, 20, 20, 20)
        # layout.setSpacing(15)

        for key, value in fields:
            lbl = QLabel(f"{key}:")
            lbl.setStyleSheet("font-weight: bold; color: #7f8c8d;")
            
            # --- LOGIC FOR DIFFERENT INPUT TYPES ---
            if key == "Type":
                input_field = QComboBox()
                input_field.addItems(["Salary", "Hourly", "Contractual", "Seasonal", "Student"])
                input_field.setCurrentText(str(value))
                
            elif key == "Hired Status":
                input_field = QComboBox()
                input_field.addItems(["Hired", "Initial Interview", "Job Offer Sent", "For Review", 
                                      "Hiring Team Interview", "Offer Declined", "Active", 
                                      "Probation", "Separated"])
                input_field.setCurrentText(str(value))
                
            elif key == "Gender":
                input_field = QComboBox()
                input_field.addItems(["Male", "Female", "Non-Binary", "Prefer not to say"])
                input_field.setCurrentText(str(value))
                
            elif key in ["Birthday", "Date Hired"]:
                input_field = QDateEdit()
                input_field.setCalendarPopup(True)
                input_field.setDisplayFormat("yyyy-MM-dd")
                # Parse the date string from DB into QDate object
                if value and value != "N/A":
                    input_field.setDate(QDate.fromString(str(value), "yyyy-MM-dd"))
                else:
                    input_field.setDate(QDate.currentDate())
            
            else:
                # Default to QLineEdit for everything else (Nickname, Email, etc.)
                input_field = QLineEdit(str(value) if value and value != "N/A" else "")

            # --- COMMON SETTINGS ---
            if isinstance(input_field, QLineEdit):
                input_field.setReadOnly(True)  # QLineEdit supports ReadOnly
            else:
                input_field.setEnabled(False)  # QComboBox and QDateEdit use Enabled
                
            input_field.setStyleSheet(view_style)
            self.inputs[key] = input_field
            layout.addRow(lbl, input_field)

        # for key, value in fields:
        #     lbl = QLabel(f"{key}:")
        #     lbl.setStyleSheet("font-weight: bold; color: #7f8c8d;")

        #     # Use QLineEdit instead of QLabel so it can be toggled
        #     val_input = QLineEdit(str(value) if value else "")
        #     val_input.setReadOnly(True) # Start as Read Only
        #     val_input.setStyleSheet(view_style)

        #     # val = QLabel(str(value) if value else "N/A")
        #     # val.setStyleSheet("font-size: 14px; color: #2c3e50;")
            

        #     self.inputs[key] = val_input
        #     layout.addRow(lbl, val_input)
            
            # # Add a thin separator line
            # line = QFrame()
            # line.setFrameShape(QFrame.HLine)
            # line.setFrameShadow(QFrame.Sunken)
            # line.setStyleSheet("color: #f1f2f6;")
            # layout.addRow(line)
            
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        return scroll

    def open_file(self):
        if self.file_path:
            try:
                os.startfile(os.path.abspath(self.file_path))
            except Exception as e:
                print(f"Error: {e}")

    def set_edit_mode(self, enabled):
        """Toggles the UI appearance between Viewing and Editing for all widget types"""
        self.save_btn.setVisible(enabled)
        
        # 1. Broaden the Stylesheet to cover all input types
        edit_style = """
            QLineEdit, QComboBox, QDateEdit { 
                border: 2px solid #3498db; 
                background: #ffffff; 
                padding: 5px; 
                border-radius: 4px; 
                color: #2c3e50;
            }
        """
        view_style = """
            QLineEdit, QComboBox, QDateEdit { 
                border: none; 
                background: transparent; 
                color: #2c3e50; 
                font-weight: bold; 
            }
            /* Hide the arrow on dropdowns/datepickers when just viewing */
            QComboBox::drop-down, QDateEdit::drop-down { border: 0px; }
            QComboBox::down-arrow, QDateEdit::down-arrow { image: none; }
        """

        for widget in self.inputs.values():
            # 1. Handle locking logic based on widget class
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(not enabled)
            else:
                # QComboBox and QDateEdit use setEnabled
                widget.setEnabled(enabled)
            
            # 2. Apply the visual style
            widget.setStyleSheet(edit_style if enabled else view_style)

        # 3. Handle the Action Dropdown toggle
        if enabled:
            self.action_dropdown.setItemText(1, "Cancel Edit")
        else:
            self.action_dropdown.setItemText(1, "Edit Record")
            self.action_dropdown.blockSignals(True)
            self.action_dropdown.setCurrentIndex(0)
            self.action_dropdown.blockSignals(False)

    def save_edits(self):
        # Logic to collect data from self.inputs and call db.update_employee()
        updated_data = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QComboBox):
                updated_data[key] = widget.currentText()
            elif isinstance(widget, QDateEdit):
                updated_data[key] = widget.date().toString("yyyy-MM-dd")
            else:
                updated_data[key] = widget.text()

        success = self.db.update_employee(self.username, updated_data)


        if success:
            self.refresh_ui()
            self.set_edit_mode(False)
            QMessageBox.information(self, "Success", "Changes saved to database.")
        else:
            QMessageBox.warning(self, "Error", "Failed to save changes.")

        


    def handle_action(self, index):
            """Processes the selection from the action dropdown"""
            if index == 0: return

            if index == 1:  # "Edit Record" selected
                # Toggle the mode
                if self.action_dropdown.itemText(1) == "Cancel Edit":
                    self.set_edit_mode(False)
                else:
                    self.set_edit_mode(True)
            
            elif index == 2:  # "Delete Record" selected
                self.confirm_delete()


            self.action_dropdown.blockSignals(True)
            self.action_dropdown.setCurrentIndex(0)
            self.action_dropdown.blockSignals(False)

            # Reset the dropdown to "--- Actions ---" if not in edit mode
            if not self.save_btn.isVisible():
                self.action_dropdown.setCurrentIndex(0)

    def confirm_delete(self):
        """Handles the deletion logic with a confirmation prompt"""
        reply = QMessageBox.question(
            self, 'Confirm Delete', 
            f"Are you sure you want to delete {self.username}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Note: Ensure your DatabaseManager has a delete_employee method
            if self.db.delete_employee(self.employee_id): 
                QMessageBox.information(self, "Deleted", "Employee record removed.")
                self.accept() # Close the dialog
            else:
                QMessageBox.warning(self, "Error", "Could not delete record.")

    def refresh_ui(self):
        """Re-fetches data from the DB and updates the UI widgets"""
        # 1. Get the latest data for this user
        fresh_data = self.db.get_employee_by_username(self.username)
        
        if fresh_data:
            # 2. Update the Header Labels (Top Section)
            # Based on your data indexes: 2=First Name, 3=Last Name, 13=Status
            self.name_lbl.setText(f"{fresh_data[2]} {fresh_data[3]}")
            
            # 3. Update all input fields in the tabs
            # This uses the same mapping logic we used in create_form_tab
            mapping = {
                "Nickname": fresh_data[5], "Age": fresh_data[6], "Gender": fresh_data[7], 
                "Birthday": fresh_data[17], "Email": fresh_data[8], "Cellphone": fresh_data[11],
                "Telephone": fresh_data[10], "Address": fresh_data[9],
                "Type": fresh_data[15], "Date Hired": fresh_data[16], "Hired Status": fresh_data[14]
            }

            for key, val in mapping.items():
                if key in self.inputs:
                    widget = self.inputs[key]
                    val_str = str(val) if val else ""
                    
                    if isinstance(widget, QComboBox):
                        widget.setCurrentText(val_str)
                    elif isinstance(widget, QDateEdit):
                        widget.setDate(QDate.fromString(val_str, "yyyy-MM-dd"))
                    else:
                        widget.setText(val_str)