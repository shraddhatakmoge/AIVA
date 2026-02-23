import random
from datetime import datetime
from AIVA.Shra.features.browser.memory.base_memory import BaseMemory


class YouTubeMemory(BaseMemory):

    def __init__(self):
        super().__init__("youtube_memory.json")

        if "favorites" not in self.data:
            self.data["favorites"] = []

        if "history" not in self.data:
            self.data["history"] = []

        if "last_played" not in self.data:
            self.data["last_played"] = None

        # ✅ NEW FIELD (important)
        if "last_music" not in self.data:
            self.data["last_music"] = None

        self._save()

    # -------------------------------------------------
    # HISTORY
    # -------------------------------------------------
    def add_history(self, song, is_music=True):

        if not song:
            return

        entry = {
            "song": song,
            "played_at": datetime.now().isoformat()
        }

        self.data["history"].append(entry)
        self.data["last_played"] = song

        # ✅ Only update music tracker if actual music
        if is_music:
            self.data["last_music"] = song

        self._save()

    def get_last_played(self):
        return self.data.get("last_played")

    def get_last_music(self):
        return self.data.get("last_music")

    def get_yesterday_last(self):

        if len(self.data["history"]) < 2:
            return None

        return self.data["history"][-2]["song"]

    # -------------------------------------------------
    # FAVORITES
    # -------------------------------------------------
    def add_favorite(self, song):

        if not song:
            return False

        if song not in self.data["favorites"]:
            self.data["favorites"].append(song)
            self._save()
            return True

        return False

    def remove_favorite(self, song):

        if song in self.data["favorites"]:
            self.data["favorites"].remove(song)
            self._save()
            return True

        return False

    def get_random_favorite(self):

        if not self.data["favorites"]:
            return None

        return random.choice(self.data["favorites"])

    def get_all_favorites(self):
        return self.data["favorites"]