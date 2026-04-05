import time
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front
from AIVA.Shra.features.browser.memory.spotify_memory import SpotifyMemory
from selenium.webdriver.common.action_chains import ActionChains


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

    def _safe_get(self, url):
        try:
            self.driver.get(url)
        except Exception:
            print("⚠️ Page load timeout, but letting page continue loading...")

        # 🔥 IMPORTANT: DO NOT STOP LOADING
        time.sleep(6)
    # -------------------------------------------------
    def open(self, tab_handle=None):

        # 🔥 SWITCH TO CORRECT TAB
        if tab_handle:
            self.driver.switch_to.window(tab_handle)

        # 🔥 OPEN SPOTIFY
        self.driver.get("https://open.spotify.com/")

        time.sleep(5)

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='main']")
            )
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
        try:
            btn = self._get_play_pause_button()
            if not btn:
                return False

            aria = btn.get_attribute("aria-label")
            return aria and ("Pause" in aria or "pause" in aria)
        except:
            return False

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
    # PLAY (🔥 FIXED STABLE VERSION)
    # -------------------------------------------------
    def play(self, query):

        if not query:
            return {
                "status": "error",
                "response": "No song specified to play."
            }

        # 🔥 ONLY open if not already on spotify


        if not self._is_logged_in():
            return {
                "status": "login_required",
                "response": "Please log in to Spotify once."
            }

        wait = WebDriverWait(self.driver, 30)

        try:
            encoded_query = urllib.parse.quote(query)
            songs_url = f"https://open.spotify.com/search/{encoded_query}/tracks"

            # 🔥 SAFE navigation
            self._safe_get(songs_url)

            self.driver.switch_to.window(self.driver.current_window_handle)
            bring_browser_to_front()

            first_track = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "(//div[@data-testid='tracklist-row'])[1]")
                )
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                first_track
            )

            time.sleep(1)

            self.driver.execute_script("window.focus();")

            # 🔥 CLICK PLAY BUTTON DIRECTLY (MOST RELIABLE)
            # 🔥 CLICK FIRST TRACK PLAY BUTTON
            try:
                first_track_play = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "(//div[@data-testid='tracklist-row'])[1]//button[@data-testid='play-button']"
                    ))
                )

                self.driver.execute_script("arguments[0].click();", first_track_play)

            except Exception:
                # fallback → double click track row
                actions = ActionChains(self.driver)
                actions.move_to_element(first_track).double_click().perform()

            time.sleep(2)

            # 🔥 simulate user interaction (helps autoplay)
            self.driver.execute_script("document.body.click();")
            time.sleep(1)

            # 🔥 ensure playback starts
            for _ in range(5):
                if self._is_playing():
                    break

                play_btn = self._get_play_pause_button()
                if play_btn:
                    self.driver.execute_script("arguments[0].click();", play_btn)

                time.sleep(1)

            time.sleep(2)

            if not self._is_playing():
                print("⚠️ Playback might not have started")

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

        real_title = self._get_current_track_title()

        if real_title:
            self.current_song = real_title
        else:
            self.current_song = query.strip().lower()

        self.memory.add_history(self.current_song)

        bring_browser_to_front()

        # 🔥 FINAL PLAY CHECK
        # 🔥 SOFT CHECK (DON’T FAIL HARD)
        if not self._is_playing():
            print("⚠️ Playback state uncertain, but continuing...")

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

        favorites = self.memory.get_all_favorites()

        # 🔥 NO FAVORITES CASE (MAIN FIX)
        if not favorites:
            return {
                "status": "info",
                "response": "No favorite songs found on Spotify. You can play a song and then add it to favorites."
            }

        # 🔥 PICK RANDOM
        favorite = self.memory.get_random_favorite()

        # HANDLE dict / string
        if isinstance(favorite, dict):
            song = favorite.get("song")
        else:
            song = favorite

        if not song:
            return {
                "status": "error",
                "response": "Invalid favorite format."
            }

        return self.play(song)

    def play_last(self):
        last = self.memory.get_last_played()
        if not last:
            return {"status": "error", "response": "No history found."}

        return self.play(last["song"])