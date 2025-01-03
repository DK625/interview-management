from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestVerifyInterview:
    @classmethod
    def setup_class(cls):
        cls.case_verify_interview_data = [
            {
                "input": {
                    "title": "Auto test *interview-9",
                    "job_id": "Junior Manual Tester-JOB28",
                    "candidate_id": "Auto test *interview9 (auto-test-interview-9@gmail.com)",
                    "interviewer_ids": ["finaldemo"],
                    # "schedule_date": '2025-03-02',
                    # "schedule_time_from": '21:16:33',
                    # "schedule_time_to": '21:16:38',
                    "status": "Invited",
                    "location": "R001",
                    "note": "node 9"
                },
                "validate": [
                    "Please enter date", "Please enter time", "Please enter time"
                ]
            },
            {
                "input": {
                    "title": "Auto test *interview-9",
                    "job_id": "Junior Manual Tester-JOB28",
                    "candidate_id": "Auto test *interview9 (auto-test-interview-9@gmail.com)",
                    # "interviewer_ids": ["finaldemo"],
                    # "schedule_date": '2025-03-02',
                    # "schedule_time_from": '21:16:33',
                    # "schedule_time_to": '21:16:38',
                    "status": "Invited",
                    "location": "R001",
                    "note": "node 9"
                },
                "validate": [
                    "Please enter interviews", "Please enter date", "Please enter time", "Please enter time"
                ]
            },
        ]
        cls.verify_interview_db_backup = []
        cls.candidate_db_backup = []

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

    def action_ui_verify_interview(self, interview):
        try:
            time.sleep(2)
            self.page.reload()
            self.page.click("a[href='/interview']")
            
            self.page.click("text='Add Interview'")
            if ('title' in interview):
                self.page.fill(
                    "input[placeholder='Enter interview title']", interview["title"])
            if ('job_id' in interview):
                # Select Job
                self.page.click("[data-testid='select-interview-job']")
                self.page.click(
                    f"div[title='{interview['job_id']}']", timeout=2000)
            if ('candidate_id' in interview):
                # Select Candidate
                self.page.click("[data-testid='select-interview-candidate']")
                self.page.click(
                    f"div[title^='{interview['candidate_id']}']")
            if ('interviewer_ids' in interview):
                # Select Interviewers
                self.page.click(
                    "[data-testid='select-interview-interviewers']")
                for interviewer in interview["interviewer_ids"]:
                    self.page.click(f"div[title='{interviewer}']")
                self.page.keyboard.press("Escape")
            if ('schedule_date' in interview):
                # Set Schedule Date
                self.page.click("[data-testid='date-interview-schedule']")
                self.page.fill(
                    "input[placeholder='Select date']", interview["schedule_date"])
                self.page.click("text='ADD INTERVIEW SCHEDULE'")
            if ('schedule_time_from' in interview):
                # Set Time Range
                self.page.click("[data-testid='time-interview-from']")
                self.page.fill("input[placeholder='Select time']",
                               interview["schedule_time_from"])
                self.page.click("text='OK'")
            if ('schedule_time_to' in interview):
                self.page.click("[data-testid='time-interview-to']")
                self.page.fill("#layout-multiple-horizontal_schedule_time_from",
                               interview["schedule_time_to"], timeout=1000)
                self.page.click("text='ADD INTERVIEW SCHEDULE'")
            if ('location' in interview):
                # Fill Location and Note
                self.page.fill(
                    "input[placeholder='Enter location']", interview["location"])
            if ('note' in interview):
                self.page.fill(
                    "input[placeholder='Enter note']", interview["note"])
            # Submit form
            self.page.click("button:text('Submit')")
            print(f"\n✓ verify interview: {id}")
        except Exception as e:
            print(
                f"❌ Test action verify interview {id} failed: {e}")
            raise

    def verify_db_verify_interview(self, interview):
        time.sleep(2)
        try:
            for mes in interview:
                locator = self.page.locator(
                    f"div.ant-form-item-explain-error:has-text('{mes}')")
                assert locator.count() > 0, \
                    f"không tìm thấy thông báo validate: {mes}"

            print(f"✓ Verified interview")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_verify_interview(self):
        interview_id = None
        self.login()
        try:
            for case in self.case_verify_interview_data:
                self.action_ui_verify_interview(case['input'])
                self.verify_db_verify_interview(case['validate'])

            print("\n🎉 All interviews verify successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test verify interview failed: {e}")
            raise

    @classmethod
    def backup_verify_interview(cls):
        try:
            print(f"✅ Interview restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore interview: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_verify_interview()
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
