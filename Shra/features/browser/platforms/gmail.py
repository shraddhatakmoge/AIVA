import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os


class Gmail:

    def __init__(self, driver):
        self.driver = driver
        self.service = self.authenticate()

    def authenticate(self):
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']

        # 🔥 Get ROOT directory (AIVA-shra)
        BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../../..")
        )

        cred_path = os.path.join(BASE_DIR, "credentials.json")
        token_path = os.path.join(BASE_DIR, "token.pickle")

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

    from email.mime.base import MIMEBase
    from email import encoders

    def send_email(self, to, subject, body, attachment_path=None):
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject

            # Body
            message.attach(MIMEText(body))

            # 🔥 ATTACHMENT SUPPORT
            if attachment_path:
                if not os.path.exists(attachment_path):
                    return {
                        "status": "error",
                        "response": f"Attachment not found: {attachment_path}"
                    }

                part = MIMEBase('application', 'octet-stream')

                with open(attachment_path, 'rb') as file:
                    part.set_payload(file.read())

                encoders.encode_base64(part)

                filename = os.path.basename(attachment_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={filename}'
                )

                message.attach(part)

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
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