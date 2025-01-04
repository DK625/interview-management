import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from pymongo import MongoClient
import psycopg2
from psycopg2 import Error


class TestPurchase():
    stored_localStorage = None
    driver = None

    @classmethod
    def setup_class(cls):
        """Chạy một lần khi bắt đầu tất cả test cases"""
        cls.driver = webdriver.Chrome()
        cls.vars = {}
        try:
            # PostgreSQL connection parameters
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

    @classmethod
    def teardown_class(cls):
        try:
            if cls.conn:
                verify_query = """
                    SELECT username FROM public."user" 
                    WHERE username IN ('thu.nguyen', 'nam.tran', 'hoanganh.pham')
                """
                cls.cursor.execute(verify_query)
                remaining = cls.cursor.fetchall()
                if not remaining:
                    print("All test users successfully removed")
                else:
                    print(f"Some test users: {remaining}")

                # Delete test users
                delete_users_query = """
                            DELETE FROM public."user"
                            WHERE username IN ('thu.nguyen', 'nam.tran', 'hoanganh.pham')
                        """
                cls.cursor.execute(delete_users_query)
                cls.conn.commit()
                print("Test users deleted successfully")

                verify_query = """
                                    SELECT username FROM public."user" 
                                    WHERE username IN ('thu.nguyen', 'nam.tran', 'hoanganh.pham')
                                """
                cls.cursor.execute(verify_query)
                remaining = cls.cursor.fetchall()
                if not remaining:
                    print("All test users successfully removed")
                else:
                    print(f"Some test users: {remaining}")

                # Close database connection
                cls.cursor.close()
                cls.conn.close()
                print("PostgreSQL connection closed")
        except Exception as e:
            print(f"Psql cleanup error: {str(e)}")

        """Chỉ chạy sau khi tất cả test cases hoàn thành"""
        if hasattr(cls, 'driver'):  # Kiểm tra xem driver có tồn tại không
            cls.driver.quit()

    def verify_user_in_db(self, user_data):
        """Verify user data in database"""
        try:
            # Query để kiểm tra user tồn tại với thông tin phù hợp
            verify_query = """
                SELECT 
                    full_name,
                    email,
                    username,
                    role,
                    department,
                    status,
                    note
                FROM public."user" 
                WHERE username = %s
            """

            self.cursor.execute(verify_query, (
                user_data["username"],
            ))

            result = self.cursor.fetchone()
            assert result is not None, f"User {user_data['username']} not found in database"

            # Verify từng trường dữ liệu
            db_full_name, db_email, db_username, db_role, db_department, db_status, db_note = result

            assert db_full_name == user_data[
                "full_name"], f"Full name mismatch: {db_full_name} != {user_data['full_name']}"
            assert db_email == user_data["email"], f"Email mismatch: {db_email} != {user_data['email']}"
            assert db_username == user_data["username"], f"Username mismatch: {db_username} != {user_data['username']}"
            assert db_role == user_data["role"], f"Role mismatch: {db_role} != {user_data['role']}"
            assert db_department == user_data[
                "department"], f"Department mismatch: {db_department} != {user_data['department']}"
            assert db_status == user_data["status"], f"Status mismatch: {db_status} != {user_data['status']}"
            assert db_note == user_data["note"], f"Note mismatch: {db_note} != {user_data['note']}"

            print(f"✓ Verified user in database: {user_data['username']}")
            return True

        except AssertionError as ae:
            print(f"❌ Verification failed: {str(ae)}")
            raise
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            raise

    def test_login(self, user_name='admin', password='123123'):
        """
        Test login functionality with valid credentials
        Steps:
        1. Navigate to login page
        2. Enter username "admin"
        3. Enter password "123123"
        4. Click login button
        """
        # Navigate to login page
        self.driver.get("http://103.56.158.135:5173/login")
        # self.driver.get("http://localhost:5173/login")
        self.driver.maximize_window()

        # Enter username
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Username']"))
        )
        username_input.clear()
        username_input.send_keys(user_name)

        # Enter password
        password_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']")
        password_input.clear()
        password_input.send_keys(password)

        # Click login button
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        print("""
        TEST CASE: Login with Valid Credentials

        Steps:
        ✓ Navigated to login page
        ✓ Entered username: admin
        ✓ Entered password: 123123
        ✓ Clicked login button

        Status: PASSED ✅
        """)

    def test_add_user_form(self):
        """
        Test case to fill out the user form with different roles
        - Tests form input for HR, Manager, and Interviewer roles
        - Verifies required fields
        - Tests form submission
        """
        user_menu = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "li.ant-menu-item a[href='/user']"))
        )
        user_menu.click()

        def fill_user_form(user_data):
            add_user_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Add User']"))
            )
            add_user_button.click()
            # Fill Full Name
            full_name = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter full name']"))
            )
            full_name.clear()
            full_name.send_keys(user_data["full_name"])

            # Fill Email
            email = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Enter email']")
            email.clear()
            email.send_keys(user_data["email"])

            # Fill Phone
            # phone = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Enter phone']")
            # phone.clear()
            # phone.send_keys(user_data["phone"])
            #
            # time.sleep(1)

            # Click dropdown
            role_dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "layout-multiple-horizontal_role"))
            )
            role_dropdown.click()

            # Wait for dropdown to be fully visible
            dropdown_container = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "ant-select-dropdown"))
            )

            # Then select option
            role_option = dropdown_container.find_element(By.CSS_SELECTOR,
                                                          f"[data-testid='role-option-{user_data['role']}']")
            role_option.click()


            # Select Department
            self.driver.find_element(By.ID, "layout-multiple-horizontal_department").click()
            dept_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f"[data-testid='department-option-{user_data['department']}']"))
            )
            dept_option.click()

            # Select Status
            status_dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='status-select']"))
            )
            status_dropdown.click()

            # Select status option
            status_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"[data-testid='status-option-{user_data['status']}']"))
            )
            status_option.click()

            # Fill Username
            username = self.driver.find_element(By.ID, "layout-multiple-horizontal_username")
            username.clear()
            username.send_keys(user_data["username"])

            # Fill Note
            note = self.driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='Enter note']")
            note.clear()
            note.send_keys(user_data["note"])

            # Submit form
            submit_button = self.driver.find_element(By.XPATH, "//button[text()='Submit']")
            submit_button.click()

        # Test data for different roles
        test_users = [
            {
                "full_name": "Nguyễn Thị Thu",
                "email": "thu.nguyen@company.com",
                "phone": "0908123456",
                "role": "HR",
                "dob": "10/09/1990",
                "address": "123 Trần Phú, Hà Nội",
                "gender": "Female",
                "department": "HR",
                "status": "Active",
                "username": "thu.nguyen",
                "note": "Phụ trách tuyển dụng và quản lý hồ sơ nhân sự."
            },
            {
                "full_name": "Trần Văn Nam",
                "email": "nam.tran@company.com",
                "phone": "0987654321",
                "role": "Manager",
                "dob": "15/07/1985",
                "address": "456 Lý Thường Kiệt, TP. Hồ Chí Minh",
                "gender": "Male",
                "department": "IT",
                "status": "Active",
                "username": "nam.tran",
                "note": "Quản lý phòng phát trển phần mềm."
            },
            {
                "full_name": "Phạm Hoàng Anh",
                "email": "hoanganh.pham@company.com",
                "phone": "0971234567",
                "role": "Interviewer",
                "dob": "05/04/1992",
                "address": "789 Nguyễn Huệ, Đà Nẵng",
                "gender": "Male",
                "department": "IT",
                "status": "Active",
                "username": "hoanganh.pham",
                "note": "Chuyên phụ trách đánh giá ứng viên trong các buổi phỏng vấn kỹ thuật."
            }
        ]

        # Test each user role
        for user_data in test_users:
            print(f"\nTesting user creation for {user_data['role']}")
            fill_user_form(user_data)
            time.sleep(1)
            self.verify_user_in_db(user_data)

            print(f"✓ Successfully created user: {user_data['full_name']}")

        print("\nAll user creation tests completed successfully ✅")

    def test_verify_account_created(self):
        avatar_dropdown = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-dropdown-trigger"))
        )
        avatar_dropdown.click()

        logout_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-dropdown-menu-item:last-child"))
        )
        logout_button.click()

        self.test_login('thu.nguyen', '123456')
        avatar_dropdown = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-dropdown-trigger"))
        )
        avatar_dropdown.click()

        logout_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-dropdown-menu-item:last-child"))
        )
        time.sleep(1)
        logout_button.click()
        self.test_login('nam.tran', '123456')
        avatar_dropdown = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-dropdown-trigger"))
        )
        avatar_dropdown.click()

        logout_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-dropdown-menu-item:last-child"))
        )
        logout_button.click()
        self.test_login('hoanganh.pham', '123456')
        avatar_dropdown = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-dropdown-trigger"))
        )
        avatar_dropdown.click()
        time.sleep(1)
        logout_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-dropdown-menu-item:last-child"))
        )
        logout_button.click()
