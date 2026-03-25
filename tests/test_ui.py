from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# from tests.conftest import db

def test_password_set_ui(db):
    
    test_token = "valid-ui-test-token"
    expiry = "2099-01-01 00:00:00" # Far in the future
    
    # Ensure a row exists to update, or insert a fresh one
    db.execute_query("""
        INSERT INTO employee_passwords (employee_id, Password_Token, Token_Expiry) 
        VALUES (999, ?, ?)
    """, (test_token, expiry))

    # 1. Start the Browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        # 2. Navigate to your local portal (Ensure Flask is running!)
        driver.get("http://127.0.0.1:5001/set-password/YOUR_TEST_TOKEN")
        
        # 3. Find elements and type
        pass_input = driver.find_element(By.NAME, "password")
        confirm_input = driver.find_element(By.NAME, "confirm_password")
        submit_btn = driver.find_element(By.TAG_NAME, "button")
        
        pass_input.send_keys("SecurePass123!")
        confirm_input.send_keys("SecurePass123!")
        submit_btn.click()
        
        # 4. Verify the success message appears on screen
        time.sleep(1) # Wait for page load
        assert "Success!" in driver.page_source
        
    finally:
        driver.quit()