import pytest
import os
from database_manager import DatabaseManager
from Admin_Page.Web_Portal.web_app import app as flask_app
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from database_manager import DatabaseManager

@pytest.fixture
def db():
    test_db_path = "test_onboarding.db"

    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            # This happens if a previous test crashed and didn't close the connection
            pass

    # This call to __init__ should trigger all your create_table methods
    db_manager = DatabaseManager(test_db_path)
    
    yield db_manager

    # 1. Manually close the connection established in __init__
    if hasattr(db_manager, 'conn'):
        db_manager.conn.close()
    
    # 2. Small delay (optional, but helps on slow HDDs)
    import time
    time.sleep(0.1)
    
    # 3. Cleanup
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass

@pytest.fixture
def client():
    # Setup Flask test client
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client