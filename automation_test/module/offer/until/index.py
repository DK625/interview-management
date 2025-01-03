def login(self, username='admin', password='123123'):
    """Login to application"""
    # self.page.goto("http://103.56.158.135:5173/login")
    self.page.goto("http://localhost:5173/login")
    self.page.fill("input[placeholder='Username']", username)
    self.page.fill("input[placeholder='Password']", password)
    self.page.click("button[type='submit']")
