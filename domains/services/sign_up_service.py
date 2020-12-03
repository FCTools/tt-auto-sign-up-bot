"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

import json
import logging
import os
import random
import time

from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from selenium import webdriver
from selenium.common import exceptions

from domains.services.mail_service import MailService
from domains.services.singleton import Singleton


# TODO: fix selects processing logic


class SignUpService(metaclass=Singleton):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

        self._user_agent_rotator = UserAgent(operating_systems=[OperatingSystem.WINDOWS.value,
                                                                OperatingSystem.MAC_OS_X.value,
                                                                OperatingSystem.LINUX.value],
                                             software_names=[SoftwareName.CHROME.value], limit=100)
        self._mail_service = MailService()
        self._screens = self._load_elements()

        self._headless = False
        if os.getenv('HEADLESS') and int(os.getenv('HEADLESS')):
            self._logger.info('Browser mode: headless}')
            self._headless = True

        self._logger.info('Screens elements were successfully loaded.')
        self._logger.info('SignUpService was successfully initialized.')

    def _catch_webdriver_exception(self):
        pass

    def _random_user_agent(self):
        return self._user_agent_rotator.get_random_user_agent()

    def _load_elements(self):
        screens_config_filename = os.path.join("configs", "screens.json")
        if not os.path.exists(screens_config_filename):
            self._logger.critical("Can't find screens.json")
            exit(-1)

        with open(screens_config_filename, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _click(self, browser, xpath=None, class_name=None):
        self._random_sleep()

        try:
            if xpath:
                browser.find_element_by_xpath(xpath).click()
            elif class_name:
                browser.find_element_by_class_name(class_name).click()

            self._random_sleep()
            return browser

        except exceptions.InvalidElementStateException as exc:
            self._logger.error(exc.msg)
        except exceptions.NoSuchElementException as exc:
            self._logger.error(exc.msg)
        except exceptions.InvalidSwitchToTargetException as exc:
            self._logger.error(exc.msg)
        except exceptions.WebDriverException as exc:
            self._logger.error(exc.msg)
        except Exception as exc:
            self._logger.error(str(exc))

        return browser

    def _send_keys(self, browser, value, xpath=None, class_name=None):
        self._random_sleep()

        try:
            if xpath:
                browser.find_element_by_xpath(xpath).send_keys(value)
            elif class_name:
                browser.find_element_by_class_name(class_name).send_keys(value)

            self._random_sleep()
            return browser

        except exceptions.InvalidElementStateException as exc:
            self._logger.error(exc.msg)
        except exceptions.NoSuchElementException as exc:
            self._logger.error(exc.msg)
        except exceptions.InvalidSwitchToTargetException as exc:
            self._logger.error(exc.msg)
        except exceptions.WebDriverException as exc:
            self._logger.error(exc.msg)
        except Exception as exc:
            self._logger.error(str(exc))

        return browser

    def _build_browser(self, proxy):
        proxy_parts = proxy.split(":")
        ip = proxy_parts[0]
        port = proxy_parts[1]
        proxy_string = f'{ip}:{port}'

        user_agent = self._random_user_agent()
        self._logger.debug(user_agent)

        options_list = ['start-maximized', 'disable-infobars', '-no-sandbox', '--disable-extensions',
                        f'--proxy-server={proxy_string}', f'user-agent={user_agent}',
                        'window-size=1920x1080', ]

        if self._headless:
            options_list.append('headless')

        chrome_options = webdriver.ChromeOptions()

        for option in options_list:
            chrome_options.add_argument(option)

        return webdriver.Chrome(options=chrome_options)

    def _detect_screen(self, browser):
        label_xpath = self._screens['screens_elements']['screen_2.1']['billing_country_label_xpath']
        label = self._screens['screens_elements']['screen_2.1']['billing_country_label_text']

        if len(browser.find_elements_by_xpath(label_xpath)) > 0:
            element = browser.find_element_by_xpath(label_xpath)

            if element and element.text == label:
                return 2

        return 1

    def _solve_screen_1_1(self, browser, mail, password):
        browser = self._accept_cookie_policy(browser)

        screen_elements = self._screens['screens_elements']['screen_1.1']

        browser = self._send_keys(browser, mail, xpath=screen_elements['login_xpath'])
        self._logger.debug("SCREEN 1.1 | Fill login field.")
        browser = self._send_keys(browser, password, xpath=screen_elements['password_xpath'])
        self._logger.debug("SCREEN 1.1 | Fill password field.")
        browser = self._send_keys(browser, password, xpath=screen_elements['repeat_password_xpath'])
        self._logger.debug("SCREEN 1.1 | Fill repeat password field.")
        browser = self._click(browser, xpath=screen_elements['agreement_checkbox_xpath'])
        self._logger.debug("SCREEN 1.1 | Click agreement checkbox.")
        browser = self._click(browser, xpath=screen_elements['verification_code_xpath_button'])
        self._logger.debug("SCREEN 1.1 | Click verification code button.")

        self._logger.info("SCREEN 1.1 | Fill login, password, agreement on screen 1.1 and "
                          "click verification code button.")

        if len(browser.find_elements_by_xpath(screen_elements['email_already_used_error_xpath'])) > 0 \
                and browser.find_element_by_xpath(screen_elements['email_already_used_error_xpath']).text == \
                'The email is already registered. Please log in.':
            self._logger.error(f"SCREEN 1.1 | This email is already registered: {mail}")
            return "Email is already registered.", browser

        time.sleep(45)
        verification_code = self._mail_service.find_verification_code(mail, password)
        self._logger.info(f"SCREEN 1.1 | Get verification code: {verification_code}")

        browser = self._send_keys(browser, verification_code, xpath=screen_elements['verification_code_field_xpath'])
        self._logger.debug("SCREEN 1.1 | Fill verification code.")

        browser = self._click(browser, xpath=screen_elements['submit_button_xpath'])
        self._logger.info("SCREEN 1.1 | Click submit button on screen 1.1.")

        return "OK", browser

    def _solve_screen_2_1(self, browser, country):
        browser = self._accept_cookie_policy(browser)

        screen_elements = self._screens['screens_elements']['screen_2.1']

        browser = self._click(browser, class_name=screen_elements['country_selector_class_name'])
        self._logger.debug("SCREEN 2.1 | Click country selector.")

        browser = self._send_keys(browser, country, xpath=screen_elements['country_field_xpath'])
        self._logger.debug('SCREEN 2.1 | Fill country.')

        browser = self._click(browser, xpath=screen_elements['country_field_xpath_to_click'].format(country))
        self._logger.debug("SCREEN 2.1 | Select country.")
        browser = self._click(browser, class_name=screen_elements['submit_button_class_name'])
        self._logger.debug("SCREEN 2.1 | Click submit button on screen 2.")

        return "OK", browser

    @staticmethod
    def _random_phone_number():
        first = str(random.randint(100, 999))
        second = str(random.randint(1, 888)).zfill(3)
        last = (str(random.randint(1, 9998)).zfill(4))

        while last in ['1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888']:
            last = (str(random.randint(1, 9998)).zfill(4))
        return f'{first}{second}{last}'

    @staticmethod
    def _random_sleep():
        time.sleep(random.randint(1, 3))

    def _solve_screen_1_2(self, browser, mail, country=None):
        browser = self._accept_cookie_policy(browser)

        screen_elements = self._screens['screens_elements']['screen_1.2']

        default_currency = screen_elements['default_currency']
        business_name = mail.split('@')[0]
        phone_number = self._random_phone_number()

        if country:
            browser = self._click(browser, xpath=screen_elements['country_edit_xpath'])
            self._logger.debug("SCREEN 1.2 | Click country edit button.")

            browser = self._click(browser, xpath=screen_elements['country_selector_xpath'])
            self._logger.debug("SCREEN 1.2 | Click country selector.")

            browser = self._send_keys(browser, country, xpath=screen_elements['country_field_xpath'])
            self._logger.debug('SCREEN 1.2 | Fill country.')

            browser = self._click(browser, xpath=screen_elements['country_field_xpath_to_click'].format(country))
            self._logger.debug("SCREEN 1.2 | Select country.")
        else:
            self._logger.debug("SCREEN 1.2 | No country given, set default.")

        browser = self._send_keys(browser, business_name, xpath=screen_elements['business_name_xpath'])
        self._logger.debug("SCREEN 1.2 | Fill business name.")

        browser = self._send_keys(browser, phone_number, xpath=screen_elements['phone_number_xpath'])
        self._logger.debug("SCREEN 1.2 | Fill phone number.")

        browser = self._click(browser, xpath=screen_elements['agreement_checkbox_xpath'])
        self._logger.debug("SCREEN 1.2 | Click agreement checkbox.")

        browser = self._click(browser, xpath=screen_elements['currency_selector_xpath'])
        self._logger.debug("SCREEN 1.2 | Click currency selector.")

        browser = self._click(browser, xpath=screen_elements['currency_field_xpath'].format(default_currency))
        self._logger.debug("SCREEN 1.2 | Fill currency field.")

        browser = self._click(browser, xpath=screen_elements['submit_button_xpath'])
        self._logger.debug("SCREEN 1.2 | Click submit button.")

        self._logger.info("SCREEN 1.2 | Fill country, business name, phone number, agreement, "
                          "currency on screen 1.2 and submit form.")

        return "OK", browser

    def _accept_cookie_policy(self, browser):
        cookie_accept_button_xpath = self._screens['screens_elements']['other']['cookie_accept_button_xpath']
        cookie_accept_button_text = self._screens['screens_elements']['other']['cookie_accept_button_text']
        # //*[@id="app"]/section/div[3]/div/button
        if len(browser.find_elements_by_xpath("//*[contains(text(), '{}')]".format("Accept"))) > 0:
            browser = self._click(browser, xpath="//*[contains(text(), '{}')]".format("Accept"))
            self._logger.debug("Accept cookie policy.")
        else:
            self._logger.debug('No cookie policy found.')

        return browser

    def _proxy_status(self, browser):
        screen_elements = self._screens['screens_elements']['screen_2.2']
        fullname_xpath = screen_elements['fullname_xpath']
        phone_xpath = screen_elements['phone_number_xpath']

        if len(browser.find_elements_by_xpath(fullname_xpath)) > 0 and \
                len(browser.find_elements_by_xpath(phone_xpath)) > 0:
            return "Bad proxy for registration"

        return "OK"

    def _solve_screen_1_3(self, browser, company_website, postal_code, street_address, tax_id):
        browser = self._accept_cookie_policy(browser)

        screen_elements = self._screens['screens_elements']['screen_1.3']
        self._logger.debug(browser.title)

        if len(browser.find_elements_by_xpath(screen_elements['spam_window_xpath'])) > 0:
            try:
                browser = self._click(browser, xpath=screen_elements['spam_window_xpath'])
                self._logger.debug("SCREEN 1.3 | Close spam window.")
            except:
                pass

        browser.execute_script(screen_elements['scroll_script'])
        browser.find_element_by_xpath(screen_elements['account_xpath']).click()
        self._logger.debug("SCREEN 1.3 | Click account button.")
        browser = self._click(browser, xpath=screen_elements['account_info_xpath'])
        self._logger.debug("SCREEN 1.3 | Click account info button.")

        try:
            browser.switch_to.alert.accept()
            self._logger.debug("SCREEN 1.3 | Alert closed.")
        except exceptions.NoAlertPresentException:
            self._logger.debug("SCREEN 1.3 | No alert.")

        time.sleep(30)

        browser = self._send_keys(browser, company_website, xpath=screen_elements['company_website_xpath'])
        self._logger.debug("SCREEN 1.3 | Fill company website.")

        browser = self._click(browser, xpath=screen_elements['industry_selector_xpath_1'])
        self._logger.debug("SCREEN 1.3 | Click industry selector 1.")
        browser = self._click(browser,
                              xpath=screen_elements['industry_selector_xpath_1_list'].format(random.randint(1, 25)))
        self._logger.debug("SCREEN 1.3 | Select random industry 1.")

        browser = self._click(browser, xpath=screen_elements['industry_selector_xpath_2'])
        self._logger.debug("SCREEN 1.3 | Click industry selector 2.")
        browser = self._click(browser,
                              xpath=screen_elements['industry_selector_xpath_2_list'].format(random.randint(1, 5)))
        self._logger.debug("SCREEN 1.3 | Select random industry 2.")

        browser = self._send_keys(browser, street_address, xpath=screen_elements['street_address_xpath'])
        self._logger.debug("SCREEN 1.3 | Fill street address.")

        browser.execute_script("scroll(530, 885);")
        self._random_sleep()

        browser = self._click(browser, xpath=screen_elements['state_selector_xpath'])
        self._logger.debug("SCREEN 1.3 | Click state selector.")

        browser = self._click(browser, xpath=screen_elements['states_list_xpath'].format(random.randint(1, 7)))
        self._logger.debug("SCREEN 1.3 | Select random state.")

        browser = self._click(browser, xpath=screen_elements['postal_code_xpath'])
        self._logger.debug("SCREEN 1.3 | Click postal code field.")

        browser = self._send_keys(browser, postal_code, xpath=screen_elements['postal_code_xpath'])
        self._logger.debug("SCREEN 1.3 | Fill postal code.")

        self._logger.info("SCREEN 1.3 | Fill company website, industry, street address, state/province, "
                          "postal code on screen 1.3.")

        if len(browser.find_elements_by_xpath(screen_elements['tax_id_xpath'])) > 0:
            browser = self._send_keys(browser, tax_id, xpath=screen_elements['tax_id_xpath'])
            self._logger.info("SCREEN 1.3 | Fill tax id.")
        else:
            self._logger.info('SCREEN 1.3 | No tax_id found on the page.')

        if len(browser.find_elements_by_xpath(screen_elements['city_label_xpath'])) > 0 and \
           browser.find_element_by_xpath(screen_elements['city_label_xpath']).text == 'City':
            browser = self._click(browser, xpath=screen_elements['city_selector_xpath'])
            self._logger.info('SCREEN 1.3 | Click city selector.')
            browser = self._click(browser, xpath=screen_elements['city_field_xpath'].format(random.randint(1, 5)))
            self._logger.info('SCREEN 1.3 | Select random city.')
        else:
            self._logger.info('SCREEN 1.3 | No city field found on the page.')

        browser.execute_script("scroll(296, 918);")
        browser = self._click(browser, xpath=screen_elements['submit_button_xpath'])
        self._logger.info("SCREEN 1.3 | Click submit button on screen 1.3.")

        return "OK", browser

    def _check_account_status(self, browser):
        status_xpath = self._screens['screens_elements']['screen_1.3']['status_xpath']
        status = browser.find_element_by_xpath(status_xpath).text

        tries = self._screens['screens_elements']['screen_1.3']['refresh_tries']

        while status == 'Under Review' and tries > 0:
            self._logger.info("ACCOUNT_STATUS_CHECKING | Status is under review. Refresh page....")
            time.sleep(15)
            browser.refresh()
            time.sleep(15)

            try:
                status = browser.find_element_by_xpath(status_xpath).text
            except exceptions.NoSuchElementException:
                status = 'Under Review'
                self._logger.error("ACCOUNT_STATUS_CHECKING | No status label on page (maybe, loading).")

            tries -= 1

        if status == 'Under Review' and tries == 0:
            self._logger.info("ACCOUNT_STATUS_CHECKING | Status is under review after "
                              "10 tries to page refresh. Skip this account...")

        return status, browser

    def _get_payment_type(self, browser):
        screen_elements = self._screens['screens_elements']['screen_1.3']

        browser.execute_script(screen_elements['scroll_script'])
        browser.find_element_by_xpath(self._screens['screens_elements']['screen_1.3']['account_xpath']).click()
        self._logger.debug("DETECT_PAYMENT_TYPE | Click account button.")
        browser = self._click(browser, xpath=screen_elements['account_info_xpath'])
        self._logger.debug("DETECT_PAYMENT_TYPE | Click account info button.")

        try:
            browser.switch_to.alert.accept()
            self._logger.debug("DETECT_PAYMENT_TYPE | Alert closed.")
        except exceptions.NoAlertPresentException:
            self._logger.debug("DETECT_PAYMENT_TYPE | No alert.")

        time.sleep(30)

        payment_type_xpath = screen_elements['payment_type_label_xpath']
        payment_type = browser.find_element_by_xpath(payment_type_xpath).text
        self._logger.info(f"DETECT_PAYMENT_TYPE | Detect payment type: {payment_type}")

        return payment_type, browser

    def sign_up(self,
                mail,
                password,
                proxy,
                country,
                company_website,
                street_address,
                postal_code,
                tax_id):
        payment_type = "-"

        if not self._mail_service.correct_credentials(mail, password):
            self._logger.warning("REG_MAIN | Incorrect email credentials.")
            return "Invalid password for email", payment_type
        self._logger.debug("REG_MAIN | Email credentials are correct.")

        browser = self._build_browser(proxy)
        self._logger.info("REG_MAIN | Successfully build browser.")
        browser.get("https://ads.tiktok.com/i18n/signup/")
        self._logger.info("REG_MAIN | Get start page.")

        time.sleep(30)

        if self._detect_screen(browser) == 1:
            self._logger.debug(browser.current_url)
            self._logger.info("REG_MAIN | Screen 1.1 was detected. Start registration branch 1.")

            status, browser = self._solve_screen_1_1(browser, mail, password)
            self._logger.info("REG_MAIN | Solve screen 1.1")

            if status != "OK":
                self._logger.error(f"REG_MAIN | Incorrect status: {status}")
                browser.close()
                return status, payment_type

            time.sleep(15)

            self._logger.info("REG_MAIN | Start screen 1.2 solving...")
            self._logger.debug(browser.current_url)

            status, browser = self._solve_screen_1_2(browser, mail, country)
            self._logger.info("REG_MAIN | Solve screen 1.2.")

            time.sleep(30)
            self._logger.debug(browser.current_url)

            self._logger.info("REG_MAIN | Start screen 1.3 solving...")
            status, browser = self._solve_screen_1_3(browser, company_website, postal_code, street_address, tax_id)

            self._logger.info(f"REG_MAIN | Solve screen 1.3, status: {status}, payment type: {payment_type}")

            self._logger.debug(browser.current_url)

            time.sleep(15)

            payment_type, browser = self._get_payment_type(browser)
            time.sleep(30)
            status, browser = self._check_account_status(browser)
            self._logger.debug(f"Check account status: {status}")

            browser.close()

            return status, payment_type

        elif self._detect_screen(browser) == 2:
            self._logger.debug("REG_MAIN | Detect screen 2.1. Start registration branch 2.")

            status, browser = self._solve_screen_2_1(browser, country)
            time.sleep(15)

            status = self._proxy_status(browser)
            if status != "OK":
                self._logger.info(f'REG_MAIN | Proxy status: {status}')
                browser.close()
                return status, payment_type

            self._logger.info('REG_MAIN | Proxy status is OK, continue registration (switch to branch 1).')

            status, browser = self._solve_screen_1_1(browser, mail, password)
            self._logger.info("REG_MAIN | Solve screen 1.1")

            if status != "OK":
                self._logger.error(f"REG_MAIN | Incorrect status: {status}")
                browser.close()
                return status, payment_type

            time.sleep(15)

            self._logger.info("REG_MAIN | Start screen 1.2 solving...")
            self._logger.debug(browser.current_url)

            status, browser = self._solve_screen_1_2(browser, mail)
            self._logger.info("REG_MAIN | Solve screen 1.2.")

            time.sleep(30)
            self._logger.debug(browser.current_url)

            self._logger.info("REG_MAIN | Start screen 1.3 solving...")
            status, browser = self._solve_screen_1_3(browser, company_website, postal_code, street_address, tax_id)

            self._logger.info(f"REG_MAIN | Solve screen 1.3, status: {status}, payment type: {payment_type}")

            self._logger.debug(browser.current_url)

            time.sleep(15)

            payment_type, browser = self._get_payment_type(browser)
            time.sleep(30)
            status, browser = self._check_account_status(browser)
            self._logger.debug(f"Check account status: {status}")

            browser.close()

            return status, payment_type
