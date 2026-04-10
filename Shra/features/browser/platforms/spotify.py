import datetime
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from AIVA.Shra.features.browser.window_focus import bring_browser_to_front
from features.browser.window_focus import bring_browser_to_front
# from AIVA.Shra.features.browser.memory.spotify_memory import SpotifyMemory
from features.browser.memory.spotify_memory import SpotifyMemory
from selenium.webdriver.common.action_chains import ActionChains


class Spotify:

    def __init__(self, driver):
        self.driver = driver
        self.memory = SpotifyMemory()
        self.current_song = None

    def get_url(self):
        return "https://open.spotify.com"

    def _safe_get(self, url):
        try:
            self.driver.get(url)
        except Exception:
            print("⚠️ Page load timeout, but letting page continue loading...")
        time.sleep(6)  # 🔥 increased stability

    def open(self, tab_handle=None):
        if tab_handle:
            self.driver.switch_to.window(tab_handle)

        self._safe_get("https://open.spotify.com/")
        time.sleep(5)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='main']"))
        )

        time.sleep(3)
        bring_browser_to_front()

        return {"status": "success", "response": "Opened Spotify"}

    def _is_logged_in(self):
        try:
            self.driver.find_element(By.XPATH, "//*[@data-testid='login-button']")
            return False
        except NoSuchElementException:
            return True

    def _get_current_track_title(self):
        try:
            xpaths = [
                "//div[@data-testid='now-playing-widget']//a[contains(@href,'/track/')]",
                "//footer//a[contains(@href,'/track/')]",
                "//a[@data-testid='context-item-link']"
            ]

            for xp in xpaths:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xp))
                    )
                    title = element.text.strip().lower()

                    if title:
                        return title
                except:
                    continue

            return None

        except:
            return None

    def _get_play_pause_button(self):
        try:
            return self.driver.find_element(
                By.XPATH,
                "//button[@data-testid='control-button-playpause']"
            )
        except:
            return None

    def _is_playing(self):
        try:
            btn = self._get_play_pause_button()
            if not btn:
                return False
            aria = btn.get_attribute("aria-label")
            return aria and ("Pause" in aria or "pause" in aria)
        except:
            return False

    def _toggle_play_pause(self):
        btn = self._get_play_pause_button()
        if btn:
            self.driver.execute_script("arguments[0].click();", btn)
            return True
        return False

    # -------------------------------------------------
    # 🔥 FIXED PLAY METHOD (ONLY NECESSARY MODIFICATIONS)
    # -------------------------------------------------
    def play(self, query):

        if not query:
            return {"status": "error", "response": "No song specified."}

        if not self._is_logged_in():
            return {
                "status": "login_required",
                "response": "Please log in to Spotify once."
            }
        print("🎧 Searching on Spotify...")
        wait = WebDriverWait(self.driver, 10)

        try:
            import urllib.parse

            encoded_query = urllib.parse.quote(query)
            search_url = f"https://open.spotify.com/search/{encoded_query}/tracks"

            self._safe_get(search_url)
            time.sleep(5)
            time.sleep(4)

            tracks = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@data-testid='tracklist-row']")
                )
            )
            print("✅ Tracks loaded")

            time.sleep(2)

            selected_track = tracks[0]

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                selected_track
            )

            time.sleep(1)

            # 🔥 STOP CURRENT SONG
            try:
                play_pause = self._get_play_pause_button()
                if play_pause:
                    aria = play_pause.get_attribute("aria-label")
                    if aria and ("Pause" in aria or "pause" in aria):
                        self.driver.execute_script("arguments[0].click();", play_pause)
                        time.sleep(1)
            except:
                pass

            # ✅ 🔥 MAIN FIX → DOUBLE CLICK (ADDED)
            try:
                ActionChains(self.driver).double_click(selected_track).perform()
            except Exception as e:
                print("⚠ Row double click failed, retrying...", e)

            time.sleep(2)

            # 🔥 RETRY FIXED → DOUBLE CLICK (REPLACED)
            for attempt in range(3):

                if self._is_playing():
                    break

                print(f"⚠ Retry play attempt {attempt + 1}")

                try:
                    tracks = self.driver.find_elements(By.XPATH, "//div[@data-testid='tracklist-row']")

                    if not tracks:
                        break

                    selected_track = tracks[0]

                    # ✅ 🔥 FIX → DOUBLE CLICK IN RETRY
                    ActionChains(self.driver).double_click(selected_track).perform()

                except:
                    ActionChains(self.driver).move_to_element(selected_track).double_click().perform()

                time.sleep(2)

            bring_browser_to_front()

        except Exception as e:
            print("⚠ Spotify error but continuing:", e)
            return {
                "status": "success",
                "response": f"Trying to play '{query}' on Spotify"
            }

        time.sleep(3)

        real_title = None

        for _ in range(5):
            real_title = self._get_current_track_title()
            if real_title:
                break
            time.sleep(1)

        if real_title:
            print("🎧 REAL SONG DETECTED:", real_title)
            self.current_song = real_title
        else:
            print("⚠ Using fallback (query)")
            self.current_song = query.lower()

        self.memory.add_history(self.current_song)

        return {
            "status": "success",
            "response": f"Playing '{self.current_song}' on Spotify"
        }

    def pause(self):
        if not self._is_playing():
            return {"status": "info", "response": "Spotify is already paused."}

        if self._toggle_play_pause():
            time.sleep(2)
            bring_browser_to_front()
            return {"status": "success", "response": "Paused Spotify"}

        return {"status": "error", "response": "Could not pause Spotify"}

    def resume(self):
        if self._is_playing():
            return {"status": "info", "response": "Spotify is already playing."}

        if self._toggle_play_pause():
            time.sleep(2)
            bring_browser_to_front()
            return {"status": "success", "response": "Resumed Spotify"}

        return {"status": "error", "response": "Nothing to resume"}

    # -------------------------------------------------
    # 🔥 PLAY FAVORITE (ADD THIS)
    # -------------------------------------------------
    def play_favorite(self):

        print("🎧 Playing favorite on Spotify...")
        # 🔥 GET RANDOM SONG FROM MEMORY
        fav = self.memory.get_random_favorite()

        if not fav:
            return {
                "status": "error",
                "response": "No favorite songs found."
            }

        # 🔥 HANDLE DICT FORMAT (VERY IMPORTANT)
        if isinstance(fav, dict):
            song = fav.get("song")
        else:
            song = fav

        # 🔥 CALL EXISTING PLAY FUNCTION
        return self.play(song)