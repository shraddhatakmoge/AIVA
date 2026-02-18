import difflib

WEB_APPS = {
    "youtube": "https://www.youtube.com",
    "spotify": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "google": "https://www.google.com"
}

APP_ALIASES = {
    "yt": "youtube",
    "you tube": "youtube",
    "spotfy": "spotify",
    "mail": "gmail",
    "whats app": "whatsapp"
}


def detect_app(command: str):
    command = command.lower()

    # Phrase alias match first
    for alias, actual in APP_ALIASES.items():
        if alias in command:
            return actual

    words = command.split()

    # Direct match
    for word in words:
        if word in WEB_APPS:
            return word

    # Fuzzy match
    possible_apps = list(WEB_APPS.keys())

    for word in words:
        match = difflib.get_close_matches(word, possible_apps, n=1, cutoff=0.7)
        if match:
            return match[0]

    return None
