# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import threading

from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common import TimeoutException

logger = logging.getLogger(__name__)
thread_local = threading.local()


class SeleniumMiddleware:
    MAX_RETRIES = 3
    datadome_hashes = []

    def __init__(self, selenium_grid_endpoint=None):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--window-size=1240,980")
        chrome_options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
            "excludeSwitches": ["disable-popup-blocking"],
        })

        if selenium_grid_endpoint:
            self.driver = webdriver.Remote(command_executor=selenium_grid_endpoint, options=chrome_options)
        else:
            self.driver = webdriver.Chrome(options=chrome_options)

    def __del__(self):
        self.driver.quit()

    @classmethod
    def from_crawler(cls, crawler):
        middleware_class = cls(selenium_grid_endpoint=crawler.settings.get('SELENIUM_GRID_ENDPOINT'))
        crawler.signals.connect(middleware_class.spider_opened, signal=signals.spider_opened)
        logger.info(f'selenium.start', extra=dict(crawler))
        try:
            file_path = crawler.settings.get('CAPTCHA_DATADOME_HASHES_FILE_PATH')
            with open(file_path, 'r') as file:
                middleware_class.datadome_hashes = [line.strip() for line in file if line.strip()]
        except Exception as e:
            print(f"An error occurred: {e}")

        return middleware_class

    def detect_captcha(self, page_source, request, spider):
        """ in the future we can detect_captcha define in the Spider the too :) """
        captcha_list = ['geo.captcha-delivery.com', 'ct.captcha-delivery.com']
        for captcha in captcha_list:
            if captcha in page_source:
                return True

    def process_request(self, request, spider):
        if 'selenium' not in request.meta:
            return

        logger.info(f'selenium.start', extra=dict(request))

        for _ in range(self.MAX_RETRIES):

            self.driver.set_page_load_timeout(1)
            try:
                self.driver.get(request.url)
            except TimeoutException:
                pass

            page_source = self.driver.page_source

            if self.detect_captcha(page_source, request, spider):
                captcha_cookie = self.driver.get_cookie('datadome')  # can be extended to spider
                captcha_cookie['value'] = self.datadome_hashes.pop()
                self.driver.add_cookie(captcha_cookie)
                continue

            return HtmlResponse(self.driver.current_url, body=page_source, encoding='utf-8', request=request)

        raise IgnoreRequest(f"Max retries reached for {request.url}")

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        spider.logger.critical(f"{spider} - {exception}")
        return None

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
