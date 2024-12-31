import copy

from playwright.sync_api import sync_playwright, expect
import time
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta

class TestOffer:
    @classmethod
    def setup_class(cls):
        """Setup test environment and database connection"""
        playwright = sync_playwright().start()
        cls.browser = playwright.chromium.launch(headless=False)
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        # Calculate dates
        today = datetime.now()
        contract_from = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        contract_to = (today + timedelta(days=365)).strftime("%Y-%m-%d")  # 1 year contract
        offer_data = [
            {
                "candidate": "Võ Anh Thảo",
                "department": "IT",
                "interview_schedule_id": "Automation Test Offer 1",
                "position": "Backend Developer",
                "manager_id": "hr",  # The HR approver
                "status": "Waiting for approval",
                "level": "Leader",
                "type": "Full-time",
                "contract_from": contract_from,
                "contract_to": contract_to,
                "basic_salary": "2000",
                "currency": "USD",
                "note": "IT Department offer with competitive package"
            },
            {
                "candidate": "Doan Manh Dat",
                "department": "PR",
                "interview_schedule_id": "Automation Test Offer 2",
                "position": "Bussiness Analyst",
                "manager_id": "hr",  # The HR approver
                "status": "Waiting for approval",
                "level": "Manager",
                "type": "Full-time",
                "contract_from": contract_from,
                "contract_to": contract_to,
                "basic_salary": "1800",
                "currency": "USD",
                "note": "PR Department offer with benefits"
            }
        ]

        cls.offer_data = offer_data
        cls.candidate_edited = []
        cls.offer_ids = []

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

    def verify_offer_in_db(self, offer_data):
        """Verify offer data in database"""
        time.sleep(1)
        try:
            # Query to check if offer exists with matching details
            verify_query = """
                SELECT 
                    o.id,
                    o.basic_salary,
                    o.contract_from,
                    o.contract_to,
                    o.department,
                    o.note,
                    o.position,
                    o.status,
                    o.contract_type as type,
                    c.full_name as candidate_name,
                    u.username as manager_username
                FROM public.offer o
                LEFT JOIN public.candidate c ON o.candidate_id = c.id
                LEFT JOIN public.user u ON o.manager_id = u.id
                WHERE c.full_name = %s
                AND o.department = %s
                AND o.note = %s
                ORDER BY o.created_date DESC
                LIMIT 1
            """

            self.cursor.execute(verify_query, (
                offer_data["candidate"],
                offer_data["department"],
                offer_data["note"],
            ))

            result = self.cursor.fetchone()
            assert result is not None, f"Offer for {offer_data['candidate']} not found in database"

            # Unpack database results
            (db_id, db_salary, db_contract_from, db_contract_to, db_department,
             db_note, db_position, db_status, db_type,
             db_candidate_name, db_manager_username) = result
            self.__class__.offer_ids.append(db_id)
            # Verify essential fields
            assert str(db_salary) == offer_data["basic_salary"], \
                f"Salary mismatch: {db_salary} != {offer_data['basic_salary']}"

            assert db_department == offer_data["department"], \
                f"Department mismatch: {db_department} != {offer_data['department']}"

            assert db_status == offer_data["status"], \
                f"Status mismatch: {db_status} != {offer_data['status']}"

            assert db_type == offer_data["type"], \
                f"Contract type mismatch: {db_type} != {offer_data['type']}"

            assert db_candidate_name == offer_data["candidate"], \
                f"Candidate mismatch: {db_candidate_name} != {offer_data['candidate']}"

            assert db_manager_username == offer_data["manager_id"], \
                f"Manager mismatch: {db_manager_username} != {offer_data['manager_id']}"

            assert db_note == offer_data["note"], \
                f"Note mismatch: {db_note} != {offer_data['note']}"

            # Verify dates (converting to string format for comparison)
            db_from_date = db_contract_from.strftime("%Y-%m-%d")
            db_to_date = db_contract_to.strftime("%Y-%m-%d")

            assert db_from_date == offer_data["contract_from"], \
                f"Contract from date mismatch: {db_from_date} != {offer_data['contract_from']}"

            assert db_to_date == offer_data["contract_to"], \
                f"Contract to date mismatch: {db_to_date} != {offer_data['contract_to']}"

            print(f"✓ Verified offer in database for: {offer_data['candidate']}")
            return True

        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def login(self, username='admin', password='123123'):
        """Login to application"""
        # self.page.goto("http://103.56.158.135:5173/login")
        self.page.goto("http://localhost:5173/login")
        self.page.fill("input[placeholder='Username']", username)
        self.page.fill("input[placeholder='Password']", password)
        self.page.click("button[type='submit']")

    def test_hr_create_offer(self):
        """Test creating offers"""
        self.login()
        offer_data = self.__class__.offer_data

        def fill_offer_form(offer_data):
            try:
                # Click Add Offer button
                self.page.click("text='Add Offer'")

                # Select Candidate
                # self.page.click("[data-testid='select-offer-candidate']")
                # self.page.click(f"div[title^='{offer_data['candidate_id']}']")

                # Select Department
                self.page.click("[data-testid='select-offer-department']")
                self.page.click(f"div[title='{offer_data['department']}']")

                self.page.click("[data-testid='select-offer-candidate']")
                self.page.click(f"div[title='{offer_data['candidate']}']")

                self.page.click("[data-testid='select-offer-approver']")
                self.page.click(f"div[title='{offer_data['manager_id']}']")
                # Select Status
                self.page.click("[data-testid='select-offer-status']")
                self.page.click(f"div[title='{offer_data['status']}']")

                # Select Contract Type
                self.page.click("[data-testid='select-offer-contract']")
                self.page.click(f"div[title='{offer_data['type']}']")

                # Set Contract From Date
                self.page.click("[data-testid='select-offer-from']")
                self.page.fill("#layout-multiple-horizontal_contract_from", offer_data["contract_from"], timeout=1000)
                self.page.click("text='ADD OFFER'")

                # Set Contract To Date
                self.page.click("[data-testid='select-offer-to']")
                self.page.fill("#layout-multiple-horizontal_contract_to", offer_data["contract_to"], timeout=1000)
                self.page.click("text='ADD OFFER'")

                # Fill Basic Salary
                self.page.fill("[data-testid='input-offer-salary']", offer_data["basic_salary"], timeout=1000)

                # Fill Note
                self.page.fill("[data-testid='input-offer-note']", offer_data["note"], timeout=1000)

                # Submit form
                self.page.click("button:text('Submit')")
                print(f"✓ Created offer for: {offer_data['candidate']}")

                # Wait for submission
                self.page.wait_for_timeout(1000)

            except Exception as e:
                print(f"❌ Error in creating offer: {e}")
                raise

        try:
            # Navigate to Offer page
            self.page.click("a[href='/offer']")
            print("✓ Navigated to Offer page")

            # Create each offer
            for offer in offer_data:
                fill_offer_form(offer)
                self.verify_offer_in_db(offer)

            print("\n🎉 All offers created successfully 🎉")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    def test_hr_edit_offer(self):
        """Test edit offers"""
        offer_data = []

        for offer in self.__class__.offer_data:
            offer['status'] = 'Approved offer'
            offer_data.append(offer)

        def fill_offer_form(offer):
            try:
                # Click Add Offer button
                candidate_name = offer['candidate']
                self.page.click(f"td.ant-table-cell:has-text('{candidate_name}')")

                # Select Status
                self.page.click("[data-testid='select-offer-status']")
                self.page.click(f"div[title='{offer['status']}']")

                # Submit form
                self.page.click("button:text('Submit')")
                print(f"✓ edited offer for: {offer['candidate']}")

                # Wait for submission
                self.page.wait_for_timeout(1000)

            except Exception as e:
                print(f"❌ Error in creating offer: {e}")
                raise

        def verify_db(offer_data):
            verify_query = """
                            SELECT 
                                o.status
                            FROM public.offer o
                            LEFT JOIN public.candidate c ON o.candidate_id = c.id
                            LEFT JOIN public.user u ON o.manager_id = u.id
                            WHERE candidate_id IN (
                                SELECT id FROM public.candidate
                                WHERE full_name = %s
                            )
                        """

            # Chuyển candidate thành tuple chứa một phần tử
            self.cursor.execute(verify_query, (
                (offer_data["candidate"],)  # Truyền tuple chứa một phần tử (tên ứng viên)
            ))

            result = self.cursor.fetchone()

            assert result is not None, f"Offer for {offer_data['candidate']} not found in database"

            assert result[0] == offer_data["status"], \
                f"Status mismatch: {result[0]} != {offer_data['status']}"

            print(f"✓ Verified offer in database for: {offer_data['candidate']}")
            return True

        try:
            # Navigate to Offer page
            self.page.click("a[href='/offer']")
            print("✓ Navigated to Offer page")

            for offer in offer_data:
                fill_offer_form(offer)
                verify_db(offer)
                self.__class__.candidate_edited.append(offer['candidate'])

            print("\n🎉 All offers created successfully 🎉")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    def test_hr_delete_offer(self):
        # Test delete offers
        offer_data = self.__class__.offer_data

        def fill_offer_form(id):
            try:
                # delete
                self.page.click(f"[data-testid='{id}']")
                self.page.click(".ant-btn-primary.ant-btn-sm.ant-btn-dangerous")

                # Wait for submission
                self.page.wait_for_timeout(1000)

            except Exception as e:
                print(f"❌ Error in creating offer: {e}")
                raise

        def verify_db(offer,id):
            verify_query = """
                SELECT deleted
                FROM public.offer
                WHERE id = %s
            """

            self.cursor.execute(verify_query, (id,))

            result = self.cursor.fetchone()

            assert result is not None, f"Offer for {offer['candidate']} not found in database"

            # Unpack database results
            (db_delete) = result

            # Verify essential fields
            assert str(db_delete) != None, \
                f"Xóa {offer['candidate']} không thành công"

        try:
            # Navigate to Offer page
            self.page.click("a[href='/offer']")
            print("✓ Navigated to Offer page")

            ids = self.__class__.offer_ids

            for i in range(len(ids)):
                fill_offer_form(ids[i])
                verify_db(offer_data[i] ,ids[i])

            print("\n🎉 All offers created successfully 🎉")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    @classmethod
    def teardown_class(cls):
        """Cleanup test data and close connections"""
        try:
            if cls.conn:
                candidate_names = [offer['candidate'] for offer in cls.offer_data]

                delete_offers_query = """
                    DELETE FROM public.offer
                    WHERE candidate_id IN (
                        SELECT id FROM public.candidate
                        WHERE full_name IN %s
                    )
                """

                cls.cursor.execute(delete_offers_query, (tuple(candidate_names),))
                cls.conn.commit()

                candidate_edited = cls.candidate_edited
                update_candidates_query = """
                    UPDATE public.candidate
                    SET status = 'Passed interview'
                    WHERE full_name IN %s
                """
                cls.cursor.execute(update_candidates_query, (tuple(candidate_edited),))
                cls.conn.commit()

                print("Test offers rollback successfully")
                # Verify deletion
                verify_query = """
                    SELECT o.* FROM public.offer o
                    WHERE candidate_id IN (
                        SELECT id FROM public.candidate
                        WHERE full_name IN %s
                    )
                """
                cls.cursor.execute(verify_query, (tuple(candidate_edited),))
                remaining = cls.cursor.fetchall()
                if not remaining:
                    print("All test offers successfully removed")
                else:
                    print(f"Some test offers remain: {remaining}")

                cls.cursor.close()
                cls.conn.close()
                print("PostgreSQL connection closed")
        except Exception as e:
            print(f"Cleanup error: {str(e)}")
        finally:
            cls.context.close()
            cls.browser.close()
