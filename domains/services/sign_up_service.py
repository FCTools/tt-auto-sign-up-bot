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

from domains.services.singleton import Singleton


class SignUpService(metaclass=Singleton):
    def __init__(self):
        self._user_agent_rotator = UserAgent(software_names=[OperatingSystem.WINDOWS.value,
                                                             OperatingSystem.MAC_OS_X.value,
                                                             OperatingSystem.LINUX.value],
                                             operating_systems=[SoftwareName.CHROME.value], limit=500)

    def _random_user_agent(self):
        return self._user_agent_rotator.get_random_user_agent()

    def _build_browser(self, proxy):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument(f"--proxy-server=socks5://{proxy}")
        chrome_options.add_argument(f"user-agent={self._random_user_agent()}")

        return webdriver.Chrome(options=chrome_options)

    def sign_up(self,
                mail,
                password,
                proxy,
                country,
                company_website,
                street_address,
                postal_code):
        browser = self._build_browser(proxy)

        login_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[1]/div[2]/div/div/div/input'
        agreement_checkbox_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[5]/div[1]/div'
        captcha_xpath = ''
        submit_button_xpath = '//*[@id="TikTokAds_Register"]/section/div[2]/main/form/div[7]/div/button[2]'
        verification_code_xpath = '//*[@id="TikTokAds_Register-account-center-code-btn"]'

        browser.get("https://ads.tiktok.com/i18n/signup/")
        time.sleep(5)
        browser.find_element_by_xpath(login_xpath).send_keys(mail)
        browser.find_element_by_name("password").send_keys(password)
        browser.find_element_by_name("repeatPws").send_keys(password)
        browser.find_element_by_xpath(agreement_checkbox_xpath).click()
        browser.find_element_by_xpath(verification_code_xpath).click()

        # check inbox here, put it to field and click submit button

        # browser.find_element_by_xpath(captcha_xpath).click()

        browser.find_element_by_xpath(submit_button_xpath).click()


