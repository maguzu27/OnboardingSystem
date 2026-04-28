
import sqlite3
from tkinter.tix import TEXT
import datetime
from logger_config import logger

class DatabaseManager:
    def __init__(self, db_path="onboarding.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.cursor = self.conn.cursor()
        self.create_employees_table()
        self.create_employee_requirement_attach_table()
        self.create_requirements_setup_table()
        self.create_requirements_items_table()
        self.create_jobs_master_table()
        self.create_departments_master_table()
        self.create_employee_requirements_table()
        self.create_alert_dashboard_items_table()
        self.create_alert_items_table()
        self.create_employee_passwords_table()
        self.create_account_access_table()
        self.create_training_table()
        self.create_employee_trainings_table()


    def create_employees_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE NOT NULL,
            First_Name TEXT NOT NULL,
            Last_Name TEXT NOT NULL,
            Display_Name TEXT NOT NULL,
            Nick_Name TEXT,
            Age INTEGER NOT NULL,
            Gender TEXT NOT NULL,
            Education TEXT,
            Email TEXT NOT NULL,
            Address TEXT NOT NULL,
            Telephone TEXT NOT NULL,
            Cellphone TEXT NOT NULL,
            Supervisor_id INTEGER,
            Employeement_Status TEXT,
            Hired TEXT,
            Employement_Type TEXT NOT NULL,
            Date_Hired TEXT,
            Birthday TEXT,
            Date_Created TEXT,
            Date_Updated TEXT,
            Created_By TEXT,
            Updated_By TEXT,
            Dept_ID INTEGER,
            Job_title_Id INTEGER,
            Req_Group_Name TEXT NOT NULL,
            FOREIGN KEY (Req_Group_Name) REFERENCES requirements_setup (Req_Group_Name)
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def create_employee_requirement_attach_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Requirement_Attachments (
                Attachment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Employee_Req_ID INTEGER NOT NULL,
                Employee_Name TEXT, --username
                File_path TEXT UNIQUE,
                File_name Text,
                Original_File_name Text,
                Date_Created DATE DEFAULT (datetime('now','localtime')),
                Created_By TEXT,
                Uploaded_By TEXT,
                Updated_By TEXT DEFAULT NULL,
                Date_Updated DATE DEFAULT NULL,
                File_Size INTEGER,
                Scan_Status TEXT,
                FOREIGN KEY (Employee_Req_ID) REFERENCES Employee_Requirements(Employee_Req_ID) ON DELETE CASCADE                                  
            )
        """)
        self.conn.commit()

    def create_jobs_master_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS Jobs (
            job_title_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT UNIQUE NOT NULL,
            job_description TEXT NOT NULL,
            Created_By TEXT,
            Date_Created TEXT,
            Updated_By TEXT,
            Date_Updated TEXT
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def create_departments_master_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS Departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT UNIQUE NOT NULL,
            dept_description TEXT,
            Dept_Address TEXT,
            Created_By TEXT,
            Date_Created TEXT,
            Updated_By TEXT,
            Date_Updated TEXT
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def create_requirements_setup_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS Requirements_Setup (
            Req_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Req_Group_Name TEXT NOT NULL,
            Job_ID INTEGER NOT NULL,
            Created_By TEXT,
            Date_Created DATETIME DEFAULT CURRENT_TIMESTAMP,
            Updated_By TEXT,
            Date_Updated DATETIME
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def upsert_master_data(self, table_type, record_id, data):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            if table_type == "Jobs":
                if record_id is None: # NEW
                    query = """INSERT INTO Jobs (job_title, job_description, Created_By, Date_Created) 
                               VALUES (?, ?, ?, ?)"""
                    self.cursor.execute(query, (data['title'], data['desc'], data['admin'], now))
                else: # EDIT
                    query = """UPDATE Jobs SET job_title=?, job_description=?, Updated_By=?, Date_Updated=? 
                               WHERE job_title_id=?"""
                    self.cursor.execute(query, (data['title'], data['desc'], data['admin'], now, record_id))
            
            else: # Departments
                if record_id is None: # NEW
                    query = """INSERT INTO Departments (dept_name, dept_description, Dept_Address, Created_By, Date_Created) 
                               VALUES (?, ?, ?, ?, ?)"""
                    self.cursor.execute(query, (data['name'], data['desc'], data['address'], data['admin'], now))
                else: # EDIT
                    query = """UPDATE Departments SET dept_name=?, dept_description=?, Dept_Address=?, Updated_By=?, Date_Updated=? 
                               WHERE dept_id=?"""
                    self.cursor.execute(query, (data['name'], data['desc'], data['address'], data['admin'], now, record_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"DATABASE ERROR: {e}")
            return False

    def delete_master_data(self, table_type, record_id):
        print(f"Attempting to delete from {table_type} with ID {record_id}")
        pk= None
        table = None
        if table_type == "Jobs":
            pk = "job_title_id"
            table = "Jobs"
        elif table_type == "Departments":
            pk = "dept_id"
            table = "Departments"
        elif table_type == "Requirements":
            pk = "Req_id"
            table = "Requirements_Setup"
        elif table_type == "Trainings":
            pk = "training_id"
            table = "Trainings"
        print(f"Constructed DELETE query for table {table} with primary key {pk}")
        try:
            self.cursor.execute(f"DELETE FROM {table} WHERE {pk} = ?", (record_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Delete Error: {e}")
            return False
        
    def add_attachment(self, file_path, file_name, original_name, username, file_size, employee_req_id):
        try:
            # We must match the number of columns to the number of ? and the number of values
            query = """
                INSERT INTO Requirement_Attachments 
                (Employee_Name, File_path, File_name, Original_File_name, Created_By, Uploaded_By, File_Size, Scan_Status, Employee_Req_ID) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # 8 Columns = 8 Values
            values = (
                username,       # Employee_Name (now using Username string)
                file_path,      # File_path
                file_name,      # File_name
                original_name,  # Original_File_name
                username,       # Created_By
                username,       # Uploaded_By
                file_size,      # File_Size
                "Clean",         # Scan_Status
                employee_req_id  # Employee_Req_ID (foreign key to link to the specific requirement)
            )
            
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return False
        
    def add_employee(self, data_dict):
        try:
            # Match these keys EXACTLY to the keys in your data_dict
            query = """
                INSERT INTO employees (
                    Username, First_Name, Last_Name, Display_Name, Nick_Name, 
                    Age, Gender, Email, Address, Telephone, Cellphone, 
                    Supervisor_id, Employeement_Status, Hired, Employement_Type, Date_Hired, 
                    Birthday, Date_Created, Date_Updated, Created_By, Updated_By, 
                    Dept_ID, Job_title_Id
                ) VALUES (
                    :Username, :First_Name, :Last_Name, :Display_Name, :Nick_Name, 
                    :Age, :Gender, :Email, :Address, :Telephone, :Cellphone, 
                    :Supervisor_id, :Employeement_Status, :Hired, :Employement_Type, :Date_Hired, 
                    :Birthday, :Date_Created, :Date_Updated, :Created_By, :Updated_By, 
                    :Dept_ID, :Job_title_Id
                )
            """
            self.cursor.execute(query, data_dict)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False

    def delete_employee(self, emp_id):
        try:
            # Use the exact column name from your image: employee_id
            query = "DELETE FROM employees WHERE employee_id = ?"
            self.cursor.execute(query, (emp_id,))
            self.conn.commit()
            
            # Check if any row was actually affected
            if self.cursor.rowcount > 0:
                logger.info(f"delete_employee: Employee with ID {emp_id} deleted successfully.")
                return True
            return False
        except Exception as e:
            logger.error(f"delete_employee: Database Delete Error: {e}")
            return False

    def get_all_employees(self):
        cursor = self.conn.cursor()
        query = """
        SELECT 
            employee_id, Username, First_Name, Last_Name, Display_Name, Nick_Name,
            Age, Gender, Email, Address, Telephone, Cellphone,
            Supervisor_id, Employeement_Status, Hired, Employement_Type,
            Date_Hired, Birthday, Date_Created, Date_Updated, 
            Created_By, Updated_By, Dept_ID, Job_title_Id
        FROM employees
        """
        cursor.execute(query)
        return cursor.fetchall()

    def get_employee_by_username(self, username):
        try:
            # Update the query to use 'Username' instead of 'name'
            self.cursor.execute(
                """Select 
                    emp.Username, emp.First_name, emp.Last_name, emp.Display_name,
                    emp.Nick_Name, emp.Age, emp.Gender, emp.Email, emp.Address, emp.Telephone, emp.Cellphone, emp.Education,
                    emp.Supervisor_id, supervisor.username Supervisor,
                    emp.Employeement_Status,
                    dept.dept_id, dept.dept_name, dept.dept_description,
                    jobs.job_title, jobs.job_description, emp.employee_id
                from 
	                employees emp left join departments dept on (emp.dept_id = dept.dept_id)
	                left join jobs jobs on (jobs.job_title_id = emp.job_title_id)
                    left join (SELECT employee_id, Username FROM employees) supervisor ON (supervisor.employee_id = emp.Supervisor_id)
                WHERE 
	                emp.username =?""", (username,)
            )

            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching employee: {e}")
            return None
    
    def get_employee_attachment(self, username):
        try:
            # Using Username as the identifier for the file path
            self.cursor.execute("""
            Select 
                emp.Username, emp.First_name, emp.Last_name, emp.Display_name,
                emp.Nick_Name, emp.Age, emp.Gender, emp.Email, emp.Address, emp.Telephone, emp.Cellphone,
                emp.Supervisor_id, (SELECT username sv_name from employees where employee_id = emp.supervisor_id) Supervisor,
                emp.Employeement_Status,
                dept.dept_id, dept.dept_name, dept.dept_description,
                jobs.job_title, jobs.job_description
                
            from 
                employees emp left join departments dept on (emp.dept_id = dept.dept_id)
                left join jobs jobs on (jobs.job_title_id = emp.job_title_id)
            WHERE 
                emp.username = ?""", (username,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Attachment Error: {e}")
            return None
        
    def get_master_data(self, table_type):
        table_name = "Jobs" if table_type == "Jobs" else "Departments"
        self.cursor.execute(f"SELECT * FROM {table_name}")
        return self.cursor.fetchall()
    
    def get_job_req_group_data(self):
        table_name = "requirements_setup"
        self.cursor.execute(f"SELECT req_group_name FROM {table_name}")
        return self.cursor.fetchall()

    def delete_master_record(self, table_type, record_id):
        table_name = "Jobs" if table_type == "Jobs" else "Departments"
        pk = "job_title_id" if table_type == "Jobs" else "dept_id"
        try:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE {pk} = ?", (record_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
    def update_employee(self, target_username, ui_data, admin_username="System_Admin"):
        try:
            # This maps your UI labels (the keys in self.inputs) to DB columns
            mapping = {
                "Nickname": "Nick_Name",
                "Age": "Age",
                "Gender": "Gender",
                "Birthday": "Birthday",
                "Email": "Email",
                "Cellphone": "Cellphone",
                "Telephone": "Telephone",
                "Address": "Address",
                "Type": "Employement_Type",
                "Date Hired": "Date_Hired",
                "Hired Status": "Hired",
                "Department ID": "Dept_ID",
                "Job ID": "Job_title_Id",
                "Supervisor ID": "Supervisor_id",
                "Hired Status": "Employeement_Status",
                "First Name": "First_Name",
                "Last Name": "Last_Name",
                "Display Name": "Display_Name",
                "Updated By": "Updated_By",
                "Updated Date": "Date_Updated"

            }

            sets = []
            params = {"target_user": target_username}
            
            for ui_key, value in ui_data.items():
                if ui_key in mapping:
                    db_column = mapping[ui_key]
                    sets.append(f"{db_column} = :{db_column}")
                    params[db_column] = value

            if not sets:
                return False
            
            # Manually add the Admin and Timestamp
            sets.append("Updated_By = :admin")
            sets.append("Date_Updated = datetime('now', 'localtime')")
            params["admin"] = admin_username

            # Build the dynamic SQL query
            query = f"UPDATE employees SET {', '.join(sets)}, Date_Updated = datetime('now', 'localtime') WHERE Username = :target_user"
            
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Update Error: {e}")
            return False
        

    # Inside your DatabaseManager class
    def get_supervisor_lookup(self):
        try:
            # Fetch ID and Name to show in the dropdown
            query = "SELECT employee_id, Display_Name FROM employees ORDER BY Display_Name ASC"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lookup Error: {e}")
            return []

    def get_department_lookup(self):
        try:
            query = "SELECT dept_id, dept_name FROM Departments ORDER BY dept_name ASC"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lookup Error: {e}")
            return []
        
    def get_all_requirements(self):
        # Explicitly define the order to match your UI mapping
        query = """
            SELECT Req_id, Req_Group_Name, Job_ID, Created_By, 
                Date_Created, Updated_By, Date_Updated 
            FROM Requirements_Setup
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database Error: {e}")
            return []

    def add_requirement(self, group_name, job_id, admin_user):
        try:
            # We only list the 3 columns we are manually providing
            query = """INSERT INTO Requirements_Setup 
                    (Req_Group_Name, Job_ID, Created_By) 
                    VALUES (?, ?, ?)"""
            self.cursor.execute(query, (group_name, job_id, admin_user))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding requirement: {e}")
            return False

    def update_requirement(self, req_id, group_name, job_id, admin_user):
        query = """UPDATE Requirements_Setup 
                SET Req_Group_Name = ?, Job_ID = ?, Updated_By = ?, Date_Updated = datetime('now', 'localtime')
                WHERE Req_id = ?"""
        self.cursor.execute(query, (group_name, job_id, admin_user, req_id))
        self.conn.commit()
        return self.cursor.rowcount > 0


    def get_jobs_for_dropdown(self):
        """Returns Job_title_Id, Job_Title, and Job_Description for the UI."""
        try:
            # Adjust column names if they differ in your 'Jobs' table
            self.cursor.execute("SELECT Job_title_Id, Job_Title, Job_Description FROM Jobs")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching jobs: {e}")
            return []
        
    def create_requirements_items_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS Requirements_Setup_Items (
            Req_id INTEGER,
            Req_line_id INTEGER,
            Req_Name TEXT,
            Req_code TEXT,
            Req_Item_Type TEXT,
            Req_Description TEXT,
            PRIMARY KEY (Req_id, Req_line_id),
            FOREIGN KEY (Req_id) REFERENCES Requirements_Setup(Req_id) ON DELETE CASCADE
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def get_items_by_requirement(self, req_id):
        self.cursor.execute("SELECT * FROM Requirements_Setup_Items WHERE Req_id = ?", (req_id,))
        return self.cursor.fetchall()

    def add_requirement_item(self, req_id, line_id, name, code, item_type, desc):
        try:
            query = """INSERT INTO Requirements_Setup_Items 
                    (Req_id, Req_line_id, Req_Name, Req_code, Req_Item_Type, Req_Description) 
                    VALUES (?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(query, (req_id, line_id, name, code, item_type, desc))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        
    def update_requirement_full(self, req_id, group_name, job_id, admin_user, items_list):
        try:
            # 1. Update Header
            self.cursor.execute("""
                UPDATE Requirements_Setup 
                SET Req_Group_Name = ?, Job_ID = ?, Updated_By = ?, Date_Updated = datetime('now')
                WHERE Req_id = ?
            """, (group_name, job_id, admin_user, req_id))

            # 2. Clear existing items to sync with the new table state
            self.cursor.execute("DELETE FROM Requirements_Setup_Items WHERE Req_id = ?", (req_id,))

            # 3. Insert updated items
            for item in items_list:
                # item = (line_id, name, code, type, desc)
                self.cursor.execute("""
                    INSERT INTO Requirements_Setup_Items 
                    (Req_id, Req_line_id, Req_Name, Req_code, Req_Item_Type, Req_Description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (req_id, item[0], item[1], item[2], item[3], item[4]))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Transaction Error: {e}")
            self.conn.rollback()
            return False
        
    def create_employee_requirements_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS Employee_Requirements (
            Employee_Req_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Employee_id INTEGER NOT NULL,
            Req_id INTEGER NOT NULL,
            Req_line_id INTEGER NOT NULL,
            Requirement_Status TEXT,
            Created_By TEXT,
            Date_Created DATETIME DEFAULT CURRENT_TIMESTAMP,
            Updated_By TEXT,
            Date_Updated DATETIME,
            Requirement_Due_Date DATETIME,
            Requirement_Completion_Date DATETIME,
            FOREIGN KEY (Employee_id) REFERENCES Employees(Employee_id),
            FOREIGN KEY (Req_id, Req_line_id) REFERENCES Requirements_Setup_Items(Req_id, Req_line_id),
            UNIQUE(Employee_id, Req_id, Req_line_id)
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def add_employee_with_requirements(self, emp_data):
        """
        Inserts a new employee and automatically clones requirement items 
        into the Employee_Requirements table.
        """
        try:
            cursor = self.conn.cursor()
            
            # 1. Insert the Employee record
            # Note: Ensure the keys in emp_data match your table columns exactly
            columns = ', '.join(emp_data.keys())
            placeholders = ', '.join(['?'] * len(emp_data))
            sql_emp = f"INSERT INTO employees ({columns}) VALUES ({placeholders})"
            
            cursor.execute(sql_emp, list(emp_data.values()))
            new_emp_id = cursor.lastrowid  # Get the ID of the employee we just created

            # 2. Check if a Requirement Group was selected
            group_name = emp_data.get("Req_Group_Name")
            job_id = emp_data.get("Job_title_Id")

            if group_name and group_name != "No Requirement Group":
                # Find the Req_id for this group name
                cursor.execute("SELECT Req_id FROM Requirements_Setup WHERE Req_Group_Name = ? and Job_ID = ?", (group_name, job_id))
                res = cursor.fetchone()
                
                if res:
                    req_id = res[0]
                    
                    # 3. Fetch all items associated with that group
                    cursor.execute("""
                        SELECT Req_id, Req_line_id 
                        FROM Requirements_Setup_Items 
                        WHERE Req_id = ?
                    """, (req_id,))
                    items = cursor.fetchall()
                    
                    # 4. Insert each item into Employee_Requirements
                    for r_id, line_id in items:
                        cursor.execute("""
                            INSERT INTO Employee_Requirements (
                                Employee_id, Req_id, Req_line_id, Requirement_Status, Created_By
                            ) VALUES (?, ?, ?, ?, ?)
                        """, (new_emp_id, r_id, line_id, 'Pending', emp_data.get('Created_By')))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error in transaction: {e}")
            self.conn.rollback()
            return False
        
    def execute_query(self, query, params=None):
        """A helper to fetch all rows for a given query and parameters."""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    
    def delete_employee_requirement(self, record_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Employee_Requirements WHERE Employee_Req_ID = ?", (record_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Delete Error: {e}")
            return False
        
    def execute_non_query(self, query, params=()):
        """Executes a query that doesn't return data (Update, Insert, Delete)."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            self.conn.rollback()
            return False
        
    def create_alert_dashboard_items_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS Alert_Dashboard_Items (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Alert_Name TEXT,
            Alert_Code TEXT,
            Alert_Type TEXT,
            Alert_Description TEXT,
            Alert_Trigger_Date DATETIME,
            Alert_Status TEXT,
            Alert_Acknowledged_By TEXT,
            Alert_Acknowledged_Date DATETIME,
            Date_Created DATETIME DEFAULT CURRENT_TIMESTAMP,
            Created_By TEXT,
            Updated_By TEXT,
            Date_Updated DATETIME
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def create_alert_items_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS Alert_Items (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Alert_Name TEXT,
            Alert_Description TEXT,
            Alert_Code TEXT,
            Alert_Type TEXT,
            Employee_Record_Created BOOLEAN,
            Employee_Record_Deleted BOOLEAN,
            Employee_Record_Updated BOOLEAN,
            Employee_Updated_JobRqrmt BOOLEAN,
            Employee_Updated_TrainingRqrmt BOOLEAN,
            JobRqrmt_Due_date_X_Days INTEGER,
            JobRqrmt_Due_date_Today BOOLEAN,
            Alert_Email_Recipient TEXT,
            Alert_Username_Recipient TEXT,
            Attach_File BOOLEAN,
            Details_In_Body BOOLEAN,
            App_Home_Notification BOOLEAN,
            Alert_Start_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
            Alert_End_Date DATETIME DEFAULT NULL,
            Attribute_1 TEXT,
            Condition_1 TEXT,
            Attribute_2 TEXT,
            Condition_2 TEXT,
            Attribute_3 TEXT,
            Condition_3 TEXT,
            Attribute_4 TEXT,
            Condition_4 TEXT,
            Attribute_5 TEXT,
            Condition_5 TEXT,
            Date_Created DATETIME DEFAULT CURRENT_TIMESTAMP,
            Created_By TEXT,
            Updated_By TEXT,
            Date_Updated DATETIME
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def get_all_alert_dashboard_items(self):
        # Explicitly define the order to match your UI mapping
        query = """
            SELECT ID, Alert_Name, Alert_Code, Alert_Type, Alert_Description, 
                Alert_Status, Alert_Trigger_Date, Alert_Acknowledged_By, Alert_Acknowledged_Date
            FROM Alert_Dashboard_Items
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database Error: {e}")
            return []
        

    def add_alert_item(self, data_tuple):
        print(f"Adding alert with data: {data_tuple}")  # Debug statement to check the input data
        query = """
        INSERT INTO Alert_Items (
            Alert_Name, Employee_Record_Created, Employee_Record_Deleted, Employee_Record_Updated,
            Employee_Updated_JobRqrmt, Employee_Updated_TrainingRqrmt, JobRqrmt_Due_date_X_Days,
            JobRqrmt_Due_date_Today, Alert_Email_Recipient, Alert_Username_Recipient,
            Attach_File, Details_In_Body, App_Home_Notification, Created_By,
            Attribute_1, Condition_1, Attribute_2, Condition_2, Attribute_3, Condition_3,
            Attribute_4, Condition_4, Attribute_5, Condition_5
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) 
        """ # Ensure there are 24 question marks here
        return self.execute_non_query(query, data_tuple)
    
    def get_all_alert_setup_items(self):
        # Explicitly define the order to match your UI mapping
        query = """
            SELECT ID, Alert_Name, Date_Created, Created_By, Updated_By, Date_Updated
            FROM Alert_Items
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database Error: {e}")
            return []
        
    def get_alert_by_id(self, alert_id):
        query = """
            SELECT
                ID,
                Alert_Name,
                Employee_Record_Created,
                Employee_Record_Deleted,
                Employee_Record_Updated,
                Employee_Updated_JobRqrmt,
                Employee_Updated_TrainingRqrmt,
                JobRqrmt_Due_date_X_Days,
                JobRqrmt_Due_date_Today,
                Alert_Email_Recipient,
                Alert_Username_Recipient,
                Attach_File,
                Details_In_Body,
                App_Home_Notification,
                Attribute_1,
                Condition_1,
                Attribute_2,
                Condition_2,
                Attribute_3,
                Condition_3,
                Attribute_4,
                Condition_4,
                Attribute_5,
                Condition_5
            FROM Alert_Items 
            WHERE ID = ?
        """

        try:
            # Using fetchone() because IDs are unique; we only expect one row
            result = self.execute_query(query, (alert_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Database Error: {e}")
            return None
        
    def delete_alert_item(self, alert_id):
        try:
            self.cursor.execute("DELETE FROM Alert_Items WHERE ID = ?", (alert_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Delete Error: {e}")
            return False

    def update_alert_item(self, row_id, sql_tuple):
        params = sql_tuple + (row_id,)
        
        query = """
        UPDATE Alert_Items 
        SET 
            Alert_Name =?,
            Employee_Record_Created =?,
            Employee_Record_Deleted =?,
            Employee_Record_Updated =?,
            Employee_Updated_JobRqrmt =?,
            Employee_Updated_TrainingRqrmt =?,
            JobRqrmt_Due_date_X_Days =?,
            JobRqrmt_Due_date_Today =?,
            Alert_Email_Recipient =?,
            Alert_Username_Recipient =?,
            Attach_File =?,
            Details_In_Body =?,
            App_Home_Notification =?,
            Updated_By =?,
            Attribute_1 =?,
            Condition_1 =?,
            Attribute_2 =?,
            Condition_2 =?,
            Attribute_3 =?,
            Condition_3 =?,
            Attribute_4 =?,
            Condition_4 =?,
            Attribute_5 =?,
            Condition_5 =?

        WHERE ID = ?
        """

        try:
            print(f"Alert with ID {params} updated successfully.")
            return self.execute_non_query(query, params)

        except Exception as e:
            print(f"Error updating alert: {e}")
            return False
    
    def create_employee_passwords_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS employee_passwords (
            employee_id INTEGER,
            Password TEXT NOT NULL, -- Store hashed passwords, not plain text!
            Password_Token TEXT,
            Token_Expiry DATETIME,
            Date_Created DATETIME DEFAULT CURRENT_TIMESTAMP,
            Date_Updated DATETIME,
            Password_Reset_By TEXT,
            Password_Reset_Date DATETIME,
            Password_Reset_Request BOOLEAN DEFAULT 0,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            PRIMARY KEY (employee_id)
        )
        """

        self.cursor.execute(query)
        self.conn.commit()

    def save_password_token(self, token, email, username, expiry):
        """
        Finds the employee_id via email and saves the security token.
        'expiry' should be a datetime object.
        """
        try:
            # 1. Get the employee_id from the employees table
            self.cursor.execute("SELECT employee_id FROM employees WHERE Username = ?", (username,))
            result = self.cursor.fetchone()
            
            # if not result:
            #     print(f"Error: No employee found with email {email}")
            #     return False
                
            emp_id = result[0]
            expiry_str = expiry.strftime('%Y-%m-%d %H:%M:%S')

            # 2. Insert or Update the password table
            # We use COALESCE for Password to avoid overwriting a real password with NULL
            # during the initial token generation.
            query = """
            INSERT INTO employee_passwords (
                employee_id, 
                Password, 
                Password_Token, 
                Token_Expiry, 
                Date_Updated
            ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(employee_id) DO UPDATE SET
                Password_Token = excluded.Password_Token,
                Token_Expiry = excluded.Token_Expiry,
                Date_Updated = CURRENT_TIMESTAMP;
            """
            
            # We pass "PENDING_SET" as a placeholder for the Password column 
            # since it's NOT NULL in your schema.
            self.cursor.execute(query, (emp_id, "PENDING_SET", token, expiry_str))
            self.conn.commit()
            return True

        except Exception as e:
            print(f"Database error in save_password_token: {e}")
            self.conn.rollback()
            return False
    
    # def execute_query(self, query, params=()):
    #     # Create a fresh connection for this specific write
    #     conn = sqlite3.connect(self.db_path)
    #     try:
    #         # Enable WAL mode for this connection specifically
    #         conn.execute("PRAGMA journal_mode=WAL;")
    #         cursor = conn.cursor()
    #         cursor.execute(query, params)
    #         conn.commit()  # This is the physical save to the disk
    #         logger.info(f"execute_query: SQL Executed: {query} | Rows affected: {cursor.rowcount}")
    #     except Exception as e:
    #         logger.error(f"Database Error during execute_query: {e}")
    #         conn.rollback()
    #     finally:
    #         conn.close()

    def fetch_one(self, query, params=()):
        """Handles fetching a single row"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            logger.info(f"fetch_one: SQL Executed: {query} | Rows affected: {cursor.rowcount}")
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"Database Error during fetch_one: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def set_employee_password(self, employee_id, new_password):
        """Updates password and returns number of rows affected."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE employee_passwords 
                SET Password = ?, Date_Updated = CURRENT_TIMESTAMP 
                WHERE employee_id = ?""",
                (new_password, employee_id)
            )
            conn.commit()
            logger.info(f"set_employee_password: Password update: {cursor.rowcount} row(s) affected for employee_id={employee_id}")
            return cursor.rowcount  # 0 means the employee_id row doesn't exist!
        except Exception as e:
            logger.error(f"Database Error during set_employee_password: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()    

    def set_employee_password_token (self, employee_id):
        """Updates password token and returns number of rows affected."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE employee_passwords 
                SET Password_Token = NULL, Date_Updated = CURRENT_TIMESTAMP 
                WHERE employee_id = ?""",
                (employee_id,)
            )
            conn.commit()
            logger.info(f"set_employee_password_token: Password token cleared: {cursor.rowcount} row(s) affected for employee_id={employee_id}") 
            return cursor.rowcount  # 0 means the employee_id row doesn't exist!
        except Exception as e:
            logger.error(f"Database Error during set_employee_password_token: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def dispatch_alert_event(self, event_type, employee_name, performed_by="System"):
        # Using 'with' here ensures the connection is closed even if the code crashes
        with sqlite3.connect(self.db_path, timeout=10) as conn:
            # 'timeout=10' tells SQLite to wait up to 10 seconds if another user 
            # is currently writing, instead of crashing immediately.
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            
            try:
                # 1. Fetch templates
                query_find = f"SELECT Alert_Name, Alert_Code, Alert_Type, Alert_Description FROM Alert_Items WHERE {event_type} = 1"
                cursor.execute(query_find)
                alerts = cursor.fetchall()

                if not alerts:
                    return

                # 2. Batch Insert (Highly efficient for multiple users)
                insert_query = """
                    INSERT INTO Alert_Dashboard_Items (
                        Alert_Name, Alert_Code, Alert_Type, Alert_Description, 
                        Alert_Trigger_Date, Alert_Status, Created_By, Date_Created
                    ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 'Pending', ?, CURRENT_TIMESTAMP)
                """
                
                # Prepare all data first
                payload = []
                for a in alerts:
                    desc = f"{a[3]} - Employee {employee_name} was {event_type.split('_')[-1].lower()}."
                    payload.append((a[0], a[1], a[2], desc, performed_by))

                # executemany is much faster for enterprise loads than a loop
                cursor.executemany(insert_query, payload)
                
                # No need for conn.commit() inside 'with sqlite3.connect' - it's automatic!
                
            except Exception as e:
                logger.error(f"Database Error during dispatch_alert_event: Critical Transaction Failure for {event_type}: {e}")
                conn.rollback()

    def fetch_all(self, query, params=()):
        """Handles fetching all rows for a query"""
        conn = sqlite3.connect(self.db_path)
        try:
            # This allows you to access columns by name like row['Alert_Name']
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            conn.close()

    def verify_login(self, username, password):

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT COALESCE(a.Role, 'employee'), e.Username
                FROM employees e
                LEFT JOIN employee_passwords p ON e.employee_id = p.employee_id
                LEFT JOIN account_access a ON e.employee_id = a.Employee_id
                WHERE e.Username = ? AND p.Password = ?
            """

            cursor.execute(query, (username, password))
            result = cursor.fetchone() # This actually gets the data
            if result:
                # result will be something like ('admin', 'magatjo')
                logger.info(f"Login successful for: {result[1]}")
                return result 
        
            logger.warning(f"Login failed for: {username}")

            return None

        # # Note: In a production app, you would use werkzeug.security.check_password_hash

        # print(f"Executing login query for user: '{username}', query: {query}")  # Debug statement before executing the query
        # result = self.execute_query(query, (username, password))

        
        # if result:
        #     print(f"Login successful for user: {result[0][1]} with role: {result[0][0]}")  # Debug statement
        #     return result[0]  # Returns e.g., ('admin', 'JohnDoe') or ('employee', 'JaneDoe')
        # return None
    
    def create_account_access_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS account_access (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Employee_id INTEGER NOT NULL,
            Role TEXT NOT NULL,
            Created_By TEXT,
            Date_Created DATETIME DEFAULT CURRENT_TIMESTAMP,
            Updated_By TEXT,
            Date_Updated DATETIME,
            FOREIGN KEY (Employee_id) REFERENCES Employees(Employee_id)
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def update_employee_profile(self, username, new_nickname, new_age, new_gender, new_address, new_telephone, new_cellphone, new_education):
        query = "UPDATE employees SET Nick_Name = ?, Age = ?, Gender = ?, Address = ?, Telephone = ?, Cellphone = ?, Education = ? WHERE Username = ?"
        try:
            # Reusing your existing connection logic
            self.cursor.execute(query, (new_nickname, new_age, new_gender, new_address, new_telephone, new_cellphone, new_education, username))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Update Error: {e}")
            return False
        
    def create_training_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS Trainings (
            training_id INTEGER PRIMARY KEY AUTOINCREMENT,
            training_name TEXT UNIQUE NOT NULL,
            training_description TEXT NOT NULL,
            training_type TEXT NOT NULL,
            training_duration INTEGER NOT NULL,
            training_provider TEXT NOT NULL,
            training_contact_name TEXT NOT NULL,
            training_contact_email TEXT NOT NULL,
            training_resources TEXT,
            group_requirement TEXT,
            Created_By TEXT,
            Date_Created TEXT,
            Updated_By TEXT,
            Date_Updated TEXT
        )
        """
        self.cursor.execute(query)
        self.conn.commit()


    def create_employee_trainings_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS Employee_Trainings (
            employee_id INTEGER NOT NULL,
            training_id INTEGER NOT NULL,
            required BOOLEAN DEFAULT 1,
            required_by_date DATETIME,
            completion_status TEXT DEFAULT 'Not Started',
            completion_date DATETIME,
            percentage_completed INTEGER DEFAULT 0,
            assigned_by TEXT,
            approved_by TEXT,
            Created_By TEXT,
            Date_Created TEXT,
            Updated_By TEXT,
            Date_Updated TEXT,
            PRIMARY KEY (employee_id, training_id),
            FOREIGN KEY (employee_id) REFERENCES Employees(Employee_id),
            FOREIGN KEY (training_id) REFERENCES Trainings(training_id)

            
        )
        """
        self.cursor.execute(query)
        self.conn.commit()


    def get_all_training_items(self):
        query = """
            SELECT 
                training_id, training_name, training_description, 
                training_type, training_duration, training_provider,
                group_requirement, training_resources, created_by, 
                training_contact_name, training_contact_email
            FROM Trainings
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database Error: {e}")
            return []
    
    def get_employee_training_items(self, employee_id=None, training_id=None):
        query = """
            SELECT 
                ET.employee_id, TR.training_id, ET.required,
                ET.required_by_date,  ET.completion_status,  ET.completion_date,
                ET.percentage_completed, ET.assigned_by, ET.approved_by, TR.training_description, TR.training_name,
                TR.Training_resources
            FROM Employee_Trainings ET LEFT JOIN Trainings TR
            ON ET.training_id = TR.training_id
        """ 

        if employee_id:
            query += " WHERE ET.employee_id = ?"
        if training_id:
            query += " WHERE ET.training_id = ?"
        if training_id and employee_id:
            query += " WHERE ET.employee_id = ? AND ET.training_id = ?"
            
        try:
            if employee_id and training_id:
                self.cursor.execute(query, (employee_id, training_id))
            elif employee_id:
                self.cursor.execute(query, (employee_id,))
            elif training_id:
                self.cursor.execute(query, (training_id,))
            else:
                self.cursor.execute(query)

            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database Error: {e}")
            return []
    
    def get_employee_trainings_by_id(self, training_id):
        query = """
            SELECT 
                ET.employee_id, TR.training_id, ET.required,
                ET.required_by_date,  ET.completion_status,  ET.completion_date,
                ET.percentage_completed, ET.assigned_by, ET.approved_by, TR.training_description, TR.training_name
            FROM Employee_Trainings ET LEFT JOIN Trainings TR
            ON ET.training_id = TR.training_id
            WHERE TR.training_id = ?
        """
        try:
            self.cursor.execute(query, (training_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database Error: {e}")
            return []

    def add_training(self, name, desc, t_type, duration, provider, contact_name, contact_email, resources, group, created_by):
        try:
            query = """
                INSERT INTO Trainings (
                    training_name, training_description, training_type, 
                    training_duration, training_provider, training_contact_name, 
                    training_contact_email, training_resources, group_requirement, 
                    Created_By, Date_Created
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(query, (
                name, desc, t_type, duration, provider, 
                contact_name, contact_email, resources, group, 
                created_by, date_now
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding training: {e}")
            return False
        
    def add_employee_training(self, employee_id, training_id, required, required_by_date, assigned_by):
        print(f"Adding employee training: emp_id={employee_id}, training_id={training_id}, required={required}, required_by_date={required_by_date}, assigned_by={assigned_by}")  # Debug statement
        try:
            query = """
                INSERT INTO Employee_Trainings (
                    employee_id, training_id, required, required_by_date, assigned_by
                ) VALUES (?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (
                employee_id, training_id, required, required_by_date, assigned_by
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding employee training: {e}")
            return False
            self.cursor.execute(query, (
                name, desc, t_type, duration, provider, 
                contact_name, contact_email, resources, group, 
                created_by, date_now
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding training: {e}")
            return False

    def update_training(self, t_id, name, desc, t_type, duration, provider, resources, group, updated_by, contact_name, contact_email):
        try:
            query = """
                UPDATE Trainings SET 
                    training_name = ?, training_description = ?, training_type = ?, 
                    training_duration = ?, training_provider = ?, training_resources = ?, 
                    group_requirement = ?, Updated_By = ?, Date_Updated = ?, training_contact_name = ?, training_contact_email = ?
                WHERE training_id = ?
            """
            date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(query, (
                name, desc, t_type, duration, provider, resources, group, 
                updated_by, date_now, contact_name, contact_email, t_id
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Update Error: {e}")
            return False
        
    def update_employee_training(self, employee_id, training_id, required, required_by_date, assigned_by):
        try:
            query = """
                UPDATE Employee_Trainings SET 
                    required = ?, required_by_date = ?, assigned_by = ?
                WHERE employee_id = ? AND training_id = ?
            """
            self.cursor.execute(query, (
                required, required_by_date, assigned_by, employee_id, training_id
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Update Error: {e}")
            return False

    def update_employee_training_status(self, employee_id, training_id, status, completion_date):
        print(f"Updating training status: emp_id={employee_id}, training_id={training_id}, status={status}, completion_date={completion_date}")  # Debug statement
        try:
            query = """
                UPDATE Employee_Trainings 
                SET completion_status = ?, completion_date = ?
                WHERE employee_id = ? AND training_id = ?
            """
          
            self.cursor.execute(query, (status, completion_date, employee_id, training_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Update Error: {e}")
            return False
        

    def create_leave_planning_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS LEAVE_PLANNING (
            leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            leave_start_date TEXT NOT NULL,
            leave_end_date TEXT NOT NULL,
            leave_reason TEXT,
            leave_status TEXT DEFAULT 'Pending',
            leave_approved_by TEXT,
            leave_approved_date TEXT,
            Created_By TEXT,
            Date_Created DATETIME DEFAULT CURRENT_TIMESTAMP,
            Updated_By TEXT,
            Date_Updated DATETIME,
        )
        """
        self.cursor.execute(query)
        self.conn.commit()