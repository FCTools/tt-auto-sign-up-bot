"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

import os
import pickle
from pprint import pprint

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from domains.accounts.tt_account import TikTokAccount


class GoogleTableParser:
    def __init__(self):
        self._credentials_filename = os.path.join("../..", "credentials.json")
        self._service = None
        self._headers = ['mail', 'password']
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

    def get_accounts_to_sign_up(self, doc_id):
        document = self._service.spreadsheets().values().get(spreadsheetId=doc_id, range="A1:L100").execute()

        return document["values"][1:]
