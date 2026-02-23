from selenium.common.exceptions import WebDriverException
from AIVA.Shra.features.browser.driver import DriverManager
from AIVA.Shra.features.browser.platforms.youtube import YouTube
from AIVA.Shra.features.browser.platforms.spotify import Spotify
from AIVA.Shra.features.browser.platforms.google import Google
from AIVA.Shra.features.browser.platforms.gmail import Gmail
from AIVA.Shra.features.browser.platforms.whatsapp import WhatsApp
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front


class BrowserController:

    def __init__(self):
        self.driver = None
        self.platform_instances = {}
        self.tabs = {}

    # -------------------------------------------------
    # ENSURE DRIVER
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
    # OPEN TAB
    # -------------------------------------------------
    def _open_new_tab(self, target):

        platform = self.platform_instances[target]

        if not self.tabs:
            handle = self.driver.current_window_handle
            self.tabs[target] = handle
            return platform.open()

        url = platform.get_url()
        self.driver.execute_script(f"window.open('{url}', '_blank');")

        new_handle = self.driver.window_handles[-1]
        self.driver.switch_to.window(new_handle)

        self.tabs[target] = new_handle
        bring_browser_to_front()

        return {
            "status": "success",
            "response": f"Opened {target.capitalize()}"
        }

    # -------------------------------------------------
    # SWITCH TAB
    # -------------------------------------------------
    def _switch_to_tab(self, target):

        handle = self.tabs.get(target)

        if not handle:
            return False

        try:
            if handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                bring_browser_to_front()
                return True
            else:
                self.tabs.pop(target, None)
                return False
        except WebDriverException:
            self.tabs.pop(target, None)
            return False

    # -------------------------------------------------
    # NORMALIZE ACTION
    # -------------------------------------------------
    def _normalize_action(self, action):

        mapping = {
            "play_music": "play",
            "stop_music": "stop",
            "pause_music": "pause",
            "resume_music": "resume",
            "open_app": "open",
            "close_app": "close",
            "add_to_favourite": "add_to_favorites",
            "add_to_favorite": "add_to_favorites",
            "play_favourites": "play_favorite",
            "play_favourite": "play_favorite",
        }

        return mapping.get(action, action)

    # -------------------------------------------------
    # RULE BASED FAVORITE DETECTION
    # -------------------------------------------------
    def _rule_based_override(self, structured):

        action = structured.get("action")
        target = structured.get("target")
        query = structured.get("query")

        if action in ["play_music", "play"] and not query:
            return {
                "action": "add_to_favorites",
                "target": target,
                "query": None,
                "original_command": structured.get("original_command")
            }

        return structured

    # -------------------------------------------------
    # SMART TARGET DETECTION
    # -------------------------------------------------
    def _detect_target_from_text(self, structured):

        target = structured.get("target")

        if target:
            return target

        original = structured.get("original_command", "")
        original = original.lower()

        for platform_name in self.platform_instances.keys():
            if platform_name in original:
                return platform_name

        # Default fallback
        return "youtube"

    # -------------------------------------------------
    # HANDLE COMMAND
    # -------------------------------------------------
    def handle(self, structured):

        self._ensure_driver()

        structured = self._rule_based_override(structured)

        action = structured.get("action")
        query = structured.get("query")

        # 🔥 Smart target detection
        target = self._detect_target_from_text(structured)

        if target not in self.platform_instances:
            return {
                "status": "error",
                "response": "Platform not supported"
            }

        platform = self.platform_instances[target]

        action = self._normalize_action(action)

        # -------------------------------------------------
        # OPEN
        # -------------------------------------------------
        if action == "open":

            if target in self.tabs and self._switch_to_tab(target):
                return {
                    "status": "success",
                    "response": f"{target.capitalize()} already open"
                }

            return self._open_new_tab(target)

        # -------------------------------------------------
        # CLOSE
        # -------------------------------------------------
        if action == "close":

            if target in self.tabs and self._switch_to_tab(target):
                try:
                    self.driver.close()
                    self.tabs.pop(target, None)
                    return {
                        "status": "success",
                        "response": f"Closed {target.capitalize()}"
                    }
                except Exception:
                    return {
                        "status": "error",
                        "response": "Could not close tab"
                    }

        # -------------------------------------------------
        # AUTO OPEN IF NOT OPEN
        # -------------------------------------------------
        if target not in self.tabs:
            self._open_new_tab(target)
        else:
            self._switch_to_tab(target)

        # -------------------------------------------------
        # SAFE METHOD EXECUTION
        # -------------------------------------------------
        if hasattr(platform, action):

            method = getattr(platform, action)

            try:
                if query:
                    return method(query)
                else:
                    return method()
            except TypeError:
                return {
                    "status": "error",
                    "response": "Required information missing for this action."
                }
            except Exception as e:
                return {
                    "status": "error",
                    "response": str(e)
                }

        return {
            "status": "error",
            "response": f"Action '{action}' not supported"
        }