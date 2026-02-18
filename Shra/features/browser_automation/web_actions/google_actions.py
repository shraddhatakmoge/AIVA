import urllib.parse
import webbrowser


def search_google(query: str):
    if not query:
        print("[Google] No search query provided.")
        return

    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    webbrowser.open(url)

    print(f"[Google] Searching: {query}")
