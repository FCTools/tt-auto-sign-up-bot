"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

import time
import os
from copy import deepcopy
from queue import Queue
from domains.services.account_manager import AccountManager
from threading import Thread, Lock


class WorkingLoop:
    def __init__(self):
        self._required_environment_variables_list = ['CHECKING_TIMEOUT',
                                                     'SIGN_UP_INFO_SOURCE_DOCUMENT_ID',
                                                     'PATH_TO_GOOGLE_API_CREDENTIALS',
                                                     'PARSING_RANGE',
                                                     ]

        self._check_environment()

        self._accounts_to_register = Queue()
        self._account_manager = AccountManager()
        self._lock = Lock()

        self._checking_timeout = float(os.getenv("CHECKING_TIMEOUT"))

    def _check_environment(self):
        for env_var in self._required_environment_variables_list:
            if not os.environ.get(env_var):
                # log that can't find required environment variable
                exit(-1)

        if not os.path.exists(os.getenv('PATH_TO_GOOGLE_API_CREDENTIALS')):
            # log that can't find google credentials file
            exit(-1)

    def _accounts_register_process(self):
        while True:
            if not self._accounts_to_register.empty():
                with self._lock:
                    account_to_register = self._accounts_to_register.get()
                status = account_to_register.sign_up()
                self._account_manager.update_sign_up_status(account_to_register, status)
            else:
                time.sleep(self._checking_timeout)

    def _extend_queue(self):
        accounts_to_sign_up = self._account_manager.get_accounts_to_sign_up()

        with self._lock:
            for account in accounts_to_sign_up:
                self._accounts_to_register.put(deepcopy(account))

    def _process(self):
        self._sign_up_thread = Thread(target=self._accounts_register_process, args=(), daemon=True)
        self._sign_up_thread.start()

        while True:
            self._extend_queue()
            time.sleep(self._checking_timeout)

    def launch(self):
        self._process()
