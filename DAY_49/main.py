import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
from datetime import datetime
from time import sleep

load_dotenv()

account_email = os.getenv("ACCOUNT_EMAIL")
account_password = os.getenv("ACCOUNT_PASSWORD")

gym_url = "https://appbrewery.github.io/gym/"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
driver = webdriver.Chrome(options=chrome_options)

driver.get(gym_url)

wait = WebDriverWait(driver, timeout=10)


def login():
    login_button = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "#login-button")))
    login_button.click()

    email = wait.until(ec.presence_of_element_located((By.NAME, "email")))
    email.clear()
    email.send_keys(account_email)
    password = wait.until(ec.presence_of_element_located((By.NAME, "password")))
    password.clear()
    password.send_keys(account_password)
    submit_button = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "#submit-button")))
    submit_button.click()

    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".Schedule_scheduleTitle__zfZxg")))


total_tuesday_and_thursday_classes = 0


def book_class():
    global total_tuesday_and_thursday_classes
    classes_booked = 0
    waitlists_joined = 0
    already_booked_or_waitlisted = 0
    total_tuesday_and_thursday_classes = 0
    class_processed = []

    class_cards = driver.find_elements(By.CSS_SELECTOR, "div[id^='class-card-']")
    for card in class_cards:
        card_id = card.get_attribute("id")
        parts = card_id.split("-")
        class_date = parts[3], parts[4], parts[5]
        class_date = "-".join(class_date)
        class_date = datetime.strptime(class_date, "%Y-%m-%d")
        weekday = class_date.strftime("%A")
        if weekday == "Tuesday" or weekday == "Thursday":
            class_time = parts[6]
            if class_time == "1800":
                class_name = parts[2]
                button_id = card_id.replace("class-card-", "book-button-")
                class_button = wait.until(ec.presence_of_element_located((By.ID, button_id)))
                button_text = class_button.text
                week_day = class_date.strftime("%a")
                class_month = class_date.strftime("%b")
                day = class_date.strftime("%d")
                total_tuesday_and_thursday_classes += 1
                classes = f"{class_name} class on {week_day}, {class_month} {day}"
                if button_text == "Booked":
                    already_booked_or_waitlisted += 1
                    print(f"✔ Already booked: {classes}")
                    class_processed.append(f"[Previously Booked] {classes}")
                elif button_text == "Book Class":
                    retry(lambda: (
                        class_button.click(),
                        wait.until(ec.text_to_be_present_in_element((By.ID, button_id), "Booked"))
                    ), description="Booking class")

                    button_text = driver.find_element(By.ID, button_id).text

                    if button_text == "Booked":
                        classes_booked += 1
                        print(f"✔ Successfully booked: {classes}")
                        class_processed.append(f"[New Booking] {classes}")
                    else:
                        print(f"✘ Booking {classes} was unsuccessful!")
                elif button_text == "Waitlisted":
                    already_booked_or_waitlisted += 1
                    print(f"✔ Already on waitlist: {classes}")
                    class_processed.append(f"[Previously on Waitlist] {classes}")
                elif button_text == "Join Waitlist":
                    retry(lambda: (
                        wait.until(ec.element_to_be_clickable((By.ID, button_id))).click(),
                        wait.until(ec.text_to_be_present_in_element((By.ID, button_id), "Waitlisted"))
                    ), description="Joining waitlist")

                    button_text = driver.find_element(By.ID, button_id).text

                    if button_text == "Waitlisted":
                        waitlists_joined += 1
                        print(f"✔ Joined waitlist for: {classes}")
                        class_processed.append(f"[New Waitlist] {classes}")
                    else:
                        print(f"✘ Joining waitlist for {classes} was unsuccessful!")

    # print("--- BOOKING SUMMARY ---")
    # print(f"New bookings made: {classes_booked}")
    # print(f"New waitlist entries: {waitlists_joined}")
    # print(f"Classes already booked/waitlisted: {already_booked_or_waitlisted}")
    # for text in class_processed:
    #     print(f"☐ {text}")


def get_my_bookings():
    mybooking_section = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "#my-bookings-link")))
    mybooking_section.click()
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".MyBookings_pageTitle__i0Jkj")))

    verified_bookings = 0
    my_bookings = driver.find_elements(By.CSS_SELECTOR, "div[id^='booking-card-'], div[id^='waitlist-card-']")
    verified_class_list = []
    for booking in my_bookings:
        class_name = booking.find_element(By.CSS_SELECTOR, "h3[id^=booking-class-name-],"
                                                           " h3[id^='waitlist-class-name-']")
        class_name = class_name.text
        class_date = booking.find_element(By.TAG_NAME, "p")
        class_date = class_date.text
        booking_status = booking.get_attribute("data-booking-status")
        if "Tue" in class_date and "6:00 PM" in class_date:
            if booking_status == "confirmed" or booking_status == "waitlisted":
                verified_class_list.append(class_name)
                verified_bookings += 1
        elif "Thu" in class_date and "6:00 PM" in class_date:
            if booking_status == "confirmed" or booking_status == "waitlisted":
                verified_class_list.append(class_name)
                verified_bookings += 1

    print(f"\n--- Total Tuesday/Thursday 6pm classes: {total_tuesday_and_thursday_classes} ---")

    print("\n--- VERIFYING ON MY BOOKINGS PAGE ---")
    for text in verified_class_list:
        print(f"✔ Verified: {text}")

    print("\n--- VERIFICATION RESULT ---")
    print(f"Expected: {total_tuesday_and_thursday_classes} booking(s)")
    print(f"Found: {verified_bookings} booking(s)")
    if total_tuesday_and_thursday_classes == verified_bookings:
        print("✅ SUCCESS: All bookings verified")
    else:
        result = total_tuesday_and_thursday_classes - verified_bookings
        print(f"❌ MISMATCH: Missing {result} booking(s)")


def retry(func, retries=7, description=None):
    for num in range(retries):
        try:
            return func()
        except WebDriverException as e:
            print(type(e))
            sleep(2)
            print(f"{description}: Attempt {num + 1} failed. Retrying...")
    else:
        print("All attempts to retry failed!")


retry(login, description="Login")
book_class()
retry(get_my_bookings, description="Verifying classes")
