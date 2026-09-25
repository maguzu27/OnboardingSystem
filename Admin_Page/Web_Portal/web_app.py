import sqlite3
import datetime
import hashlib
from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Locate the root onboarding.db file relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# If web_app.py is in Admin_Page/Web_Portal, navigate up to the root folder:
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "onboarding.db"))

@app.route('/set-password/<token>', methods=['GET', 'POST'])
def set_password_page(token):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
   
    # 1. Verify token exists and hasn't expired
    cursor.execute("""
        SELECT email FROM password_resets 
        WHERE token = ? AND expiry > datetime('now', 'localtime')
    """, (token,))

    result = cursor.fetchone()


    if not result:
        conn.close()
        return "<h1>Link Invalid or Expired</h1><p>Please request a new reset link from the app.</p>", 403

    email = result[0]

    # 2. Handle Form Submission (POST)
    if request.method == 'POST':
        new_password = request.form.get('password')

        # Hash the password to match your login system (SHA-256)
        hashed_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()

        # Update the user's password in the employees table
        cursor.execute("UPDATE employee_passwords SET Password = ? WHERE employee_id = (SELECT employee_id FROM employees WHERE Email = ?)", (hashed_password, email))

        # Delete the token so it cannot be re-used
        cursor.execute("DELETE FROM password_resets WHERE token = ?", (token,))

        conn.commit()
        conn.close()

        return "<h1>Success!</h1><p>Your password has been reset. You can now close this tab and log in using your PyQt desktop application.</p>"

    # 3. Render the Form (GET)
    conn.close()
    return render_template('set_password.html')

if __name__ == '__main__':
    # Runs the local web server on http://127.0.0.1:5001
    app.run(host='127.0.0.1', port=5001, debug=True)