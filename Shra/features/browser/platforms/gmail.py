from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front


class Gmail:

    def __init__(self, driver):
        self.driver = driver

    def get_url(self):
        return "https://mail.google.com"

    def _is_logged_in(self):
        try:
            self.driver.find_element(By.XPATH, "//div[text()='Compose']")
            return True
        except:
            return False

    def open(self):
        self.driver.get(self.get_url())
        bring_browser_to_front()

        if not self._is_logged_in():
            return {
                "status": "login_required",
                "response": "Please login to Gmail once."
            }

        return {
            "status": "success",
            "response": "Opened Gmail"
        }