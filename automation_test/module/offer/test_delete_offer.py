import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error


class TestDeleteOffer:
    @classmethod
    def setup_class(cls):
        cls.case_delete_offer_data = [
            {
                "input": {
                    "department": "Purchasing",
                    "candidate": "data Auto test *offer5",
                    "approved": "admin",
                    "contract_type": "Part-time",
                    "basic_salary": "300",
                    "note": "note 5"
                },
            },
            {
                "input": {
                    "department": "Purchasing",
                    "candidate": "data Auto test *offer6",
                    "approved": "hr",
                    "contract_type": "Remote",
                    "basic_salary": "300",
                    "note": "note 6"
                },
            }
        ]
        cls.delete_offer_db_backup = []

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

    def get_state_db_delete_offer(self, offer):
        """Lấy trạng thái người dùng từ cơ sở dữ liệu"""
        where_conditions = []
        values = []
        for key, value in offer.items():
            where_conditions.append(f"{key} = %s")
            values.append(value)

        query = """
            SELECT 
              o.*
            FROM public.offer o
            LEFT JOIN public.candidate c ON o.candidate_id = c.id
            LEFT JOIN public.user u ON o.manager_id = u.id
            WHERE c.full_name = %s
            AND o.department = %s
            AND o.note = %s
            LIMIT 1
        """
        self.cursor.execute(
            query, (offer['candidate'], offer['department'], offer['note']))
        record = self.cursor.fetchone()

        if record:
            self.delete_offer_db_backup.append(record)
            return record['id']
        return None

    def action_ui_delete_offer(self, id):
        try:
            self.page.click("a[href='/offer']")
            
            element = self.page.locator("span.ant-select-selection-item[title='10 / page']")
            if element.is_visible(): 
                self.page.click("span.ant-select-selection-item[title='10 / page']")
                self.page.click("div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid='{id}']")
            self.page.click(".ant-btn-primary.ant-btn-sm.ant-btn-dangerous")
        except Exception as e:
            print(f"❌ Test action delete offer failed: {e}")
            raise

    def verify_db_delete_offer(self, id):
        query = """
            SELECT
                deleted
            FROM public.offer
            WHERE id = %s
        """
        self.cursor.execute(query, (id,))
        record = self.cursor.fetchone()

        assert str(record['deleted']) != None, \
            f"Xóa offer {id} không thành công"

    def test_delete_offer(self):
        self.login()
        try:
            for case in self.case_delete_offer_data:
                input_data = case['input']
                offer_id = self.get_state_db_delete_offer(input_data)
                self.action_ui_delete_offer(offer_id)
                self.verify_db_delete_offer(offer_id)

            print("\n🎉 All offers deleted successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete offer failed: {e}")
            raise

    @classmethod
    def backup_delete_offer(cls):
        try:
            for offer in cls.delete_offer_db_backup:
                columns = ', '.join(offer.keys())
                values = tuple(offer.values())
                update_query = f"""
                    UPDATE public.offer
                    SET ({columns}) = ({', '.join(['%s'] * len(offer))})
                    WHERE id = %s
                """
                cls.cursor.execute(update_query, (*values, offer['id']))
                cls.conn.commit()

                print(f"✅ Offer {offer['id']} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore offer: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_delete_offer()
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
