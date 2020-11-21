"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

import os
from pprint import pprint

from domains.accounts.tt_account import TikTokAccount
from domains.services.google_table_parser import GoogleTableParser


class AccountManager:
    def __init__(self):
        self._document_id = os.getenv("SIGN_UP_INFO_SOURCE_DOCUMENT_ID")
        self._table_parser = GoogleTableParser()

    def _get_updates(self):
        accounts_to_sign_up = self._table_parser.get_accounts_to_sign_up()
        if not accounts_to_sign_up:
            return []

        return accounts_to_sign_up

    def get_accounts_to_sign_up(self):
        result = []
        new_entries = self._get_updates()

        for account in new_entries:
            if account and int(account[-1]):
                result.append(TikTokAccount(account))

        return result

    def update_sign_up_status(self, account, status):
        self._table_parser.update_sign_up_status(account, status)

#
# manager = AccountManager()
# accounts = manager.get_accounts_to_sign_up()
#
# for account in accounts:
#     account.sign_up()
