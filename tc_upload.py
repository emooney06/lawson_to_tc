from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
from selenium.webdriver.support.ui import WebDriverWait
import time
import pyautogui

upload_path = 'C:\\Users\Ethan\OneDrive\TigerConnect_MPaCC'
upload_subdir = 'tc_support_files'
upload_file = 'final_compiled_schedule.csv'

def drive_tc_upload():
    driver = webdriver.Chrome()
    driver.get("https://login.tigerconnect.com/app/messenger/index.html?_ga=2.103280259.2040127355.1581561402-2100901986.1581561402")
    driver.maximize_window()


    time.sleep(10)
    driver.find_element_by_xpath(".//*[@name='username']").send_keys('ejmooney@salud.unm.edu')

    continue_button = driver.find_element_by_xpath(".//*[@id='tc-SignInForm__UsernameForm']/form/div[3]")
    continue_button.click()
    time.sleep(7)

    driver.find_element_by_xpath(".//*[@id='tc-SignInForm__PasswordForm']/form/div[2]/div/input").send_keys('python#1')
    continue_button = driver.find_element_by_xpath(".//*[@id='tc-SignInForm__PasswordForm']/form/div[3]/button")
    continue_button.click()
    time.sleep(15)
    
    roles_button = driver.find_element_by_xpath(".//*[@id='app']/div/div[1]/div/div[2]/div/div[1]")
    roles_button.click()
    time.sleep(10)

    upload_cal_button = driver.find_element_by_xpath(".//*[@id='app']/div/div[2]/div[1]/div[1]/div/div/div[2]/div[2]")
    upload_cal_button.click()
    time.sleep(5)

    upload_tool = driver.find_element_by_xpath("./html/body/div[2]/div/div/ul/li[1]")
    upload_tool.click()
    time.sleep(3)
    
    pyautogui.moveTo(1300,850)
    pyautogui.click()
    time.sleep(3)
    pyautogui.typewrite(upload_path)
    pyautogui.press('enter')
    time.sleep(3)
    pyautogui.typewrite(upload_subdir)
    pyautogui.press('enter')
    time.sleep(3)
    pyautogui.typewrite(upload_file)
    pyautogui.press('enter')
    
drive_tc_upload()



#time.sleep(5)
#driver.find_element_by_xpath(".//*[@id='app']/div/div[2]/div[1]/div[1]/div/div/div[2]/div[2]")
#driver.find_element_by_xpath("./html/body/div[2]/div/div/ul/li[1]")

#driver.find_element_by_xpath("./html/body/div[6]/div/div/div/div[3]/button[2]")

#driver.find_elements_by_xpath('.//span[@class = "Select File"]')
#webelement.text('select file')
#for elem in driver.find_elements_by_xpath('.//span[@class = "select file"]'):
#    print(elem.text)

#id="root"

#element = driver.find_element_by_xpath("//a[@span='select file']").text()
#hrefs = element.find_elements_by_xpath("//a[@class='primary-button']")

#select_file = driver.find_element_by_xpath("./html/body/div[6]/div/div/div/div[3]/button[2]")
#hrefs = element.find_elements_by_xpath("//a[@class='primary-button']")


#select_file = driver.find_element_by_xpath("//*[contains(text(), 'Select File')]").format(text)

##<button class="primaryButton___3iAn0 button___u8AaY" aria-label="select file"><span>Select File</span></button>
##body > div:nth-child(7) > div > div > div > div.footer___zm2KI > button.primaryButton___3iAn0.button___u8AaY
##document.querySelector("body > div:nth-child(7) > div > div > div > div.footer___zm2KI > button.primaryButton___3iAn0.button___u8AaY")
##/html/body/div[6]/div/div/div/div[3]/button[2]
##/html/body/div[6]/div/div/div/div[3]/button[2]
##select_file = driver.find_element_by_xpath("./html/body/div[6]/div/div/div/div[3]/button[2]/span")

#select_file = driver.find_element_by_xpath("./html/body/div[6]/div/div/div/div[3]/button[2]/span")
#upload_tool.click()

#time.sleep(15)
#driver.close()

##elem = driver.find_element_by_name("q")
##elem.clear()
##elem.send_keys("pycon")
##elem.send_keys(Keys.RETURN)
##assert "No results found." not in driver.page_source
##driver.close()
