import pytest
from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import time


class TestUserIntegration:
    @classmethod
    def setup_class(cls):
        cls.case_create_user_data = [
            {
                "input": {
                    "full_name": "Auto test *user1",
                    "email": "auto-test-1@gmail.com",
                    "username": "test01",
                    "department": "Marketing",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 1"
                }
            },
            {
                "input": {
                    "full_name": "Auto test *user2",
                    "email": "auto-test-2@gmail.com",
                    "username": "test02",
                    "department": "AF",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 2"
                }
            }
        ]
        cls.create_user_db_backup = []

        cls.case_edit_user_data = [
            {
                "input": {
                    "full_name": "Auto test *user3",
                    "email": "auto-test-3@gmail.com",
                    "username": "test03",
                    "department": "Marketing",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 3"
                },
                "validate": {
                    "full_name": "change-Auto test *user3",
                    "email": "change-auto-test-3@gmail.com",
                    "username": "change-test03",
                    "department": "Marketing",
                    "role": "Manager",
                    "status": "Active",
                    "note": "change-note 3"
                }
            },
            {
                "input": {
                    "full_name": "Auto test *user4",
                    "email": "auto-test-4@gmail.com",
                    "username": "test04",
                    "department": "AF",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 4"
                },
                "validate": {
                    "full_name": "change-Auto test *user4",
                    "email": "change-auto-test-4@gmail.com",
                    "username": "change-test04",
                    "department": "AF",
                    "role": "Manager",
                    "status": "Active",
                    "note": "change-note 4"
                }
            }
        ]
        cls.edit_user_db_backup = []

        cls.case_delete_user_data = [
            {
                "input": {
                    "full_name": "Auto test *user5",
                    "email": "auto-test-5@gmail.com",
                    "username": "test05",
                    "department": "Marketing",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 5"
                }
            },
            {
                "input": {
                    "full_name": "Auto test *user6",
                    "email": "auto-test-6@gmail.com",
                    "username": "test06",
                    "department": "AF",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 6"
                }
            }
        ]
        cls.delete_user_db_backup = []

        cls.case_verify_user_data = [
            {
                "input": {
                    "full_name": "Auto test *user9",
                    "email": "auto-test-9@gmail.com",
                    "username": "test09",
                    # "department": "Marketing",
                    # "role": "Manager",
                    "status": "Active",
                    "note": "note 9"
                },
                "validate": [
                    "Please select department", "Please enter role"
                ]
            },
            {
                "input": {
                    "full_name": "Auto test *user10",
                    "email": "auto-test-10@gmail.com",
                    # "username": "test010",
                    "department": "AF",
                    "role": "Manager",
                    "status": "Active",
                    "note": "note 10"
                },
                "validate": [
                    "Please enter username"
                ]
            }
        ]

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
        # context = self.browser.new_context()

        # self.page = context.new_page()
        """Login to application"""
        # self.page.goto("http://localhost:5173/login")
        self.page.goto("http://103.56.158.135:5173/login")
        self.page.fill("input[placeholder='Username']", username)
        self.page.fill("input[placeholder='Password']", password)
        self.page.click("button[type='submit']")

    def logout(self):
        self.page.click(".ant-dropdown-trigger")
        self.page.click(".ant-dropdown-menu-item:last-child")

    # create
    def action_ui_create_user(self, user):
        try:
            self.page.click("a[href='/user']")

            self.page.click("text='Add User'")
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
            # Click status
            self.page.click(
                f"div[data-testid='status-select']")
            self.page.click(f"div[title='{user['status']}']")
            # Fill note
            self.page.fill(
                "textarea[placeholder='Enter note']", user["note"])
            # Click submit
            self.page.click("button:text('Submit')")
            print(f"✓ Created user: {user['full_name']}")
        except Exception as e:
            print(f"❌ Test action create user {user['full_name']} failed: {e}")
            raise

    def verify_db_create_user(self, user):
        time.sleep(2)
        try:
            query = """
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

            self.cursor.execute(query, (
                user["email"],
            ))
            result = self.cursor.fetchone()
            assert result is not None, f"User {user['full_name']} not found in database"
            self.create_user_db_backup.append(result['id'])
            assert result['full_name'] == user["full_name"], \
                f"Full name mismatch: {result['full_name']} != {user['full_name']}"
            assert result['email'] == user["email"], \
                f"Email mismatch: {result['email']} != {user['email']}"
            assert result['department'] == user["department"], \
                f"Department mismatch: {result['department']} != {user['department']}"
            assert result['role'] == user["role"], \
                f"Role mismatch: {result['role']} != {user['role']}"
            assert result['note'] == user["note"], \
                f"Note mismatch: {result['note']} != {user['note']}"

            print(f"✓ Verified user in database: {user['full_name']}")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_create_user(self):
        self.login()
        try:
            for case in self.case_create_user_data:
                user = case['input']
                self.action_ui_create_user(user)
                self.verify_db_create_user(user)

            print("\n🎉 All users create successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete user failed: {e}")
            raise

    # edit
    def get_state_db_edit_user(self, user):
        """Lấy trạng thái người dùng từ cơ sở dữ liệu"""
        where_conditions = []
        values = []
        for key, value in user.items():
            where_conditions.append(f"{key} = %s")
            values.append(value)

        query = f"SELECT * FROM public.user WHERE {' AND '.join(where_conditions)};"

        self.cursor.execute(query, tuple(values))
        record = self.cursor.fetchone()

        if record:
            self.edit_user_db_backup.append(record)
            return record['id']
        return None

    def action_ui_edit_user(self, id, user):
        try:
            self.page.click("a[href='/user']")

            element = self.page.locator(
                "span.ant-select-selection-item[title='10 / page']")
            if element.is_visible():
                self.page.click(
                    "span.ant-select-selection-item[title='10 / page']")
                self.page.click(
                    "div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid-edit='{id}']")
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
            # Click status
            self.page.click(
                f"div[data-testid='status-select']")
            self.page.click(f"div[title='{user['status']}']")
            # Fill note
            self.page.fill(
                "textarea[placeholder='Enter note']", user["note"])
            # Click submit
            self.page.click("button:text('Submit')")
            print(f"\n✓ edit user: {user['full_name']}")
        except Exception as e:
            print(f"❌ Test action edit user {user['full_name']} failed: {e}")
            raise

    def verify_db_edit_user(self, id, user):
        time.sleep(2)
        try:
            query = """
                SELECT 
                    id,
                    full_name,
                    email,
                    department,
                    role,
                    note
                FROM public.user
                WHERE id = %s
                LIMIT 1
            """

            self.cursor.execute(query, (id,))
            result = self.cursor.fetchone()
            assert result is not None, f"User {user['full_name']} not found in database"
            assert result['full_name'] == user["full_name"], \
                f"Full name mismatch: {result['full_name']} != {user['full_name']}"
            assert result['email'] == user["email"], \
                f"Email mismatch: {result['email']} != {user['email']}"
            assert result['department'] == user["department"], \
                f"Department mismatch: {result['department']} != {user['department']}"
            assert result['role'] == user["role"], \
                f"Role mismatch: {result['role']} != {user['role']}"
            assert result['note'] == user["note"], \
                f"Note mismatch: {result['note']} != {user['note']}"

            print(f"✓ Verified user in database: {user['full_name']}")
        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_edit_user(self):
        # self.login()
        try:
            for case in self.case_edit_user_data:
                input_data = case['input']
                user_id = self.get_state_db_edit_user(input_data)
                self.action_ui_edit_user(user_id, case['validate'])
                self.verify_db_edit_user(user_id, case['validate'])

            print("\n🎉 All users edit successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete user failed: {e}")
            raise

    # delete
    def get_state_db_delete_user(self, user):
        """Lấy trạng thái người dùng từ cơ sở dữ liệu"""
        where_conditions = []
        values = []
        for key, value in user.items():
            where_conditions.append(f"{key} = %s")
            values.append(value)

        query = f"SELECT * FROM public.user WHERE {' AND '.join(where_conditions)};"

        self.cursor.execute(query, tuple(values))
        record = self.cursor.fetchone()

        if record:
            self.delete_user_db_backup.append(record)
            return record['id']
        return None

    def action_ui_delete_user(self, id):
        try:
            self.page.click("a[href='/user']")

            element = self.page.locator(
                "span.ant-select-selection-item[title='10 / page']")
            if element.is_visible():
                self.page.click(
                    "span.ant-select-selection-item[title='10 / page']")
                self.page.click(
                    "div.ant-select-item-option-content:has-text('50 / page')")
            self.page.click(f"[data-testid='{id}']")
            self.page.click(".ant-btn-primary.ant-btn-sm.ant-btn-dangerous")
        except Exception as e:
            print(f"❌ Test action delete user failed: {e}")
            raise

    def verify_db_delete_user(self, id):
        query = """
            SELECT
                deleted
            FROM public.user
            WHERE id = %s
        """
        self.cursor.execute(query, (id,))
        record = self.cursor.fetchone()

        assert str(record['deleted']) != None, \
            f"Xóa user {id} không thành công"

    def test_delete_user(self):
        # self.login()
        try:
            for case in self.case_delete_user_data:
                input_data = case['input']
                user_id = self.get_state_db_delete_user(input_data)
                self.action_ui_delete_user(user_id)
                self.verify_db_delete_user(user_id)

            print("\n🎉 All users deleted successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete user failed: {e}")
            raise

    # verify
    def action_ui_verify_user(self, user):
        try:
            time.sleep(2)
            self.page.reload()
            self.page.click("a[href='/user']")

            self.page.click("text='Add User'")
            if ("department" in user):
                self.page.click(
                    "form div.ant-form-item:has(> div label:text('Department')) .ant-select-selector")
                self.page.click(f"div[title='{user['department']}']")
            if ("role" in user):
                self.page.click(
                    "form div.ant-form-item:has(> div label:text('Role')) .ant-select-selector")
                self.page.click(f"div[title='{user['role']}']")
            if ("full_name" in user):
                self.page.fill(
                    "input[placeholder='Enter full name']", user["full_name"])
            if ("email" in user):
                self.page.fill(
                    "input[placeholder='Enter email']", user["email"])
            if ("username" in user):
                self.page.fill(
                    "input[placeholder='Enter username']", user["username"])
            if ("status" in user):
                self.page.click(
                    f"div[data-testid='status-select']")
                self.page.click(f"div[title='{user['status']}']")
            if ("note" in user):
                self.page.fill(
                    "textarea[placeholder='Enter note']", user["note"])

            # Click submit
            self.page.click("button:text('Submit')")
            print(f"✓ Created user: {user['full_name']}")
        except Exception as e:
            print(f"❌ Test action create user {user['full_name']} failed: {e}")
            raise

    def verify_db_verify_user(self, user):
        time.sleep(2)
        try:
            for mes in user:
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

    def test_verify_user(self):
        # self.login()
        try:
            for case in self.case_verify_user_data:
                self.action_ui_verify_user(case['input'])
                self.verify_db_verify_user(case['validate'])

            print("\n🎉 All users create successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete user failed: {e}")
            raise
        self.page.reload()
        self.logout()

    # role
    def verify_role(self):
        time.sleep(2)
        try:
            request = self.page.locator(
                f"a[href='/request']")
            assert request.count() == 0, \
                f"Phân quyền truy cập sai /request"

            offer = self.page.locator(
                f"a[href='/offer']")
            assert offer.count() == 0, \
                f"Phân quyền truy cập sai /offer"

            user = self.page.locator(
                f"a[href='/user']")
            assert user.count() == 0, \
                f"Phân quyền truy cập sai /user"

            print(f"✓ Verified role offer")
        except AssertionError as ae:
            print(f"❌ Verification role failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ verification error: {str(e)}")
            raise

    def test_role_user(self):

        self.login("linh.nv1", "123456")
        try:
            self.verify_role()
            print("\n🎉 All users create successfully 🎉")
        except Exception as e:
            print(f"\n❌ Test delete user failed: {e}")
            raise

    @classmethod
    def backup_create_user(cls):
        try:
            ids = cls.create_user_db_backup
            placeholders = ', '.join(['%s'] * len(ids))
            delete_query = f"""
                DELETE FROM public.user
                WHERE id IN ({placeholders})
            """

            cls.cursor.execute(delete_query, tuple(ids))
            cls.conn.commit()
            print(f"✅ User {ids} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore user: {e}")

    @classmethod
    def backup_edit_user(cls):
        try:
            for user in cls.edit_user_db_backup:
                columns = ', '.join(user.keys())
                values = tuple(user.values())
                update_query = f"""
                    UPDATE public.user
                    SET ({columns}) = ({', '.join(['%s'] * len(user))})
                    WHERE id = %s
                """
                cls.cursor.execute(update_query, (*values, user['id']))
                cls.conn.commit()

                print(f"✅ User {user['id']} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore user: {e}")

    @classmethod
    def backup_delete_user(cls):
        try:
            for user in cls.delete_user_db_backup:
                columns = ', '.join(user.keys())
                values = tuple(user.values())
                update_query = f"""
                    UPDATE public.user
                    SET ({columns}) = ({', '.join(['%s'] * len(user))})
                    WHERE id = %s
                """
                cls.cursor.execute(update_query, (*values, user['id']))
                cls.conn.commit()

                print(f"✅ User {user['id']} restored successfully.")
        except Exception as e:
            print(f"❌ Failed to restore user: {e}")

    @classmethod
    def teardown_class(cls):
        """Dọn dẹp tài nguyên sau khi kiểm tra xong"""
        try:
            cls.backup_create_user()
            cls.backup_edit_user()
            cls.backup_delete_user()
            if cls.conn:
                cls.cursor.close()
                cls.conn.close()
                print("PostgreSQL connection closed")
        except Exception as e:
            print(f"❌ Cleanup error: {str(e)}")
        finally:
            cls.context.close()
            cls.browser.close()
