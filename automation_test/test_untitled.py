# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestUntitled():
  def setup_method(self, method):
    self.driver = webdriver.Chrome()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_untitled(self):
    self.driver.get("http://localhost:5173/")
    self.driver.set_window_size(1552, 840)
    self.driver.find_element(By.LINK_TEXT, "User").click()
    self.driver.find_element(By.CSS_SELECTOR, ".ant-btn > span:nth-child(2)").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_full_name").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_full_name").send_keys("dfsdf")
    self.driver.find_element(By.CSS_SELECTOR, ".w-full:nth-child(1) > .ant-form-item:nth-child(2) .ant-input-affix-wrapper").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_email").send_keys("sdfdsf")
    self.driver.find_element(By.ID, "layout-multiple-horizontal_phone").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_phone").send_keys("6565646546")
    self.driver.find_element(By.ID, "layout-multiple-horizontal_role").click()
    self.driver.find_element(By.CSS_SELECTOR, ".ant-select-item-option-active > .ant-select-item-option-content").click()
    self.driver.find_element(By.CSS_SELECTOR, ".ant-picker-input").click()
    element = self.driver.find_element(By.CSS_SELECTOR, ".ant-picker-header-super-next-btn")
    actions = ActionChains(self.driver)
    actions.move_to_element(element).perform()
    self.driver.find_element(By.CSS_SELECTOR, ".ant-picker-clear path").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_dob").send_keys("2002-02-02")
    self.driver.find_element(By.CSS_SELECTOR, ".w-full:nth-child(3)").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_address").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_address").send_keys("erereergr")
    self.driver.find_element(By.CSS_SELECTOR, ".w-full:nth-child(4)").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_gender").click()
    self.driver.find_element(By.CSS_SELECTOR, "div:nth-child(8) .ant-select-item:nth-child(2) > .ant-select-item-option-content").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_department").click()
    self.driver.find_element(By.CSS_SELECTOR, "div:nth-child(9) .ant-select-item:nth-child(2) > .ant-select-item-option-content").click()
    self.driver.find_element(By.CSS_SELECTOR, ".w-full:nth-child(5)").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_status").click()
    self.driver.find_element(By.CSS_SELECTOR, "div:nth-child(10) .ant-select-item:nth-child(2) > .ant-select-item-option-content").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_username").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_username").send_keys("dfhfdfhfdhfdhh")
    self.driver.find_element(By.ID, "layout-multiple-horizontal_note").click()
    self.driver.find_element(By.ID, "layout-multiple-horizontal_note").send_keys("dfhdfhfdhfdhfhfh")
    self.driver.find_element(By.CSS_SELECTOR, ".hover\\3A bg-blue-700").click()
  
