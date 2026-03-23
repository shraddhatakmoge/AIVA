from difflib import get_close_matches


class SimpleCommandParser:

    def __init__(self):
        self.valid_platforms = ["youtube", "spotify", "google", "gmail", "whatsapp"]

        self.platform_aliases = {
            "google": ["google", "googl", "gogle", "googel", "googel"],
            "youtube": ["youtube", "youtu", "youtub", "youtbe", "you tube", "yt"],
            "spotify": ["spotify", "spotfy", "spotifi", "spoti"],
            "gmail": ["gmail", "g mail", "gmaill", "mail"],
            "whatsapp": ["whatsapp", "whats app", "watsapp", "whatsup"]
        }

    def _normalize_platform(self, target: str):
        if not target:
            return None

        target = target.lower().strip()

        # exact match first
        if target in self.valid_platforms:
            return target

        # alias match
        for platform, aliases in self.platform_aliases.items():
            if target in aliases:
                return platform

        # fuzzy match fallback
        match = get_close_matches(target, self.valid_platforms, n=1, cutoff=0.7)
        if match:
            return match[0]

        return target

    def parse(self, command: str):

        command = command.lower().strip()

        # =================================================
        # MULTI INTENT COMMANDS
        # =================================================
        if " and " in command:
            parts = [p.strip() for p in command.split(" and ")]
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
        if command in ["close browser", "exit browser", "shutdown browser"]:
            return {
                "status": "success",
                "action": "close_browser"
            }

        # =================================================
        # CONTEXTUAL FAVORITE COMMANDS
        # =================================================
        if "add this" in command and "favorite" in command:
            return {
                "status": "success",
                "action": "add_to_favorites"
            }

        if "play my favorite" in command:
            return {
                "status": "success",
                "action": "play_favorite"
            }

        if "play last song" in command:
            return {
                "status": "success",
                "action": "play_last"
            }

        if "play yesterday" in command:
            return {
                "status": "success",
                "action": "play_yesterday"
            }

        # =================================================
        # OPEN
        # =================================================
        if command.startswith("open "):
            target = command.replace("open ", "").strip()
            target = self._normalize_platform(target)

            return {
                "status": "success",
                "action": "open",
                "target": target
            }

        # =================================================
        # SEARCH
        # =================================================
        for prefix in ["search ", "seach ", "serch ", "sarch "]:
            if command.startswith(prefix):
                remaining = command[len(prefix):].strip()

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
        if command.startswith("play "):
            remaining = command.replace("play ", "").strip()

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
        if command.startswith("close "):
            target = command.replace("close ", "").strip()
            target = self._normalize_platform(target)

            if target in self.valid_platforms:
                return {
                    "status": "success",
                    "action": "close",
                    "target": target
                }

        return None