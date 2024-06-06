from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

import polygon


class GoogleFinanceScraper:
    BASE_URL = "https://www.google.com/finance/quote/{}:NASDAQ"
    driver = None

    def __init__(self):
        self.driver = webdriver.Remote(
            command_executor="http://127.0.0.1:4444",
            options=webdriver.FirefoxOptions()
        )

    def get_stock_data(self, stock_ticker):
        url = self.BASE_URL.format(stock_ticker)
        try:
            self.driver.get(url)

            ticker_name_element = self.driver.find_element(By.CSS_SELECTOR, 'div.zzDege')
            summary_box = self.driver.find_elements(By.CSS_SELECTOR, 'div.gyFHrc')
            summary_box_dict = {
                el.find_element(By.CSS_SELECTOR, 'div.mfs7Fc').text: el.find_element(By.CSS_SELECTOR, 'div.P6K39c').text
                for el in summary_box
            }

        except NoSuchElementException:
            raise Exception(f"Not found data for ticker {stock_ticker} on GoogleFinance")

        except Exception as ex:
            raise Exception(f"Unexpected Error for ticker: {stock_ticker} - message {ex}")

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

        return {
            'company_code': stock_ticker,
            'company_name': ticker_name_element.text,
            **filtered_and_renamed_dict,
        }


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Fetch stock data from Polygon API.")
    parser.add_argument('--stock_ticker', type=str, help='The stock ticker symbol.', required=False)
    args = parser.parse_args()

    google_finance_scraper = GoogleFinanceScraper()
    stock_checks = ["AAPL", "AMZN", "GOOGL", "DASD"] if not args.stock_ticker else [args.stock_ticker]
    for ticker in stock_checks:
        try:
            stock_data = google_finance_scraper.get_stock_data(ticker)
            print(f"Success: {stock_data}")
        except Exception as e:
            print(f"Fail: {e}")
