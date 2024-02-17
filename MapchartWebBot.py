print('hello world')

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.accept_insecure_certs = True
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

service = Service(executable_path='C:/Users/Ryan/Documents/ChromeDriver/chromedriver-win64/chromedriver.exe')
browser = webdriver.Chrome(service=service, options=options)
browser.get("https://www.google.com")
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID, 'APjFqb'))).click()
WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'APjFqb'))).send_keys('xyz')


#browser = webdriver.Chrome()
browser.get("https://www.mapchart.net/usa-counties.html")
time.sleep(6)

# wait until the 'Save - Upload map configuration' button is clickable and click it
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID, 'downup'))).click()
#button = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, "downup")))

with open('OutputTemplate.txt', 'r') as file:
    data = file.read()

# wait until the textarea is present and paste the text 'xyz' into it
WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'upload-textarea'))).send_keys(data)

# wait until the 'upload-config' button is clickable and click it
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID, 'upload-config'))).click()

time.sleep(20)

print('End of Webbot script')