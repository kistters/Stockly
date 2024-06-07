import logging

from selenium import webdriver

from django.conf import settings
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class WebDriverManager:

    @staticmethod
    def new_session_driver():
        logger.info('driver.session.new')
        options = webdriver.FirefoxOptions()
        options.headless = True  # Enable headless mode for performance

        return webdriver.Remote(
            command_executor=settings.SELENIUM_GRID_ENDPOINT,
            options=options
        )

    def __enter__(self) -> WebDriver:
        self.driver = self.new_session_driver()
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        logger.info('driver.session.quit')
        self.driver.quit()
        if exc_type is not None:
            logger.exception('WebDriver encountered an exception', exc_info=(exc_type, exc_value, traceback))
