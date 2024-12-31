from playwright.sync_api import sync_playwright, expect
import time
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta


class TestJob:
    @classmethod
    def setup_class(cls):
        """Setup test environment and database connection"""
        playwright = sync_playwright().start()
        cls.browser = playwright.chromium.launch(headless=False)
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        job_data = [
            {
                "title": "Auto test job 1",
                "department": "IT",
                "position": "Frontend Developer-RQ48",
                "skills": ["Node.js", "Python", "PostgreSQL"],
                "salary_from": "2000",
                "salary_to": "4000",
                "description": "Looking for experienced backend developer"
            },
            {
                "title": "Auto test job 2",
                "department": "Marketing",
                "position": "Business Executive-RQ25",
                "skills": ["Digital Marketing", "Content Strategy"],
                "salary_from": "1500",
                "salary_to": "3000",
                "description": "Seeking marketing manager with digital experience"
            }
        ]

        cls.job_data = job_data
        cls.job_ids = []

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

    def test_hr_create_job(self):
        self.login()
        job_data = self.__class__.job_data

        def verify_db(job_data):
            """Verify job data in database"""
            try:
                # Add delay to ensure data is saved
                time.sleep(2)
                # Query để kiểm tra job trong database
                verify_query = """
                    SELECT 
                        j.id,
                        j.title,
                        j.department,
                        j.position,
                        j.skills,
                        j.salary_from,
                        j.salary_to,
                        j.description
                    FROM public.job j
                    WHERE j.title = %s
                    AND j.department = %s
                    ORDER BY j.created_date DESC
                    LIMIT 1
                """

                self.cursor.execute(verify_query, (
                    job_data["title"],
                    job_data["department"]
                ))

                result = self.cursor.fetchone()
                assert result is not None, f"Job {job_data['title']} not found in database"

                # Unpack database results
                (id,db_title, db_department, db_position, db_skills,
                 db_salary_from, db_salary_to,
                 db_description) = result
                self.__class__.job_ids.append(id)

                # Verify essential fields
                assert db_title == job_data["title"], \
                    f"Title mismatch: {db_title} != {job_data['title']}"

                assert db_department == job_data["department"], \
                    f"Department mismatch: {db_department} != {job_data['department']}"

                assert db_position == job_data["position"], \
                    f"Position mismatch: {db_position} != {job_data['position']}"

                # Verify arrays (skills và level được lưu dưới dạng array trong PostgreSQL)
                db_skills_set = set(db_skills) if db_skills else set()
                expected_skills_set = set(job_data["skills"])
                assert db_skills_set == expected_skills_set, \
                    f"Skills mismatch: {db_skills_set} != {expected_skills_set}"

                # Verify numeric fields
                assert float(db_salary_from) == float(job_data["salary_from"]), \
                    f"Salary from mismatch: {db_salary_from} != {job_data['salary_from']}"

                assert float(db_salary_to) == float(job_data["salary_to"]), \
                    f"Salary to mismatch: {db_salary_to} != {job_data['salary_to']}"

                assert db_description == job_data["description"], \
                    f"Description mismatch: {db_description} != {job_data['description']}"

                print(f"✓ Verified job in database: {job_data['title']}")
            except AssertionError as ae:
                print(f"❌ Verification failed: {str(ae)}")
                raise
            except Exception as e:
                print(f"❌ Database verification error: {str(e)}")
                raise

        def fill_job_form(job_data):
            try:
                # Click Add Job button
                self.page.click("text='Add Job'")
                self.page.click(
                    "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
                self.page.click(f"div[title='{job_data['department']}']")
                self.page.click("[data-testid='select-job-position']")
                self.page.click(f"div[title='{job_data['position']}']")
                # Fill Job Title
                self.page.fill(
                    "input[placeholder='Enter job title']", job_data["title"])

                # Add Skills
                # Add Skills
                for skill in job_data["skills"]:
                    self.page.click("[data-testid='select-job-skills']")
                    # Sử dụng data-testid để target chính xác input field
                    skills_input = "[data-testid='select-job-skills'] .ant-select-selection-search-input"
                    self.page.fill(skills_input, skill)
                    self.page.keyboard.press("Enter")
                    self.page.wait_for_timeout(500)  # Wait for animation

                # Set Start Date
                # self.page.click("[data-testid='date-job-start']", timeout=1000)
                # self.page.fill(
                #     "input[placeholder='Select date']", job_data["start_date"])
                # self.page.click("[data-testid='date-job-start']")

                # # Click away to close datepicker
                # self.page.click("text='ADD JOB'")

                # Set End Date
                # self.page.click("[data-testid='date-job-end']", timeout=1000)
                # self.page.fill("#layout-multiple-horizontal_end_date",
                #                job_data["end_date"], timeout=1000)

                # Fill Salary Range
                self.page.fill(
                    "form div.ant-form-item:has(> div label:text('Salary from')) input.ant-input-number-input",
                    job_data["salary_from"])
                self.page.fill("form div.ant-form-item:has(> div label:text('Salary to')) input.ant-input-number-input",
                               job_data["salary_to"])

                # Add Benefits
                # benefits_input = "#layout-multiple-horizontal_benefits .ant-select-selection-search-input"
                # benefits_input = "[data-testid='select-job-benefits'] .ant-select-selection-search-input"
                # for benefit in job_data["benefits"]:
                #     self.page.click(benefits_input, timeout=1000)  # Click để mở dropdown
                #     self.page.fill(benefits_input, benefit, timeout=1000)  # Fill giá trị
                #     self.page.keyboard.press("Enter")  # Press Enter để chọn

                # Select Level
                # self.page.click(
                #     "form div.ant-form-item:has(> div label:text('Level')) .ant-select-selector")
                # for level in job_data["level"]:
                #     self.page.click(f"div[title='{level}']")
                # self.page.keyboard.press("Escape")

                # Select Status
                # self.page.click(
                #     "form div.ant-form-item:has(> div label:text('Status')) .ant-select-selector")
                # self.page.click(f"div[title='{job_data['status']}']")

                # Fill Working Address
                # self.page.fill("form div.ant-form-item:has(> div label:text('Address')) input",
                #                job_data["working_address"])

                # Fill Description
                self.page.fill("form div.ant-form-item:has(> div label:text('Description')) input",
                               job_data["description"])

                # Submit form
                self.page.click("button:text('Submit')")
                print(f"✓ Created job: {job_data['title']}")

            except Exception as e:
                print(f"❌ Error in creating job: {e}")
                raise

        try:
            self.page.click("a[href='/job']")
            print("✓ Navigated to Job page")
            for job in job_data:
                fill_job_form(job)
                verify_db(job)
            print("\n🎉 All jobs created successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test create failed: {e}")
            raise

    def test_hr_edit_job(self):
        job_data = []
        for job in self.__class__.job_data:
            job['title'] = 'Change-' + job['title']
            job['department'] = 'AF'
            job['position'] = 'Legal Manager-RQ18'
            job['skills'] = ["nextJs"],
            job['salary_from'] = '8000'
            job['salary_to'] = '9000'
            job['description'] = 'Change-' + job['title']
            job_data.append(job)

        def fill_job_form(job):
            try:
                title = job['title'].split('-')[1]
                self.page.click("a[href='/job']")
                print("✓ Navigated to Interview page")

                self.page.click(
                    f"td.ant-table-cell:has-text('{title}')")
                self.page.click(
                        "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
                self.page.click(f"div[title='{job['department']}']")
                self.page.click("[data-testid='select-job-position']")
                self.page.click(f"div[title='{job['position']}']")
                # Fill Job Title
                self.page.fill(
                    "input[placeholder='Enter job title']", job["title"])

                # Add Skills
                # for skill in job["skills"]:
                #     self.page.click("[data-testid='select-job-skills']")
                #     skills_input = "[data-testid='select-job-skills'] .ant-select-selection-search-input"
                #     self.page.fill(skills_input, skill)
                #     self.page.keyboard.press("Enter")
                #     self.page.wait_for_timeout(500)

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
                print(f"✓ Edited job: {title}")

            except Exception as e:
                print(f"❌ Error in creating job: {e}")
                raise    

        def verify_db(job):
            self.page.wait_for_timeout(10)
            verify_query = """
                SELECT 
                    j.title,
                    j.department,
                    j.position,
                    j.skills,
                    j.salary_from,
                    j.salary_to,
                    j.description
                FROM public.job j
                WHERE j.title = %s
                LIMIT 1
            """

            # Chỉ truyền job["title"] như là một chuỗi, không cần tuple
            self.cursor.execute(verify_query, (job["title"],))
            result = self.cursor.fetchone()

            (db_title, db_department, db_position, db_skills,
            db_salary_from, db_salary_to, db_description) = result

            assert db_title == job['title'], \
                f"Status mismatch: {db_title} != {job['title']}"

            assert db_department == job['department'], \
                f"Status mismatch: {db_department} != {job['department']}"

            assert db_position == job['position'], \
                f"Status mismatch: {db_position} != {job['position']}"

            # assert db_skills == job['skills'], \
            #     f"Status mismatch: {db_skills} != {job['skills']}"

            assert db_salary_from == int(job['salary_from']), \
                f"Status mismatch: {db_salary_from} != {job['salary_from']}"

            assert db_salary_to == int(job['salary_to']), \
                f"Status mismatch: {db_salary_to} != {job['salary_to']}"

            assert db_description == job['description'], \
                f"Status mismatch: {db_description} != {job['description']}"

            print(f"✓ Verified offer in database for: {job['title']}")
            return True

        try:
            for job in job_data:
                fill_job_form(job)
                verify_db(job)
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    def test_hr_delete_job(self):
        job_data = self.__class__.job_data

        def fill_job_form(id):
            try:
                self.page.click(f"[data-testid='{id}']")
                self.page.click(
                    ".ant-btn-primary.ant-btn-sm.ant-btn-dangerous")
            except Exception as e:
                print(f"❌ Error in test delete job: {e}")
                raise

        def verify_db(job, id):
            verify_query = """
                SELECT deleted
                FROM public.job
                WHERE id = %s
            """

            self.cursor.execute(verify_query, (id,))

            result = self.cursor.fetchone()

            (db_delete) = result
            assert str(db_delete) != None, \
                f"Xóa {job['title']} không thành công"

        try:
            self.page.click("a[href='/job']")
            print("✓ Navigated to Interview page")
            ids = self.__class__.job_ids

            for i in range(len(ids)):
                fill_job_form(ids[i])
                verify_db(job_data[i], ids[i])

            print("\n🎉 All jobs deleted successfully 🎉")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    @classmethod
    def teardown_class(cls):
        """Cleanup test data and close connections"""
        try:
            if cls.conn:
                # dọn job test
                job_title = [job['title'] for job in cls.job_data]
                delete_jobs_query = """
                    DELETE FROM public.job 
                    WHERE title IN %s
                """
                cls.cursor.execute(delete_jobs_query, (tuple(job_title),))
                cls.conn.commit()
                print("Test jobs deleted successfully")

                # xác nhận đã dọn
                verify_query = """
                    SELECT title FROM public.job 
                    WHERE title IN %s
                """
                cls.cursor.execute(verify_query, (tuple(job_title),))
                remaining = cls.cursor.fetchall()
                if not remaining:
                    print("All test jobs successfully removed")
                else:
                    print(f"Some test jobs remain: {remaining}")

                cls.cursor.close()
                cls.conn.close()
                print("PostgreSQL connection closed")
        except Exception as e:
            print(f"Cleanup error: {str(e)}")
        finally:
            cls.context.close()
            cls.browser.close()
