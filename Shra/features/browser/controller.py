import os
import glob
from difflib import get_close_matches
import random
from pathlib import Path
from AIVA.Shra.features.browser.driver import DriverManager
from AIVA.Shra.features.browser.platforms.youtube import YouTube
from AIVA.Shra.features.browser.platforms.spotify import Spotify
from AIVA.Shra.features.browser.platforms.google import Google
from AIVA.Shra.features.browser.platforms.gmail import Gmail
from AIVA.Shra.features.browser.platforms.whatsapp import WhatsApp
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front
from contacts import CONTACTS


class BrowserController:

    def __init__(self):
        self.driver = None
        self.platform_instances = {}
        self.tabs = {}
        self.last_active_platform = None
        self.pending_email = None
        self.previous_tab = None  # 🔥 NEW
        self.tab_metadata = {}  # 🔥 NEW
        self.contacts = CONTACTS
        self.pending_action = None

    # -------------------------------------------------
    # ENSURE DRIVER
    # -------------------------------------------------
    def _ensure_driver(self):

        if self.driver:
            try:
                if self.driver.session_id:
                    _ = self.driver.title  # ✅ SAFE CHECK
                    return
                else:
                    raise Exception("Invalid session")

            except Exception as e:
                print("⚠ Driver check failed, retrying once...", e)
                try:
                    _ = self.driver.title
                    return
                except:
                    print("⚠ Driver session lost. Restarting...")

        # 🔥 RESET EVERYTHING
        self.driver = DriverManager.get_instance().get_driver()

        if not self.platform_instances:
            self.platform_instances = {
                "youtube": YouTube(self.driver),
                "spotify": Spotify(self.driver),
                "google": Google(self.driver),
                "whatsapp": WhatsApp(self.driver),
            }



        # 🔥 CRITICAL FIX
        self.tabs = {}
        self.tab_metadata = {}
        self.previous_tab = None

    # -------------------------------------------------
    # OPEN TAB
    # -------------------------------------------------

    def _open_new_tab(self, target):

        platform = self.platform_instances[target]

        # 🔥 Selenium native tab (UI-independent, no hardcoding)
        self.driver.switch_to.new_window('tab')

        new_handle = self.driver.current_window_handle



        # Save tab
        self.tabs[target] = new_handle
        self.last_active_platform = target

        self.tab_metadata[new_handle] = {
            "platform": target,
            "title": ""
        }

        bring_browser_to_front()

        # 🔥 Pass tab handle to platform
        return platform.open(tab_handle=new_handle)
    # -------------------------------------------------
    # SWITCH TAB
    # -------------------------------------------------

    from pathlib import Path

    def find_file_by_name(self, filename):
        home = Path.home()

        search_dirs = [
            home / "Downloads",
            home / "Documents",
            home / "Desktop"
        ]

        search_dirs = [str(p) for p in search_dirs if p.exists()]

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
                self.previous_tab = self.driver.current_window_handle
                self.driver.switch_to.window(handle)
                self.last_active_platform = target
                bring_browser_to_front()
                return True
            else:
                raise Exception("Handle invalid")

        except Exception:
            # 🔥 FIX: remove broken handle
            print(f"⚠ Tab handle invalid, but keeping platform active")
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
        context_actions = ["pause", "resume", "stop"]

        if action in context_actions and self.last_active_platform:
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
            elif query:
                result = method(query)
            else:
                result = method()

            if result is None:
                return {
                    "status": "error",
                    "response": f"'{action}' did not return a response."
                }

            # 🔥 SAVE TAB TITLE (ADD THIS BEFORE RETURN)
            try:
                title = self.driver.title.lower()
                handle = self.driver.current_window_handle

                if handle in self.tab_metadata:
                    self.tab_metadata[handle]["title"] = title
            except:
                pass

            return result

        except Exception as e:
            return {
                "status": "error",
                "response": str(e)
            }

    def switch_to_tab_by_name(self, name):

        name = name.lower()

        for handle, meta in self.tab_metadata.items():

            # 🔥 MATCH PLATFORM (spotify, youtube etc.)
            if meta.get("platform") == name:
                self.driver.switch_to.window(handle)
                bring_browser_to_front()
                return {
                    "status": "success",
                    "response": f"Switched to {name}"
                }

            # 🔥 MATCH WEBSITE TITLE (azure, apple etc.)
            if name in meta.get("title", ""):
                self.driver.switch_to.window(handle)
                bring_browser_to_front()
                return {
                    "status": "success",
                    "response": f"Switched to {name} website"
                }

        return {
            "status": "error",
            "response": f"No tab found for {name}"
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

        # 🔥 HANDLE EMAIL CONTINUATION (CRITICAL FIX)
        if structured.get("action") == "continue_email" and self.pending_email:

            user_input = structured.get("query", "").strip()
            user_lower = user_input.lower()

            step = self.pending_email.get("step")

            # EMAIL ADDRESS STEP
            if step == "email":

                # 🔥 HANDLE DICT CASE ({"to": "shra"})
                if isinstance(structured.get("query"), dict):
                    user_input = structured["query"].get("to", "")

                # 🔥 HANDLE STRING CASE ("send mail to shra")
                user_input = str(user_input).lower().strip()

                if "send mail to" in user_input:
                    user_input = user_input.replace("send mail to", "").strip()

                if user_input in self.contacts:
                    user_input = self.contacts[user_input]

                self.pending_email["to"] = user_input
                self.pending_email["step"] = "subject"

                return {
                    "status": "ask",
                    "response": "What should be the subject?"
                }
                self.pending_email["step"] = "subject"

                return {
                    "status": "ask",
                    "response": "What should be the subject?"
                }

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

                matches = self.find_file_by_name(clean_input)

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
                    gmail = Gmail(self.driver)

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

        # -------------------------------------------------
        # 🔥 HANDLE PLATFORM REPLY (spotify / youtube)
        # -------------------------------------------------
        if self.pending_action:

            # 🔥 FORCE RAW USER INPUT (CRITICAL FIX)
            if isinstance(structured, str):
                user_input = structured.lower()

            else:
                user_input = (
                        structured.get("original_command")
                        or structured.get("query")
                        or ""
                )

            user_input = str(user_input).lower().strip()

            print("🔥 FINAL INPUT:", user_input)

            # 🔥 SAFETY
            if not user_input:
                return {
                    "status": "ask",
                    "response": "Please say Spotify or YouTube."
                }

            # ---------------- SPOTIFY ----------------
            if "spotify" in user_input:

                try:
                    print("🔥 Spotify flow started")

                    self._ensure_driver()

                    platform = self.platform_instances.get("spotify")
                    print("DEBUG platform:", platform)

                    if not platform:
                        return {
                            "status": "error",
                            "response": "Spotify not initialized."
                        }

                    if "spotify" not in self.tabs:
                        print("📂 Opening Spotify tab")
                        self._open_new_tab("spotify")
                    else:
                        print("🔁 Switching to Spotify tab")
                        self._switch_to_tab("spotify")

                    self.last_active_platform = "spotify"
                    self.pending_action = None

                    print("🎧 Calling play_favorite()")

                    result = platform.play_favorite()

                    print("✅ RESULT:", result)

                    if not result:
                        return {
                            "status": "error",
                            "response": "Spotify returned no response."
                        }

                    if result.get("status") == "login_required":
                        return {
                            "status": "info",
                            "response": "Please login to Spotify first."
                        }

                    return result

                except Exception as e:
                    print("❌ Spotify crash:", e)

                    return {
                        "status": "error",
                        "response": f"Spotify failed: {str(e)}"
                    }
            # ---------------- YOUTUBE ----------------
            elif "youtube" in user_input or "yt" in user_input:

                self._ensure_driver()  # 🔥 CRITICAL FIX

                platform = self.platform_instances.get("youtube")

                if "youtube" not in self.tabs:
                    self._open_new_tab("youtube")
                else:
                    self._switch_to_tab("youtube")

                self.last_active_platform = "youtube"
                self.pending_action = None

                return platform.play_favorite()

            return {
                "status": "ask",
                "response": "Please say Spotify or YouTube."
            }
        # -------------------------------------------------
        # 🔥 MOOD HANDLER (NEW FEATURE)
        # -------------------------------------------------
        if action == "handle_mood":

            mood = query.get("mood")

            if mood == "sad":

                sad_playlists = [
                    "lofi calm music",
                    "healing instrumental music",
                    "sad chill songs",
                    "peaceful piano music",
                    "relaxing ambient music"
                ]

                return self.handle({
                    "action": "play_music",
                    "target": "youtube",
                    "query": random.choice(sad_playlists)
                })
            elif mood == "happy":
                return self.handle({
                    "action": "play_music",
                    "target": "youtube",
                    "query": "happy upbeat songs"
                })

            elif mood == "stressed":
                return self.handle({
                    "action": "play_music",
                    "target": "youtube",
                    "query": "relaxing meditation music"
                })

            elif mood == "bored":
                return self.handle({
                    "action": "search",
                    "target": "youtube",
                    "query": "fun interesting videos"
                })
        # 🔥 NEW SWITCH HANDLER
        if action == "switch_to_app":
            target_name = structured.get("query")
            return self.switch_to_tab_by_name(target_name)

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
        # -------------------------------------------------
        # 🔥 FIX: ADD TO FAVORITES (CRITICAL FIX)
        # -------------------------------------------------
        if action == "add_to_favorites":



            target = self.last_active_platform
            platform = self.platform_instances.get(target)

            if not platform:
                return {
                    "status": "error",
                    "response": "No active platform."
                }

            # 🔥 USE CURRENT SONG INSTEAD OF QUERY
            if hasattr(platform, "current_song") and platform.current_song:
                return platform.memory.add_favorite(platform.current_song)

            return {
                "status": "error",
                "response": "No song is currently playing."
            }

        # -------------------------------------------------
        # 🔥 FIX: REMOVE FROM FAVORITES (CRITICAL FIX)
        # -------------------------------------------------
        if action == "remove_favorite":

            target = self.last_active_platform
            platform = self.platform_instances.get(target)

            if not platform:
                return {
                    "status": "error",
                    "response": "No active platform."
                }

            # 🔥 USE CURRENT SONG INSTEAD OF QUERY
            if hasattr(platform, "current_song") and platform.current_song:
                return platform.memory.remove_favorite(platform.current_song)

            return {
                "status": "error",
                "response": "No song is currently playing."
            }

        # -------------------------------------------------
        # 🔥 PLAY FAVORITES HANDLER (NEW)
        # -------------------------------------------------
        if action == "play_favorite":

            target = structured.get("target")  # ✅ FIRST DEFINE

            # 🔥 ASK USER FIRST
            if not target and not self.last_active_platform:
                self.pending_action = "play_favorite"
                return {
                    "status": "ask",
                    "response": "Do you want Spotify or YouTube?"
                }

            # 🔥 FALLBACK
            if not target:
                target = self.last_active_platform

            # 🔥 NOW VALIDATE (AFTER target EXISTS)
            if target not in ["spotify", "youtube"]:
                self.pending_action = "play_favorite"
                return {
                    "status": "ask",
                    "response": "Do you want Spotify or YouTube?"
                }

            # ✅ START DRIVER HERE
            self._ensure_driver()

            if target not in self.tabs:
                self._open_new_tab(target)
            else:
                self._switch_to_tab(target)

            self.last_active_platform = target
            platform = self.platform_instances[target]

            return platform.play_favorite()

        # ✅ READ EMAIL HANDLER
        if action == "read_latest_email":

            # 🔥 ENSURE DRIVER FIRST
            self._ensure_driver()

            gmail = Gmail(self.driver)

            if not gmail:
                return {
                    "status": "error",
                    "response": "Gmail not initialized."
                }

            count = 1
            if isinstance(query, dict):
                count = query.get("count", 1)

            return gmail.read_latest_emails(count)
        if not action:
            return {
                "status": "error",
                "response": "No action provided."
            }
        # 🔥 FORCE TARGET FROM USER COMMAND (VERY IMPORTANT)
        original_command = structured.get("original_command", "").lower()

        # 🔥 ONLY FORCE TARGET FOR EXPLICIT COMMANDS
        if action in ["play", "open", "search"]:
            if "youtube" in original_command or "yt" in original_command:
                structured["target"] = "youtube"

            elif "spotify" in original_command:
                structured["target"] = "spotify"

        print("DEBUG last_active_platform:", self.last_active_platform)
        target = self._detect_target(structured)
        structured["target"] = target
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


        # CLOSE TAB
        if action == "close":
            if target in self.tabs:
                try:
                    self._switch_to_tab(target)

                    # ❌ Don't close last tab
                    if len(self.driver.window_handles) == 1:
                        return {
                            "status": "info",
                            "response": "Cannot close the last tab. Use 'close browser' instead."
                        }

                    self.driver.close()
                    self.tabs.pop(target, None)

                    # 🔥🔥 CRITICAL FIX: SWITCH TO SAFE TAB
                    if self.driver.window_handles:
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        bring_browser_to_front()

                    return {
                        "status": "success",
                        "response": f"Closed {target.capitalize()}"
                    }

                except Exception as e:
                    return {
                        "status": "error",
                        "response": f"Could not close tab: {str(e)}"
                    }
        # OPEN (🔥 FINAL FIX)
        # OPEN (🔥 PROFESSIONAL TAB MANAGEMENT)
        if action == "open":

            # 🔥 IF TAB ALREADY EXISTS → SWITCH
            if target in self.tabs:
                switched = self._switch_to_tab(target)

                if switched:
                    return {
                        "status": "success",
                        "response": f"Switched to {target.capitalize()}"
                    }

            # 🔥 ELSE → OPEN NEW TAB
            return self._open_new_tab(target)

        # AUTO OPEN
        just_opened = False
        if action != "open" and target not in self.tabs:
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
            try:
                result = self._execute_platform_method(platform, action, query)
            except Exception:
                print("⚠ Retrying after driver reset...")
                self._ensure_driver()
                result = self._execute_platform_method(platform, action, query)

        # 🔥 HANDLE SUCCESS + INFO (DO NOT FALLBACK)
        # 🔥 HANDLE SUCCESS + INFO (FIX LAST ACTIVE PLATFORM LOGIC)
        if result.get("status") == "success":

            # 🔥 ALWAYS track platform for media actions
            if action in ["play", "pause", "resume", "stop"]:
                self.last_active_platform = target

            # 🔥 ALSO track if response contains "Playing"
            if "Playing" in result.get("response", ""):
                self.last_active_platform = target
            return result
        # 🔥 HANDLE LOGIN REQUIRED
        if result.get("status") == "login_required":
            return {
                "status": "info",
                "response": "Please login to Spotify first. I’ll continue after that."
            }
        # 🔥 ONLY fallback on real error
        return result