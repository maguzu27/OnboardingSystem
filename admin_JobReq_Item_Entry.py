from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QFormLayout, QFrame)

class AddRequirementItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Requirement Item")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog { background-color: #f8f9fa; }
            QLineEdit, QComboBox { 
                padding: 10px; 
                border: 1px solid #dee2e6; 
                border-radius: 5px; 
                background: white;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("New Item Details")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Form Container
        self.frame = QFrame()
        self.frame.setStyleSheet("background: white; border-radius: 8px; border: 1px solid #dee2e6;")
        form = QFormLayout(self.frame)
        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(15)

        self.name_input = QLineEdit()
        self.code_input = QLineEdit()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Document (PDF/DOC)", "Image (JPG/PNG)", "Digital Signature", "Text Input", "Certification"])
        
        self.desc_input = QLineEdit()

        form.addRow("Requirement Name:", self.name_input)
        form.addRow("Requirement Code:", self.code_input)
        form.addRow("Item Type:", self.type_combo)
        form.addRow("Description:", self.desc_input)

        layout.addWidget(self.frame)

        # Buttons
        btns = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Add Item")
        save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 8px 20px;")
        save_btn.clicked.connect(self.accept)

        btns.addStretch()
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "code": self.code_input.text(),
            "type": self.type_combo.currentText(),
            "desc": self.desc_input.text()
        }