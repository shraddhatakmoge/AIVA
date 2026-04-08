import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os
from email.mime.base import MIMEBase
from email import encoders
from AIVA.Shra.features.browser.window_focus import bring_browser_to_front

class Gmail:

    def __init__(self, driver):
        self.driver = driver
        self.service = self.authenticate()

        # 🔥 NEW: local memory to avoid duplicates
        self.read_ids = set()

    def authenticate(self):
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify'
        ]

        # 🔥 Get ROOT directory (AIVA-shra)
        # 🔥 Get directory of THIS FILE (portable)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 🔥 Go up 3 levels → reach AIVA/Shra/
        ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../.."))

        cred_path = os.path.join(ROOT_DIR, "credentials.json")
        token_path = os.path.join(ROOT_DIR, "token.pickle")

        creds = None

        # Load token if exists
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # First-time login
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_path, SCOPES
            )
            creds = flow.run_local_server(
                port=0,
                open_browser=True
            )

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def open(self, tab_handle=None):

        try:
            # 🔥 If tab handle provided → switch
            if tab_handle:
                self.driver.switch_to.window(tab_handle)

            # 🔥 Always open URL in THIS tab only
            self.driver.get("https://mail.google.com")


            bring_browser_to_front()

            return {
                "status": "success",
                "response": "Opened Gmail"
            }

        except Exception as e:
            return {
                "status": "error",
                "response": str(e)
            }
    def read_latest_email(self):
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=1
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return {
                    "status": "error",
                    "response": "No emails found."
                }

            msg_id = messages[0]['id']

            msg = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()

            headers = msg['payload']['headers']

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")

            return {
                "status": "success",
                "response": f"Latest email from {sender}: {subject}"
            }

        except Exception as e:
            return {
                "status": "error",
                "response": str(e)
            }

    def read_latest_emails(self, count=1):

        try:
            # 🔥 LIMIT SAFE RANGE
            count = max(1, min(count, 5))  # 1 to 5 only

            results = self.service.users().messages().list(
                userId='me',
                maxResults=count,
                q="is:unread"
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return {
                    "status": "error",
                    "response": "No new unread emails."
                }

            output = []
            count_added = 0

            for msg_data in messages:

                msg_id = msg_data['id']

                # 🔥 SKIP already read emails
                if msg_id in self.read_ids:
                    continue

                msg = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='metadata',
                    metadataHeaders=['Subject', 'From']
                ).execute()

                headers = msg['payload']['headers']

                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")

                count_added += 1
                output.append(f"{count_added}. From {sender} — {subject}")

                # 🔥 STORE LOCALLY
                self.read_ids.add(msg_id)

                # 🔥 ALSO mark in Gmail
                self.mark_as_read(msg_id)

                if count_added >= count:
                    break
            if not output:
                return {
                    "status": "info",
                    "response": "No new unread emails."
                }

            return {
                "status": "success",
                "response": "\n".join(output)
            }


        except Exception as e:
            return {
                "status": "error",
                "response": str(e)
            }


    def mark_as_read(self, msg_id):
        self.service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()


    def send_email(self, to, subject, body, attachment_path=None):
        try:
            message = MIMEMultipart()
            message["to"] = to
            message["subject"] = subject or "No Subject"

            # Body
            message.attach(MIMEText(body or ""))

            # Attachment
            if attachment_path:
                clean_path = attachment_path.strip().strip('"').strip("'")

                if not os.path.exists(clean_path):
                    return {
                        "status": "error",
                        "response": f"Attachment not found: {clean_path}"
                    }

                part = MIMEBase("application", "octet-stream")

                with open(clean_path, "rb") as file:
                    part.set_payload(file.read())

                encoders.encode_base64(part)

                filename = os.path.basename(clean_path)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{filename}"'
                )

                message.attach(part)

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            self.service.users().messages().send(
                userId="me",
                body={"raw": raw}
            ).execute()

            return {
                "status": "success",
                "response": f"Email sent to {to}"
            }

        except Exception as e:
            return {
                "status": "error",
                "response": str(e)
            }