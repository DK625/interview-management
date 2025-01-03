from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestEditUser:
    @classmethod
    def setup_class(cls):
        cls.case_edit_user_data = [
            {
                "input": {
                    "full_name": "Auto test *user3",
                    "email": "auto-test-3@gmail.com",
                    "username": "test03",
                    "department": "Marketing",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 3"
                },
                "validate": {
                    "full_name": "change-Auto test *user3",
                    "email": "change-auto-test-3@gmail.com",
                    "username": "change-test03",
                    "department": "Marketing",
                    "role": "Manager",
                    "status": "Active",
                    "note": "change-note 3"
                }
            },
            {
                "input": {
                    "full_name": "Auto test *user4",
                    "email": "auto-test-4@gmail.com",
                    "username": "test04",
                    "department": "AF",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 4"
                },
                "validate": {
                    "full_name": "change-Auto test *user4",
                    "email": "change-auto-test-4@gmail.com",
                    "username": "change-test04",
                    "department": "AF",
                    "role": "Manager",
                    "status": "Active",
                    "note": "change-note 4"
                }
            }
        ]
        cls.edit_user_db_backup = []
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

    def get_state_db_edit_user(self, user):
        """Lấy trạng thái người dùng từ cơ sở dữ liệu"""
        where_conditions = []
        values = []
        for key, value in user.items():
            where_conditions.append(f"{key} = %s")
            values.append(value)

        query = f"SELECT * FROM public.user WHERE {' AND '.join(where_conditions)};"

        self.cursor.execute(query, tuple(values))
        record = self.cursor.fetchone()

        if record:
            self.edit_user_db_backup.append(record)
            return record['id']
        return None

    def action_ui_edit_user(self, id, user):
        try:
            self.page.click("a[href='/user']")
            
            element = self.page.locator("span.ant-select-selection-item[title='10 / page']")
            if element.is_visible(): 
                self.page.click("span.ant-select-selection-item[title='10 / page']")
                self.page.click("div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid-edit='{id}']")
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
            print(f"\n✓ edit user: {user['full_name']}")
        except Exception as e:
            print(f"❌ Test action edit user {user['full_name']} failed: {e}")
            raise

    def verify_db_edit_user(self, id, user):
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
                WHERE id = %s
                LIMIT 1
            """

            self.cursor.execute(query, (id,))
            result = self.cursor.fetchone()
            assert result is not None, f"User {user['full_name']} not found in database"
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

    def test_edit_user(self):
        self.login()
        try:
            for case in self.case_edit_user_data:
                input_data = case['input']
                user_id = self.get_state_db_edit_user(input_data)
                self.action_ui_edit_user(user_id, case['validate'])
                self.verify_db_edit_user(user_id, case['validate'])

            print("\n🎉 All users edit successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete user failed: {e}")
            raise

    @classmethod
    def backup_edit_user(cls):
        try:
            for user in cls.edit_user_db_backup:
                columns = ', '.join(user.keys())
                values = tuple(user.values())
                update_query = f"""
                    UPDATE public.user
                    SET ({columns}) = ({', '.join(['%s'] * len(user))})
                    WHERE id = %s
                """
                cls.cursor.execute(update_query, (*values, user['id']))
                cls.conn.commit()

                print(f"✅ User {user['id']} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore user: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_edit_user()
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
