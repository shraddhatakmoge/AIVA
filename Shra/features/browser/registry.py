from AIVA.Shra.features.browser.platforms.youtube import YouTube
from AIVA.Shra.features.browser.platforms.google import Google
from AIVA.Shra.features.browser.platforms.spotify import Spotify
from AIVA.Shra.features.browser.platforms.gmail import Gmail
from AIVA.Shra.features.browser.platforms.whatsapp import WhatsApp


PLATFORM_REGISTRY = {
    "youtube": YouTube,
    "google": Google,
    "spotify": Spotify,
    "gmail": Gmail,
    "whatsapp": WhatsApp
}