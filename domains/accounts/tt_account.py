"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

from domains.services.sign_up_service import SignUpService


class TikTokAccount:
    def __init__(self, credentials, signed_up=False):
        self._mail = credentials[0]
        self._password = credentials[1]
        self._proxy = credentials[2]
        self._country = credentials[3]
        self._company_website = credentials[4]
        self._street_address = credentials[5]
        self._postal_code = credentials[6]

        self._signed_up = signed_up

        self._sign_up_service = SignUpService()

    @property
    def email(self):
        return self._mail

    def sign_up(self):
        status = self._sign_up_service.sign_up(mail=self._mail,
                                               password=self._password,
                                               proxy=self._proxy,
                                               country=self._country,
                                               company_website=self._company_website,
                                               street_address=self._street_address,
                                               postal_code=self._postal_code)

        if status != "OK":
            print(status)
            return status
            # do smth to handle it and write status to the table
        else:
            pass
            # write about success registration to the table
