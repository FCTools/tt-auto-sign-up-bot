"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""
import json
import os
import random
import time

from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from selenium import webdriver

from domains.services.mail_service import MailService
from domains.services.singleton import Singleton

from selenium.common import exceptions


class SignUpService(metaclass=Singleton):
    def __init__(self):
        self._user_agent_rotator = UserAgent(operating_systems=[OperatingSystem.WINDOWS.value,
                                                                OperatingSystem.MAC_OS_X.value,
                                                                OperatingSystem.LINUX.value],
                                             software_names=[SoftwareName.CHROME.value], limit=100)
        self._mail_service = MailService()
        self._screens = self._load_elements()

    def _random_user_agent(self):
        return self._user_agent_rotator.get_random_user_agent()

    @staticmethod
    def _load_elements():
        screens_config_filename = os.path.join("configs", "screens.json")
        if not os.path.exists(screens_config_filename):
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
        except exceptions.InvalidElementStateException as exc:
            print(exc)
            return browser
        except exceptions.NoSuchElementException as exc:
            print(exc)
            return browser
        except exceptions.InvalidSwitchToTargetException as exc:
            print(exc)
            return browser
        except exceptions.WebDriverException as exc:
            print(exc)
            return browser
        except Exception as exc:
            print(exc)
            return browser

        self._random_sleep()
        return browser

    def _send_keys(self, browser, value, xpath=None, class_name=None):
        self._random_sleep()

        try:
            if xpath:
                browser.find_element_by_xpath(xpath).send_keys(value)
            elif class_name:
                browser.find_element_by_class_name(class_name).send_keys(value)
        except exceptions.InvalidElementStateException as exc:
            print(exc)
            return browser
        except exceptions.NoSuchElementException as exc:
            print(exc)
            return browser
        except exceptions.InvalidSwitchToTargetException as exc:
            print(exc)
            return browser
        except exceptions.WebDriverException as exc:
            print(exc)
            return browser
        except Exception as exc:
            print(exc)
            return browser

        self._random_sleep()
        return browser

    def _build_browser(self, proxy):
        proxy_parts = proxy.split(":")
        ip = proxy_parts[0]
        port = proxy_parts[1]
        user = proxy_parts[2]
        password = proxy_parts[3]
        proxy_string = f'{ip}:{port}'
        user_agent = self._random_user_agent()
        print(user_agent)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument(f"--proxy-server={proxy_string}")
        chrome_options.add_argument(f"user-agent={user_agent}")

        return webdriver.Chrome(options=chrome_options)

    @staticmethod
    def _detect_screen(browser):
        label_xpath = '//*[@id="app"]/section/div[1]/section/div/div/section/div[5]/div/div[2]/div[2]/form/div[1]/label'
        if len(browser.find_elements_by_xpath(label_xpath)) > 0:
            element = browser.find_element_by_xpath(label_xpath)

            if element and element.text == 'Your Billing Country/Region':
                return 2

        return 1

    def _solve_screen_1(self, browser, mail, password):
        login_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[1]/div[2]/div/div/div/input'
        password_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[2]/div/div/div/input'
        repeat_password_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[3]/div/div/div/input'
        agreement_checkbox_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[5]/div[1]/div'
        submit_button_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[7]/div/button[2]'
        verification_code_xpath_button = '//*[@id="TikTokAds_Register-account-center-code-btn"]'
        verification_code_field_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[4]/div/div/div[1]/input'

        browser = self._send_keys(browser, mail, xpath=login_xpath)
        browser = self._send_keys(browser, password, xpath=password_xpath)
        browser = self._send_keys(browser, password, xpath=repeat_password_xpath)
        browser = self._click(browser, xpath=agreement_checkbox_xpath)
        browser = self._click(browser, xpath=verification_code_xpath_button)

        error_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[6]/div'
        if len(browser.find_elements_by_xpath(error_xpath)) > 0 and \
                browser.find_element_by_xpath(error_xpath).text == 'The email is already registered. Please log in.':
            return "Email is already registered.", browser

        time.sleep(15)
        verification_code = self._mail_service.find_verification_code(mail, password)

        browser = self._send_keys(browser, verification_code, xpath=verification_code_field_xpath)
        browser = self._click(browser, xpath=submit_button_xpath)

        return "OK", browser

    def _solve_screen_2(self, browser, country):
        browser = self._click(browser, class_name="vi-input__inner")
        browser = self._send_keys(browser, country, class_name="vi-input__inner")
        browser = self._click(browser, class_name="vi-button--primary")

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
    def _random_state():
        states = ['Washington', 'Utah', 'Arizona', 'California', 'Wisconsin', 'Maine', 'Nebraska', 'Minnesota',
                  'New York', 'Michigan', 'Connecticut', 'Delaware', 'Pennsylvania', 'Indiana', 'South Carolina', ]

        return random.choice(states)

    @staticmethod
    def _random_sleep():
        time.sleep(random.randint(1, 3))

    def _solve_screen_3(self, browser, mail, country):
        country_edit_xpath = '//*[@id="app"]/section/div[1]/section/div/div/section/div[5]/div/section/form/div[1]' \
                             '/div[1]/div[1]/label/div/span[2]'
        country_selector_xpath = '//*[@id="app"]/section/div[1]/section/div/div/section/div[5]/div/section/form/' \
                                 'div[1]/div[1]/div[1]/div/div/div[1]/span/span/i'
        country_field_xpath = '//*[@id="app"]/section/div[1]/section/div/div/section/div[5]/div/section/form/div[1]/' \
                              'div[1]/div[1]/div/div/div[1]/input'

        business_name_xpath = '//*[@id="app"]/section/div[1]/section/div/div/section/div[5]/div/section/form/div[1]/' \
                              'div[1]/div[2]/div/div/input'

        currency_selector_xpath = '//*[@id="app"]/section/div[1]/section/div/div/section/div[5]/div/section/form/' \
                                  'div[1]/div[1]/div[3]/div/div/div[1]/span/span/i'
        currency_field_xpath = '//*[@id="app"]/section/div[1]/section/div/div/section/div[5]/div/section/form/div[1]/' \
                               'div[1]/div[3]/div/div/div[1]/input'

        phone_xpath = '//*[@id="app"]/section/div[1]/section/div/div/section/div[5]/div/section/form/' \
                      'div[1]/div[2]/div[2]/div/div[1]/input'

        agreement_xpath = '//*[@id="form-item-vw"]/div[1]/div[2]/label/span/span'

        submit_button_xpath = '//*[@id="app"]/section/div[1]/section/div/div/section/div[5]/div/section/' \
                              'form/div[4]/div/button'

        default_currency = "USD"
        business_name = mail.split('@')[0]
        phone_number = self._random_phone_number()

        browser = self._click(browser, xpath=country_edit_xpath)
        browser = self._click(browser, xpath=country_selector_xpath)
        browser = self._send_keys(browser, country, xpath=country_field_xpath)
        browser = self._send_keys(browser, business_name, xpath=business_name_xpath)
        browser = self._send_keys(browser, phone_number, xpath=phone_xpath)
        browser = self._click(browser, xpath=agreement_xpath)
        browser = self._click(browser, xpath=currency_selector_xpath)
        browser = self._send_keys(browser, default_currency, xpath=currency_field_xpath)
        browser = self._click(browser, xpath=submit_button_xpath)

        return "OK", browser

    def _solve_screen_4(self, browser):
        company_name_xpath = '//*[@id="__layout"]/div/div/div[3]/div[2]/form/div[1]/div[1]/div[1]/div/div[1]/input'
        fullname_xpath = '//*[@id="__layout"]/div/div/div[3]/div[2]/form/div[1]/div[1]/div[2]/div/div[1]/input'
        email_xpath = '//*[@id="__layout"]/div/div/div[3]/div[2]/form/div[1]/div[1]/div[3]/div/div[1]/input'
        phone_xpath = '//*[@id="__layout"]/div/div/div[3]/div[2]/form/div[1]/div[1]/div[4]/div/div[1]/input'
        checkbox_xpath = '//*[@id="__layout"]/div/div/div[3]/div[2]/form/div[2]/div/div/label/span[1]/span'

        submit_button_xpath = '//*[@id="__layout"]/div/div/div[3]/div[2]/form/button'

        if len(browser.find_elements_by_xpath(fullname_xpath)) > 0 and \
                len(browser.find_elements_by_xpath(phone_xpath)) > 0:
            return "Bad proxy for registration", browser

        return "OK", browser

    def _solve_screen_5(self, browser, company_website, postal_code, street_address):
        company_website_xpath = '//*[@id="description"]/div/div[1]/textarea'

        industry_selector_xpath_1 = '//*[@id="first_industry"]/div/div/div[1]/span/span/i'

        industry_selector_xpath_2 = '//*[@id="second_industry"]/div/div/div[1]/span/span/i'

        street_address_xpath = '//*[@id="address_detail"]/div/div[1]/input'
        postal_code_xpath = '//*[@id="post_code"]/div/div[1]/input'
        state_selector_xpath = '//*[@id="state"]/div/div/div[1]/span/span/i'
        submit_button_xpath = '//*[@id="app"]/section/div[3]/section/div/div/section/div[2]/form/div[6]/button'

        account_xpath = '/html/body/header/div/div[2]/div/div[4]/div/div/div/div'
        account_info_xpath = '/html/body/header/div/div[2]/div/div[4]/div/div[2]/div/ul[1]/li[2]/a'

        browser = self._click(browser, xpath=account_xpath)
        browser = self._click(browser, xpath=account_info_xpath)
        browser.switch_to.alert.accept()
        time.sleep(15)
        browser = self._send_keys(browser, company_website, xpath=company_website_xpath)
        browser = self._click(browser, xpath=industry_selector_xpath_1)
        browser = self._click(browser, xpath=f'//*[@id="first_industry"]/div/div/div[2]/div[2]/div[1]/ul/li[{random.randint(1, 25)}]')
        browser = self._click(browser, xpath=industry_selector_xpath_2)
        browser = self._click(browser, xpath=f'//*[@id="second_industry"]/div/div/div[2]/div[2]/div[1]/ul/li[{random.randint(1, 5)}]')
        browser = self._send_keys(browser, street_address, xpath=street_address_xpath)
        browser = self._click(browser, xpath=state_selector_xpath)
        browser = self._click(browser, xpath=f'//*[@id="state"]/div/div/div[2]/div[2]/div[1]/ul/li[{random.randint(1, 50)}]')
        browser = self._click(browser, xpath=postal_code_xpath)
        browser = self._send_keys(browser, postal_code, xpath=postal_code_xpath)

        # detect payment type here

        browser = self._click(browser, xpath=submit_button_xpath)
        return "OK", browser

    def sign_up(self,
                mail,
                password,
                proxy,
                country,
                company_website,
                street_address,
                postal_code):
        payment_type = "-"

        browser = self._build_browser(proxy)
        browser.get("https://ads.tiktok.com/i18n/signup/")

        time.sleep(30)

        if self._detect_screen(browser) == 1:
            status, browser = self._solve_screen_1(browser, mail, password)

            if status != "OK":
                browser.close()
                return status
            time.sleep(15)

            status, browser = self._solve_screen_3(browser, mail, country)

            time.sleep(20)

            status, browser = self._solve_screen_5(browser, company_website, postal_code, street_address)
            payment_type = "Manual payment"

            time.sleep(15)
            browser.close()

            return status, payment_type

        elif self._detect_screen(browser) == 2:
            status, browser = self._solve_screen_2(browser, country)
            status, browser = self._solve_screen_4(browser)

            browser.close()
            return status, payment_type
