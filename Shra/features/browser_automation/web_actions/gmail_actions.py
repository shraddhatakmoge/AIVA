from ..browser_controller import open_url


def send_email(to: str, subject: str, body: str, file_path: str = None):
    print(f"[Gmail] Sending email to {to}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")

    if file_path:
        print(f"Attachment: {file_path}")

    open_url("https://mail.google.com")
