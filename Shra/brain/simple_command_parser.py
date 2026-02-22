class SimpleCommandParser:

    def parse(self, command: str):

        command = command.lower().strip()

        valid_platforms = ["youtube", "spotify", "google", "gmail", "whatsapp"]

        # ---------------- OPEN ----------------
        if command.startswith("open "):
            target = command.replace("open ", "").strip()

            return {
                "status": "success",
                "action": "open",
                "target": target
            }

        # ---------------- SEARCH ----------------
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

        # ---------------- PLAY ----------------
        if command.startswith("play "):
            remaining = command.replace("play ", "").strip()

            if " on " in remaining:
                query, target = remaining.split(" on ", 1)
                return {
                    "status": "success",
                    "action": "search",
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
                "action": "search",
                "target": "youtube",
                "query": remaining
            }

        # ---------------- CLOSE ----------------
        if command.startswith("close"):

            parts = command.split()

            # close youtube
            if len(parts) > 1 and parts[1] in valid_platforms:
                return {
                    "status": "success",
                    "action": "close",
                    "target": parts[1]
                }

            # just close
            return {
                "status": "success",
                "action": "close",
                "target": "current"
            }

        return None