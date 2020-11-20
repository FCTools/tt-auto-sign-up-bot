"""
Copyright © 2020 FC Tools. All rights reserved.
Author: German Yakimov
"""

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

    def _detect_screen(self, browser):
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
        captcha_xpath = ''
        submit_button_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[7]/div/button[2]'
        verification_code_xpath_button = '//*[@id="TikTokAds_Register-account-center-code-btn"]'
        verification_code_field_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[4]/div/div/div[1]/input'

        time.sleep(5)
        browser.find_element_by_xpath(login_xpath).send_keys(mail)
        time.sleep(1)
        browser.find_element_by_name("password").send_keys(password)
        time.sleep(1)
        browser.find_element_by_name("repeatPwd").send_keys(password)
        time.sleep(1)
        browser.find_element_by_xpath(agreement_checkbox_xpath).click()
        time.sleep(2)
        browser.find_element_by_xpath(verification_code_xpath_button).click()

        # time.sleep(120)
        verification_code = self._mail_service.find_verification_code(mail, password)
        browser.find_element_by_xpath(verification_code_field_xpath).send_keys(verification_code)
        time.sleep(2)
        browser.find_element_by_xpath(submit_button_xpath).click()

        return "OK", browser

    def _solve_screen_2(self, browser, country):
        time.sleep(5)
        browser.find_element_by_class_name("vi-input__inner").click()
        browser.find_element_by_class_name("vi-input__inner").send_keys(country)
        time.sleep(1)
        browser.find_element_by_class_name("vi-button--primary").click()

        return "OK", browser

    def _solve_screen_3(self, browser):
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
        time.sleep(10)

        if self._detect_screen(browser) == 1:
            status, browser = self._solve_screen_1(browser, mail, password)
            status, browser = self._solve_screen_3(browser)
        elif self._detect_screen(browser) == 2:
            status, browser = self._solve_screen_2(browser, country)
            status, browser = self._solve_screen_4(browser)

            if status != "OK":
                browser.close()
                return status

        # check inbox here, put it to field and click submit button

        # browser.find_element_by_xpath(captcha_xpath).click()

        # browser.find_element_by_xpath(submit_button_xpath).click()


