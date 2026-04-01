import inspect
import os
from selenium.common.exceptions import WebDriverException
from AIVA.Shra.features.browser.driver import DriverManager
from AIVA.Shra.features.browser.platforms.youtube import YouTube
from AIVA.Shra.features.browser.platforms.spotify import Spotify
from AIVA.Shra.features.browser.platforms.google import Google
from AIVA.Shra.features.browser.platforms.gmail import Gmail
from AIVA.Shra.features.browser.platforms.whatsapp import WhatsApp
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front

import glob

def find_file_by_name(filename):
    search_dirs = [
        os.path.join(os.path.expanduser("~"), "Downloads"),
        os.path.join(os.path.expanduser("~"), "Documents"),
        os.path.join(os.path.expanduser("~"), "Desktop")
    ]

    matches = []

    for folder in search_dirs:
        matches.extend(glob.glob(os.path.join(folder, f"*{filename}*")))

    return matches

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

        # 🔥 OPEN EMPTY TAB ONLY (NO URL)
        self.driver.execute_script("window.open('', '_blank');")

        new_handle = self.driver.window_handles[-1]
        self.driver.switch_to.window(new_handle)

        self.tabs[target] = new_handle
        self.last_active_platform = target

        bring_browser_to_front()

        # 🔥 LET PLATFORM HANDLE URL
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

        action = structured.get("action")
        target = structured.get("target")

        # 🔥 1. ALWAYS respect user explicit target
        if target:
            return target

        # 🔥 2. Context-aware actions → use last active
        context_actions = ["pause", "resume", "stop", "add_to_favorites"]

        if action in context_actions:
            if self.last_active_platform:
                return self.last_active_platform

        # 🔥 3. fallback to last active
        if self.last_active_platform:
            return self.last_active_platform

        # 🔥 4. default fallback
        return "youtube"
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

        # 🔥 MULTI-STEP EMAIL FLOW (FIXED)
        if self.pending_email:
            # 🔥 FORCE RAW INPUT (BYPASS PARSER COMPLETELY)
            # 🔥 FINAL FIX (DO NOT CHANGE ANYTHING ELSE)

            if isinstance(structured, dict):
                user_input = structured.get("query") or structured.get("message") or ""
                if not user_input:
                    user_input = str(structured)
            else:
                user_input = str(structured)

            user_input = str(user_input).strip()

            step = self.pending_email.get("step")

            # SUBJECT
            if step == "subject":
                self.pending_email["subject"] = user_input
                self.pending_email["step"] = "body"
                return {"status": "ask", "response": "What should I write in the email?"}

            # BODY
            if step == "body":
                self.pending_email["body"] = user_input
                self.pending_email["step"] = "attachment"
                return {"status": "ask", "response": "Do you want to attach anything? (yes/no)"}

            # ATTACHMENT DECISION
            if step == "attachment":
                if user_input.lower() in ["yes", "y"]:
                    self.pending_email["step"] = "attachment_file"
                    return {"status": "ask", "response": "What file do you want to attach? (e.g., resume, pdf, image)"}
                else:
                    self.pending_email["step"] = "confirm"

            # ATTACHMENT FILE
            if step == "attachment_file":

                clean_input = user_input.strip().strip('"').strip("'")

                # CASE 1: full path
                if os.path.exists(clean_input):
                    self.pending_email["attachment"] = clean_input
                    self.pending_email["step"] = "confirm"

                else:
                    matches = find_file_by_name(clean_input)

                    if not matches:
                        return {
                            "status": "ask",
                            "response": f"I couldn’t find any file named '{clean_input}'. Try again."
                        }

                    # store matches for confirmation
                    self.pending_email["file_matches"] = matches
                    self.pending_email["step"] = "confirm_file"

                    return {
                        "status": "ask",
                        "response": f"I found: {os.path.basename(matches[0])}. Is this the file you want? (yes/no)"
                    }

            if step == "confirm_file":

                if user_input.lower() in ["yes", "y"]:
                    selected = self.pending_email["file_matches"][0]
                    self.pending_email["attachment"] = selected
                    self.pending_email["step"] = "confirm"

                    return {
                        "status": "ask",
                        "response": "Got it. Do you want to send the email now? (yes/no)"
                    }

                elif user_input.lower() in ["no", "n"]:
                    # 🔥 THIS IS THE MISSING FIX
                    self.pending_email["step"] = "attachment_file"

                    return {
                        "status": "ask",
                        "response": "Okay, tell me the file name again."
                    }

                else:
                    return {
                        "status": "ask",
                        "response": "Please answer yes or no."
                    }
            # CONFIRMATION
            if step == "confirm":

                # FIRST TIME → SHOW PREVIEW
                if user_input.lower() not in ["yes", "y", "no", "n"]:
                    preview = f"""
        To: {self.pending_email['to']}
        Subject: {self.pending_email['subject']}
        Body: {self.pending_email['body']}
        Attachment: {self.pending_email.get('attachment', 'None')}
        """
                    return {
                        "status": "ask",
                        "response": f"{preview}\nDo you want to send it? (yes/no)"
                    }

                # CANCEL
                if user_input.lower() in ["no", "n", "cancel", "stop"]:
                    self.pending_email = None
                    return {
                        "status": "success",
                        "response": "Email discarded."
                    }

                # SEND
                gmail = Gmail(None)

                to = self.pending_email["to"]
                subject = self.pending_email["subject"]
                body = self.pending_email["body"]
                attachment = self.pending_email.get("attachment")

                self.pending_email = None

                return gmail.send_email(to, subject, body, attachment)

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

        # ✅ READ EMAIL HANDLER
        if action == "read_latest_email":
            gmail = Gmail(None)
            return gmail.read_latest_email()

        if not action:
            return {
                "status": "error",
                "response": "No action provided."
            }

        target = self._detect_target(structured)

        # 🔥 FIX: sync structured with actual target
        structured["target"] = target
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

        # EMAIL ENTRY
        if action == "send_email":

            query_data = structured.get("query", {})
            to = query_data.get("to")

            from contacts import CONTACTS

            if to:
                to_clean = to.strip().lower()

                if to_clean in CONTACTS:
                    to = CONTACTS[to_clean]


                elif "@" not in to:

                    self.pending_email = {

                        "to": None,

                        "subject": None,

                        "body": None,

                        "attachment": None,

                        "step": "email"

                    }

                    return {

                        "status": "ask",

                        "response": f"I don't know {to}. Please tell me the email."

                    }

            self.pending_email = {
                "to": to,
                "subject": None,
                "body": None,
                "attachment": None,
                "step": "subject"
            }

            return {
                "status": "ask",
                "response": "What should be the subject?"
            }

        # GMAIL OPEN
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

                    # 🔥 FIX: Prevent closing last tab
                    if len(self.driver.window_handles) == 1:
                        return {
                            "status": "info",
                            "response": "Cannot close the last tab. Use 'close browser' instead."
                        }

                    self.driver.close()
                    self.tabs.pop(target, None)

                    return {
                        "status": "success",
                        "response": f"Closed {target.capitalize()}"
                    }

                except Exception as e:
                    return {
                        "status": "error",
                        "response": f"Could not close tab: {str(e)}"
                    }
        # AUTO OPEN (🔥 FIX APPLIED HERE)
        just_opened = False

        if target not in self.tabs:
            open_result = self._open_new_tab(target)
            just_opened = True

            if open_result.get("status") not in ["success", "login_required"]:
                return open_result
        else:
            self._switch_to_tab(target)

        # EXECUTE (🔥 FIX APPLIED HERE)
        if just_opened and action == "play":
            result = platform.play(query)
        else:
            result = self._execute_platform_method(platform, action, query)

        if result.get("status") == "success":
            self.last_active_platform = target

        return result