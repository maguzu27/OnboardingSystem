
import sqlite3
from tkinter.tix import TEXT

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("onboarding.db")
        self.cursor = self.conn.cursor()
        self.create_employees_table()
        self.create_employee_requirement_attach_table()
        self.create_requirements_setup_table()
        self.create_requirements_items_table()

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
            Job_title_Id INTEGER
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def create_employee_requirement_attach_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Requirement_Attachments (
                Attachment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
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
                Scan_Status TEXT                                   
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
        from datetime import datetime
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
        table = "Jobs" if table_type == "Jobs" else "Departments"
        pk = "job_title_id" if table_type == "Jobs" else "dept_id"
        try:
            self.cursor.execute(f"DELETE FROM {table} WHERE {pk} = ?", (record_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Delete Error: {e}")
            return False
        
    def add_attachment(self, file_path, file_name, original_name, username, file_size):
        try:
            # We must match the number of columns to the number of ? and the number of values
            query = """
                INSERT INTO Requirement_Attachments 
                (Employee_Name, File_path, File_name, Original_File_name, Created_By, Uploaded_By, File_Size, Scan_Status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
                "Clean"         # Scan_Status
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
                return True
            return False
        except Exception as e:
            print(f"Database Delete Error: {e}")
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
            self.cursor.execute("SELECT * FROM employees WHERE Username=?", (username,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching employee: {e}")
            return None
    
    def get_employee_attachment(self, username):
        try:
            # Using Username as the identifier for the file path
            self.cursor.execute("SELECT File_path FROM Requirement_Attachments WHERE employee_name=?", (username,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Attachment Error: {e}")
            return None
        
    def get_master_data(self, table_type):
        # Dynamic table selection (be careful with table_type sanitization)
        table_name = "Jobs" if table_type == "Jobs" else "Departments"
        self.cursor.execute(f"SELECT * FROM {table_name}")
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