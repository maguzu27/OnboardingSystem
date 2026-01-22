
import sqlite3

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("onboarding.db")
        self.cursor = self.conn.cursor()
        self.create_employees_table()
        self.create_employee_requirement_attach_table()

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
        

    def update_employee(self, username, ui_data):
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
                "Hired Status": "Employeement_Status"
                
            }

            sets = []
            params = {"target_user": username}
            
            for ui_key, value in ui_data.items():
                if ui_key in mapping:
                    db_column = mapping[ui_key]
                    sets.append(f"{db_column} = :{db_column}")
                    params[db_column] = value

            if not sets:
                return False

            # Build the dynamic SQL query
            query = f"UPDATE employees SET {', '.join(sets)}, Date_Updated = datetime('now', 'localtime') WHERE Username = :target_user"
            
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Update Error: {e}")
            return False