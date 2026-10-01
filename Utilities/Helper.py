import secrets
import datetime
import sqlite3
import token

class HelperClass():
    """Dialog to perform bulk editing on selected employees."""
    def __init__(self, db):
        super().__init__()
        self.db = db
     
    def generate_onboarding_token(self, email, username):
        try:
            conn = sqlite3.connect("onboarding.db")
            cursor = conn.cursor()

            token = secrets.token_urlsafe(32)
            expiry = datetime.datetime.now() + datetime.timedelta(hours=24)

            cursor.execute("DELETE FROM password_resets WHERE email = ?", (email,))
            cursor.execute("INSERT INTO password_resets (email, token, expiry) VALUES (?, ?, ?)",(email, token, expiry))
            conn.commit()

            reset_link = f"http://127.0.0.1:5001/set-password/{token}"

            return reset_link

        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None