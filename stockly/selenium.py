import json
import logging
import os

from selenium import webdriver
from fake_useragent import UserAgent

from django.conf import settings
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class WebDriverManager:
    domain = None

    @staticmethod
    def new_session_driver():
        logger.info('driver.session.new')
        user_agent = UserAgent()
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={user_agent.chrome}')
        options.add_argument("--window-size=1920,1080")

        return webdriver.Remote(
            command_executor=settings.SELENIUM_GRID_ENDPOINT,
            options=options
        )

    def _load_cookies(self):
        try:
            with open(self.json_cookies_file, 'r') as file:
                cookies = json.load(file)
                for cookie in cookies.get(self.domain, []):
                    self.driver.add_cookie(cookie)
        except FileNotFoundError:
            with open(self.json_cookies_file, 'w') as file:
                json.dump({self.domain: []}, file)

    def _save_cookies(self):
        with open(self.json_cookies_file, 'w') as file:
            json.dump({self.domain: self.driver.get_cookies()}, file, indent=2)

    def __init__(self, domain: str = None):
        self.json_cookies_file = settings.SELENIUM_COOKIES_FILE_JSON
        self.domain = domain

    def __enter__(self) -> WebDriver:
        self.driver = self.new_session_driver()

        if self.domain:
            self.driver.get('https://' + self.domain)
            self._load_cookies()

        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        logger.info('driver.session.quit')
        self._save_cookies()
        self.driver.quit()
        if exc_type is not None:
            logger.exception('WebDriver encountered an exception', exc_info=(exc_type, exc_value, traceback))
