import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget


from database_manager import DatabaseManager
from login_window import LoginWindow
from admin_screens import AdminHome
from Employee_Page.employee_dashboard import EmployeeDashboard
from Admin_Page.Manage_Employees.admin_manage_employees import AdminManageEmployees
from Admin_Page.Master_Tables_Setup.admin_master_table_manager import MasterTableManager
from Admin_Page.Job_Requirements.admin_requirements_setup_manager import RequirementsSetupManager
from Admin_Page.Setup_Alerts.Admin_Setup_Alerts_Manager import AlertsSetupManager
from Admin_Page.Trainings_Setup.Admin_Setup_Trainings import AdminTrainingManagement


class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.logged_in_user = None
        self.admin_name = "Admin User"
        self.setStyleSheet("""
            QPushButton { border-radius: 5px; padding: 5px; }
            QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 3px; }
        """)

        self.login_page = LoginWindow(self.db, self.handle_routing)
        self.admin_home = AdminHome("Admin User", self.go_to_manage_employees, self.show_login)
        self.admin_manage_page = AdminManageEmployees(self.db, self.logged_in_user, self.go_to_admin_home)
        self.employee_page = EmployeeDashboard(self.db, self.show_login)
        self.master_table_page = MasterTableManager(self.db, self.admin_name, self.go_to_admin_home)
        self.admin_requirements_page = RequirementsSetupManager(self.db, self.admin_name, self.go_to_admin_home)
        self.admin_alerts_page = AlertsSetupManager(self.db, self.admin_name, self.go_to_admin_home)
        self.admin_trainings_page = AdminTrainingManagement(self.db, self.admin_name, self.go_to_admin_home)

        
        self.addWidget(self.login_page)       # 0
        self.addWidget(self.admin_home)       # 1
        self.addWidget(self.admin_manage_page) # 2
        self.addWidget(self.employee_page)    # 3
        self.addWidget(self.master_table_page) #4
        self.addWidget(self.admin_requirements_page) #5
        self.addWidget(self.admin_alerts_page) #6
        self.addWidget(self.admin_trainings_page) #7
        
        self.setWindowTitle("Corporate Onboarding System")
        self.resize(1000, 700)
        self.setCurrentIndex(0)

    def handle_routing(self, role, username):
        self.logged_in_user = username

        if role == "admin":
            self.admin_home.admin_label.setText(f"Welcome, {username}")
            self.setCurrentIndex(1)
        else:
            self.employee_page.load_employee_data(username)
            self.setCurrentIndex(3)

    def go_to_manage_employees(self, screen_class=None):
        if screen_class == MasterTableManager:
            self.master_table_page.load_table_data(self.master_table_page.jobs_table, "Jobs")
            self.master_table_page.load_table_data(self.master_table_page.departments_table, "Departments")
            self.setCurrentIndex(4)
        elif screen_class == RequirementsSetupManager:
            self.admin_requirements_page.load_data()
            self.setCurrentIndex(5)
        elif screen_class == AlertsSetupManager:
            self.admin_alerts_page.load_data()
            self.setCurrentIndex(6)
        elif screen_class == AdminTrainingManagement:
            self.admin_trainings_page.refresh_data()
            self.setCurrentIndex(7)
        else:
            # Default behavior for "Manage Employees"
            self.admin_manage_page.load_data()
            self.setCurrentIndex(2)

    def go_to_admin_home(self):
        self.setCurrentIndex(1)

    def show_login(self):
        self.login_page.username.clear()
        self.login_page.password.clear()
        self.login_page.admin_settings_btn.hide()
        self.setCurrentIndex(0)

    def on_login_success(self, role, username):
        self.logged_in_user = username  # <--- 2. Save the username here!
        
        if role == "admin":
            self.show_admin_dashboard()
        else:
            self.show_employee_portal()

    def show_admin_dashboard(self):
        # 3. Pass that saved username to your management screen
        self.admin_manage_page = AdminManageEmployees(
            self.db, 
            self.logged_in_user, # Passing the real username
            self.go_to_admin_home
        )
        self.stacked_widget.addWidget(self.admin_manage_page)
        self.stacked_widget.setCurrentWidget(self.admin_manage_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())