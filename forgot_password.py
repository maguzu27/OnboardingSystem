import sqlite3
import datetime
import secrets
import smtplib
import ssl
from email.message import EmailMessage
from xmlrpc import server
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Forgot Password")
        self.setFixedSize(320, 180)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        info_lbl = QLabel("Enter your registered email address to receive a password reset link:")
        info_lbl.setWordWrap(True)
        layout.addWidget(info_lbl)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g. employee@company.com")
        layout.addWidget(self.email_input)

        send_btn = QPushButton("Send Reset Link")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; padding: 8px;
                font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        send_btn.clicked.connect(self.send_reset_request)
        layout.addWidget(send_btn)

    def send_reset_request(self):
        email = self.email_input.text().strip()
        if not email or "@" not in email:
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
            return

        try:
            conn = sqlite3.connect("onboarding.db")
            cursor = conn.cursor()

            # # Ensure table exists
            # cursor.execute("""
            #     CREATE TABLE IF NOT EXISTS Password_Resets (
            #         email TEXT,
            #         token TEXT UNIQUE,
            #         expiry DATETIME
            #     )
            # """)

            cursor.execute("SELECT employee_id FROM employees WHERE Email = ?", (email,))
            user = cursor.fetchone()

            if user:
                token = secrets.token_urlsafe(32)
                expiry = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute("DELETE FROM password_resets WHERE email = ?", (email,))
                cursor.execute("INSERT INTO password_resets (email, token, expiry) VALUES (?, ?, ?)", 
                               (email, token, expiry))
                conn.commit()

                # Send direct email
                sender_email = "magatjohnpaul27@gmail.com"
                sender_password = "uyzc rtux idwo cdia"
                reset_link = f"http://127.0.0.1:5001/set-password/{token}"

                msg = EmailMessage()
                msg['Subject'] = "Password Reset Request"
                msg['From'] = sender_email
                msg['To'] = email
                msg.set_content(f"Click the link to reset your password:\n\n{reset_link}")

                context = ssl.create_default_context()
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls(context=context)
                    server.login(sender_email, sender_password)
                    server.send_message(msg)

            conn.close()

            QMessageBox.information(
                self, 
                "Reset Link Sent", 
                "If an account exists with that email, a password reset link has been sent to your inbox."
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send reset link: {e}")