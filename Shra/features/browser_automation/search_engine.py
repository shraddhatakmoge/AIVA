import urllib.parse
from .browser_controller import open_url


def search_google(query: str):
    if not query:
        print("[Google] No search query provided.")
        return

    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}"

    print(f"[Google] Searching: {query}")
    open_url(url)
