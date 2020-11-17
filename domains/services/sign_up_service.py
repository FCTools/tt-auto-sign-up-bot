from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions

from domains.services.singleton import Singleton


class SignUpService(metaclass=Singleton):
    def __init__(self):
        pass

    def _build_browser(self, proxy, user_agent):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument(f"--proxy-server=socks5://{proxy}")
        chrome_options.add_argument(f"user-agent={user_agent}")

        return webdriver.Chrome(options=chrome_options)

    def sign_up(self,
                mail,
                password,
                proxy,
                user_agent,
                country,
                company_website,
                street_address,
                postal_code,
                tax_id):
        browser = self._build_browser(proxy, user_agent)


