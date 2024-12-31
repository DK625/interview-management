from playwright.sync_api import sync_playwright, expect
import time
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta


class TestInterview:
    @classmethod
    def setup_class(cls):
        """Setup test environment and database connection"""
        playwright = sync_playwright().start()
        cls.browser = playwright.chromium.launch(headless=False)
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        today = datetime.now()
        interview_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        time_from = "09:00:00"
        time_to = "10:00:00"

        interview_data = [
            {
                "title": "Automation Test Interview 1",
                "job_id": "Fresher Warehouse Staff-JOB24",  # Will need to select from dropdown
                # Will need to select from dropdown
                "candidate_id": "Nguyễn Đình Phúc (nguyendinhphuc.work@gmail.com)",
                # Will need to select from dropdown
                "interviewer_ids": ["purchasingmanager"],
                "schedule_date": interview_date,
                "schedule_time_from": time_from,
                "schedule_time_to": time_to,
                "status": "Invited",
                "location": "Meeting Room 1",
                "note": "Technical assessment and culture fit evaluation"
            },
            {
                "title": "Automation Test Interview 2",
                "job_id": "Business Executive Intern-JOB21",  # Will need to select from dropdown
                # Will need to select from dropdown
                "candidate_id": "Nguyễn Minh Thảo (vuminhthao39@gmail.com)",
                # Will need to select from dropdown
                "interviewer_ids": ["marketingmanager"],
                "schedule_date": interview_date,
                "schedule_time_from": time_from,
                "schedule_time_to": time_to,
                "status": "Invited",
                "location": "Meeting Room 2",
                "note": "Marketing strategy discussion"
            }
        ]

        cls.interview_data = interview_data
        cls.candidate_edited = []
        cls.interview_ids = []

        try:
            cls.db_params = {
                "host": "103.56.158.135",
                "database": "interview_management",
                "user": "postgres",
                "password": "woskxn"
            }
            cls.conn = psycopg2.connect(**cls.db_params)
            cls.cursor = cls.conn.cursor()
            print("PostgreSQL connection established")
        except (Exception, Error) as error:
            print(f"Error connecting to PostgreSQL: {error}")

    def login(self, username='admin', password='123123'):
        """Login to application"""
        # self.page.goto("http://103.56.158.135:5173/login")
        self.page.goto("http://localhost:5173/login")
        self.page.fill("input[placeholder='Username']", username)
        self.page.fill("input[placeholder='Password']", password)
        self.page.click("button[type='submit']")

    def test_hr_create_interview(self):
        self.login()
        interview_data = self.__class__.interview_data

        def verify_db(interview_data):
            """Verify interview data in database"""
            try:
                # Query to check if interview exists with matching details
                verify_query = """
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
                """

                self.cursor.execute(verify_query, (
                    interview_data["title"],
                    interview_data["location"],
                    interview_data["note"]
                ))

                result = self.cursor.fetchone()
                assert result is not None, f"Interview {interview_data['title']} not found in database"

                # Verify each field matches
                db_id, db_title, db_date, db_time_from, db_time_to, db_location, db_note = result
                self.__class__.interview_ids.append(db_id)
                assert db_title == interview_data[
                    "title"], f"Title mismatch: {db_title} != {interview_data['title']}"
                assert db_location == interview_data[
                    "location"], f"Location mismatch: {db_location} != {interview_data['location']}"
                assert db_note == interview_data[
                    "note"], f"Note mismatch: {db_note} != {interview_data['note']}"

                print(
                    f"✓ Verified interview in database: {interview_data['title']}")
                return True

            except AssertionError as ae:
                print(f"❌ Verification failed: {str(ae)}")
                raise
            except Exception as e:
                print(f"❌ Database verification error: {str(e)}")
                raise

        def fill_interview_form(interview_data):
            try:
                # Click Add Interview button
                self.page.click("text='Add Interview'")

                # Fill Schedule Title
                self.page.fill(
                    "input[placeholder='Enter interview title']", interview_data["title"])

                # Select Job
                self.page.click("[data-testid='select-interview-job']")
                self.page.click(
                    f"div[title='{interview_data['job_id']}']", timeout=2000)

                # Select Candidate
                self.page.click("[data-testid='select-interview-candidate']")
                self.page.click(
                    f"div[title^='{interview_data['candidate_id']}']")

                # # Select Position
                # self.page.click("[data-testid='select-interview-position']")
                # self.page.click(f"div[title='{interview_data['position']}']")

                # Select Interviewers
                self.page.click(
                    "[data-testid='select-interview-interviewers']")
                for interviewer in interview_data["interviewer_ids"]:
                    self.page.click(f"div[title='{interviewer}']")
                self.page.keyboard.press("Escape")

                # # Select Status
                # self.page.click("[data-testid='select-interview-status']")
                # self.page.click(f"div[title='{interview_data['status']}']")

                # Set Schedule Date
                self.page.click("[data-testid='date-interview-schedule']")
                self.page.fill(
                    "input[placeholder='Select date']", interview_data["schedule_date"])
                self.page.click("text='ADD INTERVIEW SCHEDULE'")

                # Set Time Range
                self.page.click("[data-testid='time-interview-from']")
                self.page.fill("input[placeholder='Select time']",
                               interview_data["schedule_time_from"])
                self.page.click("text='OK'")

                self.page.click("[data-testid='time-interview-to']")
                self.page.fill("#layout-multiple-horizontal_schedule_time_from",
                               interview_data["schedule_time_to"], timeout=1000)
                self.page.click("text='ADD INTERVIEW SCHEDULE'")

                # Fill Location and Note
                self.page.fill(
                    "input[placeholder='Enter location']", interview_data["location"])
                self.page.fill(
                    "input[placeholder='Enter note']", interview_data["note"])

                # Submit form
                self.page.click("button:text('Submit')")
                print(f"✓ Created interview: {interview_data['title']}")

                # Wait for submission
                self.page.wait_for_timeout(1000)

            except Exception as e:
                print(f"❌ Error in creating interview: {e}")
                raise

        try:
            self.page.click("a[href='/interview']")
            print("✓ Navigated to Interview page")
            for interview in interview_data:
                fill_interview_form(interview)
                verify_db(interview)
            print("\n🎉 All interviews created successfully 🎉")
            self.page.wait_for_timeout(1000)

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    def test_hr_edit_interview(self):
        interview_data = []
        for interview in self.__class__.interview_data:
            interview['status'] = 'Passed'
            interview_data.append(interview)

        def fill_interview_form(interview, email):
            self.page.click("a[href='/interview']")
            print("✓ Navigated to Interview page")

            self.page.click(
                f"td.ant-table-cell:has-text('{interview['title']}')")

            # đổi lại trạng thái
            self.page.click("div[data-testid='select-interview-status']")
            self.page.click("div[title='Interviewed']")

            self.page.click("[data-testid='select-result']")
            self.page.click(f"div[title='{interview['status']}']")

            # Submit form
            self.page.click("button:text('Submit')")
            print(f"✓ edited interview for: {interview['candidate_id']}")
            self.page.wait_for_timeout(3000)

        def verify_db(interview, email):
            self.page.wait_for_timeout(10)
            verify_query = """
                SELECT 
                    status
                FROM public.interview_schedule 
                WHERE title = %s
                AND location = %s
                AND note = %s
            """

            self.cursor.execute(verify_query, (
                (interview["title"], interview["location"], interview["note"])
            ))
            result = self.cursor.fetchone()
            assert result[0] == "Passed", \
                f"Status mismatch: {result[0]} != 'Passed'"

            # kiểm tra trạng thái candidate
            verify_query = """
                                SELECT status FROM public.candidate
                                WHERE email = %s
                            """
            self.cursor.execute(verify_query, (
                (email,)
            ))
            result = self.cursor.fetchone()
            assert result[0] == "Passed interview", \
                f"Status mismatch candidate: {result[0]} != 'Passed interview' {interview['title']}"

            print(f"✓ Verified offer in database for: {interview['title']}")
            return True

        try:
            for interview in interview_data:
                parts = interview['candidate_id'].split('(')
                candidate_email = parts[1].replace(')', '').strip()

                fill_interview_form(interview, candidate_email)
                verify_db(interview, candidate_email)
                self.__class__.candidate_edited.append(candidate_email)
            self.page.wait_for_timeout(1000)

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    def test_hr_delete_interview(self):
        interview_data = self.__class__.interview_data

        def fill_interview_form(id):
            try:
                self.page.click(f"[data-testid='{id}']")
                self.page.click(
                    ".ant-btn-primary.ant-btn-sm.ant-btn-dangerous")
                self.page.wait_for_timeout(1000)

            except Exception as e:
                print(f"❌ Error in creating interview: {e}")
                raise

        def verify_db(interview, id):
            verify_query = """
                        SELECT deleted
                        FROM public.interview_schedule 
                        WHERE id = %s
                    """

            self.cursor.execute(verify_query, (id,))

            result = self.cursor.fetchone()

            (db_delete) = result
            assert str(db_delete) != None, \
                f"Xóa {interview['title']} {db_delete} không thành công"

        try:
            self.page.click("a[href='/interview']")
            print("✓ Navigated to Interview page")
            ids = self.__class__.interview_ids

            for i in range(len(ids)):
                fill_interview_form(ids[i])
                verify_db(interview_data[i], ids[i])

            print("\n🎉 All interviews created successfully 🎉")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    @classmethod
    def teardown_class(cls):
        """Cleanup test data and close connections"""
        try:
            if cls.conn:
                interview_titles = [interview['title']
                                    for interview in cls.interview_data]
                # Delete test interviews based on titles
                delete_interviews_query = """
                        DELETE FROM public.interview_schedule 
                        WHERE title IN %s
                    """
                cls.cursor.execute(delete_interviews_query,
                                   (tuple(interview_titles),))
                cls.conn.commit()
                print("Test interviews rollback successfully")

                # backup candidate
                candidate_edited = cls.candidate_edited
                update_candidates_query = """
                                    UPDATE public.candidate
                                    SET status = 'Waiting for interview'
                                    WHERE email IN %s
                                """
                cls.cursor.execute(update_candidates_query,
                                   (tuple(candidate_edited),))
                cls.conn.commit()

                # Verify deletion
                verify_query = """
                        SELECT title FROM public.interview_schedule 
                        WHERE title IN %s
                    """
                cls.cursor.execute(verify_query, (tuple(interview_titles),))
                remaining = cls.cursor.fetchall()
                if not remaining:
                    print("All test interviews successfully removed")
                else:
                    print(f"Some test interviews remain: {remaining}")

                cls.cursor.close()
                cls.conn.close()
                print("PostgreSQL connection closed")
        except Exception as e:
            print(f"Cleanup error: {str(e)}")
        finally:
            cls.context.close()
            cls.browser.close()
