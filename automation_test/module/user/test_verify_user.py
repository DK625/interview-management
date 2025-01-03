from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestVerifyUser:
    @classmethod
    def setup_class(cls):
        cls.case_verify_user_data = [
            {
                "input": {
                    "full_name": "Auto test *user9",
                    "email": "auto-test-9@gmail.com",
                    "username": "test09",
                    # "department": "Marketing",
                    # "role": "Manager",
                    "status": "Active",
                    "note": "note 9"
                },
                "validate": [
                    "Please select department", "Please enter role"
                ]
            },
            {
                "input": {
                    "full_name": "Auto test *user10",
                    "email": "auto-test-10@gmail.com",
                    # "username": "test010",
                    "department": "AF",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 10"
                },
                "validate": [
                    "Please enter username"
                ]
            }
        ]

        # Playwright setup
        playwright = sync_playwright().start()
        cls.browser = playwright.chromium.launch(headless=False)
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        try:
            cls.db_params = {
                "host": "103.56.158.135",
                "database": "interview_management",
                "user": "postgres",
                "password": "woskxn"
            }
            cls.conn = psycopg2.connect(**cls.db_params)
            cls.cursor = cls.conn.cursor(cursor_factory=RealDictCursor)
            print("PostgreSQL connection established")
        except (Exception, Error) as error:
            print(f"Error connecting to PostgreSQL: {error}")

    def login(self, username='admin', password='123123'):
        """Login to application"""
        self.page.goto("http://localhost:5173/login")
        self.page.fill("input[placeholder='Username']", username)
        self.page.fill("input[placeholder='Password']", password)
        self.page.click("button[type='submit']")

    def action_ui_verify_user(self, user):
        try:
            time.sleep(2)
            self.page.reload()
            self.page.click("a[href='/user']")
            
            self.page.click("text='Add User'")
            if ("department" in user):
                self.page.click(
                    "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
                self.page.click(f"div[title='{user['department']}']")
            if ("role" in user):
                self.page.click(
                    "form div.ant-form-item:has(> div label:text('Role')) .ant-select-selector")
                self.page.click(f"div[title='{user['role']}']")
            if ("full_name" in user):
                self.page.fill(
                    "input[placeholder='Enter full name']", user["full_name"])
            if ("email" in user):
                self.page.fill(
                    "input[placeholder='Enter email']", user["email"])
            if ("username" in user):
                self.page.fill(
                    "input[placeholder='Enter username']", user["username"])
            if ("status" in user):
                self.page.click(
                    f"div[data-testid='status-select']")
                self.page.click(f"div[title='{user['status']}']")
            if ("note" in user):
                self.page.fill(
                    "textarea[placeholder='Enter note']", user["note"])

            # Click submit
            self.page.click("button:text('Submit')")
            print(f"✓ Created user: {user['full_name']}")
        except Exception as e:
            print(f"❌ Test action create user {user['full_name']} failed: {e}")
            raise

    def verify_db_verify_user(self, user):
        time.sleep(2)
        try:
            for mes in user:
                locator = self.page.locator(
                    f"div.ant-form-item-explain-error:has-text('{mes}')")
                assert locator.count() > 0, \
                    f"không tìm thấy thông báo validate: {mes}"

            print(f"✓ Verified offer")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_verify_user(self):
        self.login()
        try:
            for case in self.case_verify_user_data:
                self.action_ui_verify_user(case['input'])
                self.verify_db_verify_user(case['validate'])

            print("\n🎉 All users create successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete user failed: {e}")
            raise

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            if cls.conn:
                cls.cursor.close()
                cls.conn.close()
                print("PostgreSQL connection closed")
        except Exception as e:
            print(f"❌ Cleanup error: {str(e)}")
        finally:
            cls.context.close()
            cls.browser.close()


if __name__ == "__main__":
    pytest.main([__file__])
