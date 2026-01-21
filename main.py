import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget


from database_manager import DatabaseManager
from login_window import LoginWindow
from admin_screens import AdminHome
from employee_dashboard import EmployeeDashboard
from admin_manage_employees import AdminManageEmployees

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setStyleSheet("""
            QPushButton { border-radius: 5px; padding: 5px; }
            QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 3px; }
        """)

        self.login_page = LoginWindow(self.handle_routing)
        self.admin_home = AdminHome("Admin User", self.go_to_manage_employees, self.show_login)
        self.admin_manage_page = AdminManageEmployees(self.db, self.go_to_admin_home)
        self.employee_page = EmployeeDashboard(self.db, self.show_login)
        
        self.addWidget(self.login_page)       # 0
        self.addWidget(self.admin_home)       # 1
        self.addWidget(self.admin_manage_page) # 2
        self.addWidget(self.employee_page)    # 3
        
        self.setWindowTitle("Corporate Onboarding System")
        self.resize(1000, 700)
        self.setCurrentIndex(0)

    def handle_routing(self, role, username):
        if role == "admin":
            self.admin_home.admin_label.setText(f"Welcome, {username}")
            self.setCurrentIndex(1)
        else:
            self.employee_page.load_employee_data(username)
            self.setCurrentIndex(3)

    def go_to_manage_employees(self):
        self.admin_manage_page.load_data()
        self.setCurrentIndex(2)

    def go_to_admin_home(self):
        self.setCurrentIndex(1)

    def show_login(self):
        self.login_page.username.clear()
        self.login_page.password.clear()
        self.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())