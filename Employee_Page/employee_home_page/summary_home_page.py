from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout)
from PyQt5.QtCore import Qt

class MetricCard(QFrame):
    """Reusable card component for key dashboard statistics."""
    def __init__(self, title, value, accent_color="#3498db"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                border-left: 6px solid {accent_color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #7f8c8d; font-size: 13px; font-weight: bold; border: none;")
        
        self.val_label = QLabel(str(value))
        self.val_label.setStyleSheet("color: #2c3e50; font-size: 26px; font-weight: bold; border: none;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.val_label)

    def set_value(self, value):
        self.val_label.setText(str(value))


class HomePage(QWidget):
    def __init__(self, db, username=None):
        super().__init__()
        self.db = db
        self.username = username
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(20)

        # Overview Header
        overview_title = QLabel("📊 Dashboard Overview")
        overview_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(overview_title)

        # Metric Cards Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        self.card_total = MetricCard("Total Assigned Trainings", 0, "#3498db")       # Blue
        self.card_completed = MetricCard("Completed Trainings", 0, "#2ecc71")       # Green
        self.card_in_progress = MetricCard("In Progress Trainings", 0, "#f1c40f")    # Yellow
        self.card_pending = MetricCard("Pending Trainings", 0, "#e67e22")            # Orange

        grid_layout.addWidget(self.card_total, 0, 0)
        grid_layout.addWidget(self.card_completed, 0, 1)
        grid_layout.addWidget(self.card_in_progress, 1, 0)
        grid_layout.addWidget(self.card_pending, 1, 1)

        layout.addLayout(grid_layout)
        layout.addStretch()

    def refresh_data(self, username=None):
        if username:
            self.username = username
            
        if not self.username:
            return

        emp_data = self.db.get_employee_by_username(self.username)
        if not emp_data:
            return

        employee_id = emp_data[20]
        rows = self.db.get_employee_training_items(employee_id) or []

        # Calculate metrics from Employee_Trainings status column (Index 4)
        total = len(rows)
        completed = 0
        in_progress = 0
        pending = 0

        for row in rows:
            # Assuming row[4] contains status ("Completed", "In Progress", "Pending")
            status = str(row[4]).strip().lower()
            if status == "completed":
                completed += 1
            elif status == "in progress":
                in_progress += 1
            else:
                pending += 1

        # Update card labels
        self.card_total.set_value(total)
        self.card_completed.set_value(completed)
        self.card_in_progress.set_value(in_progress)
        self.card_pending.set_value(pending)