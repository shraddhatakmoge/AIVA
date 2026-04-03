# volume_control.py

import re
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class VolumeController:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices._dev.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )
        self.volume = interface.QueryInterface(IAudioEndpointVolume)

    # ----------------------------
    # BASIC GET/SET
    # ----------------------------

    def get_volume(self):
        return round(self.volume.GetMasterVolumeLevelScalar() * 100)

    def set_volume(self, level):
        level = max(0, min(100, level))
        self.volume.SetMasterVolumeLevelScalar(level / 100, None)
        return f"Volume set to {level}%"

    def increase_volume(self, step=10):
        current = self.get_volume()
        return self.set_volume(current + step)

    def decrease_volume(self, step=10):
        current = self.get_volume()
        return self.set_volume(current - step)

    def mute(self):
        self.volume.SetMute(1, None)
        return "Volume muted"

    def unmute(self):
        self.volume.SetMute(0, None)
        return "Volume unmuted"


# -----------------------------------
# GLOBAL INSTANCE
# -----------------------------------

volume = VolumeController()


# -----------------------------------
# COMMAND HANDLER FUNCTION
# -----------------------------------

def handle_volume_command(command: str):
    command = command.lower().strip()

    # ---------------------------------
    # INTENT WORD GROUPS
    # ---------------------------------
    increase_words = ["increase", "raise", "boost", "up", "higher", "louder"]
    decrease_words = ["decrease", "lower", "reduce", "down", "dim", "quieter"]
    set_words = ["set", "make", "change"]
    max_words = ["max", "maximum", "full"]
    volume_words = ["volume", "sound", "audio"]

    # ---------------------------------
    # 1️⃣ MUTE / UNMUTE
    # ---------------------------------
    if "unmute" in command:
        return volume.unmute()

    if "mute" in command:
        return volume.mute()

    # ---------------------------------
    # 2️⃣ MAX VOLUME
    # ---------------------------------
    if any(word in command for word in max_words):
        return volume.set_volume(100)

    # ---------------------------------
    # 3️⃣ EXTRACT NUMBER IF EXISTS
    # ---------------------------------
    number_match = re.search(r'(\d+)', command)
    number = int(number_match.group(1)) if number_match else None

    # ---------------------------------
    # 4️⃣ RELATIVE CHANGE (BY X)
    # ---------------------------------
    if "by" in command and number is not None:
        if any(word in command for word in increase_words):
            return volume.increase_volume(number)

        if any(word in command for word in decrease_words):
            return volume.decrease_volume(number)

    # ---------------------------------
    # 5️⃣ ABSOLUTE CHANGE (TO X)
    # ---------------------------------
    if "to" in command and number is not None:
        return volume.set_volume(number)

    # ---------------------------------
    # 6️⃣ SIMPLE SET (number only)
    # ---------------------------------
    if any(word in command for word in set_words) and number is not None:
        return volume.set_volume(number)

    # ---------------------------------
    # 7️⃣ SIMPLE INCREASE
    # ---------------------------------
    if any(word in command for word in increase_words):
        return volume.increase_volume()

    # ---------------------------------
    # 8️⃣ SIMPLE DECREASE
    # ---------------------------------
    if any(word in command for word in decrease_words):
        return volume.decrease_volume()

    # ---------------------------------
    # 9️⃣ If no volume-related words
    # ---------------------------------
    if not any(word in command for word in volume_words):
        return None

    return "Volume command not understood"