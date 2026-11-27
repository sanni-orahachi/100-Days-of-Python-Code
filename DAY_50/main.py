from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

TINDOG_URL = "https://app.100daysofpython.dev/services/tindog/u/ESQvUDtzPz5oTMcJ5XJdw1OtXxSxaUBP"
EMAIL = "test@gmail.com"
PASSWORD = "123456"
wait = WebDriverWait(driver, timeout=3)

driver.get(TINDOG_URL)
driver.maximize_window()
login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".tindog-login-pill")))
login_button.click()

facebark_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-facebark.tindog-login-method")))
facebark_button.click()

wait.until(EC.number_of_windows_to_be(2))

driver.switch_to.window(driver.window_handles[1])
email = wait.until(EC.presence_of_element_located((By.NAME, "email")))
email.send_keys(EMAIL)
password = wait.until(EC.presence_of_element_located((By.NAME, "pass")))
password.send_keys(PASSWORD)
submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
submit_button.click()

wait.until(EC.number_of_windows_to_be(1))
driver.switch_to.window(driver.window_handles[0])
allow_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary")))
allow_button.click()
disable_notifs_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-secondary")))
disable_notifs_button.click()


def cookies():
    cookies_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary")))
    cookies_button.click()


try:
    cookies()
except StaleElementReferenceException:
    cookies()
    print("There was a slight issue. Sorry!")

for i in range(20):
    like_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-like")))

    driver.execute_script("""
        window.scrollTo(0, document.documentElement.scrollHeight);
        arguments[0].click();
    """, like_button)

    try:
        match_found = wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".match-popup"),
                "It's a Match!"
            )
        )

        if match_found:
            continue_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".match-popup-link"))
            )
            continue_button.click()

    except TimeoutException:
        pass

print("Program ran successfully!")
