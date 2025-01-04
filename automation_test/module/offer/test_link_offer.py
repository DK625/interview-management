import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestLinkOffer:
    @classmethod
    def setup_class(cls):
        cls.case_link_offer_data = [
            {
                "input": {
                    "department": "IT",
                    "contract_type": "Full-time",
                    "note": "note 9"
                },
                "validate": {
                    "status": "Approved offer",
                    "db_candidate_status": "Approved offer",
                },
            },
            {
                "input": {
                    "department": "IT",
                    "contract_type": "Full-time",
                    "note": "note 10"
                },
                "validate": {
                    "status": "Rejected offer",
                    "db_candidate_status": "Rejected offer",
                },
            }
        ]
        cls.link_offer_db_backup = []
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

    def get_state_db_link_offer(self, offer):
        """Lấy trạng thái người dùng từ cơ sở dữ liệu"""
        where_conditions = []
        values = []
        for key, value in offer.items():
            where_conditions.append(f"{key} = %s")
            values.append(value)
        query = """
            SELECT 
              o.*,
              c.status as db_candidate_status,
              c.id as db_candidate_id
            FROM public.offer o
            LEFT JOIN public.candidate c ON o.candidate_id = c.id
            WHERE o.department = %s
            AND o.contract_type = %s
            AND o.note = %s
            LIMIT 1
        """

        self.cursor.execute(query, (
            (offer["department"], offer["contract_type"],
             offer["note"])
        ))
        record = self.cursor.fetchone()

        assert record != None, \
            f"Không tìm thấy bán ghi"

        keys_in_candidate = ['db_candidate_id', 'db_candidate_status']
        tmp_offer = {
            key: value for key, value in record.items()
            if key not in keys_in_candidate
        }
        tmp_candidate = {"db_candidate_status": record['db_candidate_status'],
                         "db_candidate_id": record['db_candidate_id']}
        if record:
            self.link_offer_db_backup.append(tmp_offer)
            self.candidate_db_backup.append(tmp_candidate)
            return record['id']
        return None

    def action_ui_link_offer(self, id, offer):
        try:
            self.page.click("a[href='/offer']")
            
            element = self.page.locator("span.ant-select-selection-item[title='10 / page']")
            if element.is_visible(): 
                self.page.click("span.ant-select-selection-item[title='10 / page']")
                self.page.click("div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid-edit='{id}']")
            # Select Status
            self.page.click("[data-testid='select-offer-status']")
            self.page.click(f"div[title='{offer['status']}']")
            candidate_name = self.page.locator("[data-testid='select-offer-candidate']").get_attribute("data-value")
            # Submit form
            self.page.click("button:text('Submit')")
            self.page.click("a[href='/candidate']")
            candidate_status = self.page.locator(f"[data-testid='candidate-status-{candidate_name}']").text_content()
            assert offer['db_candidate_status'] == candidate_status
            print(f"\n✓ link offer: {id}")
        except Exception as e:
            print(
                f"❌ Test action link offer {id} failed: {e}")
            raise

    def verify_db_link_offer(self, id, offer):
        time.sleep(2)
        try:
            query = """
              SELECT 
                o.*,
                c.status as db_candidate_status
              FROM public.offer o
              LEFT JOIN public.candidate c ON o.candidate_id = c.id
              WHERE o.id = %s
              LIMIT 1
          """

            self.cursor.execute(query, (
                (id,)
            ))
            record = self.cursor.fetchone()
            assert record is not None, f"Offer {id} not found in database"

        

            assert record['status'] == offer["status"], \
                f"status mismatch: {record['status']} != {offer['status']}"
            assert record['db_candidate_status'] == offer["status"], \
                f"db_candidate_status mismatch: {record['db_candidate_status']} != {offer['status']}"

            print(f"✓ Verified offer in database: {id}")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_link_offer(self):
        offer_id = None
        self.login()
        try:
            for case in self.case_link_offer_data:
                input_data = case['input']
                offer_id = self.get_state_db_link_offer(input_data)
                self.action_ui_link_offer(offer_id, case['validate'])
                self.verify_db_link_offer(offer_id, case['validate'])

            print("\n🎉 All offers link successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test link offer failed: {e}")
            raise

    @classmethod
    def backup_link_offer(cls):
        try:
            count = 0
            for offer in cls.link_offer_db_backup:
                columns = ', '.join(offer.keys())
                values = tuple(offer.values())
                update_query = f"""
                    UPDATE public.offer
                    SET ({columns}) = ({', '.join(['%s'] * len(offer))})
                    WHERE id = %s
                """
                cls.cursor.execute(update_query, (*values, offer['id']))
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

                print(f"✅ Offer {offer['id']} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore offer: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_link_offer()
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
