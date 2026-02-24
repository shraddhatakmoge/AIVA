import random
from datetime import datetime
from AIVA.Shra.features.browser.memory.base_memory import BaseMemory


class SpotifyMemory(BaseMemory):

    def __init__(self):
        super().__init__("spotify_memory.json")

        if not isinstance(self.data, dict):
            self.data = {}

        self.data.setdefault("favorites", [])
        self.data.setdefault("history", [])

        self._migrate_data()
        self._save()

    # -------------------------------------------------
    # Utilities
    # -------------------------------------------------

    def _normalize(self, text: str):
        if not text:
            return None
        return text.strip().lower()

    def _reload(self):
        self.data = self._load()

        if not isinstance(self.data, dict):
            self.data = {}

        self.data.setdefault("favorites", [])
        self.data.setdefault("history", [])

        self._migrate_data()

    def _migrate_data(self):
        """
        Ensures favorites and history are always stored in structured dict format.
        """

        # Migrate favorites
        migrated_favorites = []
        for item in self.data.get("favorites", []):
            if isinstance(item, str):
                migrated_favorites.append({
                    "song": self._normalize(item),
                    "spotify_id": None,
                    "added_at": None
                })
            elif isinstance(item, dict):
                migrated_favorites.append({
                    "song": self._normalize(item.get("song")),
                    "spotify_id": item.get("spotify_id"),
                    "added_at": item.get("added_at")
                })

        self.data["favorites"] = migrated_favorites

        # Migrate history
        migrated_history = []
        for item in self.data.get("history", []):
            if isinstance(item, str):
                migrated_history.append({
                    "song": self._normalize(item),
                    "spotify_id": None,
                    "played_at": None
                })
            elif isinstance(item, dict):
                migrated_history.append({
                    "song": self._normalize(item.get("song")),
                    "spotify_id": item.get("spotify_id"),
                    "played_at": item.get("played_at")
                })

        self.data["history"] = migrated_history

    # -------------------------------------------------
    # History
    # -------------------------------------------------

    def add_history(self, song: str, spotify_id: str = None):
        song = self._normalize(song)
        if not song:
            return

        self._reload()

        self.data["history"].append({
            "song": song,
            "spotify_id": spotify_id,
            "played_at": datetime.now().isoformat()
        })

        self._save()

    def get_last_played(self):
        self._reload()
        if not self.data["history"]:
            return None
        return self.data["history"][-1]

    # -------------------------------------------------
    # Favorites
    # -------------------------------------------------

    def add_favorite(self, song: str, spotify_id: str = None):
        """
        Adds favorite using canonical resolved song.
        Duplicate prevention uses spotify_id if available,
        otherwise falls back to normalized title.
        """

        song = self._normalize(song)

        if not song:
            return {
                "status": "error",
                "response": "Invalid song."
            }

        self._reload()

        # STRICT duplicate check
        for item in self.data["favorites"]:

            # If spotify_id available → use it
            if spotify_id and item.get("spotify_id"):
                if item["spotify_id"] == spotify_id:
                    return {
                        "status": "info",
                        "response": f"'{song}' is already in favorites."
                    }

            # Fallback to title match
            if item["song"] == song:
                return {
                    "status": "info",
                    "response": f"'{song}' is already in favorites."
                }

        # Add new favorite
        self.data["favorites"].append({
            "song": song,
            "spotify_id": spotify_id,
            "added_at": datetime.now().isoformat()
        })

        self._save()

        return {
            "status": "success",
            "response": f"Added '{song}' to favorites."
        }

    def remove_favorite(self, song: str):
        song = self._normalize(song)

        if not song:
            return {
                "status": "error",
                "response": "Invalid song."
            }

        self._reload()

        for item in self.data["favorites"]:
            if item["song"] == song:
                self.data["favorites"].remove(item)
                self._save()
                return {
                    "status": "success",
                    "response": f"Removed '{song}' from favorites."
                }

        return {
            "status": "info",
            "response": f"'{song}' is not in favorites."
        }

    def get_random_favorite(self):
        self._reload()
        if not self.data["favorites"]:
            return None
        return random.choice(self.data["favorites"])

    def get_all_favorites(self):
        self._reload()
        return self.data["favorites"]