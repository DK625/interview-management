from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestCreateUser:
    @classmethod
    def setup_class(cls):
        cls.case_create_user_data = [
            {
                "input": {
                    "full_name": "Auto test *user1",
                    "email": "auto-test-1@gmail.com",
                    "username": "test01",
                    "department": "Marketing",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 1"
                }
            },
            {
                "input": {
                    "full_name": "Auto test *user2",
                    "email": "auto-test-2@gmail.com",
                    "username": "test02",
                    "department": "AF",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 2"
                }
            }
        ]
        cls.create_user_db_backup = []

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

    def action_ui_create_user(self, user):
        try:
            self.page.click("a[href='/user']")
            
            self.page.click("text='Add User'")
            self.page.click(
                "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
            self.page.click(f"div[title='{user['department']}']")
            self.page.click(
                "form div.ant-form-item:has(> div label:text('Role')) .ant-select-selector")
            self.page.click(f"div[title='{user['role']}']")
            # Fill full name
            self.page.fill(
                "input[placeholder='Enter full name']", user["full_name"])
            # Fill email
            self.page.fill(
                "input[placeholder='Enter email']", user["email"])
            # Fill username
            self.page.fill(
                "input[placeholder='Enter username']", user["username"])
            # Click status
            self.page.click(
                f"div[data-testid='status-select']")
            self.page.click(f"div[title='{user['status']}']")
            # Fill note
            self.page.fill(
                "textarea[placeholder='Enter note']", user["note"])
            # Click submit
            self.page.click("button:text('Submit')")
            print(f"✓ Created user: {user['full_name']}")
        except Exception as e:
            print(f"❌ Test action create user {user['full_name']} failed: {e}")
            raise

    def verify_db_create_user(self, user):
        time.sleep(2)
        try:
            query = """
                SELECT 
                    id,
                    full_name,
                    email,
                    department,
                    role,
                    note
                FROM public.user
                WHERE email = %s
                LIMIT 1
            """

            self.cursor.execute(query, (
                user["email"],
            ))
            result = self.cursor.fetchone()
            assert result is not None, f"User {user['full_name']} not found in database"
            self.create_user_db_backup.append(result['id'])
            assert result['full_name'] == user["full_name"], \
                f"Full name mismatch: {result['full_name']} != {user['full_name']}"
            assert result['email'] == user["email"], \
                f"Email mismatch: {result['email']} != {user['email']}"
            assert result['department'] == user["department"], \
                f"Department mismatch: {result['department']} != {user['department']}"
            assert result['role'] == user["role"], \
                f"Role mismatch: {result['role']} != {user['role']}"
            assert result['note'] == user["note"], \
                f"Note mismatch: {result['note']} != {user['note']}"

            print(f"✓ Verified user in database: {user['full_name']}")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_create_user(self):
        self.login()
        try:
            for case in self.case_create_user_data:
                user = case['input']
                self.action_ui_create_user(user)
                self.verify_db_create_user(user)

            print("\n🎉 All users create successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete user failed: {e}")
            raise

    @classmethod
    def backup_create_user(cls):
        try:
            ids = cls.create_user_db_backup
            placeholders = ', '.join(['%s'] * len(ids))
            delete_query = f"""
                DELETE FROM public.user
                WHERE id IN ({placeholders})
            """

            cls.cursor.execute(delete_query, tuple(ids))
            cls.conn.commit()
            print(f"✅ User {ids} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore user: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup()
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
