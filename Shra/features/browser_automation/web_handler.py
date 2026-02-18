from .url_utils import clean_command, remove_words
from .app_registry import WEB_APPS, detect_app
from .browser_controller import open_url
from .search_engine import search_google

from .web_actions.youtube_actions import open_youtube_home, search_youtube
from .web_actions.spotify_actions import search_spotify
from .web_actions.gmail_actions import send_email
from .web_actions.whatsapp_actions import send_whatsapp_message


def handle_web_command(command: str):
    command = clean_command(command)
    app = detect_app(command)

    # -------------------------
    # YOUTUBE UNIVERSAL HANDLER
    # -------------------------
    if app == "youtube":

        # PLAY intent → use Selenium
        if "play" in command:
            from .web_actions.youtube_actions import play_on_youtube

            query = remove_words(command, ["play", "on", "youtube", "song"])
            play_on_youtube(query)
            return

        # SEARCH intent → URL-based search
        if "search" in command:
            query = remove_words(command, ["search", "on", "youtube"])
            search_youtube(query)
            return

        # OPEN youtube only
        if "open" in command:
            open_youtube_home()
            return

        # If only youtube + query (no keywords)
        query = remove_words(command, ["youtube"])
        if query:
            search_youtube(query)
            return

        open_youtube_home()
        return

    # -------------------------
    # SPOTIFY UNIVERSAL HANDLER
    # -------------------------
    if app == "spotify":
        query = remove_words(command, ["search", "play", "open", "on", "spotify"])

        if not query:
            open_url(WEB_APPS["spotify"])
            return

        search_spotify(query)
        return

    # -------------------------
    # OPEN OTHER APPS
    # -------------------------
    if "open" in command and app:
        open_url(WEB_APPS[app])
        return

    # -------------------------
    # SEND MAIL
    # -------------------------
    if "send mail" in command:
        try:
            parts = command.split("to", 1)[1].strip()
            to_part, rest = parts.split("subject", 1)
            subject_part, body_part = rest.split("body", 1)

            to = to_part.strip()
            subject = subject_part.strip()
            body = body_part.strip()

            send_email(to, subject, body)
            return
        except:
            print("Invalid mail format.")
            return

    # -------------------------
    # WHATSAPP
    # -------------------------
    if "whatsapp" in command:
        try:
            parts = command.split("to", 1)[1].strip()
            contact, message = parts.split(" ", 1)

            send_whatsapp_message(contact, message)
            return
        except:
            print("Invalid WhatsApp format.")
            return

    # -------------------------
    # DEFAULT GOOGLE SEARCH
    # -------------------------
    search_google(command)
