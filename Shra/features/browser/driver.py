from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
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
                _ = self.driver.current_url
                return self.driver
            except Exception:
                print("⚠ Driver session invalid. Restarting Chrome...")
                self._safe_quit()
                self.driver = None

        self._start_driver()
        return self.driver

    # -------------------------------------------------
    # Start Chrome with Dedicated Automation Profile
    # -------------------------------------------------
    def _start_driver(self):

        chrome_options = Options()

        chrome_options.add_argument("--start-maximized")

        # Use REAL trusted profile
        chrome_options.add_argument(r"--user-data-dir=C:\AIVA_Real_Profile")

        # 🔥 VERY IMPORTANT: remove automation detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        service = Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # 🔥 Hide webdriver flag
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)

        print("✅ Chrome started with REAL trusted profile")
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