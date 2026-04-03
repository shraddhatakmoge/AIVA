import webbrowser
import urllib.parse
import os

# ------------ SETTINGS -------------

receivers = [
    "sharvaree.jakate@gmail.com",
    "alexajinx1404@gmail.com"
]

subject = "AI Final Year Project Update"

body = """
Hello Sir/Madam,

This email is sent from my AI based final year project.

Thank you.
"""

# Optional attachment path (leave empty if none)
attachment_path = ""   # Example: "C:/Users/Akanksha/Desktop/report.pdf"

# ----------------------------------

to_field = ",".join(receivers)

subject = urllib.parse.quote(subject)
body = urllib.parse.quote(body)

gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={to_field}&su={subject}&body={body}"

chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"

webbrowser.get(chrome_path).open(gmail_url)

# Open attachment file explorer if attachment provided
if attachment_path != "":
    os.startfile(os.path.dirname(attachment_path))

print("Gmail compose opened in Chrome.")
print("Attach file manually if needed.")
