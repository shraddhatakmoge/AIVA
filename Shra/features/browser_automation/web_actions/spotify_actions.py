import urllib.parse
from ..browser_controller import open_url


def search_spotify(query: str):
    if not query:
        open_url("https://open.spotify.com")
        return

    encoded = urllib.parse.quote(query)
    url = f"https://open.spotify.com/search/{encoded}"

    print(f"[Spotify] Searching: {query}")
    open_url(url)
