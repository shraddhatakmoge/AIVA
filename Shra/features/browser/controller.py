import inspect
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
        self.last_active_platform = None
        self.pending_email = None

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
            "whatsapp": WhatsApp(self.driver),
        }

        self.tabs = {}
        self.last_active_platform = None

    # -------------------------------------------------
    # OPEN TAB
    # -------------------------------------------------
    def _open_new_tab(self, target):

        platform = self.platform_instances[target]

        if not self.tabs:
            handle = self.driver.current_window_handle
            self.tabs[target] = handle
            self.last_active_platform = target
            return platform.open()

        url = platform.get_url()
        self.driver.execute_script(f"window.open('{url}', '_blank');")

        new_handle = self.driver.window_handles[-1]
        self.driver.switch_to.window(new_handle)

        self.tabs[target] = new_handle
        self.last_active_platform = target

        bring_browser_to_front()

        return platform.open()

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
                self.last_active_platform = target
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
    # TARGET DETECTION
    # -------------------------------------------------
    def _detect_target(self, structured):

        target = structured.get("target")

        if target:
            return target

        if self.last_active_platform:
            return self.last_active_platform

        return "youtube"

    # -------------------------------------------------
    # SAFE METHOD EXECUTION
    # -------------------------------------------------
    def _execute_platform_method(self, platform, action, query):

        if not hasattr(platform, action):
            return {
                "status": "error",
                "response": f"Action '{action}' not supported on this platform"
            }

        method = getattr(platform, action)

        try:
            if isinstance(query, dict):
                # 🔥 SPECIAL CASE FOR WHATSAPP
                if platform.__class__.__name__ == "WhatsApp":
                    result = method(query)
                else:
                    result = method(**query)
            elif query is not None:
                result = method(query)
            else:
                result = method()

            if result is None:
                return {
                    "status": "error",
                    "response": f"'{action}' did not return a response."
                }

            return result

        except Exception as e:
            return {
                "status": "error",
                "response": str(e)
            }

    # -------------------------------------------------
    # HANDLE COMMAND
    # -------------------------------------------------
    def handle(self, structured):

        # 🔥 VOICE FOLLOW-UP HANDLER
        if self.pending_email:

            user_input = structured.get("query") or structured.get("message") or ""

            if isinstance(user_input, dict):
                user_input = str(user_input)

            if "@" in user_input:
                to_email = user_input.strip()

                subject = self.pending_email.get("subject")
                body = self.pending_email.get("body")

                self.pending_email = None

                gmail = Gmail(None)
                return gmail.send_email(to_email, subject, body)

            else:
                return {
                    "status": "ask",
                    "response": "That doesn't look like an email. Please say a valid email address."
                }

        if not structured:
            return {
                "status": "error",
                "response": "Invalid command structure."
            }

        # MULTI ACTION SUPPORT
        if "actions" in structured:
            results = []
            for act in structured["actions"]:
                result = self.handle(act)
                results.append(result)

            return {
                "status": "success",
                "response": results
            }

        action = structured.get("action")
        query = structured.get("query")

        if not action:
            return {
                "status": "error",
                "response": "No action provided."
            }

        # 🔥 FIX 1: TARGET WAS MISSING
        target = self._detect_target(structured)

        # CLOSE ENTIRE BROWSER
        if action == "close_browser":
            try:
                self.driver.quit()
                self.driver = None
                self.tabs = {}
                self.last_active_platform = None

                return {
                    "status": "success",
                    "response": "Closed entire browser session."
                }
            except Exception as e:
                return {
                    "status": "error",
                    "response": str(e)
                }

        # GMAIL SEND
        if action == "send_email":
            gmail = Gmail(None)

            query_data = structured.get("query", {})

            to = query_data.get("to")
            subject = query_data.get("subject")
            message = query_data.get("body")

            from contacts import CONTACTS

            if to:
                to_clean = to.strip().lower()

                if to_clean in CONTACTS:
                    to = CONTACTS[to_clean]

                elif "@" not in to:
                    self.pending_email = {
                        "to_name": to_clean,
                        "subject": subject,
                        "body": message
                    }

                    return {
                        "status": "ask",
                        "response": f"I don't know {to}. Please tell me the email."
                    }

            if not message:
                message = "No message provided"
            if not subject:
                subject = "No Subject"

            return gmail.send_email(to, subject, message)

        # 🔥 FIX 2: GMAIL OPEN (ADDED — SAFE)
        if action == "open" and structured.get("target") in ["gmail", "mail"]:
            import webbrowser
            webbrowser.open("https://mail.google.com")

            return {
                "status": "success",
                "response": "Opened Gmail"
            }

        # NORMAL FLOW
        self._ensure_driver()

        if target not in self.platform_instances:
            return {
                "status": "error",
                "response": f"Platform '{target}' not supported"
            }

        action = self._normalize_action(action)
        platform = self.platform_instances[target]

        # OPEN
        if action == "open":
            if target in self.tabs and self._switch_to_tab(target):
                return {
                    "status": "success",
                    "response": f"{target.capitalize()} already open"
                }

            return self._open_new_tab(target)

        # CLOSE TAB
        if action == "close":
            if target in self.tabs:
                try:
                    self._switch_to_tab(target)
                    self.driver.close()
                    self.tabs.pop(target, None)

                    remaining_handles = self.driver.window_handles

                    if remaining_handles:
                        self.driver.switch_to.window(remaining_handles[0])
                        bring_browser_to_front()

                        for name, handle in self.tabs.items():
                            if handle == remaining_handles[0]:
                                self.last_active_platform = name
                                break
                    else:
                        self.last_active_platform = None

                    return {
                        "status": "success",
                        "response": f"Closed {target.capitalize()}"
                    }

                except Exception as e:
                    return {
                        "status": "error",
                        "response": f"Could not close tab: {str(e)}"
                    }

            return {
                "status": "error",
                "response": f"{target.capitalize()} is not open."
            }

        # AUTO OPEN
        if target not in self.tabs:
            open_result = self._open_new_tab(target)
            if open_result.get("status") not in ["success", "login_required"]:
                return open_result
        else:
            self._switch_to_tab(target)

        # EXECUTE
        result = self._execute_platform_method(platform, action, query)

        if result.get("status") == "success":
            self.last_active_platform = target

        return result