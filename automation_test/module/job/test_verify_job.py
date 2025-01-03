from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestVerifyJob:
    @classmethod
    def setup_class(cls):
        cls.case_verify_job_data = [
            {
                "input": {
                    "title": "Auto test *job9",
                    # "department": "IT",
                    # "position": "Frontend Developer-RQ48",
                    # "skills": ["react"],
                    "salary_from": "2000",
                    "salary_to": "8000",
                    "description": "description test 9"
                },
                "validate": [
                    "Please select department", "Please enter position", "Please enter skill",
                    "Please enter start date", "Please enter end date", "Please select level",
                    "Please select status"
                ]
            },
            {
                "input": {
                    "title": "Auto test *job10",
                    "department": "HR",
                    "position": "Training Specialist-RQ12",
                    # "skills": ["react"],
                    # "salary_from": "2000",
                    # "salary_to": "6000",
                    "description": "description test 10"
                },
                "validate": [
                    "Please enter skill"
                ]
            },
        ]

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

    def action_ui_verify_job(self, job):
        try:
            time.sleep(2)
            self.page.reload()
            self.page.click("a[href='/job']")
            
            self.page.click("text='Add Job'")
            if ('title' in job):
                self.page.fill(
                    "input[placeholder='Enter job title']", job["title"])
            if ('department' in job):
                self.page.click(
                    "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
                self.page.click(f"div[title='{job['department']}']")
            if ('position' in job):
                self.page.click("[data-testid='select-job-position']")
                self.page.click(f"div[title='{job['position']}']")
            if ('skills' in job):
                for skill in job["skills"]:
                    self.page.click("[data-testid='select-job-skills']")
                    skills_input = "[data-testid='select-job-skills'] .ant-select-selection-search-input"
                    self.page.fill(skills_input, skill)
                    self.page.keyboard.press("Enter")
                    self.page.wait_for_timeout(500)
            if ('salary_from' in job):
                self.page.fill(
                    "form div.ant-form-item:has(> div label:text('Salary from')) input.ant-input-number-input",
                    job["salary_from"])
            if ('salary_to' in job):
                self.page.fill("form div.ant-form-item:has(> div label:text('Salary to')) input.ant-input-number-input",
                               job["salary_to"])
            if ('description' in job):
                self.page.fill("form div.ant-form-item:has(> div label:text('Description')) input",
                               job["description"])

            # Submit form
            self.page.click("button:text('Submit')")
            print(f"\n✓ verify job: {id}")
        except Exception as e:
            print(
                f"❌ Test action verify job {id} failed: {e}")
            raise

    def verify_db_verify_job(self, job):
        time.sleep(2)
        try:
            for mes in job:
                locator = self.page.locator(
                    f"div.ant-form-item-explain-error:has-text('{mes}')")
                assert locator.count() > 0, \
                    f"không tìm thấy thông báo validate: {mes}"

            print(f"✓ Verified job")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_verify_job(self):
        self.login()
        try:
            for case in self.case_verify_job_data:
                self.action_ui_verify_job(case['input'])
                self.verify_db_verify_job(case['validate'])

            print("\n🎉 All jobs verify successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test verify job failed: {e}")
            raise

    @classmethod
    def backup_verify_job(cls):
        try:
            print(f"✅ Job restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore job: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_verify_job()
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
