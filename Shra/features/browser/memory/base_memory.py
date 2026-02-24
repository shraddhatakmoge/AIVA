import json
import os


class BaseMemory:

    def __init__(self, file_name):

        memory_dir = os.path.dirname(__file__)
        self.file_path = os.path.join(memory_dir, file_name)

        # Ensure file exists before loading
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

        self.data = self._load()

    # -------------------------------------------------
    # LOAD MEMORY
    # -------------------------------------------------
    def _load(self):

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                if not isinstance(data, dict):
                    return {}

                return data

        except Exception:
            return {}

    # -------------------------------------------------
    # SAVE MEMORY
    # -------------------------------------------------
    def _save(self):

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)