class SimpleCommandParser:

    def parse(self, command: str):

        command = command.lower().strip()

        valid_platforms = ["youtube", "spotify", "google", "gmail", "whatsapp"]

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

            return {
                "status": "success",
                "action": "open",
                "target": target
            }

        # =================================================
        # SEARCH
        # =================================================
        if command.startswith("search "):
            remaining = command.replace("search ", "").strip()

            if " on " in remaining:
                query, target = remaining.split(" on ", 1)
                return {
                    "status": "success",
                    "action": "search",
                    "target": target.strip(),
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
                return {
                    "status": "success",
                    "action": "play_music",
                    "target": target.strip(),
                    "query": query.strip()
                }

            if remaining in valid_platforms:
                return {
                    "status": "success",
                    "action": "open",
                    "target": remaining
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
            parts = command.split()

            if len(parts) > 1 and parts[1] in valid_platforms:
                return {
                    "status": "success",
                    "action": "close",
                    "target": parts[1]
                }

        return None