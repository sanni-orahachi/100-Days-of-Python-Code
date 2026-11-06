from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from time import sleep, time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://ozh.github.io/cookieclicker/")

sleep(3)

try:
    language = driver.find_element(By.CSS_SELECTOR, value="#langSelect-EN")
    language.click()
    print("Selected English as the language!")
except NoSuchElementException:
    print("No Language Menu")

try:
    got_it_button = driver.find_element(By.CSS_SELECTOR, value=".cc_btn_accept_all")
    got_it_button.click()
    print("Clicked the got it button!")
except NoSuchElementException:
    print("No cookies pop up.")

sleep(3)
cookie_button = driver.find_element(By.CSS_SELECTOR, value="#bigCookie")

start_time = time()
check_time = time()

condition = True
while condition:
    cookie_button.click()
    if time() - start_time >= 300:
        condition = False
        while True:
            try:
                cookies_per_second = driver.find_element(By.CSS_SELECTOR, value="#cookiesPerSecond").text
                print(cookies_per_second)
                break
            except StaleElementReferenceException:
                pass
    else:
        if time() - check_time >= 5:
            print("Let's buy some items.")
            cookie_text = driver.find_element(By.CSS_SELECTOR, value="#cookies").text.split()
            cookie_text = cookie_text[0]
            num_of_cookies = int(cookie_text.replace(",", ""))

            items = []
            products = driver.find_elements(By.CSS_SELECTOR, value=".product")

            for product in products:
                product_class = product.get_attribute("class")
                if "enabled" in product_class:
                    product_price = product.find_element(By.CSS_SELECTOR, value=".price")
                    product_price = product_price.text
                    price_of_product = int(product_price.replace(",", ""))
                    items.append((product, price_of_product))
            try:
                most_expensive_product = max(items, key=lambda item: item[1])
                if num_of_cookies >= most_expensive_product[1]:
                    most_expensive_product[0].click()
            except ValueError:
                print("No affordable product at the moment.")
            check_time = time()
