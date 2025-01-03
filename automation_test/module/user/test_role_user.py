from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestRoleUser:
    @classmethod
    def setup_class(cls):
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

    def verify_role(self):
        time.sleep(2)
        try:
            request = self.page.locator(
                f"a[href='/request']")
            assert request.count() == 0, \
                f"Phân quyền truy cập sai /request"
            
            offer = self.page.locator(
                f"a[href='/offer']")
            assert offer.count() == 0, \
                f"Phân quyền truy cập sai /offer"

            user = self.page.locator(
                f"a[href='/user']")
            assert user.count() == 0, \
                f"Phân quyền truy cập sai /user"
            
            print(f"✓ Verified role offer")
        except AssertionError as ae:
            print(f"❌ Verification role failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ verification error: {str(e)}")
            raise

    def test_role_user(self):
        self.login("linh.nv1", "123456")
        try:
            self.verify_role()
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
