from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestEditInterview:
    @classmethod
    def setup_class(cls):
        cls.case_edit_interview_data = [
            {
                "input": {
                    "title": "Auto test *interview-3",
                    "job_id": "Business Executive Intern-JOB21",
                    "candidate_id": "Auto test *data-interview3 (data-interview-3@gmail.com)",
                    "schedule_date": '2025-01-27',
                    "schedule_time_from": '21:47:04',
                    "schedule_time_to": '21:47:12',
                    "status": "Invited",
                    "location": "R003",
                    "note": "data 3"
                },
                "validate": {
                    "title": "change-Auto test *interview-3",
                    "job_id": "Fresher Warehouse Staff-JOB24",
                    "candidate_id": "tmp-Auto test *data-interview0 (tmp-data-interview-0@gmail.com)",
                    "schedule_date": '2025-01-27',
                    "schedule_time_from": '21:47:50',
                    "schedule_time_to": '21:50:12',
                    "status": "Invited",
                    "location": "change-R003",
                    "note": "change-data 3"
                },
            },
            {
                "input": {
                    "title": "Auto test *interview-4",
                    "job_id": "Fresher Warehouse Staff-JOB24",
                    "candidate_id": "Auto test *data-interview4 (data-interview-4@gmail.com)",
                    "schedule_date": '2025-01-29',
                    "schedule_time_from": '21:47:04',
                    "schedule_time_to": '21:47:12',
                    "status": "Invited",
                    "location": "R004",
                    "note": "data 4"
                },
                "validate": {
                    "title": "change-Auto test *interview-4",
                    "job_id": "Business Executive Intern-JOB21",
                    "candidate_id": "Auto test *data-interview3 (data-interview-3@gmail.com)",
                    "schedule_date": '2025-01-29',
                    "schedule_time_from": '21:47:04',
                    "schedule_time_to": '21:57:12',
                    "status": "Invited",
                    "location": "change-R004",
                    "note": "change-data 4"
                },
            }
        ]
        cls.edit_interview_db_backup = []
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

    def get_state_db_edit_interview(self, interview):
        """Lấy trạng thái người dùng từ cơ sở dữ liệu"""
        where_conditions = []
        values = []
        for key, value in interview.items():
            where_conditions.append(f"{key} = %s")
            values.append(value)

        query = """
            SELECT * 
            FROM public.interview_schedule 
            WHERE title = %s
            AND status = %s
            AND location = %s
            AND note = %s
        """

        self.cursor.execute(query, (
            (interview["title"], interview["status"],
             interview["location"], interview["note"])
        ))
        record = self.cursor.fetchone()

        if record:
            self.edit_interview_db_backup.append(record)
            return record['id']
        return None

    def action_ui_edit_interview(self, id, interview):
        try:
            self.page.click("a[href='/interview']")
            
            element = self.page.locator("span.ant-select-selection-item[title='10 / page']")
            if element.is_visible(): 
                self.page.click("span.ant-select-selection-item[title='10 / page']")
                self.page.click("div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid-edit='{id}']")
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

            # # Select Interviewers
            # self.page.click(
            #     "[data-testid='select-interview-interviewers']")
            # for interviewer in interview["interviewer_ids"]:
            #     self.page.click(f"div[title='{interviewer}']")
            # self.page.keyboard.press("Escape")

            # Set Schedule Date
            self.page.click("[data-testid='date-interview-schedule']")
            self.page.fill(
                "input[placeholder='Select date']", interview["schedule_date"])
            self.page.click("text='EDIT INTERVIEW SCHEDULE'")

            # Set Time Range
            self.page.click("[data-testid='time-interview-from']")
            self.page.fill("input[placeholder='Select time']",
                           interview["schedule_time_from"])
            self.page.click("text='OK'")
            self.page.click("[data-testid='time-interview-to']")
            self.page.fill("#layout-multiple-horizontal_schedule_time_from",
                           interview["schedule_time_to"], timeout=1000)
            self.page.click("text='EDIT INTERVIEW SCHEDULE'")

            # Fill Location and Note
            self.page.fill(
                "input[placeholder='Enter location']", interview["location"])
            self.page.fill(
                "input[placeholder='Enter note']", interview["note"])

            # Submit form
            self.page.click("button:text('Submit')")
            print(f"\n✓ edit interview: {interview['title']}")
        except Exception as e:
            print(
                f"❌ Test action edit interview {interview['title']} failed: {e}")
            raise

    def verify_db_edit_interview(self, id, interview):
        time.sleep(2)
        try:
            query = """
                SELECT 
                    title,
                    status,
                    location,
                    note
                FROM public.interview_schedule
                WHERE id = %s
                LIMIT 1
            """

            self.cursor.execute(query, (id,))
            result = self.cursor.fetchone()
            assert result is not None, f"Interview {interview['title']} not found in database"

            assert result['title'] == interview["title"], \
                f"title mismatch: {result['title']} != {interview['title']}"
            assert result['status'] == interview["status"], \
                f"status mismatch: {result['status']} != {interview['status']}"
            assert result['location'] == interview["location"], \
                f"location mismatch: {result['location']} != {interview['location']}"
            assert result['note'] == interview["note"], \
                f"note mismatch: {result['note']} != {interview['note']}"

            print(f"✓ Verified interview in database: {interview['title']}")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_edit_interview(self):
        self.login()
        try:
            for case in self.case_edit_interview_data:
                input_data = case['input']
                interview_id = self.get_state_db_edit_interview(input_data)
                self.action_ui_edit_interview(interview_id, case['validate'])
                self.verify_db_edit_interview(interview_id, case['validate'])

            print("\n🎉 All interviews edit successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete interview failed: {e}")
            raise

    @classmethod
    def backup_edit_interview(cls):
        try:
            for interview in cls.edit_interview_db_backup:
                columns = ', '.join(interview.keys())
                values = tuple(interview.values())
                update_query = f"""
                    UPDATE public.interview_schedule
                    SET ({columns}) = ({', '.join(['%s'] * len(interview))})
                    WHERE id = %s
                """
                cls.cursor.execute(update_query, (*values, interview['id']))
                cls.conn.commit()

                print(f"✅ Interview {interview['id']} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore interview: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_edit_interview()
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
