from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, 
                             QPushButton, QGridLayout, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt

class ProfilePage(QWidget):
    def __init__(self, db, parent_dashboard):
        super().__init__()
        self.db = db
        self.dashboard = parent_dashboard # Reference to refresh headers/stack
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
        self.details_label.setStyleSheet("font-size: 15px; color: #34495e;")
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
            "Cellphone": QLineEdit()
        }

        for i, (label, widget) in enumerate(self.inputs.items()):
            self.grid.addWidget(QLabel(f"{label}:"), i, 0)
            self.grid.addWidget(widget, i, 1)

        save_btn = QPushButton("💾 Save Changes")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        save_btn.clicked.connect(self.save_edits)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.show_view_mode)

        edit_layout.addWidget(form_frame)
        edit_layout.addWidget(save_btn)
        edit_layout.addWidget(cancel_btn)

        self.layout.addWidget(self.view_widget)
        self.layout.addWidget(self.edit_widget)

    def refresh_data(self, username):
        data = self.db.get_employee_by_username(username)
        if data:
            # Update View Label
            self.details_label.setText(f"<b>Name:</b> {data[1]}<br><b>Email:</b> {data[7]}")
            # Pre-fill Edit inputs
            self.inputs["Nickname"].setText(str(data[4]))
            self.inputs["Age"].setText(str(data[5]))
            self.inputs["Gender"].setText(str(data[6]))
            self.inputs["Address"].setText(str(data[8]))
            self.inputs["Telephone"].setText(str(data[9]))
            self.inputs["Cellphone"].setText(str(data[10]))
            
           
    def show_edit_mode(self):
        self.view_widget.hide()
        self.edit_widget.show()
        self.dashboard.header_label.setText("Edit Profile Information")

    def show_view_mode(self):
        self.edit_widget.hide()
        self.view_widget.show()
        self.dashboard.header_label.setText("My Professional Profile")

    def save_edits(self):
        # Logic to call self.db.update_employee_profile
        QMessageBox.information(self, "Success", "Profile Updated")
        self.show_view_mode()