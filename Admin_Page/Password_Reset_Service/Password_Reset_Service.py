import sqlite3
from flask import Flask, request, render_template
import datetime, timedelta, hashlib, os, secrets, smtplib, ssl, email.message, re

app = Flask(__name__)


def is_expired(expiry_time):
    return datetime.datetime.now() > datetime.datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S")

@app.route('/set-password/<token>', methods=['GET', 'POST'])
def set_password_page():
    conn = sqlite3.connect("onboarding.db")
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM Password_Resets WHERE token = ? AND expiry > datetime('now')", (token,))
    result = cursor.fetchone()

    if not result:
        return "<h1>Link Invalid or Expired</h1><p>Please contact IT support.</p>", 403

    email = result[0]

    # 3. Handle the form submission
    if request.method == 'POST':
        new_password = request.form.get('password')
        # In a real app, you would hash the password here (e.g., using werkzeug.security)
        
        # Update the employee's password
        cursor.execute("UPDATE employees SET password = ? WHERE Email = ?", (new_password, email))
        # Delete the token so it can't be used again
        cursor.execute("DELETE FROM Password_Resets WHERE token = ?", (token,))
        
        conn.commit()
        return "<h1>Success!</h1><p>Your password has been set. You can now log in.</p>"

    # 4. Show the actual HTML page
    return render_template('set_password.html')



    # token = request.args.get('token')
    
    # # Check if token exists in SQLite
    # user = db.query("SELECT * FROM Password_Resets WHERE Token = ?", (token,))
    
    # if user and not is_expired(user.expiry):
    #     # Show the HTML form to the user
    #     return render_template('password_form.html', token=token)
    # else:
    #     return "Link expired or invalid.", 403