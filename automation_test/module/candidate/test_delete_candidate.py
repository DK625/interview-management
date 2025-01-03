from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error


class TestDeleteCandidate:
    @classmethod
    def setup_class(cls):
        cls.case_candidate_data = [
            {
                "input": {
                    "full_name": "Auto test *user5",
                    "email": "auto-test-5@gmail.com",
                    "phone": "089623653",
                    "department": "IT",
                    "position": "Fullstack Developer",
                    "highest_level": "Master Degree",
                    "year_experience": "3",
                    "status": "Waiting for interview",
                    "note": "node test 5"
                }
            },
            {
                "input": {
                    "full_name": "Auto test *user6",
                    "email": "auto-test-6@gmail.com",
                    "phone": "089623663",
                    "department": "AF",
                    "position": "Cashier",
                    "highest_level": "Master Degree",
                    "year_experience": "3",
                    "status": "Waiting for interview",
                    "note": "node test 6"
                }
            }
        ]
        cls.candidate_db_backup = []

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

    def get_state_db(self, candidate):
        """Lấy trạng thái người dùng từ cơ sở dữ liệu"""
        where_conditions = []
        values = []
        for key, value in candidate.items():
            where_conditions.append(f"{key} = %s")
            values.append(value)

        query = f"SELECT * FROM public.candidate WHERE {' AND '.join(where_conditions)};"

        self.cursor.execute(query, tuple(values))
        record = self.cursor.fetchone()

        if record:
            self.candidate_db_backup.append(record)
            return record['id']
        return None

    def action_ui(self, id):
        try:
            self.page.click("a[href='/candidate']")
            self.page.click(f"[data-testid='{id}']")
            self.page.click(".ant-btn-primary.ant-btn-sm.ant-btn-dangerous")
        except Exception as e:
            print(f"❌ Test action delete candidate failed: {e}")
            raise

    def verify_db(self, id):
        query = """
            SELECT
                deleted
            FROM public.candidate
            WHERE id = %s
        """
        self.cursor.execute(query, (id,))
        record = self.cursor.fetchone()

        assert str(record['deleted']) != None, \
            f"Xóa candidate {id} không thành công"

    def test_delete_candidate(self):
        self.login()
        try:
            for case in self.case_candidate_data:
                input_data = case['input']
                candidate_id = self.get_state_db(input_data)
                self.action_ui(candidate_id)
                self.verify_db(candidate_id)

            print("\n🎉 All candidates deleted successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete candidate failed: {e}")
            raise

    @classmethod
    def backup(cls):
        try:
            for candidate in cls.candidate_db_backup:
                columns = ', '.join(candidate.keys())
                values = tuple(candidate.values())
                update_query = f"""
                    UPDATE public.candidate
                    SET ({columns}) = ({', '.join(['%s'] * len(candidate))})
                    WHERE id = %s
                """
                cls.cursor.execute(update_query, (*values, candidate['id']))
                cls.conn.commit()

                print(f"✅ Candidate {candidate['id']} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore candidate: {e}")

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
