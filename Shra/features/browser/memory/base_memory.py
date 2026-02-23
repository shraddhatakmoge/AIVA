import json
import os


class BaseMemory:

    def __init__(self, file_name):

        memory_dir = os.path.dirname(__file__)
        self.file_path = os.path.join(memory_dir, file_name)

        self.data = {}

        self._load()

    # -------------------------------------------------
    # LOAD MEMORY
    # -------------------------------------------------
    def _load(self):

        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        else:
            self._save()

    # -------------------------------------------------
    # SAVE MEMORY
    # -------------------------------------------------
    def _save(self):

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)