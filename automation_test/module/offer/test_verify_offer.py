import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestVerifyOffer:
    @classmethod
    def setup_class(cls):
        cls.case_verify_offer_data = [
            {
                "input": {
                    "department": "IT",
                    # "candidate": "Auto test *offer9",
                    "approved": "admin",
                    "contract_type": "Remote",
                    "basic_salary": "100",
                    # "contract_from": "2025-01-02",
                    # "contract_to": "2025-01-02",
                    "note": "note 9"
                },
                "validate": [
                    "Please enter time", "Please enter time", "Please choose a candidate"
                ]
            },
            {
                "input": {
                    "department": "IT",
                    # "candidate": "Auto test *offer9",
                    "approved": "admin",
                    "contract_type": "Remote",
                    # "basic_salary": "100",
                    "contract_from": "2025-01-02",
                    "contract_to": "2025-01-02",
                    "note": "note 1"
                },
                "validate": [
                    "Please enter salary", "Please choose a candidate"
                ]
            },
        ]

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

    def action_ui_verify_offer(self, offer):
        try:
            time.sleep(2)
            self.page.reload()
            self.page.click("a[href='/offer']")
            
            self.page.click("text='Add Offer'")
            if ('department' in offer):
                self.page.click("[data-testid='select-offer-department']")
                self.page.click(f"div[title='{offer['department']}']")
            if ('candidate' in offer):
                self.page.click("[data-testid='select-offer-candidate']")
                self.page.click(f"div[title='{offer['candidate']}']")
            if ('approved' in offer):
                self.page.click("[data-testid='select-offer-approver']")
                self.page.click(f"div[title='{offer['approved']}']")
            if ('contract_type' in offer):
                self.page.click("[data-testid='select-offer-contract']")
                self.page.click(f"div[title='{offer['contract_type']}']")

            if ('contract_from' in offer):
                self.page.click("[data-testid='select-offer-from']")
                self.page.fill("#layout-multiple-horizontal_contract_from",
                               offer["contract_from"], timeout=1000)
                self.page.click("text='ADD OFFER'")

            if ('contract_to' in offer):
                self.page.click("[data-testid='select-offer-to']")
                self.page.fill("#layout-multiple-horizontal_contract_to",
                               offer["contract_to"], timeout=1000)
                self.page.click("text='ADD OFFER'")

            if ('basic_salary' in offer):
                self.page.fill("[data-testid='input-offer-salary']",
                               offer["basic_salary"], timeout=1000)

            if ('note' in offer):
                self.page.fill("[data-testid='input-offer-note']",
                               offer["note"], timeout=1000)

            # Submit form
            self.page.click("button:text('Submit')")
            print(f"\n✓ verify offer: {id}")
        except Exception as e:
            print(
                f"❌ Test action verify offer {id} failed: {e}")
            raise

    def verify_db_verify_offer(self, offer):
        time.sleep(2)
        try:
            for mes in offer:
                locator = self.page.locator(
                    f"div.ant-form-item-explain-error:has-text('{mes}')")
                assert locator.count() > 0, \
                    f"không tìm thấy thông báo validate: {mes}"

            print(f"✓ Verified offer")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_verify_offer(self):
        self.login()
        try:
            for case in self.case_verify_offer_data:
                self.action_ui_verify_offer(case['input'])
                self.verify_db_verify_offer(case['validate'])

            print("\n🎉 All offers verify successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test verify offer failed: {e}")
            raise

    @classmethod
    def backup_verify_offer(cls):
        try:
            print(f"✅ Offer restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore offer: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_verify_offer()
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
