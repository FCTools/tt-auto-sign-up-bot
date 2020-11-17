import os
from pprint import pprint

from domains.accounts.tt_account import TikTokAccount
from domains.services.google_table_parser import GoogleTableParser


class AccountManager:
    def __init__(self):
        self._document_id = os.getenv("DOC_ID")
        self._table_parser = GoogleTableParser()

    def _get_updates(self):
        accounts_to_sign_up = self._table_parser.get_accounts_to_sign_up(self._document_id)
        if not accounts_to_sign_up:
            return []

        return accounts_to_sign_up

    def get_accounts_to_sign_up(self):
        result = []
        new_entries = self._get_updates()

        for account in new_entries:
            if int(account[-1]):
                result.append(TikTokAccount(account))

        return result


manager = AccountManager()
accounts = manager.get_accounts_to_sign_up()
