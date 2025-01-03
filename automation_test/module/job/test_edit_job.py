from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestEditJob:
    @classmethod
    def setup_class(cls):
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
        self.login()
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
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_edit_job()
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
