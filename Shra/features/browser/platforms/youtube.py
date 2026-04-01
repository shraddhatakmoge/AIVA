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
    # 🔥 SAFE GET (ADDED - DO NOT REMOVE ORIGINAL FLOW)
    # -------------------------------------------------
    def _safe_get(self, url):
        try:
            time.sleep(1.5)
            self.driver.get(url)
        except:
            print("⚠️ Page load timeout, stopping...")
            self.driver.execute_script("window.stop();")

    # -------------------------------------------------
    # 🔥 SAFE CURRENT URL (ADDED - NO LOGIC CHANGE)
    # -------------------------------------------------
    def _get_safe_current_url(self):
        try:
            return self.driver.current_url
        except:
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                return self.driver.current_url
            except:
                return ""

    # -------------------------------------------------
    # OPEN
    # -------------------------------------------------
    def open(self):
        # 🔥 replaced driver.get with safe_get (no behavior change)
        self._safe_get(self.get_url())
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
    # INTERNAL: GET VIDEO ELEMENT
    # -------------------------------------------------
    def _get_video_element(self):
        return self.driver.execute_script("""
            return document.querySelector('video');
        """)

    # -------------------------------------------------
    # INTERNAL: CHECK PLAY STATE
    # -------------------------------------------------
    def _is_playing(self):
        return self.driver.execute_script("""
            const video = document.querySelector('video');
            if (!video) return null;
            return !video.paused;
        """)

    # -------------------------------------------------
    # 🔥 NEW: GET REAL CURRENT VIDEO TITLE
    # -------------------------------------------------
    def _get_current_video_title(self):
        try:
            title_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h1//yt-formatted-string")
                )
            )

            title = title_element.text.strip().lower()
            return title if title else None

        except:
            return None

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

        # 🔥 ONLY THIS PART MODIFIED (SAFE URL CHECK)
        current_url = self._get_safe_current_url()
        if "youtube" not in current_url:
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
    # PLAY (CANONICAL FIX APPLIED)
    # -------------------------------------------------
    def play(self, query):

        if not query:
            return {
                "status": "error",
                "response": "No song specified."
            }

        wait = WebDriverWait(self.driver, 20)

        # 🔥 ONLY THIS PART MODIFIED (SAFE URL CHECK)
        current_url = self._get_safe_current_url()
        if "youtube" not in current_url:
            self.open()

        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )

        search_box.clear()
        search_box.send_keys(query)
        search_box.submit()

        try:
            wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//a[@id="video-title"]'))
            )

            videos = self.driver.find_elements(By.XPATH, '//a[@id="video-title"]')

            selected_video = None
            query_lower = query.lower()

            for video in videos:
                title = video.get_attribute("title")

                if not title:
                    continue

                title_lower = title.lower()

                if (
                        query_lower in title_lower and
                        "ad" not in title_lower and
                        "news" not in title_lower and
                        "live" not in title_lower
                ):
                    selected_video = video
                    break

            if not selected_video and videos:
                selected_video = videos[0]

            if selected_video:
                self.driver.execute_script("arguments[0].click();", selected_video)
                time.sleep(3)
            else:
                return {
                    "status": "error",
                    "response": "No suitable video found."
                }

        except TimeoutException:
            return {
                "status": "error",
                "response": "No videos found."
            }

        real_title = self._get_current_video_title()

        if real_title:
            self.current_song = real_title
        else:
            self.current_song = query.strip().lower()

        self.memory.add_history(self.current_song)

        bring_browser_to_front()

        return {
            "status": "success",
            "response": f"Playing '{self.current_song}' on YouTube"
        }

    # -------------------------------------------------
    # PAUSE
    # -------------------------------------------------
    def pause(self):

        try:
            state = self._is_playing()

            if state is None:
                return {
                    "status": "error",
                    "response": "No active video."
                }

            if not state:
                return {
                    "status": "info",
                    "response": "YouTube is already paused."
                }

            self.driver.execute_script("""
                const video = document.querySelector('video');
                if (video) video.pause();
            """)

            bring_browser_to_front()

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
    # RESUME
    # -------------------------------------------------
    def resume(self):

        try:
            state = self._is_playing()

            if state is None:
                return {
                    "status": "error",
                    "response": "No active video."
                }

            if state:
                return {
                    "status": "info",
                    "response": "YouTube is already playing."
                }

            self.driver.execute_script("""
                const video = document.querySelector('video');
                if (video) video.play();
            """)

            bring_browser_to_front()

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
    # STOP
    # -------------------------------------------------
    def stop(self):
        return self.pause()

    # -------------------------------------------------
    # ADD TO FAVORITES
    # -------------------------------------------------
    def add_to_favorites(self):

        live_song = self._get_current_video_title()

        if live_song:
            self.current_song = live_song

        song = self.current_song or self.memory.get_last_played()

        if not song:
            return {
                "status": "error",
                "response": "No song available to add."
            }

        return self.memory.add_favorite(song)

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

        return self.memory.remove_favorite(song)

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