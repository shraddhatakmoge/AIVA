from AIVA.Shra.features.browser.music.music_preferences import MusicPreferences


class MusicManager:

    def __init__(self, controller):
        self.controller = controller
        self.preferences = MusicPreferences()
        self.last_music_platform = None

    # -------------------------------------------------
    def update_last_platform(self, platform):
        if platform in ["youtube", "spotify"]:
            self.last_music_platform = platform

    # -------------------------------------------------
    def resolve_platform(self, target):

        if target in ["youtube", "spotify"]:
            return target

        default = self.preferences.get_default_platform()
        if default:
            return default

        if self.last_music_platform:
            return self.last_music_platform

        return None  # ask user

    # -------------------------------------------------
    def play_favorite(self, target=None):

        platform = self.resolve_platform(target)

        if not platform:
            return {
                "status": "ask_platform",
                "response": "Do you want YouTube or Spotify for favorites?"
            }

        result = self.controller.handle({
            "action": "play_favorite",
            "target": platform
        })

        if result["status"] == "success":
            self.update_last_platform(platform)

        return result

    # -------------------------------------------------
    def set_default_platform(self, platform):
        self.preferences.set_default_platform(platform)