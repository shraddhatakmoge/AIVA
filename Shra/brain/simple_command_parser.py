from difflib import get_close_matches
import re


class SimpleCommandParser:

    def __init__(self):
        self.valid_platforms = ["youtube", "spotify", "google", "gmail", "whatsapp"]

        self.platform_aliases = {
            "google": ["google", "googl", "gogle", "googel"],
            "youtube": ["youtube", "youtu", "youtub", "youtbe", "you tube", "yt"],
            "spotify": ["spotify", "spotfy", "spotifi", "spoti"],
            "gmail": ["gmail", "g mail", "gmaill"],
            "whatsapp": ["whatsapp", "whats app", "watsapp", "whatsup"]
        }

    def _normalize_platform(self, target: str):
        if not target:
            return None

        target = target.lower().strip()

        if target in self.valid_platforms:
            return target

        for platform, aliases in self.platform_aliases.items():
            if target in aliases:
                return platform

        match = get_close_matches(target, self.valid_platforms, n=1, cutoff=0.7)
        if match:
            return match[0]

        return target

    def _parse_send_file_command(self, original_command: str, lower_command: str):
        file_match = re.match(
            r"^send\s+(?:(file|image|document)\s+)?(.+?)(?:\s+(file|image|document))?\s+to\s+(.+)$",
            original_command,
            re.IGNORECASE
        )

        if not file_match:
            return None

        prefix_type = file_match.group(1)
        file_part = file_match.group(2).strip()
        suffix_type = file_match.group(3)
        contact_part = file_match.group(4).strip()

        if not (prefix_type or suffix_type):
            return None

        target = "whatsapp"

        recipient_lower = contact_part.lower()
        if " on " in recipient_lower:
            on_index = recipient_lower.rfind(" on ")
            explicit_target = contact_part[on_index + 4:].strip()
            contact_part = contact_part[:on_index].strip()

            normalized_target = self._normalize_platform(explicit_target)
            if normalized_target in self.valid_platforms:
                target = normalized_target

        query = {
            "contact_name": contact_part
        }

        if "\\" in file_part or "/" in file_part or ":" in file_part:
            query["file_path"] = file_part
            query["file_name"] = file_part.split("\\")[-1].split("/")[-1]
        else:
            query["file_name"] = file_part

        if prefix_type:
            query["file_type"] = prefix_type.lower()
        elif suffix_type:
            query["file_type"] = suffix_type.lower()

        return {
            "status": "success",
            "action": "send_file",
            "target": target,
            "query": query
        }

    def _autocorrect_command(self, command: str):
        words = command.lower().split()

        corrected_words = []

        for word in words:
            normalized = self._normalize_platform(word)

            # 🔥 Only replace if word itself is NOT meaningful command word
            if normalized in self.valid_platforms and word not in ["mail"]:
                corrected_words.append(normalized)
            else:
                corrected_words.append(word)

        return " ".join(corrected_words)


    def parse(self, command: str):
        original_command = command.strip()

        # 🔥 AUTO-CORRECT FIRST
        corrected_command = self._autocorrect_command(original_command)

        # 🔥 DEBUG PRINT (optional)
        if corrected_command != original_command.lower():
            print(f"🤖 Auto-corrected: {corrected_command}")

        lower_command = corrected_command.lower().strip()
        # 🔥 SKIP YOUTUBE AD
        if "skip ad" in lower_command or "skip ads" in lower_command:
            return {
                "status": "success",
                "action": "skip_ad",
                "target": "youtube"
            }

        # 🔥 ADD THIS (DO NOT REMOVE ANYTHING ELSE)
        if "go back to website" in lower_command or "switch back" in lower_command or lower_command == "go back":
            return {
                "status": "success",
                "action": "switch_back",
                "target": "browser"  # 🔥 IMPORTANT FIX
            }

        if "go back to google" in lower_command or "switch to google" in lower_command:
            return {
                "status": "success",
                "action": "switch_to_google",
                "target": "google"
            }

        # 🔥 FORCE CONTROL COMMANDS FIRST
        volume_keywords = ["volume", "volum", "volumne", "sound", "audio"]

        if any(cmd in lower_command for cmd in ["mute", "unmute"]) or any(v in lower_command for v in volume_keywords):

            # 🔥 detect platform (optional)
            if any(x in lower_command for x in ["yt", "youtube"]):
                target = "youtube"
            elif "spotify" in lower_command:
                target = "spotify"
            else:
                target = None  # 🔥 fallback to last_active_platform

            if "unmute" in lower_command:
                return {"status": "success", "action": "unmute", "target": target}

            elif "mute" in lower_command:
                return {"status": "success", "action": "mute", "target": target}

            elif any(x in lower_command for x in ["increase", "up", "raise", "louder"]):
                return {"status": "success", "action": "volume_up", "target": target}

            elif any(x in lower_command for x in ["decrease", "down", "lower", "reduce"]):
                return {"status": "success", "action": "volume_down", "target": target}




        # 🔥 NEW: switch to app / website
        if "switch to" in lower_command:
            name = lower_command.replace("switch to", "").strip()

            return {
                "status": "success",
                "action": "switch_to_app",
                "query": name
            }

        if " and " in lower_command:
            parts = [p.strip() for p in re.split(r"\b(?:and|then|after that)\b", original_command, flags=re.IGNORECASE) if p.strip()]
            print("DEBUG MULTI PARTS:", parts)
            actions = []

            last_target = None

            for part in parts:
                parsed = self.parse(part)

                if parsed and parsed.get("status") == "success":

                    # 🔥 ADD THIS LINE (CRITICAL FIX)
                    parsed["original_command"] = part.lower()

                    # 🔥 carry forward target
                    if last_target and not parsed.get("target"):
                        parsed["target"] = last_target

                    if parsed.get("target"):
                        last_target = parsed["target"]

                    actions.append(parsed)

            if actions:
                return {
                    "status": "success",
                    "actions": actions
                }

        if lower_command in ["close browser", "exit browser", "shutdown browser"]:
            return {
                "status": "success",
                "action": "close_browser"
            }

        if "add this" in lower_command and "favorite" in lower_command:
            return {
                "status": "success",
                "action": "add_to_favorites"
            }
        if "remove this" in lower_command and "favorite" in lower_command:
            return {
                "status": "success",
                "action": "remove_favorite"
            }

        if "play my favorite" in lower_command:

            # 🔥 CHECK FOR PLATFORM (IMPORTANT FIX)
            if " on " in lower_command:
                _, target = lower_command.split(" on ", 1)
                target = self._normalize_platform(target.strip())

                return {
                    "status": "success",
                    "action": "play_favorite",
                    "target": target
                }

            return {
                "status": "success",
                "action": "play_favorite"
            }


        if "play last song" in lower_command:

            if " on " in lower_command:
                _, target = lower_command.split(" on ", 1)
                target = self._normalize_platform(target.strip())

                return {
                    "status": "success",
                    "action": "play_last",
                    "target": target
                }

            return {
                "status": "success",
                "action": "play_last"
            }

        if "play yesterday" in lower_command:
            return {
                "status": "success",
                "action": "play_yesterday"
            }
        if "open first result" in lower_command:
            return {
                "status": "success",
                "action": "open_result",
                "target": "google",
                "query": {"index": 1}
            }

        if "open second result" in lower_command:
            return {
                "status": "success",
                "action": "open_result",
                "target": "google",
                "query": {"index": 2}
            }


        # -------------------------------------------------
        # 🔥 MOOD DETECTION (NEW FEATURE)
        # -------------------------------------------------
        mood_keywords = {
            "sad": ["sad", "lonely", "low", "depressed", "bad day"],
            "happy": ["happy", "excited", "good mood"],
            "stressed": ["stressed", "tired", "overwhelmed", "anxious"],
            "bored": ["bored", "nothing to do"]
        }

        for mood, words in mood_keywords.items():
            if any(word in lower_command for word in words):
                return {
                    "status": "success",
                    "action": "handle_mood",
                    "query": {"mood": mood}
                }

        if lower_command.startswith("open "):

            remaining = lower_command.replace("open ", "", 1).strip()

            # direct result commands
            if remaining == "first result":
                return {
                    "status": "success",
                    "action": "open_result",
                    "target": "google",
                    "query": {"index": 1}
                }

            if remaining == "second result":
                return {
                    "status": "success",
                    "action": "open_result",
                    "target": "google",
                    "query": {"index": 2}
                }

            if remaining == "third result":
                return {
                    "status": "success",
                    "action": "open_result",
                    "target": "google",
                    "query": {"index": 3}
                }

            # ✅ IMPORTANT FIX: handle "open ibm one", "open amazon first", etc.
            match = re.match(r"(.+?)\s+(first|one|1|second|two|2|third|three|3)\s*$", remaining)
            print("DEBUG OPEN MATCH:", remaining)

            if match:
                name = match.group(1).strip()
                rank_word = match.group(2).strip()

                index_map = {
                    "first": 1, "one": 1, "1": 1,
                    "second": 2, "two": 2, "2": 2,
                    "third": 3, "three": 3, "3": 3,
                }

                print("🔥 FORCE RETURN OPEN:", name, index_map[rank_word])

                return {
                    "status": "success",
                    "action": "open_result_by_name",
                    "target": "google",
                    "query": {
                        "name": name,
                        "index": index_map[rank_word]
                    }
                }
            # 🔥 HARD STOP (prevents falling into search)
            return {
                "status": "success",
                "action": "open_result_by_name",
                "target": "google",
                "query": {
                    "name": remaining,
                    "index": 1
                }
            }
            # platform open
            normalized = self._normalize_platform(remaining)
            if normalized in self.valid_platforms:
                return {
                    "status": "success",
                    "action": "open",
                    "target": normalized
                }

            # fallback open result by name
            words = remaining.split()

            index_map = {
                "first": 1, "1": 1, "one": 1,
                "second": 2, "2": 2, "two": 2,
                "third": 3, "3": 3, "three": 3,
            }

            index = None
            name_parts = []

            for w in words:
                if w in index_map:
                    index = index_map[w]
                else:
                    name_parts.append(w)

            name = " ".join(name_parts).strip()

            if name:
                print("DEBUG OPEN NAME:", name, "INDEX:", index)

                return {
                    "status": "success",
                    "action": "open_result_by_name",
                    "target": "google",
                    "query": {
                        "name": name.strip(),
                        "index": index if index else 1
                    }
                }

            return {
                "status": "error",
                "response": "Unknown open command"
            }


        if lower_command in [
            "read me my messages",
            "read my messages",
            "read messages",
            "read whatsapp messages",
        ]:
            return {
                "status": "success",
                "action": "read_messages",
                "target": "whatsapp",
                "query": {
                    "count": 5,
                    "unread_only": True
                }
            }
        # OPEN SEARCH RESULT

        # SCROLL
        if "scroll down" in lower_command:
            return {
                "status": "success",
                "action": "scroll",
                "query": {"direction": "down"}
            }



        if "scroll up" in lower_command:
            return {
                "status": "success",
                "action": "scroll",
                "query": {"direction": "up"}
            }

        if lower_command in [
            "read latest messages",
        ]:
            return {
                "status": "success",
                "action": "read_messages",
                "target": "whatsapp",
                "query": {
                    "count": 5,
                    "unread_only": False
                }
            }

        if lower_command in [
            "read unread messages",
            "read my unread messages",
            "read unread whatsapp messages",
        ]:
            return {
                "status": "success",
                "action": "read_messages",
                "target": "whatsapp",
                "query": {
                    "count": 5,
                    "unread_only": True
                }
            }

        if lower_command.startswith("read messages from "):
            contact_name = original_command[len("read messages from "):].strip()
            return {
                "status": "success",
                "action": "read_messages",
                "target": "whatsapp",
                "query": {
                    "contact_name": contact_name,
                    "count": 5
                }
            }

        match = re.match(r"read last (\d+) messages from (.+)", lower_command)
        if match:
            count = int(match.group(1))
            contact_name = original_command[len(f"read last {match.group(1)} messages from "):].strip()
            return {
                "status": "success",
                "action": "read_messages",
                "target": "whatsapp",
                "query": {
                    "contact_name": contact_name,
                    "count": count
                }
            }

        # =====================================================
        # 🔥 IMPROVED EMAIL PARSING (DO NOT TOUCH REST)
        # =====================================================
        if "send email" in lower_command or "send mail" in lower_command:

            to = None
            subject = None
            body = None

            # Extract email OR name
            email_match = re.search(r"[\w\.-]+@[\w\.-]+", lower_command)

            if email_match:
                to = email_match.group(0)
            else:
                # 🔥 fallback: extract after "to"
                if " to " in lower_command:
                    to_part = lower_command.split(" to ", 1)[1]

                    # stop at subject/message if present
                    for stop_word in ["subject", "message"]:
                        if stop_word in to_part:
                            to_part = to_part.split(stop_word)[0]

                    to = to_part.strip().split()[0]
            # Extract subject
            if "subject" in lower_command:
                subject_part = lower_command.split("subject", 1)[1]
                if "message" in subject_part:
                    subject = subject_part.split("message")[0].strip()
                else:
                    subject = subject_part.strip()

            # Extract body/message
            if "message" in lower_command:
                body = lower_command.split("message", 1)[1].strip()

            # Fallbacks
            if not subject:
                subject = None

            if not body:
                # Try extracting loose text as body
                if to:
                    parts = lower_command.split(to)
                    if len(parts) > 1:
                        possible_body = parts[1].replace("subject", "").strip()
                        if possible_body:
                            body = possible_body

                if not body:
                    body = None

            if to:
                return {
                    "status": "success",
                    "action": "send_email",
                    "target": "gmail",
                    "query": {
                        "to": to,
                        "subject": subject,
                        "body": body
                    }
                }
        # =====================================================

        # 🔥 dynamic email count
        match = re.match(r"read (?:my )?(\d+) emails?", lower_command)
        if match:
            count = int(match.group(1))
            return {
                "status": "success",
                "action": "read_latest_email",
                "target": "gmail",
                "query": {"count": count}
            }

        if lower_command in ["read my email", "read latest email", "read gmail"]:
            return {
                "status": "success",
                "action": "read_latest_email",
                "target": "gmail",
                "query": {"count": 1}
            }

        parsed_file = self._parse_send_file_command(original_command, lower_command)
        if parsed_file:
            return parsed_file

        for prefix in ["send message ", "send "]:
            if lower_command.startswith(prefix):
                remaining_original = original_command[len(prefix):].strip()
                remaining_lower = lower_command[len(prefix):].strip()

                if " to " in remaining_lower:
                    split_index = remaining_lower.rfind(" to ")

                    message_part = remaining_original[:split_index].strip()
                    recipient_part = remaining_original[split_index + 4:].strip()

                    target = "whatsapp"

                    recipient_lower = recipient_part.lower()
                    if " on " in recipient_lower:
                        on_index = recipient_lower.rfind(" on ")
                        explicit_target = recipient_part[on_index + 4:].strip()
                        recipient_part = recipient_part[:on_index].strip()

                        normalized_target = self._normalize_platform(explicit_target)
                        if normalized_target in self.valid_platforms:
                            target = normalized_target

                    clean_number = "".join(ch for ch in recipient_part if ch.isdigit())

                    query = {
                        "message": message_part
                    }

                    if clean_number and clean_number == recipient_part.replace(" ", ""):
                        query["phone_number"] = clean_number
                    else:
                        query["contact_name"] = recipient_part.strip()

                    return {
                        "status": "success",
                        "action": "send_message",
                        "target": target,
                        "query": query
                    }

        for prefix in ["search ", "seach ", "serch ", "sarch "]:
            if lower_command.startswith(prefix):
                remaining = lower_command[len(prefix):].strip()

                if " on " in remaining:
                    query, target = remaining.split(" on ", 1)
                    target = self._normalize_platform(target.strip())

                    return {
                        "status": "success",
                        "action": "search",
                        "target": target,
                        "query": query.strip()
                    }

                return {
                    "status": "success",
                    "action": "search",
                    "target": "google",
                    "query": remaining
                }

        if lower_command.startswith("play "):
            remaining = lower_command.replace("play ", "", 1).strip()

            if " on " in remaining:
                query, target = remaining.split(" on ", 1)
                target = self._normalize_platform(target.strip())

                return {
                    "status": "success",
                    "action": "play_music",
                    "target": target,
                    "query": query.strip()
                }

            normalized_remaining = self._normalize_platform(remaining)

            if normalized_remaining in self.valid_platforms:
                return {
                    "status": "success",
                    "action": "open",
                    "target": normalized_remaining
                }

            return {
                "status": "success",
                "action": "play_music",
                "query": remaining
            }

        # PAUSE / RESUME / STOP WITH TARGET
        # ------------------------------
        for action_word in ["pause", "resume", "stop"]:
            if lower_command.startswith(action_word):

                remaining = lower_command.replace(action_word, "", 1).strip()

                # CASE 1: "on youtube"
                if " on " in remaining:
                    _, target = remaining.split(" on ", 1)
                    target = self._normalize_platform(target.strip())

                    return {
                        "status": "success",
                        "action": action_word,
                        "target": target
                    }

                # CASE 2: "resume spotify"
                if remaining:
                    possible_target = self._normalize_platform(remaining)

                    if possible_target in self.valid_platforms:
                        return {
                            "status": "success",
                            "action": action_word,
                            "target": possible_target
                        }

                # CASE 3: no target → fallback
                return {
                    "status": "success",
                    "action": action_word
                }

        if lower_command.startswith("close "):
            target = lower_command.replace("close ", "", 1).strip()
            target = self._normalize_platform(target)

            if target in self.valid_platforms:
                return {
                    "status": "success",
                    "action": "close",
                    "target": target
                }

        return {
            "status": "error",
            "response": "Unknown command"
        }

