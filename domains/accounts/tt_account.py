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

        self._tax_id = credentials[7]
        self._payment_type = None

        self._signed_up = signed_up

        self._sign_up_service = SignUpService()

    @property
    def email(self):
        return self._mail

    @property
    def password(self):
        return self._password

    @property
    def proxy(self):
        return self._proxy

    @property
    def country(self):
        return self._country

    @property
    def company_website(self):
        return self._company_website

    @property
    def street_address(self):
        return self._street_address

    @property
    def postal_code(self):
        return self._postal_code

    @property
    def tax_id(self):
        return self._tax_id

    @property
    def payment_type(self):
        if self._payment_type:
            return self._payment_type
        return "-"

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
