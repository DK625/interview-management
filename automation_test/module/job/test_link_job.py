from datetime import datetime
import re
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestLinkJob:
    @classmethod
    def setup_class(cls):
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

        playwright = sync_playwright().start()
        cls.browser = playwright.chromium.launch(headless=False)
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        try:
            cls.db_params = {
                "host": "103.56.158.135",
                "database": "job_management",
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
            start_date = self.page.input_value("#layout-multiple-horizontal_start_date")
            end_date = self.page.input_value("#layout-multiple-horizontal_end_date")

            assert start_date, f"Job {id} not found in start_date"
            assert end_date, f"Job {id} not found in end_date"

            self.page.reload()
            self.page.click("a[href='/request']")

            element = self.page.locator("span.ant-select-selection-item[title='10 / page']")
            if element.is_visible(): 
                self.page.click("span.ant-select-selection-item[title='10 / page']")
                self.page.click("div.ant-select-item-option-content:has-text('50 / page')")


            date_range = self.page.inner_text(f"tr[data-row-key='{id}'] td:nth-child(8)").strip()

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
        self.login()
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

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
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
