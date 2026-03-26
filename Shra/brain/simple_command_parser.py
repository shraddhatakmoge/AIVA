from difflib import get_close_matches
import re


class SimpleCommandParser:

    def __init__(self):
        self.valid_platforms = ["youtube", "spotify", "google", "gmail", "whatsapp"]

        self.platform_aliases = {
            "google": ["google", "googl", "gogle", "googel"],
            "youtube": ["youtube", "youtu", "youtub", "youtbe", "you tube", "yt"],
            "spotify": ["spotify", "spotfy", "spotifi", "spoti"],
            "gmail": ["gmail", "g mail", "gmaill", "mail"],
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

    def parse(self, command: str):
        original_command = command.strip()
        lower_command = command.lower().strip()

        # =================================================
        # MULTI INTENT COMMANDS
        # =================================================
        if " and " in lower_command:
            parts = [p.strip() for p in original_command.split(" and ")]
            actions = []

            for part in parts:
                parsed = self.parse(part)
                if parsed and parsed.get("status") == "success":
                    actions.append(parsed)

            if actions:
                return {
                    "status": "success",
                    "actions": actions
                }

        # =================================================
        # CLOSE ENTIRE BROWSER
        # =================================================
        if lower_command in ["close browser", "exit browser", "shutdown browser"]:
            return {
                "status": "success",
                "action": "close_browser"
            }

        # =================================================
        # CONTEXTUAL FAVORITE COMMANDS
        # =================================================
        if "add this" in lower_command and "favorite" in lower_command:
            return {
                "status": "success",
                "action": "add_to_favorites"
            }

        if "play my favorite" in lower_command:
            return {
                "status": "success",
                "action": "play_favorite"
            }

        if "play last song" in lower_command:
            return {
                "status": "success",
                "action": "play_last"
            }

        if "play yesterday" in lower_command:
            return {
                "status": "success",
                "action": "play_yesterday"
            }

        # =================================================
        # OPEN
        # =================================================
        if lower_command.startswith("open "):
            target = lower_command.replace("open ", "", 1).strip()
            target = self._normalize_platform(target)

            return {
                "status": "success",
                "action": "open",
                "target": target
            }

        # =================================================
        # READ MESSAGES
        # =================================================
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

        # =================================================
        # SEND MESSAGE
        # =================================================
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

        # =================================================
        # SEARCH
        # =================================================
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

        # =================================================
        # PLAY
        # =================================================
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

        # =================================================
        # CLOSE TAB
        # =================================================
        if lower_command.startswith("close "):
            target = lower_command.replace("close ", "", 1).strip()
            target = self._normalize_platform(target)

            if target in self.valid_platforms:
                return {
                    "status": "success",
                    "action": "close",
                    "target": target
                }

        return None