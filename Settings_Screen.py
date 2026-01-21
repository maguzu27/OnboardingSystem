import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt



class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Configuration")
        self.setMinimumSize(500, 350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 1. Create a Table instead of a Form for better visibility
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Variable", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Read-only
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        
        # 2. Read the file
        settings = self.load_settings()

        # 3. Populate Table
        if settings:
            self.table.setRowCount(len(settings))
            for row, (key, value) in enumerate(settings.items()):
                # Variable Column (Key) - Make this non-editable
                key_item = QTableWidgetItem(key)
                key_item.setFlags(key_item.flags() ^ Qt.ItemIsEditable) 
                self.table.setItem(row, 0, key_item)

                # Value Column - Editable by default
                self.table.setItem(row, 1, QTableWidgetItem(value))
        else:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("Error"))
            self.table.setItem(0, 1, QTableWidgetItem("No data found in .env"))

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")

        # 4. Finalize Layout
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #34495e; color: white; padding: 10px; font-weight: bold;")

        layout.addWidget(QLabel("<b>Environment Variables:</b>"))
        layout.addWidget(self.table)
        layout.addWidget(close_btn)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def load_settings(self):
        settings = {}
        env_path = os.path.join(os.getcwd(), ".env")
        
        try:
            if os.path.exists(env_path):
                # Using utf-8-sig handles files saved with "BOM" (Excel/Notepad issue)
                with open(env_path, "r", encoding="utf-8-sig") as f:
                    for line in f:
                        line = line.strip()
                        # Only process lines that have an '=' and aren't comments
                        if "=" in line and not line.startswith("#"):
                            parts = line.split("=", 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()
                                settings[key] = value
        except Exception as e:
            print(f"Error reading file: {e}")
            
        return settings
    
    def save_settings(self):
        # 1. Get the correct path to the .env file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(base_dir, ".env")

        try:
            with open(env_path, "w", encoding="utf-8") as f:
                for row in range(self.table.rowCount()):
                    # Get the Variable (Key) and the new Value from the table
                    key_item = self.table.item(row, 0)
                    val_item = self.table.item(row, 1)

                    if key_item and val_item:
                        key = key_item.text().strip()
                        value = val_item.text().strip()
                        
                        # Prevent saving the "Error" row if it exists
                        if key != "Error":
                            f.write(f"{key}={value}\n")

            QMessageBox.information(self, "Success", "Configuration updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save changes: {e}")