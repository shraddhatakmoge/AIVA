import random
from AIVA.Shra.features.browser.memory.base_memory import BaseMemory


class SpotifyMemory(BaseMemory):

    def __init__(self):
        super().__init__("spotify_memory.json")

        if "favorites" not in self.data:
            self.data["favorites"] = []

        if "history" not in self.data:
            self.data["history"] = []

        self._save()

    def add_history(self, song):

        if song:
            self.data["history"].append(song)
            self._save()

    def get_last_played(self):

        if not self.data["history"]:
            return None

        return self.data["history"][-1]

    def add_favorite(self, song):

        if song and song not in self.data["favorites"]:
            self.data["favorites"].append(song)
            self._save()

    def remove_favorite(self, song):

        if song in self.data["favorites"]:
            self.data["favorites"].remove(song)
            self._save()

    def get_random_favorite(self):

        if not self.data["favorites"]:
            return None

        return random.choice(self.data["favorites"])

    def get_all_favorites(self):
        return self.data["favorites"]