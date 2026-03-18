import sys
import os
import datetime
from tabnanny import check
from flask import Flask, request, render_template

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

from database_manager import DatabaseManager

app = Flask(__name__)
db_path = os.path.join(root_dir, "onboarding.db")
print(f"--- WEB PORTAL IS USING DATABASE AT: {os.path.abspath(db_path)} ---")
db = DatabaseManager(db_path)
# db_path = os.path.join(root_dir, "onboarding.db")
# db = DatabaseManager(db_path)

def is_expired(expiry_time):
    return datetime.datetime.now() > datetime.datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S")

@app.route('/')
def home():
    return "<h1>IT Portal</h1><p>The password reset system is active.</p>"

@app.route('/set-password/<token>', methods=['GET', 'POST'])
def set_password_page(token):
    # breakpoint()
    query = """
        SELECT employee_id
        FROM employee_passwords 
        WHERE Password_Token = ? AND Token_Expiry > datetime('now') 
    """
    result = db.fetch_one(query, (token,))

    if not result:
        return "<h1>Link Invalid or Expired</h1><p>Please contact IT support.</p>", 403

    # email = result[0]
    employee_id = result[0]
    print(f"Token valid for employee_id: {employee_id}")

    # 3. Handle the form submission
    if request.method == 'POST':
        new_password = request.form.get('password')

        # check = db.fetch_one("SELECT employee_id FROM employee_passwords WHERE employee_id = ?", (employee_id,))
  
        # if check == 0:
        #     print(f"WARNING: UPDATE affected 0 rows for employee_id={employee_id}. Row may not exist.")
        #     return "<h1>Error</h1><p>Password could not be saved. Please contact IT support.</p>", 500
        
        db.set_employee_password(employee_id, new_password)
        db.set_employee_password_token(employee_id)  # Clear the token and expiry after use

   
     

        # db.execute_query("UPDATE employee_passwords SET Password = ? WHERE employee_id = ?", (new_password, employee_id))

        # db.execute_query("UPDATE employee_passwords SET Password_Token = null WHERE employee_id = ?", (employee_id,))


        
        # print(f"Received new password for employee_id {employee_id}: {new_password}")

        # In a real app, you would hash the password here (e.g., using werkzeug.security)
        
        # Update the employee's password
        # db.execute_query("UPDATE employee_passwords SET Password = ? WHERE employee_id = ?", (new_password, employee_id))

        # db.execute_query("UPDATE employee_passwords SET Password_Token = null WHERE employee_id = ?", (employee_id,))



        # Delete the token so it can't be used again
        # db.execute_query("DELETE FROM employee_passwords WHERE password_token = ?", (token,))
        
        return "<h1>Success!</h1><p>Your password has been set. You can now log in.</p>"

    # 4. Show the actual HTML page
    return render_template('set_password.html')

if __name__ == '__main__':
    # debug=True allows the server to reload automatically when you save changes
    app.run(debug=True, port=5001)

    # token = request.args.get('token')
    
    # # Check if token exists in SQLite
    # user = db.query("SELECT * FROM Password_Resets WHERE Token = ?", (token,))
    
    # if user and not is_expired(user.expiry):
    #     # Show the HTML form to the user
    #     return render_template('password_form.html', token=token)
    # else:
    #     return "Link expired or invalid.", 403