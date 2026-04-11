import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from difflib import SequenceMatcher
# from AIVA.Shra.features.browser.window_focus import bring_browser_to_front
from features.browser.window_focus import bring_browser_to_front
# from AIVA.Shra.features.browser.memory.youtube_memory import YouTubeMemory
from features.browser.memory.youtube_memory import YouTubeMemory


class YouTube:

    def __init__(self, driver):
        self.driver = driver
        self.memory = YouTubeMemory()
        self.current_song = None

    def _similarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

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
    def open(self, tab_handle=None):

        if tab_handle:
            self.driver.switch_to.window(tab_handle)

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
        # 🔥 LOAD MORE RESULTS (CRITICAL FIX)
        for _ in range(3):
            self.driver.execute_script("window.scrollBy(0, 1200);")
            time.sleep(1.5)

        try:
            wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//a[@id="video-title"]'))
            )

            # 🔥 ALWAYS REFRESH ELEMENTS (FIX STALE ISSUE)
            videos = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//a[@id="video-title"]'))
            )
            # 🔥 REFRESH ELEMENTS AFTER SCROLL
            videos = self.driver.find_elements(By.XPATH, '//a[@id="video-title"]')

            selected_video = None
            query_lower = query.lower()
            query_words = query_lower.split()

            best_match = None
            best_score = 0

            for video in videos:
                title = video.get_attribute("title")

                if not title:
                    continue

                title_lower = title.lower()

                # skip unwanted
                if any(x in title_lower for x in ["ad", "news", "live"]):
                    continue

                # 🔥 SCORE MATCHING
                # 🔥 NEW FUZZY MATCHING
                title_words = title_lower.split()

                # 🔥 compare with each word (fix typo issues)
                word_scores = [self._similarity(query_lower, word) for word in title_words]

                similarity = max(word_scores) if word_scores else 0

                # 🔥 bonus: also compare full title
                full_similarity = self._similarity(query_lower, title_lower)

                # take best of both
                final_score = max(similarity, full_similarity)

                if final_score > best_score:
                    best_score = final_score
                    best_match = video

                if similarity > best_score:
                    best_score = similarity
                    best_match = video

            # final selection
            # 🔥 ONLY ACCEPT IF MATCH IS GOOD
            required_score = max(1, len(query_words) // 2)

            # 🔥 FINAL SELECTION LOGIC (BEST PRACTICE)

            SIMILARITY_THRESHOLD = 0.35  # you can tune (0.3–0.4)

            if best_match and best_score >= SIMILARITY_THRESHOLD:
                selected_video = best_match
            else:
                # 🔥 fallback → first video
                selected_video = videos[0] if videos else None

            if not selected_video:
                return {
                    "status": "error",
                    "response": "No videos found."
                }

            if selected_video:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    selected_video
                )
                time.sleep(1)

                try:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        selected_video
                    )
                    time.sleep(1)

                    self.driver.execute_script("arguments[0].click();", selected_video)

                except:
                    # 🔥 RE-FETCH ELEMENT AND RETRY
                    fresh_videos = self.driver.find_elements(By.XPATH, '//a[@id="video-title"]')

                    if fresh_videos:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});",
                            fresh_videos[0]
                        )
                        time.sleep(1)

                        self.driver.execute_script("arguments[0].click();", fresh_videos[0])
                time.sleep(3)



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

    def skip_ad(self):
        try:
            is_ad = self.driver.execute_script("""
                const video = document.querySelector('video');
                if (!video) return false;

                // 🔥 ads usually have very small duration or changing src
                return document.querySelector('.ad-showing') !== null 
                       || document.querySelector('.ytp-ad-player-overlay') !== null
                       || document.querySelector('.ytp-ad-text') !== null;
            """)

            if not is_ad:
                return {
                    "status": "info",
                    "response": "No ad is currently playing."
                }
            time.sleep(3)  # 🔥 IMPORTANT FIX
            # 🔥 TRY MULTIPLE METHODS
            for _ in range(15):

                # -------- METHOD 1: Selenium Click --------
                try:
                    skip_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((
                            By.CSS_SELECTOR,
                            ".ytp-ad-skip-button, .ytp-ad-skip-button-modern"
                        ))
                    )

                    skip_btn.click()

                    return {
                        "status": "success",
                        "response": "⏭️ Skipped the ad"
                    }

                except:
                    pass

                # -------- METHOD 2: JS FORCE CLICK --------
                skipped = self.driver.execute_script("""
                    let btn =
                        document.querySelector('.ytp-ad-skip-button-modern') ||
                        document.querySelector('.ytp-ad-skip-button') ||
                        document.querySelector('.ytp-ad-skip-button-container button');

                    if (btn) {

                        // 🔥 CHECK IF BUTTON TEXT IS "Skip"
                        let text = btn.innerText.toLowerCase();

                        if (!text.includes("skip")) {
                            return false;
                        }

                        btn.removeAttribute('disabled');

                        btn.click();

                        btn.dispatchEvent(new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true
                        }));

                        return true;
                    }

                    return false;
                """)
                if skipped:
                    return {
                        "status": "success",
                        "response": "⏭️ Skipped the ad"
                    }

                time.sleep(1)

            return {
                "status": "info",
                "response": "⏳ Skip not available yet (long ad)."
            }

        except Exception as e:
            return {
                "status": "error",
                "response": f"Skip failed: {str(e)}"
            }
    def mute(self):
        try:
            is_playing = self._is_playing()

            if is_playing is None:
                bring_browser_to_front()
                time.sleep(1)
                return {
                    "status": "error",
                    "response": "❌ No active YouTube video."
                }

            # 🔥 STEP 1: CHECK IF AD IS PLAYING
            is_ad = self.driver.execute_script("""
                return document.querySelector('.ytp-ad-player-overlay') !== null
    || document.querySelector('.ytp-ad-text') !== null;
            """)

            # 🔥 STEP 2: IF AD → USE BUTTON (REAL USER ACTION)
            if is_ad:
                result = self.driver.execute_script("""
                    const btn = document.querySelector('.ytp-mute-button');
                    if (!btn) return "NO_BUTTON";

                    let label = btn.getAttribute('aria-label')?.toLowerCase() || "";

                    // 🔥 if already muted → don't click
                    if (label.includes("unmute")) {
                        return "ALREADY_MUTED";
                    }

                    // 🔥 otherwise click
                    btn.click();
                    return "MUTED";
                """)

                if result == "ALREADY_MUTED":
                    return {"status": "info", "response": "Ad is already muted"}

                if result == "MUTED":
                    return {"status": "success", "response": "Muted ad"}


                return {
                    "status": "error",
                    "response": "⚠️ Ad is playing. Could not mute."
                }

            # 🔥 STEP 3: NORMAL VIDEO → USE PROPERTY
            # STEP 1: check already muted
            # 🔥 ALWAYS USE BUTTON (REAL USER ACTION)
            result = self.driver.execute_script("""
                const video = document.querySelector('video');
                const btn = document.querySelector('.ytp-mute-button');

                if (!video || !btn) return "NO_VIDEO";

                if (video.muted) {
                    return "ALREADY_MUTED";
                }

                btn.click();
                return "MUTED";
            """)

            if result == "ALREADY_MUTED":
                return {"status": "info", "response": "YouTube is already muted"}

            if result == "MUTED":
                return {"status": "success", "response": "Muted YouTube"}



        except:
            return {"status": "error", "response": "Mute failed."}

    def unmute(self):
        try:
            is_playing = self._is_playing()

            if is_playing is None:
                return {
                    "status": "error",
                    "response": "❌ No active YouTube video."
                }

            # 🔥 STEP 1: HANDLE AD FIRST
            is_ad = self.driver.execute_script("""
                return document.querySelector('.ytp-ad-player-overlay') !== null
                    || document.querySelector('.ytp-ad-text') !== null;
            """)

            if is_ad:
                result = self.driver.execute_script("""
                    const btn = document.querySelector('.ytp-mute-button');
                    if (!btn) return "NO_BUTTON";

                    let label = btn.getAttribute('aria-label')?.toLowerCase() || "";

                    // 🔥 already unmuted
                    if (label.includes("mute") && !label.includes("unmute")) {
                        return "ALREADY_UNMUTED";
                    }

                    btn.click();
                    return "UNMUTED";
                """)

                if result == "ALREADY_UNMUTED":
                    return {"status": "info", "response": "Ad is already unmuted"}

                if result == "UNMUTED":
                    return {"status": "success", "response": "Unmuted ad"}



                return {
                    "status": "error",
                    "response": "⚠️ Could not unmute ad."
                }

            # 🔥 STEP 2: NORMAL VIDEO
            result = self.driver.execute_script("""
                const video = document.querySelector('video');
                const btn = document.querySelector('.ytp-mute-button');

                if (!video || !btn) return "NO_VIDEO";

                if (!video.muted) {
                    return "ALREADY_UNMUTED";
                }

                btn.click();
                return "UNMUTED";
            """)

            if result == "ALREADY_UNMUTED":
                return {"status": "info", "response": "YouTube is already unmuted"}

            if result == "UNMUTED":
                return {"status": "success", "response": "Unmuted YouTube"}

            return {
                "status": "error",
                "response": "❌ Could not unmute YouTube."
            }

        except:
            return {"status": "error", "response": "Unmute failed."}

    def volume_up(self):
        try:
            self.driver.execute_script("""
                const video = document.querySelector('video');
                if (video) {
                    video.volume = Math.min(1, video.volume + 0.2);
                }
            """)
            return {"status": "success", "response": "Increased YouTube volume"}

        except:
            return {"status": "error", "response": "Could not increase volume"}

    def volume_down(self):
        try:
            self.driver.execute_script("""
                const video = document.querySelector('video');
                if (video) {
                    video.volume = Math.max(0, video.volume - 0.2);
                }
            """)
            return {"status": "success", "response": "Decreased YouTube volume"}

        except:
            return {"status": "error", "response": "Could not decrease volume"}

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
                "response": "No favorite songs found."
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