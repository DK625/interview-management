from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error


class TestDeleteJob:
    @classmethod
    def setup_class(cls):
        cls.case_delete_job_data = [
            {
                "input": {
                    "title": "Auto test *job5",
                    "department": "IT",
                    "position": "Frontend Developer-RQ48",
                    "skills": ["react"],
                    "salary_from": "2000",
                    "salary_to": "4000",
                    "description": "description test 5"
                },
            },
            {
                "input": {
                    "title": "Auto test *job6",
                    "department": "AF",
                    "position": "Legal Manager-RQ18",
                    "skills": ["Node.js", "Python"],
                    "salary_from": "1000",
                    "salary_to": "2000",
                    "description": "description test 6"
                },
            }
        ]
        cls.delete_job_db_backup = []

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

    def get_state_db_delete_job(self, job):
        """Lấy trạng thái người dùng từ cơ sở dữ liệu"""
        where_conditions = []
        values = []
        for key, value in job.items():
            where_conditions.append(f"{key} = %s")
            values.append(value)

        query = f"SELECT * FROM public.job WHERE {' AND '.join(where_conditions)};"

        self.cursor.execute(query, tuple(values))
        record = self.cursor.fetchone()

        if record:
            self.job_db_backup.append(record)
            return record['id']
        return None

    def action_ui_delete_job(self, id):
        try:
            self.page.click("a[href='/job']")
            
            element = self.page.locator("span.ant-select-selection-item[title='10 / page']")
            if element.is_visible(): 
                self.page.click("span.ant-select-selection-item[title='10 / page']")
                self.page.click("div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid='{id}']")
            self.page.click(".ant-btn-primary.ant-btn-sm.ant-btn-dangerous")
        except Exception as e:
            print(f"❌ Test action delete job failed: {e}")
            raise

    def verify_db_delete_job(self, id):
        query = """
            SELECT
                deleted
            FROM public.job
            WHERE id = %s
        """
        self.cursor.execute(query, (id,))
        record = self.cursor.fetchone()

        assert str(record['deleted']) != None, \
            f"Xóa job {id} không thành công"

    def test_delete_job(self):
        self.login()
        try:
            for case in self.case_delete_job_data:
                input_data = case['input']
                job_id = self.get_state_db_delete_job(input_data)
                self.action_ui_delete_job(job_id)
                self.verify_db_delete_job(job_id)

            print("\n🎉 All jobs deleted successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete job failed: {e}")
            raise

    @classmethod
    def backup_delete_job(cls):
        try:
            for job in cls.job_db_backup:
                columns = ', '.join(job.keys())
                values = tuple(job.values())
                update_query = f"""
                    UPDATE public.job
                    SET ({columns}) = ({', '.join(['%s'] * len(job))})
                    WHERE id = %s
                """
                cls.cursor.execute(update_query, (*values, job['id']))
                cls.conn.commit()

                print(f"✅ Job {job['id']} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore job: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_delete_job()
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
