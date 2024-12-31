from playwright.sync_api import sync_playwright, expect
import time
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta


class TestUser:
    @classmethod
    def setup_class(cls):
        """Setup test environment and database connection"""
        playwright = sync_playwright().start()
        cls.browser = playwright.chromium.launch(headless=False)
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

        user_data = [
            {
                "full_name": "Auto test user 8",
                "email": "testlm008@gmail.com",
                "username": "testlm008",
                "department": "PR",
                "role": "Interviewer",
                "status":"Active",
                "note": "test note 8",
            },
            {
                "full_name": "Auto test user 9",
                "email": "testlm009@gmail.com",
                "username": "testlm009",
                "department": "Marketing",
                "role": "Admin",
                "status":"Active",
                "note": "test node 9",
            },
        ]

        cls.user_data = user_data
        cls.user_ids = []

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
        self.page.goto("http://103.56.158.135:5173/login")
        # self.page.goto("http://localhost:5173/login")
        self.page.fill("input[placeholder='Username']", username)
        self.page.fill("input[placeholder='Password']", password)
        self.page.click("button[type='submit']")

    def test_hr_create_user(self):
        self.login()
        user_data = self.__class__.user_data

        def verify_db(user_data):
            time.sleep(2)
            """Verify user data in database"""
            try:
                # Add delay to ensure data is saved
                time.sleep(2)
                # Query để kiểm tra user trong database
                verify_query = """
                    SELECT 
                      id,
                      full_name,
                      email,
                      department,
                      role,
                      note
                    FROM public.user
                    WHERE email = %s
                    LIMIT 1
                """

                self.cursor.execute(verify_query, (
                    user_data["email"],
                ))

                result = self.cursor.fetchone()
                assert result is not None, f"User {user_data['full_name']} not found in database"

                # Unpack database results
                (id, db_full_name, db_email, db_department, db_role, db_note) = result
                self.__class__.user_ids.append(id)

                # Verify essential fields
                assert db_full_name == user_data["full_name"], \
                    f"Title mismatch: {db_full_name} != {user_data['full_name']}"
                
                # assert self.find(data['full_name']), timeout(5000)

                assert db_email == user_data["email"], \
                    f"Email mismatch: {db_email} != {user_data['email']}"

                assert db_department == user_data["department"], \
                    f"Department mismatch: {db_department} != {user_data['department']}"

                assert db_role == user_data["role"], \
                    f"Role mismatch: {db_role} != {user_data['role']}"

                assert db_note == user_data["note"], \
                    f"Note mismatch: {db_note} != {user_data['note']}"

                print(f"✓ Verified user in database: {user_data['full_name']}")
            except AssertionError as ae:
                print(f"❌ Verification failed: {str(ae)}")
                raise
            except Exception as e:
                print(f"❌ Database verification error: {str(e)}")
                raise

        def fill_user_form(user_data):
            try:
                # Click Add User button
                self.page.click("text='Add User'")
                self.page.click(
                    "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
                self.page.click(f"div[title='{user_data['department']}']")

                self.page.click(
                    "form div.ant-form-item:has(> div label:text('Role')) .ant-select-selector")
                self.page.click(f"div[title='{user_data['role']}']")
                # Fill full name
                self.page.fill(
                    "input[placeholder='Enter full name']", user_data["full_name"])
                # Fill email
                self.page.fill(
                    "input[placeholder='Enter email']", user_data["email"])
                # Fill username
                self.page.fill(
                    "input[placeholder='Enter username']", user_data["username"])
                #Click status
                self.page.click(
                    f"div[data-testid='status-select']")
                self.page.click(f"div[title='{user_data['status']}']")
                # Fill note
                self.page.fill(
                    "textarea[placeholder='Enter note']", user_data["note"])

                # Click submit
                self.page.click("button:text('Submit')")
                print(f"✓ Created user: {user_data['full_name']}")

            except Exception as e:
                print(f"❌ Error in creating user: {e}")
                raise

        try:
            self.page.click("a[href='/user']")
            print("✓ Navigated to Job page")
            for user in user_data:
                fill_user_form(user)
                verify_db(user)
            print("\n🎉 All users created successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test create failed: {e}")
            raise

    def test_hr_edit_user(self):
        user_data = []
        for user in self.__class__.user_data:
            user['full_name'] = 'Change-' + user['full_name']
            user['email'] = 'change-' + user['email']
            user['username'] = 'Change-' + user['username']
            user['department'] = 'AF'
            user['role'] = 'Manager'
            user['status'] = "Deactivated"
            user['note'] = 'Change'
            user_data.append(user)

        def fill_user_form(user):
            try:
                full_name = user['full_name'].split('-')[1]
                self.page.click("a[href='/user']")
                print("✓ Navigated to Interview page")

                self.page.click(
                    f"td.ant-table-cell:has-text('{full_name}')")

                self.page.click(
                    "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
                self.page.click(f"div[title='{user['department']}']")

                self.page.click(
                    "form div.ant-form-item:has(> div label:text('Role')) .ant-select-selector")
                self.page.click(f"div[title='{user['role']}']")
                # Fill full name
                self.page.fill(
                    "input[placeholder='Enter full name']", user["full_name"])
                # Fill email
                self.page.fill(
                    "input[placeholder='Enter email']", user["email"])
                # Fill username
                self.page.fill(
                    "input[placeholder='Enter username']", user["username"])
                #Click status
                self.page.click(
                    f"div[data-testid='status-select']")
                self.page.click(f"div[title='{user['status']}']")
                # Fill note
                self.page.fill(
                    "textarea[placeholder='Enter note']", user["note"])
                # Submit form
                self.page.click("button:text('Submit')")
                print(f"✓ Edited user: {full_name}")

            except Exception as e:
                print(f"❌ Error in creating user: {e}")
                raise

        def verify_db(user):
            time.sleep(3)
            try:
                # Add delay to ensure data is saved
                time.sleep(2)
                # Query để kiểm tra user trong database
                verify_query = """
                    SELECT 
                      id,
                      full_name,
                      email,
                      department,
                      role,
                      note
                    FROM public.user
                    WHERE username = %s
                    AND email = %s
                    LIMIT 1
                """

                self.cursor.execute(verify_query, (
                    user["username"],
                    user["email"]
                ))

                result = self.cursor.fetchone()
                assert result is not None, f"User {user['full_name']} not found in database"

                # Unpack database results
                (id, db_full_name, db_email, db_department, db_role, db_note) = result
                self.__class__.user_ids.append(id)

                # Verify essential fields
                assert db_full_name == user["full_name"], \
                    f"Title mismatch: {db_full_name} != {user['full_name']}"

                assert db_email == user["email"], \
                    f"Email mismatch: {db_email} != {user['email']}"

                assert db_department == user["department"], \
                    f"Department mismatch: {db_department} != {user['department']}"

                assert db_role == user["role"], \
                    f"Role mismatch: {db_role} != {user['role']}"

                assert db_note == user["note"], \
                    f"Note mismatch: {db_note} != {user['note']}"

                print(f"✓ Verified user in database: {user['full_name']}")
            except AssertionError as ae:
                print(f"❌ Verification failed: {str(ae)}")
                raise
            except Exception as e:
                print(f"❌ Database verification error: {str(e)}")
                raise

        try:
            for user in user_data:
                fill_user_form(user)
                verify_db(user)
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    def test_hr_delete_user(self):
        user_data = self.__class__.user_data

        def fill_user_form(id):
            try:
                self.page.click(f"[data-testid='{id}']")
                self.page.click(
                    ".ant-btn-primary.ant-btn-sm.ant-btn-dangerous")
            except Exception as e:
                print(f"❌ Error in test delete user: {e}")
                raise

        def verify_db(user, id):
            verify_query = """
                SELECT deleted
                FROM public.user
                WHERE id = %s
            """

            self.cursor.execute(verify_query, (id,))

            result = self.cursor.fetchone()

            (db_delete) = result
            assert str(db_delete) != None, \
                f"Xóa {user['full_name']} không thành công"

        try:
            self.page.click("a[href='/user']")
            print("✓ Navigated to Interview page")
            ids = self.__class__.user_ids

            for i in range(len(ids)):
                fill_user_form(ids[i])
                verify_db(user_data[i], ids[i])

            print("\n🎉 All users deleted successfully 🎉")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    @classmethod
    def teardown_class(cls):
        """Cleanup test data and close connections"""
        try:
            if cls.conn:
                # dọn user test
                user_emails = [user['email'] for user in cls.user_data]
                delete_users_query = """
                    DELETE FROM public.user 
                    WHERE email IN %s
                """
                cls.cursor.execute(delete_users_query, (tuple(user_emails),))
                cls.conn.commit()
                print("Test users deleted successfully")

                # xác nhận đã dọn
                verify_query = """
                    SELECT id FROM public.user 
                    WHERE email IN %s
                """
                cls.cursor.execute(verify_query, (tuple(user_emails),))
                remaining = cls.cursor.fetchall()
                if not remaining:
                    print("All test users successfully removed")
                else:
                    print(f"Some test users remain: {remaining}")

                cls.cursor.close()
                cls.conn.close()
                print("PostgreSQL connection closed")
        except Exception as e:
            print(f"Cleanup error: {str(e)}")
        finally:
            cls.context.close()
            cls.browser.close()
