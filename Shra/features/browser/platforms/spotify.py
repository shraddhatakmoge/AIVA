import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front


class Spotify:

    def __init__(self, driver):
        self.driver = driver

    # -------------------------------------------------
    # URL
    # -------------------------------------------------
    def get_url(self):
        return "https://open.spotify.com"

    # -------------------------------------------------
    # OPEN
    # -------------------------------------------------
    def open(self):
        self.driver.get(self.get_url())
        bring_browser_to_front()
        return {
            "status": "success",
            "response": "Opened Spotify"
        }

    # -------------------------------------------------
    # LOGIN DETECTION (Stable)
    # -------------------------------------------------
    def _is_logged_in(self):
        try:
            # If login button exists → NOT logged in
            self.driver.find_element(
                By.XPATH,
                "//*[@data-testid='login-button']"
            )
            return False
        except:
            return True

    # -------------------------------------------------
    # SEARCH ONLY
    # -------------------------------------------------
    def search(self, query):

        if not query:
            return {
                "status": "error",
                "response": "No search query provided."
            }

        wait = WebDriverWait(self.driver, 20)

        if not self._is_logged_in():
            bring_browser_to_front()
            return {
                "status": "login_required",
                "response": "Please log in to Spotify once."
            }

        search_input = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='What do you want to play?']")
            )
        )

        search_input.clear()
        search_input.send_keys(query)
        search_input.send_keys(Keys.RETURN)

        time.sleep(2)
        bring_browser_to_front()

        return {
            "status": "success",
            "response": f"Searched {query} on Spotify"
        }

    # -------------------------------------------------
    # VERIFY PLAYING (Stable Logic)
    # -------------------------------------------------
    def _is_playing(self):
        try:
            # If play button is visible → NOT playing
            self.driver.find_element(
                By.XPATH,
                "//button[@data-testid='control-button-play']"
            )
            return False
        except:
            # Play button not found → currently playing
            return True

    # -------------------------------------------------
    # FORCE PLAY BUTTON
    # -------------------------------------------------
    def _force_play(self):
        try:
            play_button = self.driver.find_element(
                By.XPATH,
                "//button[@data-testid='control-button-play']"
            )
            play_button.click()
            return True
        except:
            return False

    # -------------------------------------------------
    # PLAY MUSIC (Reliable Version)
    # -------------------------------------------------
    def play_music(self, query):

        if not query:
            return {
                "status": "error",
                "response": "No song specified to play."
            }

        wait = WebDriverWait(self.driver, 20)

        # Step 1: Search
        search_result = self.search(query)

        if isinstance(search_result, dict) and search_result.get("status") == "login_required":
            return search_result

        try:
            # Step 2: Locate first track
            first_track = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "(//div[@data-testid='tracklist-row'])[1]")
                )
            )

            # Step 3: Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", first_track)
            time.sleep(1)

            # Step 4: Click using JavaScript (most reliable)
            self.driver.execute_script("arguments[0].click();", first_track)

        except TimeoutException:
            bring_browser_to_front()
            return {
                "status": "error",
                "response": "Could not find playable track."
            }

        time.sleep(3)

        # Step 5: Check if playing
        if self._is_playing():
            bring_browser_to_front()
            return {
                "status": "success",
                "response": f"Playing '{query}' on Spotify"
            }

        # Step 6: Try force play fallback
        if self._force_play():
            time.sleep(2)
            if self._is_playing():
                bring_browser_to_front()
                return {
                    "status": "success",
                    "response": f"Playing '{query}' on Spotify"
                }

        bring_browser_to_front()
        return {
            "status": "error",
            "response": "Playback did not start."
        }

    # -------------------------------------------------
    # Alias for play
    # -------------------------------------------------
    def play(self, query):
        return self.play_music(query)

    # -------------------------------------------------
    # PAUSE
    # -------------------------------------------------
    def pause(self):
        try:
            pause_btn = self.driver.find_element(
                By.XPATH,
                "//button[@data-testid='control-button-pause']"
            )
            pause_btn.click()
            bring_browser_to_front()
            return {
                "status": "success",
                "response": "Paused Spotify"
            }
        except:
            return {
                "status": "error",
                "response": "Nothing playing"
            }

    # -------------------------------------------------
    # RESUME
    # -------------------------------------------------
    def resume(self):
        if self._force_play():
            bring_browser_to_front()
            return {
                "status": "success",
                "response": "Resumed Spotify"
            }

        return {
            "status": "error",
            "response": "Nothing to resume"
        }

    # -------------------------------------------------
    # STOP
    # -------------------------------------------------
    def stop(self):
        return self.pause()

    # -------------------------------------------------
    # NEXT
    # -------------------------------------------------
    def next(self):
        try:
            next_btn = self.driver.find_element(
                By.XPATH,
                "//button[@data-testid='control-button-skip-forward']"
            )
            next_btn.click()
            bring_browser_to_front()
            return {
                "status": "success",
                "response": "Skipped to next song"
            }
        except:
            return {
                "status": "error",
                "response": "Cannot skip forward"
            }

    # -------------------------------------------------
    # PREVIOUS
    # -------------------------------------------------
    def previous(self):
        try:
            prev_btn = self.driver.find_element(
                By.XPATH,
                "//button[@data-testid='control-button-skip-back']"
            )
            prev_btn.click()
            bring_browser_to_front()
            return {
                "status": "success",
                "response": "Went to previous song"
            }
        except:
            return {
                "status": "error",
                "response": "Cannot skip backward"
            }