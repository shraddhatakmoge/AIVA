import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class YouTube:

    def __init__(self, driver):
        self.driver = driver

    def get_url(self):
        return "https://www.youtube.com"

    def open(self):
        self.driver.get(self.get_url())
        return {
            "status": "success",
            "response": "Opened YouTube"
        }

    def search(self, query):

        self.driver.get(self.get_url())

        wait = WebDriverWait(self.driver, 15)

        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )

        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        wait.until(
            EC.presence_of_element_located((By.ID, "video-title"))
        )

        time.sleep(2)

        videos = self.driver.find_elements(By.ID, "video-title")

        if not videos:
            return {
                "status": "error",
                "response": "No videos found"
            }

        first_video = videos[0]

        self.driver.execute_script(
            "arguments[0].click();",
            first_video
        )

        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "html5-video-player"))
        )

        time.sleep(2)

        return {
            "status": "success",
            "response": f"Playing '{query}' on YouTube"
        }

    def play_music(self, query):
        return self.search(query)