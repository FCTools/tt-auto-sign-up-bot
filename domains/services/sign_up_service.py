"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""
import random
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from domains.services.mail_service import MailService
from domains.services.singleton import Singleton


class SignUpService(metaclass=Singleton):
    def __init__(self):
        self._user_agent_rotator = UserAgent(operating_systems=[OperatingSystem.WINDOWS.value,
                                                                OperatingSystem.MAC_OS_X.value,
                                                                OperatingSystem.LINUX.value],
                                             software_names=[SoftwareName.CHROME.value], limit=100)
        self._mail_service = MailService()

    def _random_user_agent(self):
        return self._user_agent_rotator.get_random_user_agent()

    def _build_browser(self, proxy):
        proxy_parts = proxy.split(":")
        ip = proxy_parts[0]
        port = proxy_parts[1]
        user = proxy_parts[2]
        password = proxy_parts[3]
        proxy_string = f'{ip}:{port}'
        user_agent = self._random_user_agent()
        print(user_agent)
        # service_args = [f"--proxy={ip}:{port}", '--proxy-type=socks5', f"--proxy-auth={user}:{password}"]

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument(f"--proxy-server={proxy_string}")
        chrome_options.add_argument(f"user-agent={user_agent}")

        return webdriver.Chrome(options=chrome_options)

    @staticmethod
    def _detect_screen(browser):
        # email_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[1]/div[2]/div/div/label'
        # if len(browser.find_elements_by_xpath(email_xpath)) > 0:
        #     return 1
        # return 2
        label_xpath = '//*[@id="app"]/section/div[1]/section/div/div/section/div[5]/div/div[2]/div[2]/form/div[1]/label'
        if len(browser.find_elements_by_xpath(label_xpath)) > 0:
            element = browser.find_element_by_xpath(label_xpath)

            if element and element.text == 'Your Billing Country/Region':
                return 2

        return 1

    def _solve_screen_1(self, browser, mail, password):
        login_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[1]/div[2]/div/div/div/input'
        agreement_checkbox_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[5]/div[1]/div'
        submit_button_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[7]/div/button[2]'
        verification_code_xpath_button = '//*[@id="TikTokAds_Register-account-center-code-btn"]'
        verification_code_field_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[4]/div/div/div[1]/input'

        self._random_sleep()
        browser.find_element_by_xpath(login_xpath).send_keys(mail)
        self._random_sleep()
        browser.find_element_by_name("password").send_keys(password)
        self._random_sleep()
        browser.find_element_by_name("repeatPwd").send_keys(password)
        self._random_sleep()
        browser.find_element_by_xpath(agreement_checkbox_xpath).click()
        self._random_sleep()
        browser.find_element_by_xpath(verification_code_xpath_button).click()
        self._random_sleep()

        error_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[6]/div'
        if len(browser.find_elements_by_xpath(error_xpath)) > 0 and \
           browser.find_element_by_xpath(error_xpath).text == 'The email is already registered. Please log in.':
            return "Email is already registered.", browser

        # time.sleep(120)
        verification_code = self._mail_service.find_verification_code(mail, password)
        browser.find_element_by_xpath(verification_code_field_xpath).send_keys(verification_code)
        self._random_sleep()
        browser.find_element_by_xpath(submit_button_xpath).click()

        return "OK", browser

    def _solve_screen_2(self, browser, country):
        self._random_sleep()
        browser.find_element_by_class_name("vi-input__inner").click()
        self._random_sleep()
        browser.find_element_by_class_name("vi-input__inner").send_keys(country)
        self._random_sleep()
        browser.find_element_by_class_name("vi-button--primary").click()

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
        time.sleep(random.randint(1, 5))

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

        business_name = mail.split('@')[0]
        phone_number = self._random_phone_number()

        self._random_sleep()
        browser.find_element_by_xpath(country_edit_xpath).click()
        self._random_sleep()
        browser.find_element_by_xpath(country_selector_xpath).click()
        self._random_sleep()
        browser.find_element_by_xpath(country_field_xpath).send_keys(country)
        time.sleep(5)
        browser.find_element_by_xpath(business_name_xpath).send_keys(business_name)
        self._random_sleep()
        browser.find_element_by_xpath(phone_xpath).send_keys(phone_number)
        self._random_sleep()
        browser.find_element_by_xpath(agreement_xpath).click()
        self._random_sleep()
        browser.find_element_by_xpath(currency_selector_xpath).click()
        self._random_sleep()
        browser.find_element_by_xpath(currency_field_xpath).send_keys("USD")
        self._random_sleep()
        browser.find_element_by_xpath(submit_button_xpath).click()

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
        industry_field_xpath_1 = '//*[@id="first_industry"]/div/div/div[1]/input'

        industry_selector_xpath_2 = '//*[@id="second_industry"]/div/div/div[1]/span/span/i'
        industry_field_xpath_2 = '//*[@id="second_industry"]/div/div/div[1]/input'

        street_address_xpath = '//*[@id="address_detail"]/div/div[1]/input'
        postal_code_xpath = '//*[@id="post_code"]/div/div[1]/input'
        state_selector_xpath = '//*[@id="state"]/div/div/div[1]/span/span/i'
        state_field_xpath = '//*[@id="state"]/div/div/div[1]/input'
        submit_button_xpath = '//*[@id="app"]/section/div[3]/section/div/div/section/div[2]/form/div[6]/button'

        account_xpath = '/html/body/header/div/div[2]/div/div[4]/div/div/div/div'
        account_info_xpath = '/html/body/header/div/div[2]/div/div[4]/div/div[2]/div/ul[1]/li[2]/a'

        self._random_sleep()
        browser.find_element_by_xpath(account_xpath).click()
        self._random_sleep()
        browser.find_element_by_xpath(account_info_xpath).click()
        self._random_sleep()
        browser.switch_to.alert.accept()
        self._random_sleep()
        browser.find_element_by_xpath(company_website_xpath).send_keys(company_website)
        self._random_sleep()
        browser.find_element_by_xpath(industry_selector_xpath_1).click()
        self._random_sleep()
        browser.find_element_by_xpath(f'//*[@id="first_industry"]/div/div/div[2]/div[2]/div[1]/ul/li[{random.randint(1, 25)}]').click()
        self._random_sleep()
        browser.find_element_by_xpath(industry_selector_xpath_2).click()
        self._random_sleep()
        browser.find_element_by_xpath(f'//*[@id="second_industry"]/div/div/div[2]/div[2]/div[1]/ul/li[{random.randint(1, 5)}]').click()
        self._random_sleep()
        browser.find_element_by_xpath(street_address_xpath).send_keys(street_address)
        self._random_sleep()
        browser.find_element_by_xpath(state_selector_xpath).click()
        self._random_sleep()
        # browser.find_element_by_xpath(state_field_xpath).send_keys(self._random_state())
        # self._random_sleep()
        browser.find_element_by_xpath(f'//*[@id="state"]/div/div/div[2]/div[2]/div[1]/ul/li[{random.randint(1, 50)}]').click()
        self._random_sleep()
        browser.find_element_by_xpath(postal_code_xpath).click()
        self._random_sleep()
        browser.find_element_by_xpath(postal_code_xpath).send_keys(postal_code)

        # detect payment type here
        self._random_sleep()
        browser.find_element_by_xpath(submit_button_xpath).click()

        return "OK", browser

    def sign_up(self,
                mail,
                password,
                proxy,
                country,
                company_website,
                street_address,
                postal_code):
        browser = self._build_browser(proxy)
        browser.get("https://ads.tiktok.com/i18n/signup/")

        time.sleep(15)

        if self._detect_screen(browser) == 1:
            status, browser = self._solve_screen_1(browser, mail, password)

            if status != "OK":
                browser.close()
                return status

            status, browser = self._solve_screen_3(browser, mail, country)
            status, browser = self._solve_screen_5(browser, company_website, postal_code, street_address)
            return status

        elif self._detect_screen(browser) == 2:
            status, browser = self._solve_screen_2(browser, country)
            status, browser = self._solve_screen_4(browser)

            browser.close()
            return status

        # check inbox here, put it to field and click submit button

        # browser.find_element_by_xpath(captcha_xpath).click()

        # browser.find_element_by_xpath(submit_button_xpath).click()


