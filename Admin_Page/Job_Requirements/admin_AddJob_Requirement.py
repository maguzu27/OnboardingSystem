from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QWidget, QFormLayout, 
                             QFrame, QComboBox, QGridLayout)
from PyQt5.QtCore import Qt

class RequirementEntryDialog(QDialog):
    def __init__(self, db, parent=None, title="Requirement Setup", name="", job_id=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle(title)
        self.resize(500, 300)
        
        # Consistent Professional Styling
        self.setStyleSheet("""
            QDialog { background-color: #f8f9fa; }
            QLineEdit, QComboBox { 
                padding: 10px; 
                border: 1px solid #dee2e6; 
                border-radius: 5px; 
                background: white;
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #3498db; }
        """)
        
        self.inputs = {}
        self.init_ui(name, job_id)

    def init_ui(self, name, job_id):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)

        header_lbl = QLabel(self.windowTitle())
        header_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(header_lbl)

        # Content Frame
        frame = QFrame()
        frame.setStyleSheet("background: white; border-radius: 8px; border: 1px solid #dee2e6;")
        form_layout = QFormLayout(frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        # Requirement Group Name
        self.name_input = QLineEdit()
        self.name_input.setText(name)
        self.name_input.setPlaceholderText("e.g. Technical Documents")
        form_layout.addRow("Requirement Group:", self.name_input)

        # Job Dropdown (Lookup logic)
        self.job_combo = QComboBox()
        self.job_combo.addItem("Select a Job Link", None)
        
        # Fetching jobs: Using your existing get_master_data logic
        jobs_data = self.db.get_master_data("Jobs")
        for j_id, title, desc, *args in jobs_data:
            display_text = f"{title} — {desc}"
            self.job_combo.addItem(display_text, j_id) # j_id is stored as UserData

        # If editing, select the current job
        if job_id:
            idx = self.job_combo.findData(job_id)
            if idx >= 0: self.job_combo.setCurrentIndex(idx)

        form_layout.addRow("Associated Job:", self.job_combo)
        main_layout.addWidget(frame)

        # Footer Buttons
        btns = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save Record")
        self.save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 8px 20px;")
        self.save_btn.clicked.connect(self.accept)

        btns.addStretch()
        btns.addWidget(cancel_btn)
        btns.addWidget(self.save_btn)
        main_layout.addLayout(btns)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "job_id": self.job_combo.currentData()
        }