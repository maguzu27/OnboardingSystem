def test_dispatch_alert_creation(db):
    # 1. Setup: Add the RULE to the configuration table (Alert_Items)
    # This table HAS the 'Employee_Record_Created' column
    db.execute_query("""
        INSERT INTO Alert_Items (
            Alert_Name, 
            Alert_Code, 
            Alert_Type, 
            Alert_Description, 
            Employee_Record_Created
        ) VALUES (?, ?, ?, ?, ?)
    """, ('Setup Desk', 'IT01', 'Task', 'New Hire Desk Setup', 1))

    # 2. Action: Trigger the logic
    # This function scans Alert_Items and inserts into Alert_Dashboard_Items
    db.dispatch_alert_event("Employee_Record_Created", "John Doe")

    # 3. Verify: Now check the Dashboard
    results = db.fetch_all("SELECT * FROM Alert_Dashboard_Items WHERE Alert_Name = 'Setup Desk'")
    
    assert len(results) == 1