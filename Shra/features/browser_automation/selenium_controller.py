from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time
from selenium.common.exceptions import WebDriverException

# Windows focus control
import win32gui
import win32con
import win32com.client

CHROME_DRIVER_PATH = r"C:\Drivers\chromedriver.exe"

_driver = None  # Global driver instance


# ---------------------------------------------------
# SINGLE DRIVER INSTANCE (No multiple Chrome windows)
# ---------------------------------------------------
def get_driver():
    global _driver

    try:
        if _driver is None:
            raise Exception("Driver not initialized")

        # Try simple command to test if session alive
        _driver.current_url

    except:
        print("[Driver] Creating new Chrome session...")
        service = Service(CHROME_DRIVER_PATH)
        _driver = webdriver.Chrome(service=service)
        _driver.maximize_window()

    return _driver

# ---------------------------------------------------
# Bring Chrome Window to Front (Windows Only)
# ---------------------------------------------------
def bring_chrome_to_front():
    def enum_windows_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Chrome" in title:
                results.append(hwnd)

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)

    if windows:
        hwnd = windows[0]

        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')  # Required trick

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)


# ---------------------------------------------------
# Simple Ad Monitor (Optional – Not Perfect)
# ---------------------------------------------------
def skip_ads_if_present(driver):
    print("[YouTube] Monitoring for ads...")

    for _ in range(40):  # monitor for 40 seconds
        try:
            body_class = driver.find_element(By.TAG_NAME, "body").get_attribute("class")

            if "ad-showing" in body_class:
                skip_buttons = driver.find_elements(
                    By.CSS_SELECTOR,
                    ".ytp-ad-skip-button, .ytp-ad-skip-button-modern"
                )

                if skip_buttons:
                    driver.execute_script("arguments[0].click();", skip_buttons[0])
                    print("[YouTube] Ad skipped.")
                    return
            else:
                return

        except:
            pass

        time.sleep(1)

    print("[YouTube] No skippable ad or ad finished.")


# ---------------------------------------------------
# Play YouTube Video
# ---------------------------------------------------
def play_youtube_video(query: str):
    driver = get_driver()

    driver.get("https://www.youtube.com")
    time.sleep(2)

    # Accept consent if appears
    try:
        consent = driver.find_element(By.XPATH, "//button[contains(text(),'Accept')]")
        consent.click()
    except:
        pass

    # Search
    search_box = driver.find_element(By.NAME, "search_query")
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(3)

    videos = driver.find_elements(By.ID, "video-title")

    best_match = None
    highest_score = 0

    for video in videos:
        title = video.get_attribute("title")

        if not title:
            continue

        title_lower = title.lower()
        query_words = query.lower().split()

        score = sum(word in title_lower for word in query_words)

        if score > highest_score:
            highest_score = score
            best_match = video

    if best_match:
        best_match.click()
        print(f"[YouTube] Playing: {query}")
    else:
        print("[YouTube] No suitable video found.")
        return

    time.sleep(4)

    # Bring Chrome to front
    bring_chrome_to_front()

    # Monitor ads
    skip_ads_if_present(driver)
