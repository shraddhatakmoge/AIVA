import inspect
import os
import glob
from difflib import get_close_matches

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
        self.previous_tab = None  # 🔥 NEW

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

    def _switch_to_tab(self, target):

        handle = self.tabs.get(target)

        if not handle:
            return False

        try:
            if handle in self.driver.window_handles:
                # 🔥 STORE PREVIOUS TAB BEFORE SWITCHING
                self.previous_tab = self.driver.current_window_handle

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

    def switch_to_previous_tab(self):

        if self.previous_tab and self.previous_tab in self.driver.window_handles:
            self.driver.switch_to.window(self.previous_tab)
            bring_browser_to_front()

            return {
                "status": "success",
                "response": "Switched back to previous tab"
            }

        return {
            "status": "error",
            "response": "No previous tab found"
        }

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
    # EMAIL PREVIEW HELPER
    # -------------------------------------------------
    def _build_email_preview(self):
        attachment = self.pending_email.get("attachment")
        attachment_name = os.path.basename(attachment) if attachment else "None"

        return f"""Here’s your email:
To: {self.pending_email['to']}
Subject: {self.pending_email['subject']}
Body: {self.pending_email['body']}
Attachment: {attachment_name}

What would you like to do next?
You can say:
- send it
- change subject
- change body
- change attachment
- cancel"""

    # -------------------------------------------------
    # HANDLE COMMAND
    # -------------------------------------------------
    def handle(self, structured):

        # 🔥 MULTI-STEP EMAIL FLOW
        if self.pending_email:

            # 🔥 FORCE RAW INPUT (BYPASS PARSER COMPLETELY)
            if isinstance(structured, dict):
                user_input = structured.get("query") or structured.get("message") or ""

                # 🔥 CRITICAL FIX: prevent dict fallback
                if isinstance(user_input, dict):
                    user_input = ""

            else:
                user_input = str(structured)

            user_input = str(user_input).strip()
            user_lower = user_input.lower()
            step = self.pending_email.get("step")

            # SUBJECT
            if step == "subject":
                self.pending_email["subject"] = user_input
                self.pending_email["step"] = "body"
                return {
                    "status": "ask",
                    "response": "What should I write in the email?"
                }

            # BODY
            if step == "body":
                self.pending_email["body"] = user_input
                self.pending_email["step"] = "attachment"
                return {
                    "status": "ask",
                    "response": "Do you want to attach anything? (yes/no)"
                }

            # ATTACHMENT DECISION
            if step == "attachment":
                if user_lower in ["yes", "y"]:
                    self.pending_email["step"] = "attachment_file"
                    return {
                        "status": "ask",
                        "response": "What file do you want to attach? (e.g., resume, pdf, image)"
                    }

                if user_lower in ["no", "n"]:
                    self.pending_email["step"] = "confirm"
                    return {
                        "status": "ask",
                        "response": f"No attachment added.\n\n{self._build_email_preview()}"
                    }

                return {
                    "status": "ask",
                    "response": "Please answer yes or no."
                }

            # EDIT SUBJECT
            if step == "edit_subject":
                self.pending_email["subject"] = user_input
                self.pending_email["step"] = "confirm"
                return {
                    "status": "ask",
                    "response": f"Subject updated.\n\n{self._build_email_preview()}"
                }

            # EDIT BODY
            if step == "edit_body":
                self.pending_email["body"] = user_input
                self.pending_email["step"] = "confirm"
                return {
                    "status": "ask",
                    "response": f"Body updated.\n\n{self._build_email_preview()}"
                }

            # ATTACHMENT FILE
            if step == "attachment_file":

                clean_input = user_input.strip().strip('"').strip("'")

                # CASE 1: full path
                if os.path.exists(clean_input):
                    self.pending_email["attachment"] = clean_input
                    self.pending_email["step"] = "confirm"

                    filename = os.path.basename(clean_input)

                    return {
                        "status": "ask",
                        "response": f'Got it 👍 I\'ve attached "{filename}"\n\n{self._build_email_preview()}'
                    }

                matches = find_file_by_name(clean_input)

                if not matches:
                    return {
                        "status": "ask",
                        "response": f"I couldn’t find any file named '{clean_input}'. Try again."
                    }

                # 🔥 LIMIT TOP 5 RESULTS
                matches = matches[:5]

                # 🔥 CASE 1: ONLY ONE FILE → AUTO SELECT
                if len(matches) == 1:
                    selected = matches[0]

                    self.pending_email["file_matches"] = matches
                    self.pending_email["step"] = "confirm_single_file"

                    filename = os.path.basename(selected)

                    return {
                        "status": "ask",
                        "response": f'I found "{filename}". Is this the file you want to attach? (yes/no)'
                    }

                # 🔥 CASE 2: MULTIPLE FILES → ASK USER
                self.pending_email["file_matches"] = matches
                self.pending_email["step"] = "select_file"

                options = "\n".join(
                    [f"{i + 1}. {os.path.basename(f)}" for i, f in enumerate(matches)]
                )

                return {
                    "status": "ask",
                    "response": f"I found multiple files:\n{options}\n\nSelect one (number or name):"
                }

            if step == "confirm_single_file":

                matches = self.pending_email.get("file_matches", [])
                selected = matches[0]

                if user_lower in ["yes", "y"]:
                    self.pending_email["attachment"] = selected
                    self.pending_email["step"] = "confirm"

                    filename = os.path.basename(selected)

                    return {
                        "status": "ask",
                        "response": f'Got it 👍 I\'ve attached "{filename}"\n\n{self._build_email_preview()}'
                    }

                elif user_lower in ["no", "n"]:
                    self.pending_email["step"] = "attachment_file"

                    return {
                        "status": "ask",
                        "response": "Okay, tell me the file name again."
                    }

                else:
                    return {
                        "status": "ask",
                        "response": "Please say yes or no."
                    }
            # SELECT FILE
            if step == "select_file":

                matches = self.pending_email.get("file_matches", [])
                filenames = [os.path.basename(f).lower() for f in matches]

                # ---------------------------
                # 1. NUMBER (1, 2, 3)
                # ---------------------------
                if user_lower.isdigit():
                    index = int(user_lower) - 1
                    if 0 <= index < len(matches):
                        selected = matches[index]
                    else:
                        return {
                            "status": "ask",
                            "response": "Invalid number. Try again."
                        }

                # ---------------------------
                # 2. WORD NUMBERS
                # ---------------------------
                elif user_lower in ["first", "1st"]:
                    selected = matches[0]

                elif user_lower in ["second", "2nd"] and len(matches) > 1:
                    selected = matches[1]

                elif user_lower in ["third", "3rd"] and len(matches) > 2:
                    selected = matches[2]

                elif user_lower in ["fourth", "4th"] and len(matches) > 3:
                    selected = matches[3]

                elif user_lower in ["fifth", "5th"] and len(matches) > 4:
                    selected = matches[4]

                elif "last" in user_lower:
                    selected = matches[-1]

                # ---------------------------
                # 3. FUZZY MATCH
                # ---------------------------
                else:
                    close = get_close_matches(user_lower, filenames, n=1, cutoff=0.3)

                    if close:
                        idx = filenames.index(close[0])
                        selected = matches[idx]
                    else:
                        return {
                            "status": "ask",
                            "response": "I couldn't match that. Try saying part of the file name or number."
                        }

                self.pending_email["attachment"] = selected
                self.pending_email["step"] = "confirm"

                filename = os.path.basename(selected)

                return {
                    "status": "ask",
                    "response": f'✅ File selected: "{filename}"\n\n{self._build_email_preview()}\n\nDo you want to send the mail now? (yes/no)'
                }

            # CONFIRMATION
            # CONFIRMATION
            if step == "confirm":

                # ----------------------
                # YES → SEND MAIL
                # ----------------------
                if user_lower in ["yes", "y", "send", "send it", "go ahead", "ok", "okay"]:
                    gmail = Gmail(None)

                    to = self.pending_email["to"]
                    subject = self.pending_email["subject"]
                    body = self.pending_email["body"]
                    attachment = self.pending_email.get("attachment")

                    self.pending_email = None

                    return gmail.send_email(to, subject, body, attachment)

                # ----------------------
                # NO → EDIT OPTIONS
                # ----------------------
                elif user_lower in ["no", "n"]:
                    return {
                        "status": "ask",
                        "response": """What would you like to change?
            You can say:
            - change subject
            - change body
            - change attachment
            - cancel"""
                    }

                # ----------------------
                # EDIT SUBJECT
                # ----------------------
                elif "subject" in user_lower:
                    self.pending_email["step"] = "edit_subject"
                    return {
                        "status": "ask",
                        "response": "Enter new subject:"
                    }

                # ----------------------
                # EDIT BODY
                # ----------------------
                elif "body" in user_lower or "message" in user_lower:
                    self.pending_email["step"] = "edit_body"
                    return {
                        "status": "ask",
                        "response": "Enter new body:"
                    }

                # ----------------------
                # CHANGE ATTACHMENT
                # ----------------------
                elif "attachment" in user_lower or "file" in user_lower:
                    self.pending_email["step"] = "attachment_file"
                    return {
                        "status": "ask",
                        "response": "Enter new file name:"
                    }

                # ----------------------
                # CANCEL
                # ----------------------
                elif "cancel" in user_lower:
                    self.pending_email = None
                    return {
                        "status": "success",
                        "response": "Email discarded."
                    }

                # ----------------------
                # DEFAULT
                # ----------------------
                return {
                    "status": "ask",
                    "response": "Please answer yes or no."
                }
                # CANCEL
                if any(
                    phrase in user_lower
                    for phrase in ["no", "n", "5", "cancel", "stop", "discard"]
                ):
                    self.pending_email = None
                    return {
                        "status": "success",
                        "response": "Email discarded."
                    }

                # EDIT SUBJECT
                if user_lower in ["2", "edit subject"] or "subject" in user_lower:
                    self.pending_email["step"] = "edit_subject"
                    return {
                        "status": "ask",
                        "response": "Enter new subject:"
                    }

                # EDIT BODY
                if user_lower in ["3", "edit body"] or "body" in user_lower or "message" in user_lower:
                    self.pending_email["step"] = "edit_body"
                    return {
                        "status": "ask",
                        "response": "Enter new body:"
                    }

                # CHANGE / ADD ATTACHMENT
                if (
                    user_lower in ["4", "change attachment", "add attachment"]
                    or "attachment" in user_lower
                    or "file" in user_lower
                    or "attach" in user_lower
                ):
                    self.pending_email["step"] = "attachment_file"
                    return {
                        "status": "ask",
                        "response": "Enter new file name:"
                    }

                # DEFAULT → SHOW GUIDED PREVIEW
                return {
                    "status": "ask",
                    "response": self._build_email_preview()
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

        # 🔥 HANDLE NON-PLATFORM ACTIONS FIRST

        if action == "switch_back":
            return self.switch_to_previous_tab()

        if action == "switch_to_google":
            if "google" in self.tabs:
                self._switch_to_tab("google")
                return {
                    "status": "success",
                    "response": "Switched to Google"
                }
            return {
                "status": "error",
                "response": "Google tab not found"
            }
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
        # 🔥 FORCE GOOGLE TAB FOR SEARCH (CORRECT POSITION)
        if action == "search" and target == "google":

            self._ensure_driver()

            if "google" in self.tabs:
                self._switch_to_tab("google")
            else:
                self._open_new_tab("google")

            platform = self.platform_instances["google"]
            return platform.search(query)

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

        # AUTO OPEN
        just_opened = False

        if target not in self.tabs:
            open_result = self._open_new_tab(target)
            just_opened = True

            if open_result.get("status") not in ["success", "login_required"]:
                return open_result
        else:
            if action not in ["scroll"]:
                self._switch_to_tab(target)

        # EXECUTE
        # 🔥 SPECIAL FIX FOR SCROLL (ALWAYS CURRENT TAB)
        if action == "scroll":

            direction = "down"
            if isinstance(query, dict):
                direction = query.get("direction", "down")

            if direction == "down":
                self.driver.execute_script("window.scrollBy(0, 600);")
            else:
                self.driver.execute_script("window.scrollBy(0, -600);")

            return {
                "status": "success",
                "response": f"Scrolled {direction}"
            }

        # NORMAL EXECUTION
        if just_opened and action == "play":
            result = platform.play(query)
        else:
            result = self._execute_platform_method(platform, action, query)

        if result.get("status") == "success":
            self.last_active_platform = target

        return result