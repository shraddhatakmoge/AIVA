import base64
from email.mime.text import MIMEText
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

    def send_email(self, to, subject, body):
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

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