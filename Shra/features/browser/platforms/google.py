from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys   # ✅ NEW
from selenium.webdriver.support.ui import WebDriverWait   # ✅ NEW
from selenium.webdriver.support import expected_conditions as EC   # ✅ NEW
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front

import time
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

    def open_result(self, index=1):

        wait = WebDriverWait(self.driver, 10)

        results = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[h3]"))
        )

        if index <= len(results):

            element = results[index - 1]
            title = element.text.strip()
            href = element.get_attribute("href")

            if not href:
                return {
                    "status": "error",
                    "response": "Could not get link"
                }

            # 🔥 OPEN IN NEW TAB (IMPORTANT FIX)
            self.driver.execute_script("window.open(arguments[0], '_blank');", href)

            # 🔥 SWITCH TO NEW TAB
            self.driver.switch_to.window(self.driver.window_handles[-1])

            return {
                "status": "success",
                "response": f"Opening {title if title else 'result'} in new tab"
            }

        return {
            "status": "error",
            "response": "Result not found"
        }

    def open(self, tab_handle=None):
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
    # SCROLL
    # -------------------------------------------------
    def scroll(self, direction="down"):

        if direction == "down":
            self.driver.execute_script("window.scrollBy(0, 600);")
        else:
            self.driver.execute_script("window.scrollBy(0, -600);")

        return {
            "status": "success",
            "response": f"Scrolled {direction}"
        }

    import time  # ✅ ADD THIS AT TOP IF NOT PRESENT

    def open_result_by_name(self, name, index=1, max_scrolls=5):

        wait = WebDriverWait(self.driver, 10)
        name = name.lower()

        for _ in range(max_scrolls):

            results = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[h3]"))
            )

            matched = []

            for element in results:
                title = element.text.strip().lower()

                if name in title:
                    matched.append(element)

            # ✅ IF FOUND MATCHES
            if matched:

                if index > len(matched):
                    return {
                        "status": "error",
                        "response": f"Only {len(matched)} results found"
                    }

                element = matched[index - 1]
                href = element.get_attribute("href")

                if not href:
                    return {
                        "status": "error",
                        "response": "Could not get link"
                    }

                self.driver.execute_script(
                    "window.open(arguments[0], '_blank');", href
                )

                self.driver.switch_to.window(self.driver.window_handles[-1])

                return {
                    "status": "success",
                    "response": f"Opening {name} result {index}"
                }

            # 🔥 SCROLL DOWN IF NOT FOUND
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)

        return {
            "status": "error",
            "response": f"No result found for '{name}'"
        }
    # -------------------------------------------------
    # SEARCH  ✅ NEW
    # -------------------------------------------------
    def search(self, query, tab_handle=None):
        if tab_handle:
            self.driver.switch_to.window(tab_handle)
        if not query:
            return {
                "status": "error",
                "response": "No search query provided."
            }

        self.open()

        wait = WebDriverWait(self.driver, 20)

        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )

        search_box.clear()
        search_box.send_keys(query)

        # 🔥 RELIABLE SEARCH TRIGGER
        search_box.submit()

        bring_browser_to_front()

        return {
            "status": "success",
            "response": f"Searched '{query}' on Google"
        }