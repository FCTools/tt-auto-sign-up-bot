"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

import email
import imaplib


class MailService:
    def __init__(self, imap_server='imap.mail.ru'):
        self._mail_server = imap_server
        self._sender = '"TikTok For Business" <no-reply@ads-service.tiktok.com>'

    def find_verification_code(self, mail, password):
        mailbox = imaplib.IMAP4_SSL(self._mail_server)
        print(mailbox.login(mail, password))

        verification_code_email = self._last_message_from_tik_tok(mailbox)
        verification_code = self._parse_verification_code(verification_code_email)

        return verification_code

    def _last_message_from_tik_tok(self, mailbox):
        emails_list = []

        mailbox.select("inbox")
        result, data = mailbox.search(None, "UNSEEN")

        mails_ids_list = data[0].split()

        for mail_id in mails_ids_list:
            result, data = mailbox.fetch(mail_id, "(RFC822)")

            raw_email = data[0][1]
            parsed_email = email.message_from_bytes(raw_email)

            if self.email_from_tik_tok(parsed_email):
                emails_list.append((int(mail_id.decode('utf-8')), parsed_email))

        max_id = 0
        required_email = None

        for mail in emails_list:
            if mail[0] > max_id:
                max_id = mail[0]
                required_email = mail[1]

        return required_email

    def email_from_tik_tok(self, email_message):
        return str(email_message["From"]) == self._sender

    def _parse_verification_code(self, mail):
        parts = []
        for part in mail.walk():
            content = part.get_payload(decode=True)
            if content:
                parts.append(content.decode())

        required_part = parts[-1]
        required_part = required_part.split('customer')[1].split('Account')[1].split('code:')[1].split('align="left"')[
            1].replace('\n', '').replace('\r', '')
        verification_code = required_part[1:].strip().split()[0]

        return verification_code
