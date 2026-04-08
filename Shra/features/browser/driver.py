import time

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import os


class DriverManager:
    _instance = None

    def __init__(self):
        self.driver = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DriverManager()
        return cls._instance

    # -------------------------------------------------
    # Public Method: Get Driver
    # -------------------------------------------------
    def get_driver(self):

        if self.driver:
            try:
                # 🔥 SIMPLE CHECK ONLY (DON’T OVERCHECK)
                _ = self.driver.title
                return self.driver

            except Exception:
                print("⚠ Driver session invalid. Restarting Chrome...")
                self._safe_quit()
                self.driver = None

        self._start_driver()
        return self.driver

    # -------------------------------------------------
    # Start Chrome with Dedicated Project Profile
    # -------------------------------------------------
    def _start_driver(self):

        chrome_options = Options()

        # 🔥 ADD THIS LINE
        chrome_options.page_load_strategy = "none"
        chrome_options.add_argument("--start-maximized")

        # -------------------------------------------------
        # Stability Flags
        # -------------------------------------------------
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # -------------------------------------------------
        # 🔥 Persistent Chrome Profile (Login stays saved)
        # -------------------------------------------------
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        profile_path = os.path.join(BASE_DIR, "chrome_profile")

        os.makedirs(profile_path, exist_ok=True)
        chrome_options.add_argument(f"--user-data-dir={profile_path}")

        # -------------------------------------------------
        # Remove Automation Detection Flags
        chrome_options.add_argument("--remote-allow-origins=*")
        # 🔥 FIX SPOTIFY LOADING ISSUE
        chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
        chrome_options.add_argument(
            "--disable-features=PreloadMediaEngagementData,MediaEngagementBypassAutoplayPolicies")
        chrome_options.add_argument("--use-fake-ui-for-media-stream")

        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")

        # 🔥 SANDBOX FIX
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # -------------------------------------------------
        # Start Driver
        # -------------------------------------------------
        try:
            self.driver = uc.Chrome(options=chrome_options)
            self.driver.get("about:blank")  # 🔥 ensures clean base tab
            self.driver.set_page_load_timeout(8)
            time.sleep(2)
        except Exception as e:
            print("❌ Failed to start Chrome:", e)
            raise

        # -------------------------------------------------
        # Hide webdriver flag
        # -------------------------------------------------
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)

        print("✅ Chrome started with persistent profile")

    # -------------------------------------------------
    # Safe Quit
    # -------------------------------------------------
    def _safe_quit(self):
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass

    def quit_driver(self):
        self._safe_quit()
        self.driver = None