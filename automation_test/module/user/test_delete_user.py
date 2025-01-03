from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error


class TestDeleteUser:
    @classmethod
    def setup_class(cls):
        cls.case_delete_user_data = [
            {
                "input": {
                    "full_name": "Auto test *user5",
                    "email": "auto-test-5@gmail.com",
                    "username": "test05",
                    "department": "Marketing",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 5"
                }
            },
            {
                "input": {
                    "full_name": "Auto test *user6",
                    "email": "auto-test-6@gmail.com",
                    "username": "test06",
                    "department": "AF",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 6"
                }
            }
        ]
        cls.delete_user_db_backup = []

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

    def get_state_db_delete_user(self, user):
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
            self.delete_user_db_backup.append(record)
            return record['id']
        return None

    def action_ui_delete_user(self, id):
        try:
            self.page.click("a[href='/user']")
            
            element = self.page.locator("span.ant-select-selection-item[title='10 / page']")
            if element.is_visible(): 
                self.page.click("span.ant-select-selection-item[title='10 / page']")
                self.page.click("div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid='{id}']")
            self.page.click(".ant-btn-primary.ant-btn-sm.ant-btn-dangerous")
        except Exception as e:
            print(f"❌ Test action delete user failed: {e}")
            raise

    def verify_db_delete_user(self, id):
        query = """
            SELECT
                deleted
            FROM public.user
            WHERE id = %s
        """
        self.cursor.execute(query, (id,))
        record = self.cursor.fetchone()

        assert str(record['deleted']) != None, \
            f"Xóa user {id} không thành công"

    def test_delete_user(self):
        self.login()
        try:
            for case in self.case_delete_user_data:
                input_data = case['input']
                user_id = self.get_state_db_delete_user(input_data)
                self.action_ui_delete_user(user_id)
                self.verify_db_delete_user(user_id)

            print("\n🎉 All users deleted successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete user failed: {e}")
            raise

    @classmethod
    def backup_delete_user(cls):
        try:
            for user in cls.delete_user_db_backup:
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
            cls.backup_delete_user()
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
