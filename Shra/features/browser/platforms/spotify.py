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
    # SEARCH
    # -------------------------------------------------
    def search(self, query):

        wait = WebDriverWait(self.driver, 20)

        search_input = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='What do you want to play?']")
            )
        )

        search_input.clear()
        search_input.send_keys(query)
        search_input.send_keys(Keys.RETURN)

        time.sleep(2)

        return True

    # -------------------------------------------------
    # VERIFY PLAYING
    # -------------------------------------------------
    def _is_playing(self):
        try:
            # If pause button exists → something is playing
            self.driver.find_element(
                By.XPATH,
                "//button[@data-testid='control-button-pause']"
            )
            return True
        except:
            return False

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
    # PLAY MUSIC (Guaranteed)
    # -------------------------------------------------
    def play_music(self, query):

        wait = WebDriverWait(self.driver, 20)

        # Step 1: Search
        self.search(query)

        # Step 2: Click first track
        try:
            first_track = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "(//div[@role='button'])[1]")
                )
            )
            first_track.click()
        except TimeoutException:
            return {
                "status": "error",
                "response": "Could not find track on Spotify"
            }

        time.sleep(3)

        # Step 3: Verify playback
        if self._is_playing():
            bring_browser_to_front()
            return {
                "status": "success",
                "response": f"Playing '{query}' on Spotify"
            }

        # Step 4: Force play if not playing
        if self._force_play():
            time.sleep(2)
            if self._is_playing():
                bring_browser_to_front()
                return {
                    "status": "success",
                    "response": f"Playing '{query}' on Spotify"
                }

        # If still not playing
        return {
            "status": "error",
            "response": "Spotify did not start playback (check login)"
        }

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
            return {
                "status": "success",
                "response": "Paused Spotify"
            }
        except:
            return {
                "status": "error",
                "response": "Nothing playing to pause"
            }

    # -------------------------------------------------
    # RESUME
    # -------------------------------------------------
    def resume(self):
        if self._force_play():
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
            return {
                "status": "success",
                "response": "Went to previous song"
            }
        except:
            return {
                "status": "error",
                "response": "Cannot skip backward"
            }