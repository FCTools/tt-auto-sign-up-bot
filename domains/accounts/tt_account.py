"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

from email.utils import parseaddr

from domains.services.sign_up_service import SignUpService


class TikTokAccount:
    def __init__(self, credentials, signed_up=False):
        self._mail = credentials[0]
        self._password = credentials[1]
        self._proxy = credentials[2]
        self._country = credentials[3]
        self._business_name = credentials[4]
        self._phone = credentials[5]
        self._timezone = credentials[6]
        self._company_website = credentials[7]
        self._street_address = credentials[8]
        self._postal_code = credentials[9]
        self._vat_number = credentials[10]
        self._company_reg_number = credentials[11]
        self._payment_type = None

        self._signed_up = signed_up

        self._sign_up_service = SignUpService()

    @property
    def email(self):
        return self._mail

    @property
    def business_name(self):
        return self._business_name

    @property
    def timezone(self):
        return self._timezone

    @property
    def phone(self):
        return self._phone

    @property
    def vat_number(self):
        return self._vat_number

    @property
    def company_reg_number(self):
        return self._company_reg_number

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
    def payment_type(self):
        if self._payment_type:
            return self._payment_type
        return "-"

    def validate(self):
        if not parseaddr(self.email)[1] or '.' not in self.email:
            return "Incorrect email address"
        return "OK"

    def sign_up(self):
        status, payment_type = self._sign_up_service.sign_up(mail=self._mail,
                                                             password=self._password,
                                                             proxy=self._proxy,
                                                             country=self._country,
                                                             business_name=self._business_name,
                                                             phone=self._phone,
                                                             timezone=self._timezone,
                                                             company_website=self._company_website,
                                                             street_address=self._street_address,
                                                             postal_code=self._postal_code,
                                                             vat_number=self._vat_number,
                                                             company_reg_number=self._company_reg_number)
        self._payment_type = payment_type

        if status != "OK":
            print(status)
            return status
        else:
            return status
