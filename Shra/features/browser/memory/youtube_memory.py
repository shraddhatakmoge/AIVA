import random
from datetime import datetime
from AIVA.Shra.features.browser.memory.base_memory import BaseMemory


class YouTubeMemory(BaseMemory):

    def __init__(self):
        super().__init__("youtube_memory.json")

        if not isinstance(self.data, dict):
            self.data = {}

        self.data.setdefault("favorites", [])
        self.data.setdefault("history", [])
        self.data.setdefault("last_played", None)
        self.data.setdefault("last_music", None)

        self._save()

    # -------------------------------------------------
    # UTIL
    # -------------------------------------------------
    def _normalize(self, text):
        return text.strip().lower() if text else None

    def _reload(self):
        self.data = self._load()
        self.data.setdefault("favorites", [])
        self.data.setdefault("history", [])
        self.data.setdefault("last_played", None)
        self.data.setdefault("last_music", None)

    # -------------------------------------------------
    # HISTORY
    # -------------------------------------------------
    def add_history(self, song, is_music=True):

        song = self._normalize(song)
        if not song:
            return

        self._reload()

        entry = {
            "song": song,
            "played_at": datetime.now().isoformat()
        }

        self.data["history"].append(entry)
        self.data["last_played"] = song

        if is_music:
            self.data["last_music"] = song

        self._save()

    def get_last_played(self):
        self._reload()
        return self.data.get("last_played")

    def get_last_music(self):
        self._reload()
        return self.data.get("last_music")

    def get_yesterday_last(self):
        self._reload()

        if len(self.data["history"]) < 2:
            return None

        return self.data["history"][-2]["song"]

    # -------------------------------------------------
    # FAVORITES
    # -------------------------------------------------
    def add_favorite(self, song):

        song = self._normalize(song)

        if not song:
            return {
                "status": "error",
                "response": "Invalid song."
            }

        self._reload()

        if song in self.data["favorites"]:
            return {
                "status": "info",
                "response": f"'{song}' already in favorites."
            }

        self.data["favorites"].append(song)
        self._save()

        return {
            "status": "success",
            "response": f"Added '{song}' to favorites."
        }

    def remove_favorite(self, song):

        song = self._normalize(song)

        if not song:
            return {
                "status": "error",
                "response": "Invalid song."
            }

        self._reload()

        if song not in self.data["favorites"]:
            return {
                "status": "info",
                "response": f"'{song}' not found in favorites."
            }

        self.data["favorites"].remove(song)
        self._save()

        return {
            "status": "success",
            "response": f"Removed '{song}' from favorites."
        }

    def get_random_favorite(self):
        self._reload()

        if not self.data["favorites"]:
            return None

        return random.choice(self.data["favorites"])

    def get_all_favorites(self):
        self._reload()
        return self.data["favorites"]