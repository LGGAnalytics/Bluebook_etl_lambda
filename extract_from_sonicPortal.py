import os
import time
import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
import env

username = env.SONIC_USERNAME
company = env.SONIC_COMPANY
password = env.SONIC_PASSWORD

if not username or not company or not password:
    raise ValueError("Missing login credentials in env.py.")
###########################################################
###########################################################
###########################################################
# Set up download directory NEEDS TO BE CHANGED
# Set up download directory NEEDS TO BE CHANGED
# Set up download directory NEEDS TO BE CHANGED
# Set up download directory NEEDS TO BE CHANGED
###########################################################
###########################################################
###########################################################
###########################################################

download_dir = os.path.abspath("C:/Users/AzizAbbaszade/Documents/ETL")
os.makedirs(download_dir, exist_ok=True)

options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-popup-blocking")
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_settings.popups": 0,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", prefs)
driver = uc.Chrome(options=options, headless=True)

def dismiss_if_alert(driver):
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        print("Alert was present and accepted.")
        return True
    except:
        return False

def wait_for_loading_complete(timeout=180):
    try:
        print("Waiting for loading screen to appear...")
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "var f = document.getElementById('loadingFrame');"
                "return f && window.getComputedStyle(f).display === 'block';"
            )
        )
        print("Loading screen detected. Waiting for it to disappear...")
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "var f = document.getElementById('loadingFrame');"
                "return !f || window.getComputedStyle(f).display === 'none';"
            )
        )
        print("Loading completed.")
        return True
    except:
        print("Loading screen wait failed or timed out.")
        return False

def wait_for_file_download(folder, timeout=180):
    print(f"Waiting for file download in folder: {folder}")
    end = time.time() + timeout
    while time.time() < end:
        files = os.listdir(folder)
        if files and not any(f.endswith((".crdownload", ".part")) for f in files):
            print(f"File downloaded: {files}")
            return True
        time.sleep(1)
    print("File did not download in expected time.")
    return False

def login():
    print("Opening login page...")
    driver.get("https://sonic.mymicros.net/login.jsp")
    dismiss_if_alert(driver)
    try:
        print("Filling login form...")
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.NAME, "usr")))
        driver.execute_script(f'document.getElementsByName("usr")[0].value = "{username}";')
        driver.execute_script(f'document.getElementsByName("cpny")[0].value = "{company}";')
        driver.execute_script(f'document.getElementsByName("pwd")[0].value = "{password}";')
        driver.execute_script('document.getElementById("Login").click();')
        print("Login form submitted.")
        return True
    except Exception as e:
        print(f"Login failed: {e}")
        return False

def select_last_7_days():
    print("Selecting 'Last 7 Days' from filter dropdown...")
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "myPage")))
    report_div = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "reportSelectionsDiv")))
    select_element = report_div.find_element(By.ID, "calendarData")
    Select(select_element).select_by_value("Past7Days")
    run_btn = report_div.find_element(By.ID, "Run Report")
    driver.execute_script("arguments[0].click();", run_btn)
    print("'Last 7 Days' selected and report run.")
    wait_for_loading_complete()

def download_excel(driver, folder, timeout=180):
    print("Attempting to download Excel file...")
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "myPage")))
    excel_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'img[title="Excel (.xlsx)"]'))
    )
    original_windows = driver.window_handles
    driver.execute_script("arguments[0].click();", excel_btn)

    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > len(original_windows))
    new_window = [w for w in driver.window_handles if w not in original_windows][0]
    driver.switch_to.window(new_window)

    print("Excel download window opened.")

    end_time = time.time() + timeout
    found_file = False

    while time.time() < end_time:
        now = datetime.datetime.now()
        files = os.listdir(folder)
        for file in files:
            if file.startswith("BlueBook_") and file.endswith(".xlsx"):
                file_path = os.path.join(folder, file)
                mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                delta = now - mod_time
                if delta.total_seconds() <= 300:  # son 5 dakika = 300 saniye
                    print(f"Found recent file: {file}, modified {delta.total_seconds()} seconds ago.")
                    found_file = True
                    break
        if found_file:
            break
        time.sleep(1)

    if found_file:
        print("File found and recent, closing download window.")
    else:
        print("No recent BlueBook Excel file found within timeout, closing download window.")

    driver.close()  # Excel indirme penceresini kapat
    driver.switch_to.window(original_windows[0])
    print("Switched back to main window after download.")


# Start process
print("Starting automation script...")

if not login():
    driver.quit()
    raise Exception("Login failed.")

print("Navigating to REPORTING > More Reports")
driver.switch_to.default_content()
WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "sideMenu")))
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//h3[text()="REPORTING"]'))).click()
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "More Reports..."))).click()

print("Opening Blue Book report...")
driver.switch_to.default_content()
WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "myPage")))
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//h2[text()="Summary"]'))).click()
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Blue Book")]'))).click()

print("Checking for 'Next' or 'Run Report' button...")
driver.switch_to.default_content()
WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "myPage")))
try:
    next_btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "next")))
    driver.execute_script("arguments[0].click();", next_btn)
    print("'Next' button clicked.")
except:
    print("No 'Next' button found or clickable.")

try:
    run_btn = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "next")))
    if run_btn.text.strip().lower() == "run report":
        driver.execute_script("arguments[0].click();", run_btn)
        print("'Run Report' button clicked.")
        wait_for_loading_complete()
except:
    print("No 'Run Report' button or error clicking.")

try:
    select_last_7_days()
except Exception as e:
    print(f"Error selecting last 7 days: {e}")

try:
    download_excel(driver, download_dir)
except Exception as e:
    print(f"Error during Excel download: {e}")

print("Process completed. Waiting before closing browser...")
time.sleep(5)
driver.quit()
print("Browser closed. Script finished.")

