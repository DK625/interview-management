from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestCreateJob:
    @classmethod
    def setup_class(cls):
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
