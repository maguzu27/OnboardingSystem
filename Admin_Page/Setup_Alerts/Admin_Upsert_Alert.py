from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QCheckBox, QGroupBox, QPushButton, QFormLayout, 
                             QFrame, QInputDialog, QMessageBox, QScrollArea, QWidget)
from PyQt5.QtCore import Qt

class AlertEntryDialog(QDialog):
    # def __init__(self, db, current_user, parent=None):
            # dialog = AlertEntryDialog(self, self.db, self.current_user, title="Edit Alert", data=full_data)
    def __init__(self, db, current_user, parent=None, title=None, data=None):
        super().__init__(parent)
        self.db = db
        self.current_user = current_user
        self.edit_data = data
        self.setWindowTitle(title)
        self.resize(850, 800)
        self.init_ui()

        if self.edit_data:
            self.pre_fill_data()

    def pre_fill_data(self):
        """Maps row data from the database/table to the UI fields"""
        # Assuming your 'data' is the row from the database
        self.alert_name_input.setText(str(self.edit_data[1])) # Alert Name
        
        # Example: Mapping Attributes (assuming attrs start at a specific index)
        # You'll need to adjust index [14+] based on your SQL table structure
        attr_index = 14 
        for i in range(1, 6):
            if attr_index < len(self.edit_data):
                self.attr_inputs[i][0].setText(str(self.edit_data[attr_index]))   # Value
                self.attr_inputs[i][1].setText(str(self.edit_data[attr_index+1])) # Condition
                attr_index += 2

        # Mapping Notify By
        self.email_input.setText(str(self.edit_data[9]))
        self.username_input.setText(str(self.edit_data[10]))
        self.chk_attach.setChecked(bool(self.edit_data[11]))
        self.chk_details.setChecked(bool(self.edit_data[12]))
        self.chk_home_notif.setChecked(bool(self.edit_data[13]))
        
        # Set Button text to Update instead of Create
        self.save_btn.setText("Update Alert")

        days_val = self.edit_data[7]
        due_today_val = bool(self.edit_data[8])

        # If either 'days' or 'due today' was set, the master checkbox must be checked
        if days_val > 0 or due_today_val:
            self.chk_due_date.setChecked(True)
            # This will automatically trigger the toggle and enable chk_due_today
            
        if days_val > 0:
            self.chk_days_trigger.setChecked(True)
            self.days_input.setText(str(days_val))
        else:
            self.days_input.setText("0")
            
        self.chk_due_today.setChecked(due_today_val)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- Alert Name Header ---
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>Alert Name:</b>"))
        self.alert_name_input = QLineEdit()
        self.alert_name_input.setPlaceholderText("Enter alert name here...")
        header_layout.addWidget(self.alert_name_input)
        main_layout.addLayout(header_layout)

        # Scroll Area for the content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        scroll_layout = QVBoxLayout(content_widget)

        # --- Section 1: Send Alert When (Triggers) ---
        trigger_group = QGroupBox("Send Alert When...")
        t_layout = QVBoxLayout()
        
        self.chk_created = QCheckBox("Employee Record Created")
        self.chk_deleted = QCheckBox("Employee Record Deleted")
        self.chk_updated = QCheckBox("Employee Record Updated")
        self.chk_job_upd = QCheckBox("Employee Updated a Job requirement")
        self.chk_train_upd = QCheckBox("Employee Finished a Training requirement")
        
        # Due Date Logic
        self.chk_due_date = QCheckBox("Job Requirement is Due date")
        self.chk_due_date.toggled.connect(self.toggle_due_date_logic)

        self.chk_due_today = QCheckBox("Job Requirement is Due today")
        self.chk_due_today.setEnabled(False)
        
        # Sub-option for Due Date
        # self.due_date_sub_frame = QFrame()
        # sub_layout = QHBoxLayout(self.due_date_sub_frame)
        # self.chk_days_trigger = QCheckBox("Due Date is Less than")
        # self.days_input = QLineEdit("3")
        # self.days_input.setFixedWidth(40)
        # sub_layout.addWidget(self.chk_days_trigger)
        # sub_layout.addWidget(self.days_input)
        # sub_layout.addWidget(QLabel("days from today"))
        # sub_layout.addStretch()
        # self.due_date_sub_frame.setVisible(False) # Hidden by default

        self.due_date_sub_frame = QFrame()
        sub_layout = QHBoxLayout(self.due_date_sub_frame)
        self.chk_days_trigger = QCheckBox("Due Date is Less than")
        self.days_input = QLineEdit("3")
        self.days_input.setFixedWidth(40)
        sub_layout.addWidget(self.chk_days_trigger)
        sub_layout.addWidget(self.days_input)
        sub_layout.addWidget(QLabel("days from today"))
        sub_layout.addStretch()
        self.due_date_sub_frame.setVisible(False)

        # --- THE LOGIC CONNECTIONS ---
        # 1. Show/Hide the "X Days" frame
        self.chk_due_date.toggled.connect(self.due_date_sub_frame.setVisible)
        # 2. Enable/Disable the "Due Today" checkbox
        self.chk_due_date.toggled.connect(self.chk_due_today.setEnabled)
        # 3. Optional: Uncheck "Due Today" if master is unchecked
        self.chk_due_date.toggled.connect(lambda checked: self.chk_due_today.setChecked(False) if not checked else None)

        
        # self.chk_due_date.toggled.connect(self.due_date_sub_frame.setVisible)

        for w in [self.chk_created, self.chk_deleted, self.chk_updated, 
                  self.chk_job_upd, self.chk_train_upd, self.chk_due_date, 
                  self.due_date_sub_frame, self.chk_due_today]:
            t_layout.addWidget(w)
        trigger_group.setLayout(t_layout)
        scroll_layout.addWidget(trigger_group)

        # --- Section 2: Specifically When (Filters/Attributes) ---
        filter_group = QGroupBox("Specifically when...")
        f_layout = QFormLayout()
        self.attr_inputs = {} # Store attribute fields
        
        for i in range(1, 6):
            h_box = QHBoxLayout()
            attr_val = QLineEdit()
            attr_val.setPlaceholderText(f"Value {i}")
            cond_val = QLineEdit()
            cond_val.setPlaceholderText("Condition (e.g. Equal, Includes)")
            h_box.addWidget(attr_val)
            h_box.addWidget(QLabel("Condition:"))
            h_box.addWidget(cond_val)
            f_layout.addRow(f"Attribute {i}:", h_box)
            self.attr_inputs[i] = (attr_val, cond_val)
            
        filter_group.setLayout(f_layout)
        scroll_layout.addWidget(filter_group)

        # --- Section 3: Notify By ---
        notify_group = QGroupBox("Notify by...")
        n_layout = QVBoxLayout()

        # Email Section
        n_layout.addWidget(QLabel("<b>1. by Email</b>"))
        
        # Email Input with Prompt Button
        email_h = QHBoxLayout()
        self.email_input = QLineEdit()
        btn_add_email = QPushButton("+")
        btn_add_email.setFixedWidth(30)
        btn_add_email.clicked.connect(self.prompt_email)
        email_h.addWidget(self.email_input)
        email_h.addWidget(btn_add_email)
        n_layout.addWidget(QLabel("   Email address"))
        n_layout.addLayout(email_h)

        # Username Input with Lookup Button
        user_h = QHBoxLayout()
        self.username_input = QLineEdit()
        btn_lookup_user = QPushButton("+")
        btn_lookup_user.setFixedWidth(30)
        btn_lookup_user.clicked.connect(self.prompt_user_lookup)
        user_h.addWidget(self.username_input)
        user_h.addWidget(btn_lookup_user)
        n_layout.addWidget(QLabel("   Username"))
        n_layout.addLayout(user_h)

        self.chk_attach = QCheckBox("Attach File in Email")
        self.chk_details = QCheckBox("Attach details in Email Body")
        n_layout.addWidget(self.chk_attach)
        n_layout.addWidget(self.chk_details)

        # System Notification
        n_layout.addWidget(QLabel("\n<b>2. by System Notification</b>"))
        self.chk_home_notif = QCheckBox("Show Notification from Home page")
        n_layout.addWidget(self.chk_home_notif)

        notify_group.setLayout(n_layout)
        scroll_layout.addWidget(notify_group)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Save/Cancel
        btns = QHBoxLayout()
        # save_btn = QPushButton("Create Alert")
        self.save_btn = QPushButton("Create Alert")
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        self.save_btn.clicked.connect(self.save_alert)
        btns.addStretch()
        btns.addWidget(self.save_btn)
        main_layout.addLayout(btns)

    def prompt_email(self):
        text, ok = QInputDialog.getText(self, "Add Email", "Enter manual email address:")
        if ok and text:
            current = self.email_input.text()
            self.email_input.setText(f"{current}; {text}" if current else text)

    def prompt_user_lookup(self):
        # 1. Get username from input dialog
        username, ok = QInputDialog.getText(self, "User Lookup", "Enter Username to fetch email:")
        if ok and username:
            # 2. Query your DB (adjust table/column names to match your schema)
            query = "SELECT Email FROM Employees WHERE Username = ?"
            result = self.db.execute_query(query, (username,))
            
            if result:
                found_email = result[0][0]
                self.username_input.setText(username)
                # Auto-fill email if found
                current_emails = self.email_input.text()
                self.email_input.setText(f"{current_emails}; {found_email}" if current_emails else found_email)
            else:
                QMessageBox.warning(self, "Not Found", f"No email found for user: {username}")

    def get_data(self):
        # Gather all attribute values and conditions into a flat list
        attrs = []
        for i in range(1, 6):
            val_input, cond_input = self.attr_inputs[i]
            attrs.extend([val_input.text(), cond_input.text()])
        # breakpoint()
        return {
            "Alert_Name": self.alert_name_input.text(),
            "Employee_Record_Created": self.chk_created.isChecked(),
            "Employee_Record_Deleted": self.chk_deleted.isChecked(),
            "Employee_Record_Updated": self.chk_updated.isChecked(),
            "Employee_Updated_JobRqrmt": self.chk_job_upd.isChecked(),
            "Employee_Updated_TrainingRqrmt": self.chk_train_upd.isChecked(),
            "JobRqrmt_Due_date_X_Days": int(self.days_input.text()) if self.chk_days_trigger.isChecked() else 0,
            "JobRqrmt_Due_date_Today": self.chk_due_today.isChecked(),
            "Alert_Email_Recipient": self.email_input.text(),
            "Alert_Username_Recipient": self.username_input.text(),
            "Attach_File": self.chk_attach.isChecked(),
            "Details_In_Body": self.chk_details.isChecked(),
            "App_Home_Notification": self.chk_home_notif.isChecked(),
            "attrs": attrs # List containing [Attr1, Cond1, Attr2, Cond2...]
        }
    
    def save_alert(self):

        data = self.get_data()
        row_id = self.edit_data[0] if self.edit_data else None

        sql_tuple = (
            data['Alert_Name'], 
            int(data['Employee_Record_Created']),
            int(data['Employee_Record_Deleted']),
            int(data['Employee_Record_Updated']),
            int(data['Employee_Updated_JobRqrmt']),
            int(data['Employee_Updated_TrainingRqrmt']),
            data['JobRqrmt_Due_date_X_Days'],
            int(data['JobRqrmt_Due_date_Today']),
            data['Alert_Email_Recipient'],
            data['Alert_Username_Recipient'],
            int(data['Attach_File']),
            int(data['Details_In_Body']),
            int(data['App_Home_Notification']),
            self.current_user
        ) 
        sql_tuple += tuple(data['attrs'])
        
        # + (
        #     data['Attribute_1'][1][0], data['Condition_1'][1][1], # Attr 1 & Cond 1
        #     data['Attribute_2'][2][0], data['Condition_2'][2][1], # Attr 2 & Cond 2
        #     data['Attribute_3'][3][0], data['Condition_3'][3][1], # Attr 3 & Cond 3
        #     data['Attribute_4'][4][0], data['Condition_4'][4][1], # Attr 4 & Cond 4
        #     data['Attribute_5'][5][0], data['Condition_5'][5][1]  # Attr 5 & Cond 5


        # ) 
        # + tuple(data['attrs']) # Append the flat list of attributes

        if not self.alert_name_input.text():
            QMessageBox.warning(self, "Error", "Alert Name is required!")
            return
        
        # data = self.get_data()
        # Convert bools to int as you did before...

        
        
        if self.edit_data:
            # LOGIC FOR UPDATE
            row_id = self.edit_data[0]

            if self.db.update_alert_item(row_id, sql_tuple): # You'll need to create this DB method
                self.accept()
        else:
            if self.db.add_alert_item(sql_tuple):
                self.accept()

    def toggle_due_date_logic(self, checked):
        # Set visibility and enabled state
        self.due_date_sub_frame.setVisible(checked)
        self.chk_due_today.setEnabled(checked)
        
        # If the master box is UNCHECKED, reset the values
        if not checked:
            self.chk_due_today.setChecked(False)
            self.chk_days_trigger.setChecked(False)
            self.days_input.setText("0") # Set to 0 as requested