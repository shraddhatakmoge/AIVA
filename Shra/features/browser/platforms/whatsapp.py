import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front


class WhatsApp:

    def __init__(self, driver):
        self.driver = driver

    def get_url(self):
        return "https://web.whatsapp.com"

    def _is_logged_in(self):
        try:
            self.driver.find_element(By.XPATH, "//div[@title='Search input textbox']")
            return True
        except:
            return False

    def open(self):

        self.driver.get(self.get_url())
        bring_browser_to_front()

        wait = WebDriverWait(self.driver, 30)

        if not self._is_logged_in():
            print("📱 Please scan QR code once...")
            time.sleep(15)

        bring_browser_to_front()

        return {
            "status": "success",
            "response": "Opened WhatsApp Web"
        }