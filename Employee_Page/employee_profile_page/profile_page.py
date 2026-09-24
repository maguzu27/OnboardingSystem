from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, 
                             QPushButton, QGridLayout, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt

class ProfilePage(QWidget):
    def __init__(self, db, parent_dashboard):
        super().__init__()
        self.db = db
        self.dashboard = parent_dashboard # Reference to refresh headers/stack
        self.current_username = None
        self.employee_id = None
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        # --- VIEW MODE CARD ---
        self.view_widget = QWidget()
        view_layout = QVBoxLayout(self.view_widget)
        
        self.info_card = QFrame()
        self.info_card.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #dcdde1; padding: 20px;")
        card_inner_layout = QVBoxLayout(self.info_card)
        
        self.details_label = QLabel("Loading details...")
        self.details_label.setStyleSheet("font-size: 15px; color: #34495e; line-height: 1.6;")
        card_inner_layout.addWidget(self.details_label)
        
        self.edit_trigger_btn = QPushButton("✎ Edit Professional Details")
        self.edit_trigger_btn.setFixedWidth(200)
        self.edit_trigger_btn.setStyleSheet("background-color: #34495e; color: white; border-radius: 5px; padding: 8px;")
        self.edit_trigger_btn.clicked.connect(self.show_edit_mode)
        
        view_layout.addWidget(self.info_card)
        view_layout.addWidget(self.edit_trigger_btn, alignment=Qt.AlignRight)
        
        # --- EDIT MODE FORM ---
        self.edit_widget = QWidget()
        self.edit_widget.hide()
        edit_layout = QVBoxLayout(self.edit_widget)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("background: white; border-radius: 15px; padding: 20px;")
        self.grid = QGridLayout(form_frame)

        self.inputs = {
            "Nickname": QLineEdit(),
            "Age": QLineEdit(),
            "Gender": QLineEdit(),
            "Address": QLineEdit(),
            "Telephone": QLineEdit(),
            "Cellphone": QLineEdit(),
            "Education": QLineEdit(),
            "Supervisor": QLineEdit(),
            "Job Title": QLineEdit(),
            "Department": QLineEdit()
        }

        for i, (label, widget) in enumerate(self.inputs.items()):
            self.grid.addWidget(QLabel(f"{label}:"), i, 0)
            self.grid.addWidget(widget, i, 1)

        save_btn = QPushButton("💾 Save Changes")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        save_btn.clicked.connect(self.save_edits)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #7f8c8d; color: white; padding: 10px; border-radius: 5px;")
        cancel_btn.clicked.connect(self.show_view_mode)

        edit_layout.addWidget(form_frame)
        edit_layout.addWidget(save_btn)
        edit_layout.addWidget(cancel_btn)

        self.layout.addWidget(self.view_widget)
        self.layout.addWidget(self.edit_widget)

    def refresh_data(self, username):
        self.current_username = username
        data = self.db.get_employee_by_username(username)
        if data:
            self.employee_id = data[20] if len(data) > 20 else data[0]

            def get_val(idx):
                return data[idx] if len(data) > idx and data[idx] is not None else ""

            # Combined into a single formatted string (removes the comma syntax error)
            details_html = (
                f"<b>Name:</b> {get_val(1)}<br>"
                f"<b>Email:</b> {get_val(7)}<br><br>"
                f"<b>Nickname:</b> {get_val(4)}<br>"
                f"<b>Age:</b> {get_val(5)}<br>"
                f"<b>Gender:</b> {get_val(6)}<br>"
                f"<b>Address:</b> {get_val(8)}<br>"
                f"<b>Telephone:</b> {get_val(9)}<br>"
                f"<b>Cellphone:</b> {get_val(10)}<br>"
                f"<b>Education:</b> {get_val(11)}<br>"
                f"<b>Supervisor:</b> {get_val(13)}<br>"
                f"<b>Job Title:</b> {get_val(14)}<br>"
                f"<b>Department:</b> {get_val(16)}"
            )
            self.details_label.setText(details_html)
            
            # Pre-fill Edit inputs
            self.inputs["Nickname"].setText(str(get_val(4)))
            self.inputs["Age"].setText(str(get_val(5)))
            self.inputs["Gender"].setText(str(get_val(6)))
            self.inputs["Address"].setText(str(get_val(8)))
            self.inputs["Telephone"].setText(str(get_val(9)))
            self.inputs["Cellphone"].setText(str(get_val(10)))
            self.inputs["Education"].setText(str(get_val(11)))
            self.inputs["Supervisor"].setText(str(get_val(13)))
            self.inputs["Job Title"].setText(str(get_val(14)))
            self.inputs["Department"].setText(str(get_val(16)))

    def show_edit_mode(self):
        self.view_widget.hide()
        self.edit_widget.show()
        if hasattr(self.dashboard, 'header_label'):
            self.dashboard.header_label.setText("Edit Profile Information")

    def show_view_mode(self):
        self.edit_widget.hide()
        self.view_widget.show()
        if hasattr(self.dashboard, 'header_label'):
            self.dashboard.header_label.setText("My Professional Profile")

    def save_edits(self):
        if not self.current_username:
            QMessageBox.warning(self, "Error", "No active user found.")
            return

        nickname = self.inputs["Nickname"].text().strip()
        age = self.inputs["Age"].text().strip()
        gender = self.inputs["Gender"].text().strip()
        address = self.inputs["Address"].text().strip()
        telephone = self.inputs["Telephone"].text().strip()
        cellphone = self.inputs["Cellphone"].text().strip()
        education = self.inputs["Education"].text().strip()
        supervisor = self.inputs["Supervisor"].text().strip()
        job_title = self.inputs["Job Title"].text().strip()
        department = self.inputs["Department"].text().strip()

        if age and not age.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Age must be a valid number.")
            return

        try:
            success = self.db.update_employee_profile(
                username=self.current_username,
                new_nickname=nickname,
                new_age=int(age) if age else None,
                new_gender=gender,
                new_address=address,
                new_telephone=telephone,
                new_cellphone=cellphone,
                new_education=education,
                new_supervisor=supervisor,
                new_job_title=job_title,
                new_department=department
            )

            if success:
                QMessageBox.information(self, "Success", "Profile updated successfully!")
                self.refresh_data(self.current_username)
                self.show_view_mode()
            else:
                QMessageBox.warning(self, "Error", "Failed to update profile. Please try again.")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while saving: {str(e)}")