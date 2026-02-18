from ..selenium_controller import play_youtube_video
import urllib.parse
from ..browser_controller import open_url


def open_youtube_home():
    open_url("https://www.youtube.com")


def search_youtube(query: str):
    encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    open_url(url)


def play_on_youtube(query: str):
    if not query:
        open_youtube_home()
        return

    play_youtube_video(query)
