from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from driver_setup import driver
from termcolor import colored

ID = input('Enter username:\n')
PASSWORD = input('Enter password:\n')
# PATH = "/home/blackhawk/tools/webdriver/chrome/chromedriver"
PATH =driver()
frequency = 3


def add(hour, val):
    return str(int(hour) + val)


def ryt_now():
    cur_time = time.localtime()
    cur_time = time.strftime("%H:%M:%S", cur_time)
    return cur_time


def get_time():
    cur_time = ryt_now()
    hour, mn, sec = cur_time.split(':')
    if int(mn) >= 40:
        hour = str((int(hour) + 1))
    return hour


def do_login(username, password):
    id_field = driver.find_element_by_xpath("//input[@placeholder='Username']")
    pass_field = driver.find_element_by_xpath("//input[@placeholder='Password']")

    id_field.send_keys(username)
    pass_field.send_keys(password)

    pass_field.send_keys(Keys.RETURN)
    message = driver.find_element_by_xpath("//a[@title='Click here to view Meetings']")
    message.send_keys(Keys.RETURN)


def process_hr(cur_hr, minutes):
    if int(cur_hr) > 12:
        cur_hr = str((int(cur_hr) - 12))
    cur = str((minutes + 60) % 60)
    if len(cur) < 2:
        cur = '0' + cur
    return cur_hr + ':' + cur


# check for classes from cur time t in order t - 1, t, t + 1
# handle false positive of night
# can be more efficient
def check_for_class(hour):
    print(colored('[+] Checking for ongoing class', 'cyan'))
    for cur_hr in [add(hour, -2), add(hour, -1), hour, add(hour, 1)]:
        for minutes in range(0, 60):
            val = process_hr(cur_hr, minutes)
            # print('Checking class at', val)
            try:
                path = "//div[@data-start='" + val + "']"
                current_class = driver.find_element_by_xpath(path)
                extra_check = current_class.get_attribute('data-full')
                if len(extra_check) > 8:
                    continue
                print(val, ' - Class Found')
                current_class.find_element_by_xpath("./../..").send_keys(Keys.RETURN)
                return True
            except:
                pass
    return False


# not working
def greet():
    driver.switch_to.frame(driver.find_element_by_id('frame'))
    elem = driver.find_element_by_id('app')
    print(elem.get_attribute('role'))


# done
def do_polls():
    poll_number = 1
    print('Starting poll daemon')
    driver.switch_to.frame(driver.find_element_by_id('frame'))
    while True:
        try:
            wait = WebDriverWait(driver, 5)
            element = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[starts-with(@aria-labelledby,"pollAnswerLabel")]')))
            element.click()
            print('[+]', poll_number, 'poll marked.')
            poll_number += 1
        except:
            pass
        try:
            wait = WebDriverWait(driver, 10)
            element = wait.until(
                EC.presence_of_element_located((By.XPATH, '//button[@description="Logs you out of the meeting""]')))
            print('Class Finished')
            element.click()
            return
        except:
            pass


def join():
    try:
        # wait = WebDriverWait(driver, 3600)
        # wait.until(EC.visibility_of_element_located(By.ID("//a[@role='button']")))
        driver.find_element_by_class_name('btn').send_keys(Keys.RETURN)
        time.sleep(6)
        driver.switch_to.frame(driver.find_element_by_id('frame'))
        driver.find_element_by_xpath('//button[@aria-label="Listen only"]').send_keys(Keys.RETURN)
        driver.switch_to.default_content()
        return True
    except:
        driver.quit()
        print('Join Button not available. Retrying in 3 minutes')
        time.sleep(3 * 60)
        return False


def abort():
    print('Aborting')
    driver.quit()
    exit(0)


have_class = False
while True:
    chrome_options = webdriver.ChromeOptions()
    # uncomment line below to hide the class tab
    # chrome_options.headless = True
    driver = webdriver.Chrome(PATH, options=chrome_options)
    # driver.minimize_window()
    driver.get("http://myclass.lpu.in")

    try:
        do_login(ID, PASSWORD)
    except:
        print('Probably your credentials are invalid')
        abort()

    hr = get_time()
    if int(hr) >= 20:
        print('No classes are scheduled after 8 pm')
        abort()

    have_class = check_for_class(hr)

    if have_class and join():
        do_polls()
        driver.quit()
        print('Class finished, Restarting Daemon For other classes')
    else:
        print("No ongoing lectures found at", ryt_now())
        driver.quit()
        print('Sleeping for', frequency, 'minutes')
        time.sleep(frequency * 60)
