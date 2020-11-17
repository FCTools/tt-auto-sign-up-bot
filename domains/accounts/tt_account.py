from domains.services.sign_up_service import SignUpService


class TikTokAccount:
    def __init__(self, credentials, signed_up=False):
        self._mail = credentials[0]
        self._password = credentials[1]
        self._proxy = credentials[2]
        self._user_agent = credentials[3]
        self._country = credentials[4]
        self._company_website = credentials[5]
        self._street_address = credentials[6]
        self._postal_code = credentials[7]
        self._tax_id = credentials[8]
        self._payment_type = credentials[9]

        self._signed_up = signed_up

        self._sign_up_service = SignUpService()

    def sign_up(self):
        status = self._sign_up_service.sign_up(mail=self._mail,
                                               password=self._password,
                                               proxy=self._proxy,
                                               user_agent=self._user_agent,
                                               country=self._country,
                                               company_website=self._company_website,
                                               street_address=self._street_address,
                                               postal_code=self._postal_code,
                                               tax_id=self._tax_id)

    def remove_from_account_to_sign_up(self):
        pass

    def add_to_signed_up_account(self):
        pass
