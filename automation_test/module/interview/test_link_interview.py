from .until.index import get_data
import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestLinkInterview:
    @classmethod
    def setup_class(cls):
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
        self.login()
        try:
            for case in self.case_link_interview_data:
                input_data = case['input']
                interview_id = self.get_state_db_link_interview(input_data)
                self.action_ui_link_interview(interview_id, case['validate'])

            print("\n🎉 All interviews link successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test link interview failed: {e}")
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
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
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


if __name__ == "__main__":
    pytest.main([__file__])
