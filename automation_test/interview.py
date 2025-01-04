from playwright.sync_api import sync_playwright, expect
import time
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor


class TestInterview:
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

        cls.case_edit_interview_data = [
            {
                "input": {
                    "title": "Auto test *interview-3",
                    "job_id": "Business Executive Intern-JOB21",
                    "candidate_id": "Auto test *data-interview3 (data-interview-3@gmail.com)",
                    "status": "Invited",
                    "location": "R003",
                    "note": "data 3"
                },
                "validate": {
                    "title": "change-Auto test *interview-3",
                    "job_id": "Fresher Warehouse Staff-JOB24",
                    "candidate_id": "tmp-Auto test *data-interview0 (tmp-data-interview-0@gmail.com)",
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
                    "status": "Invited",
                    "location": "R004",
                    "note": "data 4"
                },
                "validate": {
                    "title": "change-Auto test *interview-4",
                    "job_id": "Business Executive Intern-JOB21",
                    "candidate_id": "Auto test *data-interview3 (data-interview-3@gmail.com)",
                    "status": "Invited",
                    "location": "change-R004",
                    "note": "change-data 4"
                },
            }
        ]
        cls.edit_interview_db_backup = []

        cls.case_delete_interview_data = [
            {
                "input": {
                    "title": "Auto test *interview-5",
                    # "job_id": "Fresher Warehouse Staff-JOB24",
                    # "candidate_id": "Auto test *data-interview5 (data-interview-5@gmail.com)",
                    # "interviewer_ids": ["purchasingmanager"],
                    # "schedule_date": interview_date,
                    # "schedule_time_from": time_from,
                    # "schedule_time_to": time_to,
                    "status": "Invited",
                    "location": "R004",
                    "note": "node test 5"
                },
            },
            {
                "input": {
                    "title": "Auto test *interview-6",
                    # "job_id": "Business Executive Intern-JOB21",
                    # "candidate_id": "Auto test *data-interview6 (data-interview-6@gmail.com)",
                    # "interviewer_ids": ["purchasingmanager"],
                    # "schedule_date": interview_date,
                    # "schedule_time_from": time_from,
                    # "schedule_time_to": time_to,
                    "status": "Invited",
                    "location": "R004",
                    "note": "node test 6"
                },
            }
        ]
        cls.delete_interview_db_backup = []

        cls.case_link_interview_data = [
            {
                "input": {
                    "title": "Auto test *interview-7",
                    "status": "Invited",
                    "location": "R007",
                    "note": "note 7"
                },
                "validate": {
                    "status": "Passed",  # Passed | Failed
                    "db_candidate_status": "Passed interview",
                },
            },
            {
                "input": {
                    "title": "Auto test *interview-8",
                    "status": "Invited",
                    "location": "R008",
                    "note": "note 8"
                },
                "validate": {
                    "status": "Failed",
                    "db_candidate_status": "Banned",
                },
            }
        ]
        cls.link_interview_db_backup = []
        cls.candidate_db_backup = []

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
        # context = self.browser.new_context()

        # self.page = context.new_page()
        """Login to application"""
        self.page.goto("http://103.56.158.135:5173/login")
        # self.page.goto("http://localhost:5173/login")
        self.page.fill("input[placeholder='Username']", username)
        self.page.fill("input[placeholder='Password']", password)
        self.page.click("button[type='submit']")

    def logout(self):
        self.page.click(".ant-dropdown-trigger")
        self.page.click(".ant-dropdown-menu-item:last-child")

    # create
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

    # edit
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
            # self.page.click("[data-testid='date-interview-schedule']")
            # self.page.fill(
            #     "input[placeholder='Select date']", interview["schedule_date"])
            # self.page.click("text='EDIT INTERVIEW SCHEDULE'")

            # Set Time Range
            # self.page.click("[data-testid='time-interview-from']")
            # self.page.fill("input[placeholder='Select time']",
            #                interview["schedule_time_from"])
            # self.page.click("text='OK'")
            # self.page.click("[data-testid='time-interview-to']")
            # self.page.fill("#layout-multiple-horizontal_schedule_time_from",
            #                interview["schedule_time_to"], timeout=1000)
            # self.page.click("text='EDIT INTERVIEW SCHEDULE'")

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

    # delete
    def get_state_db_delete_interview(self, interview):
        """Lấy trạng thái người dùng từ cơ sở dữ liệu"""
        where_conditions = []
        values = []
        for key, value in interview.items():
            where_conditions.append(f"{key} = %s")
            values.append(value)

        query = f"SELECT * FROM public.interview_schedule WHERE {' AND '.join(where_conditions)};"

        self.cursor.execute(query, tuple(values))
        record = self.cursor.fetchone()

        if record:
            self.delete_interview_db_backup.append(record)
            return record['id']
        return None

    def action_ui_delete_interview(self, id):
        try:
            self.page.click("a[href='/interview']")
            
            element = self.page.locator("span.ant-select-selection-item[title='10 / page']")
            if element.is_visible(): 
                self.page.click("span.ant-select-selection-item[title='10 / page']")
                self.page.click("div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid='{id}']")
            self.page.click(".ant-btn-primary.ant-btn-sm.ant-btn-dangerous")
        except Exception as e:
            print(f"❌ Test action delete interview failed: {e}")
            raise

    def verify_db_delete_interview(self, id):
        query = """
            SELECT
                deleted
            FROM public.interview_schedule
            WHERE id = %s
        """
        self.cursor.execute(query, (id,))
        record = self.cursor.fetchone()

        assert str(record['deleted']) != None, \
            f"Xóa interview {id} không thành công"

    def test_delete_interview(self):
        try:
            for case in self.case_delete_interview_data:
                input_data = case['input']
                interview_id = self.get_state_db_delete_interview(input_data)
                self.action_ui_delete_interview(interview_id)
                self.verify_db_delete_interview(interview_id)

            print("\n🎉 All interviews deleted successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete interview failed: {e}")
            raise

    # link
    def get_state_db_link_interview(self, interview):
        """Lấy trạng thái người dùng từ cơ sở dữ liệu"""
        where_conditions = []
        values = []
        for key, value in interview.items():
            where_conditions.append(f"{key} = %s")
            values.append(value)
        query = """
            SELECT 
              i.*,
              c.status as db_candidate_status,
              c.id as db_candidate_id
            FROM public.interview_schedule i
            LEFT JOIN public.candidate c ON i.candidate_id = c.id
            WHERE i.title = %s
            AND i.note = %s
            AND i.status = %s
            AND i.location = %s
            LIMIT 1
        """

        self.cursor.execute(query, (
            (interview["title"], interview["note"],
             interview["status"], interview["location"])
        ))
        record = self.cursor.fetchone()

        assert record != None, \
            f"Không tìm thấy bán ghi cho {interview['title']}"

        keys_in_candidate = ['db_candidate_id', 'db_candidate_status']
        tmp_interview = {
            key: value for key, value in record.items()
            if key not in keys_in_candidate
        }
        tmp_candidate = {"db_candidate_status": record['db_candidate_status'],
                         "db_candidate_id": record['db_candidate_id']}
        if record:
            self.link_interview_db_backup.append(tmp_interview)
            self.candidate_db_backup.append(tmp_candidate)
            return record['id']
        return None

    def action_ui_link_interview(self, id, interview):
        try:
            self.page.click("a[href='/interview']")

            element = self.page.locator("span.ant-select-selection-item[title='10 / page']")
            if element.is_visible():
                self.page.click("span.ant-select-selection-item[title='10 / page']")
                self.page.click("div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid-edit='{id}']")
            # Select Status
            self.page.click("[data-testid='select-interview-status']")
            self.page.click(f"div[title='Interviewed']")
            self.page.click("[data-testid='select-result']")
            self.page.click(f"div[title='{interview['status']}']")

            candidate_name = self.page.locator("[data-testid='select-interview-candidate']").get_attribute("data-value")

            # Submit form
            self.page.click("button:text('Submit')")
            self.page.click("a[href='/candidate']")
            candidate_status = self.page.locator(f"[data-testid='candidate-status-{candidate_name}']").text_content()
            assert interview['db_candidate_status'] == candidate_status

            print(f"\n✓ link interview candidate {candidate_name}")
        except Exception as e:
            print(
                f"❌ Test action link interview {id} failed: {e}")
            raise

    def verify_db_link_interview(self, id, interview):
        time.sleep(2)
        try:
            query = """
              SELECT 
                i.*,
                c.status as db_candidate_status
              FROM public.interview_schedule i
              LEFT JOIN public.candidate c ON i.candidate_id = c.id
              WHERE i.id = %s
              LIMIT 1
          """

            self.cursor.execute(query, (
                (id,)
            ))
            record = self.cursor.fetchone()
            assert record is not None, f"Interview {id} not found in database"

            assert record['status'] == interview["status"], \
                f"status mismatch: {record['status']} != {interview['status']}"
            assert record['db_candidate_status'] == interview["db_candidate_status"], \
                f"db_candidate_status mismatch: {record['db_candidate_status']} != {interview['db_candidate_status']}"

            print(f"✓ Verified interview in database: {id}")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_link_interview(self):
        interview_id = None
        try:
            for case in self.case_link_interview_data:
                input_data = case['input']
                interview_id = self.get_state_db_link_interview(input_data)
                self.action_ui_link_interview(interview_id, case['validate'])
                self.verify_db_link_interview(interview_id, case['validate'])

            print("\n🎉 All interviews link successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test link interview failed: {e}")
            raise

    # verify
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
        try:
            for case in self.case_verify_interview_data:
                self.action_ui_verify_interview(case['input'])
                self.verify_db_verify_interview(case['validate'])

            print("\n🎉 All interviews verify successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test verify interview failed: {e}")
            raise

    @classmethod
    def backup_link_interview(cls):
        try:
            count = 0
            for interview in cls.link_interview_db_backup:
                columns = ', '.join(interview.keys())
                values = tuple(interview.values())
                update_query = f"""
                    UPDATE public.interview_schedule
                    SET ({columns}) = ({', '.join(['%s'] * len(interview))})
                    WHERE id = %s
                """
                cls.cursor.execute(update_query, (*values, interview['id']))
                cls.conn.commit()

                update_query = """
                    UPDATE public.candidate
                    SET status = %s
                    WHERE id = %s
                """
                candidate = cls.candidate_db_backup[count]
                cls.cursor.execute(
                    update_query, (candidate['db_candidate_status'], candidate['db_candidate_id']))
                cls.conn.commit()
                count += 1

                print(f"✅ Interview {interview['id']} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore interview: {e}")

    @classmethod
    def backup_delete_interview(cls):
        try:
            for interview in cls.delete_interview_db_backup:
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
            cls.backup_create_interview()
            cls.backup_edit_interview()
            cls.backup_delete_interview()
            cls.backup_link_interview()
            if cls.conn:
                cls.cursor.close()
                cls.conn.close()
                print("PostgreSQL connection closed")
        except Exception as e:
            print(f"❌ Cleanup error: {str(e)}")
        finally:
            cls.context.close()
            cls.browser.close()
