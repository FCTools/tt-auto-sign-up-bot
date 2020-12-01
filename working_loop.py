"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

import logging
import os
import time
from copy import deepcopy
from multiprocessing import Queue
from threading import Thread, Lock

from domains.services.account_manager import AccountManager


class WorkingLoop:
    def __init__(self):
        logging.basicConfig(filename="debug_log.log", filemode="w",
                            format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)  # debug logging

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        self._logger = logging.getLogger(__name__)

        self._required_environment_variables_list = ['CHECKING_TIMEOUT',
                                                     'SIGN_UP_INFO_SOURCE_DOCUMENT_ID',
                                                     'PATH_TO_GOOGLE_API_CREDENTIALS',
                                                     'PARSING_RANGE',
                                                     ]

        # logging.basicConfig(filename='log.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
        #                     level=logging.INFO)

        self._check_environment()

        self._accounts_to_register = Queue()
        self._buffer = set()
        self._account_manager = AccountManager()
        self._lock = Lock()

        self._checking_timeout = float(os.getenv("CHECKING_TIMEOUT"))

        self._logger.info("Working loop was successfully initialized.")

    def _check_environment(self):
        for env_var in self._required_environment_variables_list:
            if not os.environ.get(env_var):
                self._logger.critical(f"Can't find required environment variable: {env_var}")
                exit(-1)

        if not os.path.exists(os.getenv('PATH_TO_GOOGLE_API_CREDENTIALS')):
            self._logger.critical("Can't find google credentials file.")
            exit(-1)

        checking_interval = float(os.getenv("CHECKING_TIMEOUT"))
        if checking_interval <= 0:
            self._logger.critical("CHECKING_TIMEOUT value can't be negative or null.")
            exit(-1)

        self._logger.info("Environment is correct.")

    def _accounts_register_process(self):
        time.sleep(5)  # time to load accounts to register first time

        while True:
            if not self._accounts_to_register.empty():
                with self._lock:
                    account_to_register = self._accounts_to_register.get()
                    self._buffer.add(account_to_register.email)

                validation_status = account_to_register.validate()

                if validation_status != "OK":
                    self._logger.debug(f"Invalid account, status: {validation_status}")
                    status = validation_status
                else:
                    self._logger.info(f"Start register for account with email: {account_to_register.email}")
                    status = account_to_register.sign_up()
                    self._logger.info(f"Sign up for account {account_to_register.email} completed, status: {status}")

                self._account_manager.update_sign_up_status(account_to_register, status)
                self._logger.info(f"Update status for account {account_to_register.email}.")

                with self._lock:
                    self._buffer.remove(account_to_register.email)
            else:
                self._logger.info(f"Empty queue, sleep for {self._checking_timeout} seconds.")
                time.sleep(self._checking_timeout)

    def _extend_queue(self):
        accounts_to_sign_up = self._account_manager.get_accounts_to_sign_up()
        self._logger.info(f"Get {len(accounts_to_sign_up)} accounts to sign up.")

        with self._lock:
            for account in accounts_to_sign_up:
                if account.email not in self._buffer:
                    self._accounts_to_register.put(deepcopy(account))

    def _process(self):
        self._sign_up_thread = Thread(target=self._accounts_register_process, args=(), daemon=True)
        self._sign_up_thread.start()

        self._logger.info("Start accounts register process.")
        self._logger.info("Start table monitoring process.")

        while True:
            self._extend_queue()
            time.sleep(self._checking_timeout)

    def launch(self):
        self._process()
