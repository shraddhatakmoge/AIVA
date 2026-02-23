import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front
from AIVA.Shra.features.browser.memory.youtube_memory import YouTubeMemory


class YouTube:

    def __init__(self, driver):
        self.driver = driver
        self.memory = YouTubeMemory()
        self.current_song = None

    # -------------------------------------------------
    # URL
    # -------------------------------------------------
    def get_url(self):
        return "https://www.youtube.com"

    # -------------------------------------------------
    # OPEN
    # -------------------------------------------------
    def open(self):
        self.driver.get(self.get_url())
        bring_browser_to_front()

        return {
            "status": "success",
            "response": "Opened YouTube"
        }

    # -------------------------------------------------
    # CLOSE
    # -------------------------------------------------
    def close(self):
        try:
            self.driver.close()
            return {
                "status": "success",
                "response": "Closed YouTube"
            }
        except:
            return {
                "status": "error",
                "response": "Could not close YouTube"
            }

    # -------------------------------------------------
    # SEARCH
    # -------------------------------------------------
    def search(self, query):

        if not query:
            return {
                "status": "error",
                "response": "No search query provided."
            }

        wait = WebDriverWait(self.driver, 20)

        self.open()

        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )

        search_box.clear()
        search_box.send_keys(query)
        search_box.submit()

        time.sleep(2)

        bring_browser_to_front()

        return {
            "status": "success",
            "response": f"Searched '{query}' on YouTube"
        }

    # -------------------------------------------------
    # PLAY
    # -------------------------------------------------
    def play(self, query):

        if not query:
            return {
                "status": "error",
                "response": "No song specified."
            }

        wait = WebDriverWait(self.driver, 20)

        self.open()

        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )

        search_box.clear()
        search_box.send_keys(query)
        search_box.submit()

        try:
            first_video = wait.until(
                EC.presence_of_element_located((By.ID, "video-title"))
            )
            self.driver.execute_script("arguments[0].click();", first_video)
            time.sleep(2)

        except TimeoutException:
            return {
                "status": "error",
                "response": "No videos found."
            }

        self.current_song = query
        self.memory.add_history(query)

        bring_browser_to_front()

        return {
            "status": "success",
            "response": f"Playing '{query}' on YouTube"
        }

    # -------------------------------------------------
    # -------------------------------------------------
    # PAUSE (Direct JS Control - Reliable)
    # -------------------------------------------------
    def pause(self):

        try:
            self.driver.execute_script("""
                const video = document.querySelector('video');
                if (video && !video.paused) {
                    video.pause();
                }
            """)

            return {
                "status": "success",
                "response": "Paused YouTube"
            }

        except:
            return {
                "status": "error",
                "response": "Could not pause YouTube"
            }

    # -------------------------------------------------
    # RESUME (Direct JS Control - Reliable)
    # -------------------------------------------------
    def resume(self):

        try:
            self.driver.execute_script("""
                const video = document.querySelector('video');
                if (video && video.paused) {
                    video.play();
                }
            """)

            return {
                "status": "success",
                "response": "Resumed YouTube"
            }

        except:
            return {
                "status": "error",
                "response": "Could not resume YouTube"
            }

    # -------------------------------------------------
    # STOP (Alias to pause)
    # -------------------------------------------------
    def stop(self):
        return self.pause()
    # -------------------------------------------------
    # ADD TO FAVORITES
    # -------------------------------------------------
    def add_to_favorites(self):

        song = self.current_song or self.memory.get_last_played()

        if not song:
            return {
                "status": "error",
                "response": "No song available to add."
            }

        added = self.memory.add_favorite(song)

        if not added:
            return {
                "status": "info",
                "response": f"'{song}' already in favorites."
            }

        return {
            "status": "success",
            "response": f"Added '{song}' to favorites."
        }

    # -------------------------------------------------
    # REMOVE FROM FAVORITES
    # -------------------------------------------------
    def remove_favorite(self, query=None):

        song = query or self.current_song

        if not song:
            return {
                "status": "error",
                "response": "No song specified."
            }

        removed = self.memory.remove_favorite(song)

        if not removed:
            return {
                "status": "info",
                "response": f"'{song}' not found in favorites."
            }

        return {
            "status": "success",
            "response": f"Removed '{song}' from favorites."
        }

    # -------------------------------------------------
    # PLAY RANDOM FAVORITE
    # -------------------------------------------------
    def play_favorite(self):

        song = self.memory.get_random_favorite()

        if not song:
            return {
                "status": "error",
                "response": "No favorites saved."
            }

        return self.play(song)

    # -------------------------------------------------
    # PLAY LAST
    # -------------------------------------------------
    def play_last(self):

        song = self.memory.get_last_played()

        if not song:
            return {
                "status": "error",
                "response": "No history found."
            }

        return self.play(song)

    # -------------------------------------------------
    # PLAY YESTERDAY
    # -------------------------------------------------
    def play_yesterday(self):

        song = self.memory.get_yesterday_last()

        if not song:
            return {
                "status": "error",
                "response": "No yesterday history found."
            }

        return self.play(song)