import logging

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from django.conf import settings

logger = logging.getLogger(__name__)


class GoogleScraper:
    G_FINANCE_BASE_URL = "https://www.google.com/finance/quote/{}:NASDAQ"
    G_SEARCH_BASE_URL = "https://www.google.com/search?q={}"
    driver = None

    def __init__(self):
        self.driver = webdriver.Remote(
            command_executor=settings.SELENIUM_GRID_ENDPOINT,
            options=webdriver.FirefoxOptions()
        )

    def get_stock_data(self, stock_ticker) -> dict:
        url = self.G_FINANCE_BASE_URL.format(stock_ticker)
        log_extra = {
            'stock_ticker': stock_ticker,
            'google_finance_url': url,
        }
        try:
            logger.info('googlefinance.scraper', extra={**log_extra})
            self.driver.get(url)

            ticker_name_element = self.driver.find_element(By.CSS_SELECTOR, 'div.zzDege')
            summary_box = self.driver.find_elements(By.CSS_SELECTOR, 'div.gyFHrc')
            summary_box_dict = {
                el.find_element(By.CSS_SELECTOR, 'div.mfs7Fc').text: el.find_element(By.CSS_SELECTOR, 'div.P6K39c').text
                for el in summary_box
            }

        except NoSuchElementException as ex:
            logger.exception('googlefinance.scraper.fail', extra={
                **log_extra,
                'exception': str(ex)
            })
            return {}
        except Exception as ex:
            logger.exception('googlefinance.scraper.fail.unexpected', extra={
                **log_extra,
                'exception': str(ex)
            })
            return {}

        map_desired_fields = {
            'PREVIOUS CLOSE': 'previous_close',
            'MARKET CAP': 'market_cap',
            'AVG VOLUME': 'avg_volume',
            'CEO': 'ceo',
            'HEADQUARTERS': 'headquarters'
        }

        filtered_and_renamed_dict = {
            map_desired_fields[key]: summary_box_dict[key]
            for key in map_desired_fields if key in summary_box_dict
        }

        stock_data_parsed = {
            'company_code': stock_ticker,
            'company_name': ticker_name_element.text,
            **filtered_and_renamed_dict,
        }

        logger.info('googlefinance.scraper.success', extra={
            **log_extra,
            'data_parsed': stock_data_parsed,
        })

        return stock_data_parsed

    def get_stock_values(self, stock_ticker) -> dict:
        url = self.G_SEARCH_BASE_URL.format(stock_ticker)
        log_extra = {
            'stock_ticker': stock_ticker,
            'google_search_url': url,
        }

        try:
            logger.info('googlesearch.scraper', extra={**log_extra})
            self.driver.get(url)

            stock_keys = [elm.text for elm in self.driver.find_elements(By.CSS_SELECTOR, 'td.JgXcPd')]
            stock_values = [elm.text for elm in self.driver.find_elements(By.CSS_SELECTOR, 'td.iyjjgb')]
            stock_data_dict = dict(zip(stock_keys, stock_values))

        except NoSuchElementException as ex:
            logger.exception('googlesearch.scraper.fail', extra={
                **log_extra,
                'exception': str(ex),
                'internal': f"Not found data on GoogleSearch"
            })
            return {}

        except Exception as ex:
            logger.exception('googlesearch.scraper.fail.unexpected', extra={
                **log_extra,
                'exception': str(ex)
            })
            return {}

        map_desired_fields = {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            '52-wk high': '52_week_high',
            '52-wk low': '52_week_low',
        }

        filtered_and_renamed_dict = {
            map_desired_fields[key]: stock_data_dict[key]
            for key in map_desired_fields if key in stock_data_dict
        }

        return filtered_and_renamed_dict


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Fetch stock data from Polygon API.")
    parser.add_argument('--stock_ticker', type=str, help='The stock ticker symbol.', required=False)
    args = parser.parse_args()

    google_finance_scraper = GoogleScraper()
    stock_checks = ["AAPL", "AMZN", "GOOGL", "DASD"] if not args.stock_ticker else [args.stock_ticker]
    for ticker in stock_checks:
        try:
            stock_data = google_finance_scraper.get_stock_data(ticker)
            print(f"Success: {stock_data}")
        except Exception as e:
            print(f"Fail: {e}")
