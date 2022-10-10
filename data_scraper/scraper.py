import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# options
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

# run driver
cwd = os.path.realpath(__file__)
DRIVER_PATH = '/'.join(cwd.split('/')[:-1]) + '/bin/chromedriver'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get('https://google.com')
# print(driver.page_source)
print(driver.title)
print(driver.current_url)
# https://selenium-python.readthedocs.io/locating-elements.html
element = driver.find_element(By.CLASS_NAME, 'gNO89b')
print(element.get_attribute('value')) # element.text, element.send_keys('mypassword'), element.click()

driver.quit()