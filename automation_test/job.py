from playwright.sync_api import sync_playwright, expect
import time
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import re

class TestJob:
    @classmethod
    def setup_class(cls):
        """Setup test environment and database connection"""
        playwright = sync_playwright().start()
        cls.browser = playwright.chromium.launch(headless=False)
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        cls.case_create_job_data = [
            {
                "input": {
                    "title": "Auto test *job1",
                    "department": "IT",
                    "position": "Frontend Developer-RQ48",
                    "skills": ["react"],
                    "salary_from": "2000",
                    "salary_to": "4000",
                    "description": "description test 1"
                },
            },
            {
                "input": {
                    "title": "Auto test *job2",
                    "department": "AF",
                    "position": "Legal Manager-RQ18",
                    "skills": ["Node.js", "Python"],
                    "salary_from": "1000",
                    "salary_to": "2000",
                    "description": "description test 2"
                },
            }
        ]
        cls.create_job_db_backup = []

        cls.case_edit_job_data = [
            {
                "input": {
                    "title": "Auto test *job2",
                    "department": "IT",
                    "position": "Frontend Developer-RQ48",
                    "skills": ["react"],
                    "salary_from": "2000",
                    "salary_to": "4000",
                    "description": "description test 2"
                },
                "validate": {
                    "title": "change-Auto test *job2",
                    "department": "AF",
                    "position": "Legal Manager-RQ18",
                    "salary_from": "5000",
                    "salary_to": "6000",
                    "description": "change-description test 2"
                }
            },
            {
                "input": {
                    "title": "Auto test *job3",
                    "department": "AF",
                    "position": "Legal Manager-RQ18",
                    "skills": ["Node.js"],
                    "salary_from": "1000",
                    "salary_to": "3000",
                    "description": "description test 3"
                },
                "validate": {
                    "title": "change-Auto test *job3",
                    "department": "Marketing",
                    "position": "Business Executive-RQ25",
                    "salary_from": "5000",
                    "salary_to": "6000",
                    "description": "change-description test 3"
                }
            }
        ]
        cls.edit_job_db_backup = []
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

        cls.case_link_job_data = [
            {
                "input": {
                    "department": "IT",
                    "position": "Frontend Developer-RQ48",
                },
            },
            {
                "input": {
                    "department": "AF",
                    "position": "Legal Manager-RQ18",
                },
            }
        ]
        cls.link_job_db_backup = []
        cls.candidate_db_backup = []

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
        # self.page.goto("http://localhost:5173/login")
        self.page.goto("http://103.56.158.135:5173/login")
        self.page.fill("input[placeholder='Username']", username)
        self.page.fill("input[placeholder='Password']", password)
        self.page.click("button[type='submit']")
    # create

    def action_ui_create_job(self, job):
        try:
            self.page.click("a[href='/job']")
            
            self.page.click("text='Add Job'")
            self.page.click(
                "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
            self.page.click(f"div[title='{job['department']}']")
            self.page.click("[data-testid='select-job-position']")
            self.page.click(f"div[title='{job['position']}']")
            self.page.fill(
                "input[placeholder='Enter job title']", job["title"])
            # Add Skills
            for skill in job["skills"]:
                self.page.click("[data-testid='select-job-skills']")
                skills_input = "[data-testid='select-job-skills'] .ant-select-selection-search-input"
                self.page.fill(skills_input, skill)
                self.page.keyboard.press("Enter")
                self.page.wait_for_timeout(500)  # Wait for animation
            # Fill Salary Range
            self.page.fill(
                "form div.ant-form-item:has(> div label:text('Salary from')) input.ant-input-number-input",
                job["salary_from"])
            self.page.fill("form div.ant-form-item:has(> div label:text('Salary to')) input.ant-input-number-input",
                           job["salary_to"])
            # Fill Description
            self.page.fill("form div.ant-form-item:has(> div label:text('Description')) input",
                           job["description"])
            # Submit form
            self.page.click("button:text('Submit')")
            print(f"\n✓ Created job: {job['title']}")

        except Exception as e:
            print(f"❌ Test action create job {job['full_name']} failed: {e}")
            raise

    def verify_db_create_job(self, job):
        time.sleep(2)
        try:
            query = """
                SELECT 
                    id,
                    title,
                    department,
                    position,
                    skills,
                    salary_from,
                    salary_to,
                    description
                FROM public.job
                WHERE title = %s
                AND department = %s
                LIMIT 1
            """

            self.cursor.execute(query, (
                job['title'], job['department']
            ))
            result = self.cursor.fetchone()
            assert result is not None, f"Job {job['title']} not found in database"

            self.create_job_db_backup.append(result['id'])

            assert result['title'] == job["title"], \
                f"title mismatch: {result['title']} != {job['title']}"
            assert result['department'] == job["department"], \
                f"department mismatch: {result['department']} != {job['department']}"
            assert result['position'] == job["position"], \
                f"position mismatch: {result['position']} != {job['position']}"

            db_skills_set = set(
                result['skills']) if result['skills'] else set()
            expected_skills_set = set(job["skills"])
            assert db_skills_set == expected_skills_set, \
                f"skills mismatch: {result['skills']} != {job['skills']}"

            assert float(result['salary_from']) == float(job["salary_from"]), \
                f"salary_from mismatch: {result['salary_from']} != {job['salary_from']}"
            assert float(result['salary_to']) == float(job["salary_to"]), \
                f"salary_to mismatch: {result['salary_to']} != {job['salary_to']}"
            assert result['description'] == job["description"], \
                f"description mismatch: {result['description']} != {job['description']}"

            print(f"✓ Verified job in database: {job['title']}")

        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_create_job(self):
        self.login()
        try:
            for case in self.case_create_job_data:
                job = case['input']
                self.action_ui_create_job(job)
                self.verify_db_create_job(job)

            print("\n🎉 All jobs create successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete job failed: {e}")
            raise

    # edit
    def get_state_db_edit_job(self, job):
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
            self.edit_job_db_backup.append(record)
            return record['id']
        return None

    def action_ui_edit_job(self, id, job):
        try:
            self.page.click("a[href='/job']")
            
            element = self.page.locator("span.ant-select-selection-item[title='10 / page']")
            if element.is_visible(): 
                self.page.click("span.ant-select-selection-item[title='10 / page']")
                self.page.click("div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid-edit='{id}']")
            self.page.click(
                "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
            self.page.click(f"div[title='{job['department']}']")
            self.page.click("[data-testid='select-job-position']")
            self.page.click(f"div[title='{job['position']}']")
            # Fill Job Title
            self.page.fill(
                "input[placeholder='Enter job title']", job["title"])
            # Fill Salary Range
            self.page.fill(
                "form div.ant-form-item:has(> div label:text('Salary from')) input.ant-input-number-input",
                job["salary_from"])
            self.page.fill("form div.ant-form-item:has(> div label:text('Salary to')) input.ant-input-number-input",
                           job["salary_to"])
            # Fill Description
            self.page.fill("form div.ant-form-item:has(> div label:text('Description')) input",
                           job["description"])
            # Click submit
            self.page.click("button:text('Submit')")
            print(f"\n✓ edit job: {job['title']}")
        except Exception as e:
            print(f"❌ Test action edit job {job['title']} failed: {e}")
            raise

    def verify_db_edit_job(self, id, job):
        time.sleep(2)
        try:
            query = """
                SELECT 
                    id,
                    title,
                    department,
                    position,
                    salary_from,
                    salary_to,
                    description
                FROM public.job
                WHERE title = %s
                AND department = %s
                LIMIT 1
            """

            self.cursor.execute(query, (
                job['title'], job['department']
            ))
            result = self.cursor.fetchone()
            assert result is not None, f"Job {job['title']} not found in database"

            assert result['title'] == job["title"], \
                f"title mismatch: {result['title']} != {job['title']}"
            assert result['department'] == job["department"], \
                f"department mismatch: {result['department']} != {job['department']}"
            assert result['position'] == job["position"], \
                f"position mismatch: {result['position']} != {job['position']}"

            assert float(result['salary_from']) == float(job["salary_from"]), \
                f"salary_from mismatch: {result['salary_from']} != {job['salary_from']}"
            assert float(result['salary_to']) == float(job["salary_to"]), \
                f"salary_to mismatch: {result['salary_to']} != {job['salary_to']}"
            assert result['description'] == job["description"], \
                f"description mismatch: {result['description']} != {job['description']}"

            print(f"✓ Verified job in database: {job['title']}")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_edit_job(self):
        try:
            for case in self.case_edit_job_data:
                input_data = case['input']
                job_id = self.get_state_db_edit_job(input_data)
                self.action_ui_edit_job(job_id, case['validate'])
                self.verify_db_edit_job(job_id, case['validate'])

            print("\n🎉 All jobs edit successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete job failed: {e}")
            raise

    # delete
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
            self.delete_job_db_backup.append(record)
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

    # link
    def action_ui_link_job(self, id, job):
        try:
            self.page.click("a[href='/job']")
            
            self.page.click("text='Add Job'")
            self.page.click(
                "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
            self.page.click(f"div[title='{job['department']}']")
            self.page.click("[data-testid='select-job-position']")
            self.page.click(f"div[title='{job['position']}']")
            print(f"\n✓ link job: {id}")
        except Exception as e:
            print(
                f"❌ Test action link job {id} failed: {e}")
            raise

    def verify_db_link_job(self, id):
        time.sleep(2)
        try:
            start_date = self.page.input_value(
                "#layout-multiple-horizontal_start_date")
            end_date = self.page.input_value(
                "#layout-multiple-horizontal_end_date")

            assert start_date, f"Job {id} not found in start_date"
            assert end_date, f"Job {id} not found in end_date"

            self.page.reload()
            self.page.click("a[href='/request']")

            self.page.click(
                "span.ant-select-selection-item[title='10 / page']")
            self.page.click(
                "div.ant-select-item-option-content:has-text('50 / page')")

            date_range = self.page.inner_text(
                f"tr[data-row-key='{id}'] td:nth-child(8)").strip()

            def format_date(date):
                try:
                    return datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
                except ValueError:
                    return datetime.strptime(date, "%d/%m/%Y").strftime("%d/%m/%Y")

            formatted_start_date = format_date(start_date)
            formatted_end_date = format_date(end_date)

            # Kiểm tra date_range khớp với định dạng
            expected_date_range = f"{formatted_start_date} - {formatted_end_date}"
            assert date_range == expected_date_range, \
                f"Status mismatch: {date_range} != {expected_date_range}"

            print(f"✓ Verified job in ui: {id}")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_link_job(self):
        job_id = None
        try:
            for case in self.case_link_job_data:
                input_data = case['input']
                match = re.search(r'RQ(\d+)', input_data['position'])
                if match:
                    job_id = match.group(1)
                    self.action_ui_link_job(job_id, input_data)
                    self.verify_db_link_job(job_id)
                else:
                    print(f"❌ Invalid job id: {job_id}")
            print("\n🎉 All jobs link successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test link job failed: {e}")
            raise

    # verify
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
    def backup_delete_job(cls):
        try:
            for job in cls.delete_job_db_backup:
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
    def backup_edit_job(cls):
        try:
            for job in cls.edit_job_db_backup:
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
    def backup_create_job(cls):
        try:
            ids = cls.create_job_db_backup
            placeholders = ', '.join(['%s'] * len(ids))
            delete_query = f"""
                DELETE FROM public.job
                WHERE id IN ({placeholders})
            """

            cls.cursor.execute(delete_query, tuple(ids))
            cls.conn.commit()
            print(f"✅ Job {ids} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore job: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_create_job()
            cls.backup_edit_job()
            cls.backup_delete_job()
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
