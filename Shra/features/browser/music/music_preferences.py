import os
import json


class MusicPreferences:

    def __init__(self):

        self.file_path = os.path.join(
            os.path.dirname(__file__),
            "music_preferences.json"
        )

        self.data = {
            "default_favorites_platform": None
        }

        self._load()

    # -------------------------------------------------
    def _load(self):

        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    self.data = json.load(f)
            except:
                pass
        else:
            self._save()

    # -------------------------------------------------
    def _save(self):

        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    # -------------------------------------------------
    def set_default_platform(self, platform):
        self.data["default_favorites_platform"] = platform
        self._save()

    def get_default_platform(self):
        return self.data.get("default_favorites_platform")