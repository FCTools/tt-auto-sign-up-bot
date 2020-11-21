"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleTableParser:
    def __init__(self):
        self._credentials_filename = os.getenv("PATH_TO_GOOGLE_API_CREDENTIALS")
        self._parsing_range = os.getenv("PARSING_RANGE")
        self._service = None
        self._headers = ['mail', 'password']
        self._scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        self._doc_id = os.getenv("SIGN_UP_INFO_SOURCE_DOCUMENT_ID")

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

    def get_accounts_to_sign_up(self):
        document = self._service.spreadsheets().values().get(spreadsheetId=self._doc_id,
                                                             range=self._parsing_range).execute()

        return document["values"][1:]

    def _find_row_number(self, account):
        rows = self.get_accounts_to_sign_up()
        for n, row in enumerate(rows):
            if row[0] == account.email:
                return n + 2
        return -1

    def _remove_account_from_list_1(self, account):
        row_number = self._find_row_number(account)
        if row_number == -1:
            return

        range_ = f"A{row_number}:H{row_number}"
        value_input_option = "USER_ENTERED"

        request = self._service.spreadsheets().values().batchUpdate(spreadsheetId=self._doc_id,
                                                                    body={
                                                                        "valueInputOption": value_input_option,
                                                                        "data": [
                                                                            {"range": range_,
                                                                             "majorDimension": "ROWS",
                                                                             "values": [
                                                                                 ["", "", "", "", "", "", "", ""],
                                                                             ]}
                                                                        ]
                                                                    })
        response = request.execute()

    def _add_account_to_list_2(self, account, status):
        pass

    def update_sign_up_status(self, account, status):
        self._remove_account_from_list_1(account)
        self._add_account_to_list_2(account, status)
