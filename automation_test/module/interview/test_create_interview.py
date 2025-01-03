from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestCreateInterview:
    @classmethod
    def setup_class(cls):
        cls.case_create_interview_data = [
            {
                "input": {
                    "title": "Auto test *interview-1",
                    "job_id": "Business Executive Intern-JOB21",
                    "candidate_id": "Auto test *data-interview1 (data-interview-1@gmail.com)",
                    "interviewer_ids": ["marketingmanager"],
                    "schedule_date": '2025-03-02',
                    "schedule_time_from": '21:16:33',
                    "schedule_time_to": '21:16:38',
                    "status": "Invited",
                    "location": "R001",
                    "note": "node test 1"
                },
            },
            {
                "input": {
                    "title": "Auto test *interview-2",
                    "job_id": "Business Executive Intern-JOB21",
                    "candidate_id": "Auto test *data-interview2 (data-interview-2@gmail.com)",
                    "interviewer_ids": ["test08"],
                    "schedule_date": '2025-03-02',
                    "schedule_time_from": '21:16:33',
                    "schedule_time_to": '21:16:38',
                    "status": "Invited",
                    "location": "R002",
                    "note": "node test 2"
                },
            }
        ]
        cls.create_interview_db_backup = []

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

    def action_ui_create_interview(self, interview):
        try:
            self.page.click("a[href='/interview']")
            
            self.page.click("text='Add Interview'")
            self.page.fill(
                "input[placeholder='Enter interview title']", interview["title"])

            # Select Job
            self.page.click("[data-testid='select-interview-job']")
            self.page.click(
                f"div[title='{interview['job_id']}']", timeout=2000)

            # Select Candidate
            self.page.click("[data-testid='select-interview-candidate']")
            self.page.click(
                f"div[title^='{interview['candidate_id']}']")

            # Select Interviewers
            self.page.click(
                "[data-testid='select-interview-interviewers']")
            for interviewer in interview["interviewer_ids"]:
                self.page.click(f"div[title='{interviewer}']")
            self.page.keyboard.press("Escape")

            # Set Schedule Date
            self.page.click("[data-testid='date-interview-schedule']")
            self.page.fill(
                "input[placeholder='Select date']", interview["schedule_date"])
            self.page.click("text='ADD INTERVIEW SCHEDULE'")

            # Set Time Range
            self.page.click("[data-testid='time-interview-from']")
            self.page.fill("input[placeholder='Select time']",
                           interview["schedule_time_from"])
            self.page.click("text='OK'")
            self.page.click("[data-testid='time-interview-to']")
            self.page.fill("#layout-multiple-horizontal_schedule_time_from",
                           interview["schedule_time_to"], timeout=1000)
            self.page.click("text='ADD INTERVIEW SCHEDULE'")

            # Fill Location and Note
            self.page.fill(
                "input[placeholder='Enter location']", interview["location"])
            self.page.fill(
                "input[placeholder='Enter note']", interview["note"])

            # Submit form
            self.page.click("button:text('Submit')")
            print(f"\n✓ Created interview: {interview['title']}")
        except Exception as e:
            print(
                f"❌ Test action create interview {interview['title']} failed: {e}")
            raise

    def verify_db_create_interview(self, interview):
        time.sleep(2)
        try:
            query = """
                SELECT 
                    id,
                    title,
                    schedule_date,
                    schedule_time_from,
                    schedule_time_to,
                    location,
                    note
                FROM public.interview_schedule
                WHERE title = %s
                AND location = %s
                AND note = %s
                LIMIT 1
            """

            self.cursor.execute(query, (
                interview["title"],
                interview["location"],
                interview["note"]
            ))
            result = self.cursor.fetchone()
            assert result is not None, f"Interview {interview['title']} not found in database"

            self.create_interview_db_backup.append(result['id'])

            assert result['title'] == interview["title"], \
                f"title mismatch: {result['title']} != {interview['title']}"
            assert result['location'] == interview["location"], \
                f"location mismatch: {result['location']} != {interview['location']}"
            assert result['note'] == interview["note"], \
                f"note mismatch: {result['note']} != {interview['note']}"

            print(f"✓ Verified interview in database: {interview['title']}")

        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_create_interview(self):
        self.login()
        try:
            for case in self.case_create_interview_data:
                interview = case['input']
                self.action_ui_create_interview(interview)
                self.verify_db_create_interview(interview)

            print("\n🎉 All interviews create successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete interview failed: {e}")
            raise

    @classmethod
    def backup_create_interview(cls):
        try:
            ids = cls.create_interview_db_backup
            placeholders = ', '.join(['%s'] * len(ids))
            delete_query = f"""
                DELETE FROM public.interview_schedule
                WHERE id IN ({placeholders})
            """

            cls.cursor.execute(delete_query, tuple(ids))
            cls.conn.commit()
            print(f"✅ Interview {ids} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore interview: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_create_interview()
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
