"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

import logging
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleTableParser:
    def __init__(self):
        self._logger = logging.getLogger('WorkingLoop.AccountManager.GoogleTableParser')

        self._credentials_filename = os.getenv("PATH_TO_GOOGLE_API_CREDENTIALS")
        self._parsing_range = os.getenv("PARSING_RANGE")
        self._service = None
        self._headers = ['mail', 'password']
        self._scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        self._doc_id = os.getenv("SIGN_UP_INFO_SOURCE_DOCUMENT_ID")

        self._load_credentials()

        self._done_accounts = self._filled_rows_on_page_2()

        self._logger.info("GoogleTableParser was successfully initialized.")

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
        self._logger.info("Google api credentials was successfully loaded and service was successfully built.")

    def get_accounts_to_sign_up(self):
        document = self._service.spreadsheets().values().get(spreadsheetId=self._doc_id,
                                                             range=self._parsing_range).execute()

        return document["values"][1:]

    def _filled_rows_on_page_2(self):
        portion = 10000
        total_number = portion
        result = 0

        while True:
            range_ = f"Result!A{total_number - portion + 1}:A{total_number}"
            rows = self._service.spreadsheets().values().batchGet(spreadsheetId=self._doc_id,
                                                                  ranges=[range_],
                                                                  valueRenderOption='FORMATTED_VALUE',
                                                                  dateTimeRenderOption='FORMATTED_STRING'
                                                                  ).execute()['valueRanges'][0]['values'][1:]

            if len(rows) < portion:
                return result + len(rows) + 2
            result += portion

            total_number += portion

    def _find_row_number(self, account):
        rows = self.get_accounts_to_sign_up()
        for n, row in enumerate(rows):
            if row and row[0] == account.email:
                return n + 2
        return -1

    def _remove_account_from_list_1(self, account):
        row_number = self._find_row_number(account)
        if row_number == -1:
            return

        range_ = f"A{row_number}:I{row_number}"
        value_input_option = "USER_ENTERED"

        request = self._service.spreadsheets().values().batchUpdate(spreadsheetId=self._doc_id,
                                                                    body={
                                                                        "valueInputOption": value_input_option,
                                                                        "data": [
                                                                            {"range": range_,
                                                                             "majorDimension": "ROWS",
                                                                             "values": [
                                                                                 ["", "", "", "", "", "", "", "", ""],
                                                                             ]}
                                                                        ]
                                                                    })
        # TODO: add network errors catching
        response = request.execute()
        self._logger.info(f"Remove account {account.email} from sheet 'Value'")

    def _add_account_to_list_2(self, account, status):
        free_row = self._done_accounts
        range_ = f"Result!A{free_row}:J{free_row}"

        value_input_option = "USER_ENTERED"

        request = self._service.spreadsheets().values().batchUpdate(spreadsheetId=self._doc_id,
                                                                    body={
                                                                        "valueInputOption": value_input_option,
                                                                        "data": [
                                                                            {"range": range_,
                                                                             "majorDimension": "ROWS",
                                                                             "values": [
                                                                                 [account.email,
                                                                                  account.password,
                                                                                  account.proxy,
                                                                                  account.country,
                                                                                  account.company_website,
                                                                                  account.street_address,
                                                                                  account.postal_code,
                                                                                  account.tax_id,
                                                                                  status,
                                                                                  account.payment_type],
                                                                             ]}
                                                                        ]
                                                                    })
        # TODO: add network errors catching
        response = request.execute()
        self._done_accounts += 1

        self._logger.info(f"Add account {account.email} to sheet 'Result'")

    def update_sign_up_status(self, account, status):
        self._remove_account_from_list_1(account)
        self._add_account_to_list_2(account, status)
