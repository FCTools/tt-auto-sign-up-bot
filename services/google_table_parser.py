import os
import pickle
from pprint import pprint

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleTableParser:
    def __init__(self):
        self._credentials_filename = os.path.join("..", "credentials.json")
        self._service = None
        self._scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        self._load_credentials()

    def _load_credentials(self):
        creds = None

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self._credentials_filename, self._scopes)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self._service = build('sheets', 'v4', credentials=creds)

    def get_title(self, doc_id):
        document = self._service.spreadsheets().get(spreadsheetId=doc_id).execute()
        pprint(document)

        print('The title of the document is: {}'.format(document.get('sheetId')))

    def _get_files(self):
        pprint(self._service.documents())
        pprint(self._service.documents().list(pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute())


service = GoogleTableParser()
# service._get_files()
