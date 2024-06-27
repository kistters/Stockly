# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse
from selenium import webdriver


class CaptchaRequired(Exception):
    pass


class SeleniumMiddleware:
    MAX_RETRIES = 3
    datadome_hashes = []

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=chrome_options)

    def __del__(self):
        self.driver.quit()

    @classmethod
    def from_crawler(cls, crawler):
        middleware_class = cls()
        crawler.signals.connect(middleware_class.spider_opened, signal=signals.spider_opened)

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
                raise CaptchaRequired(f"CAPTCHA required to {request.url}")

    def process_request(self, request, spider):
        if 'selenium' not in request.meta:
            return

        for _ in range(self.MAX_RETRIES):

            try:
                self.driver.get(request.url)
                page_source = self.driver.page_source
                self.detect_captcha(page_source, request, spider)
                return HtmlResponse(self.driver.current_url, body=page_source, encoding='utf-8', request=request)

            except CaptchaRequired as e:
                captcha_cookie = self.driver.get_cookie('datadome')  # can be extended to spider
                captcha_cookie['value'] = self.datadome_hashes.pop()
                self.driver.add_cookie(captcha_cookie)

            except Exception as e:
                spider.logger.exception(e)

        raise IgnoreRequest(f"Max retries reached for {request.url}")

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        spider.logger.critical(f"{spider} - {exception}")
        return None

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)