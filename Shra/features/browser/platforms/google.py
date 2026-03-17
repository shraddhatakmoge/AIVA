from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys   # ✅ NEW
from selenium.webdriver.support.ui import WebDriverWait   # ✅ NEW
from selenium.webdriver.support import expected_conditions as EC   # ✅ NEW
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

    # -------------------------------------------------
    # SEARCH  ✅ NEW
    # -------------------------------------------------
    def search(self, query):

        if not query:
            return {
                "status": "error",
                "response": "No search query provided."
            }

        # Ensure Google is open
        self.open()

        wait = WebDriverWait(self.driver, 20)

        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )

        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        bring_browser_to_front()

        return {
            "status": "success",
            "response": f"Searched '{query}' on Google"
        }