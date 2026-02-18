from ..browser_controller import open_url


def send_whatsapp_message(contact: str, message: str):
    print(f"[WhatsApp] Sending message to {contact}: {message}")
    open_url("https://web.whatsapp.com")
