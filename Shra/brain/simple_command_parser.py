class SimpleCommandParser:

    def parse(self, command: str):

        command = command.lower().strip()

        valid_platforms = ["youtube", "spotify", "google", "gmail", "whatsapp"]

        # =================================================
        # CONTEXTUAL FAVORITE COMMANDS (VERY IMPORTANT)
        # =================================================

        # Add current playing song to favorites
        if "add this" in command and "favorite" in command:
            return {
                "status": "success",
                "action": "add_to_favorites",
                "target": "youtube"
            }

        # Play random favorite
        if "play my favorite" in command:
            return {
                "status": "success",
                "action": "play_favorite",
                "target": "youtube"
            }

        # Play last played
        if "play last song" in command:
            return {
                "status": "success",
                "action": "play_last",
                "target": "youtube"
            }

        # Play yesterday played
        if "play yesterday" in command:
            return {
                "status": "success",
                "action": "play_yesterday",
                "target": "youtube"
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

            # play xyz on youtube
            if " on " in remaining:
                query, target = remaining.split(" on ", 1)
                return {
                    "status": "success",
                    "action": "play_music",
                    "target": target.strip(),
                    "query": query.strip()
                }

            # play youtube (open youtube)
            if remaining in valid_platforms:
                return {
                    "status": "success",
                    "action": "open",
                    "target": remaining
                }

            # default → play on youtube
            return {
                "status": "success",
                "action": "play_music",
                "target": "youtube",
                "query": remaining
            }

        # =================================================
        # CLOSE
        # =================================================
        if command.startswith("close"):

            parts = command.split()

            # close youtube
            if len(parts) > 1 and parts[1] in valid_platforms:
                return {
                    "status": "success",
                    "action": "close",
                    "target": parts[1]
                }

            return {
                "status": "success",
                "action": "close",
                "target": "current"
            }

        return None