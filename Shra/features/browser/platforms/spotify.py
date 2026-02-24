import time
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front
from AIVA.Shra.features.browser.memory.spotify_memory import SpotifyMemory


class Spotify:

    def __init__(self, driver):
        self.driver = driver
        self.memory = SpotifyMemory()
        self.current_song = None

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

        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        time.sleep(3)
        bring_browser_to_front()

        return {
            "status": "success",
            "response": "Opened Spotify"
        }

    # -------------------------------------------------
    # LOGIN DETECTION
    # -------------------------------------------------
    def _is_logged_in(self):
        try:
            self.driver.find_element(By.XPATH, "//*[@data-testid='login-button']")
            return False
        except NoSuchElementException:
            return True

    # -------------------------------------------------
    # GET REAL CURRENT TRACK TITLE
    # -------------------------------------------------
    def _get_current_track_title(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(@href,'/track/')]")
                )
            )

            title = element.text.strip().lower()
            return title if title else None

        except Exception:
            return None

    # -------------------------------------------------
    # GET PLAY/PAUSE BUTTON
    # -------------------------------------------------
    def _get_play_pause_button(self):
        try:
            return self.driver.find_element(
                By.XPATH,
                "//button[@data-testid='control-button-playpause']"
            )
        except:
            return None

    # -------------------------------------------------
    # IS PLAYING CHECK
    # -------------------------------------------------
    def _is_playing(self):
        btn = self._get_play_pause_button()
        if not btn:
            return False

        aria = btn.get_attribute("aria-label")
        return aria and "Pause" in aria

    # -------------------------------------------------
    # TOGGLE PLAY/PAUSE
    # -------------------------------------------------
    def _toggle_play_pause(self):
        btn = self._get_play_pause_button()
        if btn:
            self.driver.execute_script("arguments[0].click();", btn)
            return True
        return False

    # -------------------------------------------------
    # SEARCH
    # -------------------------------------------------
    def search(self, query):

        if not query:
            return {
                "status": "error",
                "response": "No search query provided."
            }

        if not self._is_logged_in():
            return {
                "status": "login_required",
                "response": "Please log in to Spotify once."
            }

        wait = WebDriverWait(self.driver, 20)

        search_input = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='What do you want to play?']")
            )
        )

        search_input.clear()
        search_input.send_keys(query)
        search_input.send_keys("\n")

        time.sleep(2)
        bring_browser_to_front()

        return {
            "status": "success",
            "response": f"Searched '{query}' on Spotify"
        }

    # -------------------------------------------------
    # PLAY (HARDENED VERSION)
    # -------------------------------------------------
    def play(self, query):

        if not query:
            return {
                "status": "error",
                "response": "No song specified to play."
            }

        self.open()

        if not self._is_logged_in():
            return {
                "status": "login_required",
                "response": "Please log in to Spotify once."
            }

        wait = WebDriverWait(self.driver, 30)

        try:
            encoded_query = urllib.parse.quote(query)
            songs_url = f"https://open.spotify.com/search/{encoded_query}/tracks"
            self.driver.get(songs_url)

            # Ensure tab is active
            self.driver.switch_to.window(self.driver.current_window_handle)
            bring_browser_to_front()

            # Wait for first track to be clickable
            first_track = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "(//div[@data-testid='tracklist-row'])[1]")
                )
            )

            # Scroll to element
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                first_track
            )

            time.sleep(1)

            # Force activation of document (important for autoplay)
            self.driver.execute_script("window.focus();")

            # Dispatch REAL double click event
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new MouseEvent('dblclick', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                }));
            """, first_track)

            time.sleep(3)

            # If still not playing → force press play button
            if not self._is_playing():
                play_btn = self._get_play_pause_button()
                if play_btn:
                    self.driver.execute_script("arguments[0].click();", play_btn)

            # Final verification wait
            WebDriverWait(self.driver, 15).until(
                lambda d: self._is_playing()
            )

        except TimeoutException:
            return {
                "status": "error",
                "response": "Could not start playback."
            }

        except Exception as e:
            return {
                "status": "error",
                "response": f"Playback failed: {str(e)}"
            }

        # Get actual title
        real_title = self._get_current_track_title()

        if real_title:
            self.current_song = real_title
        else:
            self.current_song = query.strip().lower()

        self.memory.add_history(self.current_song)

        bring_browser_to_front()

        return {
            "status": "success",
            "response": f"Playing '{self.current_song}' on Spotify"
        }

    # -------------------------------------------------
    # PAUSE
    # -------------------------------------------------
    def pause(self):

        if not self._is_playing():
            return {
                "status": "info",
                "response": "Spotify is already paused."
            }

        if self._toggle_play_pause():
            time.sleep(2)
            bring_browser_to_front()
            return {
                "status": "success",
                "response": "Paused Spotify"
            }

        return {
            "status": "error",
            "response": "Could not pause Spotify"
        }

    # -------------------------------------------------
    # RESUME
    # -------------------------------------------------
    def resume(self):

        if self._is_playing():
            return {
                "status": "info",
                "response": "Spotify is already playing."
            }

        if self._toggle_play_pause():
            time.sleep(2)
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
    # FAVORITES
    # -------------------------------------------------
    def add_to_favorites(self):
        song = self.current_song or self.memory.get_last_played()

        if not song:
            return {"status": "error", "response": "No song available to add."}

        return self.memory.add_favorite(song)

    def remove_favorite(self, query=None):
        song = query or self.current_song

        if not song:
            return {"status": "error", "response": "No song specified."}

        return self.memory.remove_favorite(song)

    def play_favorite(self):
        favorite = self.memory.get_random_favorite()
        if not favorite:
            return {"status": "error", "response": "No favorites saved."}

        return self.play(favorite["song"])

    def play_last(self):
        last = self.memory.get_last_played()
        if not last:
            return {"status": "error", "response": "No history found."}

        return self.play(last["song"])