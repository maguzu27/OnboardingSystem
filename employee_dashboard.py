from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt
import os
import shutil
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class EmployeeDashboard(QWidget):
    def __init__(self, db, logout_callback):
        super().__init__()
        self.db = db
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("My Employee Profile")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        self.info_card = QFrame()
        self.info_card.setFrameShape(QFrame.StyledPanel)
        self.info_card.setStyleSheet("background-color: #f9f9f9; padding: 20px; border-radius: 10px;")
        card_layout = QVBoxLayout(self.info_card)
        
        self.details = QLabel("Loading details...")
        self.details.setStyleSheet("font-size: 16px; line-height: 150%;")
        card_layout.addWidget(self.details)

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout_callback)

        self.upload_btn = QPushButton("Upload Onboarding Document")
        # self.upload_btn.clicked.connect(self.upload_requirement)
        self.upload_btn.clicked.connect(lambda: self.upload_requirement(self.current_user_name))
        


        layout.addWidget(title, alignment=Qt.AlignCenter)
        layout.addWidget(self.info_card)
        layout.addWidget(logout_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def load_employee_data(self, name):
        data = self.db.get_employee_by_username(name)
        if data:
            self.current_user_name = data[1]
            self.details.setText(f"<b>Name:</b> {data[1]}<br>"
                                 f"<b>Email:</b> {data[2]}<br>"
                                 f"<b>Education:</b> {data[3]}<br>"
                                 f"<b>Job Title:</b> {data[4]}<br>"
                                 f"<b>Supervisor:</b> {data[5]}")
        else:
            self.details.setText("No information found for this account.<br>Contact Admin to add your details.")

    def upload_requirement(self, employee_name):
        # 1. Open File Dialog
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Upload", "", 
            "All Files (*);;PDF Files (*.pdf);;Images (*.png *.jpg)", options=options
        )

        if file_path:
            try:
                # 2. Setup Destination
                upload_dir = "uploaded_requirements"
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                original_filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                # Create a unique filename to prevent overwriting
                unique_filename = f"{employee_name}_{original_filename}"
                destination_path = os.path.join(upload_dir, unique_filename)

                # 3. Copy file to project folder
                shutil.copy(file_path, destination_path)

                # 4. Save metadata to Database
                success = self.db.add_attachment(
                    file_path=destination_path,
                    file_name=unique_filename,
                    original_name=original_filename,
                    username=employee_name,
                    file_size=file_size
                )

                if success:
                    QMessageBox.information(self, "Success", "File uploaded and recorded successfully!")
                else:
                    QMessageBox.warning(self, "Database Error", "File copied but failed to save to database.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")