from selenium.common.exceptions import WebDriverException

from AIVA.Shra.features.browser.driver import DriverManager
from AIVA.Shra.features.browser.platforms.youtube import YouTube
from AIVA.Shra.features.browser.platforms.spotify import Spotify
from AIVA.Shra.features.browser.platforms.google import Google
from AIVA.Shra.features.browser.platforms.gmail import Gmail
from AIVA.Shra.features.browser.platforms.whatsapp import WhatsApp


class BrowserController:

    def __init__(self):
        self.driver = None
        self.platform_instances = {}
        self.tabs = {}  # platform -> window handle

    # -------------------------------------------------
    # ENSURE DRIVER IS ALIVE
    # -------------------------------------------------
    def _ensure_driver(self):
        try:
            if self.driver:
                _ = self.driver.current_url
                return
        except Exception:
            print("⚠ Driver session lost. Restarting...")

        self.driver = DriverManager.get_instance().get_driver()

        self.platform_instances = {
            "youtube": YouTube(self.driver),
            "spotify": Spotify(self.driver),
            "google": Google(self.driver),
            "gmail": Gmail(self.driver),
            "whatsapp": WhatsApp(self.driver),
        }

        self.tabs = {}

    # -------------------------------------------------
    # OPEN PLATFORM IN CLEAN NEW TAB (NO BLANKS)
    # -------------------------------------------------
    def _open_new_tab(self, target):

        platform = self.platform_instances[target]

        # If first open, reuse current tab
        if not self.tabs:
            handle = self.driver.current_window_handle
            self.tabs[target] = handle
            return platform.open()

        # Otherwise open new tab WITH URL directly
        url = platform.get_url()

        self.driver.execute_script(f"window.open('{url}', '_blank');")

        # Get newest tab
        new_handle = self.driver.window_handles[-1]
        self.driver.switch_to.window(new_handle)

        self.tabs[target] = new_handle

        return {
            "status": "success",
            "response": f"Opened {target.capitalize()}"
        }
    # -------------------------------------------------
    # SWITCH TO EXISTING TAB SAFELY
    # -------------------------------------------------
    def _switch_to_tab(self, target):

        handle = self.tabs.get(target)

        if not handle:
            return False

        try:
            if handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                return True
            else:
                self.tabs.pop(target, None)
                return False
        except WebDriverException:
            self.tabs.pop(target, None)
            return False

    # -------------------------------------------------
    # CLOSE SPECIFIC PLATFORM TAB
    # -------------------------------------------------
    def _close_tab(self, target):

        if target not in self.tabs:
            return {
                "status": "error",
                "response": f"{target.capitalize()} is not open"
            }

        handle = self.tabs[target]

        try:
            if handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                self.driver.close()
        except Exception:
            pass

        self.tabs.pop(target, None)

        # SAFELY CHECK IF SESSION STILL EXISTS
        try:
            remaining = self.driver.window_handles
        except Exception:
            # Session already dead
            self.driver = None
            return {
                "status": "success",
                "response": f"{target.capitalize()} closed"
            }

        if not remaining:
            # No tabs left → quit driver cleanly
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

        else:
            self.driver.switch_to.window(remaining[0])

        return {
            "status": "success",
            "response": f"{target.capitalize()} closed"
        }
    # -------------------------------------------------
    # MAIN HANDLER
    # -------------------------------------------------
    def handle(self, structured):

        action = structured.get("action")
        target = structured.get("target")
        query = structured.get("query")

        self._ensure_driver()

        if target not in self.platform_instances:
            return {
                "status": "error",
                "response": "Platform not supported"
            }

        platform = self.platform_instances[target]

        # ---------------------------------------------
        # OPEN COMMAND
        # ---------------------------------------------
        if action == "open":

            if target in self.tabs and self._switch_to_tab(target):
                return {
                    "status": "success",
                    "response": f"{target.capitalize()} already open"
                }

            return self._open_new_tab(target)

        # ---------------------------------------------
        # CLOSE COMMAND
        # ---------------------------------------------
        if action == "close":
            return self._close_tab(target)

        # ---------------------------------------------
        # OTHER ACTIONS (search / play)
        # ---------------------------------------------
        if target not in self.tabs:
            # Auto open if not open
            self._open_new_tab(target)
        else:
            self._switch_to_tab(target)

        if hasattr(platform, action):
            method = getattr(platform, action)

            if query:
                return method(query)

            return method()

        return {
            "status": "error",
            "response": f"Action '{action}' not supported on {target}"
        }