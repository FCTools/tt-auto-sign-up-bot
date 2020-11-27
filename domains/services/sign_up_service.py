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
        # user = proxy_parts[2]
        # password = proxy_parts[3]
        proxy_string = f'{ip}:{port}'
        user_agent = self._random_user_agent()
        print(user_agent)

        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument(f"--proxy-server={proxy_string}")
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.add_argument("headless")

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
        screen_elements = self._screens['screens_elements']['screen_1']

        browser = self._send_keys(browser, mail, xpath=screen_elements['login_xpath'])
        print("Fill login field.")
        browser = self._send_keys(browser, password, xpath=screen_elements['password_xpath'])
        print("Fill password field.")
        browser = self._send_keys(browser, password, xpath=screen_elements['repeat_password_xpath'])
        print("Fill repeat password field.")
        browser = self._click(browser, xpath=screen_elements['agreement_checkbox_xpath'])
        print("Click agreement checkbox.")
        browser = self._click(browser, xpath=screen_elements['verification_code_xpath_button'])
        print("Click verification code button.")

        if len(browser.find_elements_by_xpath(screen_elements['email_already_used_error_xpath'])) > 0 \
                and browser.find_element_by_xpath(screen_elements['email_already_used_error_xpath']).text == \
                'The email is already registered. Please log in.':
            print("This email is already registered.")
            return "Email is already registered.", browser

        time.sleep(20)
        verification_code = self._mail_service.find_verification_code(mail, password)
        print(f"Get verification code: {verification_code}")

        browser = self._send_keys(browser, verification_code, xpath=screen_elements['verification_code_field_xpath'])
        print("Fill verification code.")
        browser = self._click(browser, xpath=screen_elements['submit_button_xpath'])
        print("Click submit button.")

        return "OK", browser

    def _solve_screen_2(self, browser, country):
        screen_elements = self._screens['screens_elements']['screen_2']

        browser = self._click(browser, class_name=screen_elements['country_selector_class_name'])
        print("Click country selector.")
        browser = self._send_keys(browser, country, class_name=screen_elements['country_field_class_name'])
        print("Field country.")
        browser = self._click(browser, class_name=screen_elements['submit_button_class_name'])
        print("Click submit button on screen 2.")

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
        screen_elements = self._screens['screens_elements']['screen_3']

        default_currency = "USD"
        business_name = mail.split('@')[0]
        phone_number = self._random_phone_number()

        browser = self._click(browser, xpath=screen_elements['country_edit_xpath'])
        print("Click country edit button.")
        browser = self._click(browser, xpath=screen_elements['country_selector_xpath'])
        print("Click country selector.")
        browser = self._send_keys(browser, country, xpath=screen_elements['country_field_xpath'])
        print("Select country.")
        browser = self._send_keys(browser, business_name, xpath=screen_elements['business_name_xpath'])
        print("Fill business name.")
        browser = self._send_keys(browser, phone_number, xpath=screen_elements['phone_number_xpath'])
        print("Fill phone number.")
        browser = self._click(browser, xpath=screen_elements['agreement_checkbox_xpath'])
        print("Click agreement checkbox.")
        browser = self._click(browser, xpath=screen_elements['currency_selector_xpath'])
        print("Click currency selector.")
        browser = self._send_keys(browser, default_currency, xpath=screen_elements['currency_field_xpath'])
        print("Fill currency field.")
        browser = self._click(browser, xpath=screen_elements['submit_button_xpath'])
        print("Click submit button.")

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
        screen_elements = self._screens['screens_elements']['screen_5']

        browser = self._click(browser, xpath=screen_elements['account_xpath'])
        print("Click account button.")
        browser = self._click(browser, xpath=screen_elements['account_info_xpath'])
        print("Click account info button.")
        browser.switch_to.alert.accept()
        time.sleep(15)
        print("Accept browser alert.")
        browser = self._send_keys(browser, company_website, xpath=screen_elements['company_website_xpath'])
        print("Fill company website.")
        browser = self._click(browser, xpath=screen_elements['industry_selector_xpath_1'])
        print("Click industry selector 1.")
        browser = self._click(browser,
                              xpath=screen_elements['industry_selector_xpath_1_list'].format(random.randint(1, 25)))
        print("Select random industry 1.")
        browser = self._click(browser, xpath=screen_elements['industry_selector_xpath_2'])
        print("Click industry selector 2.")
        browser = self._click(browser,
                              xpath=screen_elements['industry_selector_xpath_2_list'].format(random.randint(1, 5)))
        print("Select random industry 2.")
        browser = self._send_keys(browser, street_address, xpath=screen_elements['street_address_xpath'])
        print("Fill street address.")
        browser = self._click(browser, xpath=screen_elements['state_selector_xpath'])
        print("Click state selector.")
        browser = self._click(browser, xpath=screen_elements['states_list_xpath'].format(random.randint(1, 50)))
        print("Select random state.")
        browser = self._click(browser, xpath=screen_elements['postal_code_xpath'])
        print("Click postal code field.")
        browser = self._send_keys(browser, postal_code, xpath=screen_elements['postal_code_xpath'])
        print("Fill postal code.")

        # detect payment type here

        browser = self._click(browser, xpath=screen_elements['submit_button_xpath'])
        print("Click submit button.")

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

        if not self._mail_service.correct_credentials(mail, password):
            print("Incorrect email credentials.")
            return "Invalid password for email", payment_type
        print("Email credentials are correct.")

        browser = self._build_browser(proxy)
        print("Successfully build browser.")
        browser.get("https://ads.tiktok.com/i18n/signup/")
        print("Get start page.")

        time.sleep(30)

        if self._detect_screen(browser) == 1:
            print("Screen 1 was detected. Start registration branch 1.")
            status, browser = self._solve_screen_1(browser, mail, password)
            print("Solve screen 1.")

            if status != "OK":
                print(f"Incorrect status: {status}")
                browser.close()
                return status
            time.sleep(15)

            print("Start screen 3 solving...")
            status, browser = self._solve_screen_3(browser, mail, country)
            print("Solved screen 3.")

            time.sleep(20)

            print("Start screen 5 solving...")
            status, browser = self._solve_screen_5(browser, company_website, postal_code, street_address)
            print(f"Solved screen 5, status: {status}, payment type: {payment_type}")
            payment_type = "Manual payment"

            time.sleep(15)
            browser.close()

            return status, payment_type

        elif self._detect_screen(browser) == 2:
            print("Detect screen 2. Start registration branch 2.")
            status, browser = self._solve_screen_2(browser, country)
            status, browser = self._solve_screen_4(browser)

            browser.close()
            return status, payment_type
