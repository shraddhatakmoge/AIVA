from selenium.webdriver.common.by import By
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front


class Google:

    def __init__(self, driver):
        self.driver = driver

    def get_url(self):
        return "https://www.google.com"

    def _is_logged_in(self):
        try:
            self.driver.find_element(By.XPATH, "//a[contains(@href,'SignOutOptions')]")
            return True
        except:
            return False

    def open(self):
        self.driver.get(self.get_url())
        bring_browser_to_front()

        if not self._is_logged_in():
            return {
                "status": "login_required",
                "response": "Please login to Google once."
            }

        return {
            "status": "success",
            "response": "Opened Google"
        }