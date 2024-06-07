import logging
from time import sleep
from datetime import date
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class PolygonAPI:
    API_ENDPOINT = "https://api.polygon.io/v1"
    MAX_RETRIES = 3
    headers = {}

    def __init__(self):
        self.api_key = settings.POLYGON_API_KEY
        self._append_authorization_header()

    def _append_authorization_header(self):
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})

    def get_stock_data(self, stock_ticker, check_date: date = None):
        date_formatted = f"{check_date:%Y-%m-%d}" if check_date else f"{date.today():%Y-%m-%d}"
        url = f'{self.API_ENDPOINT}/open-close/{stock_ticker}/{date_formatted}'

        log_extra = {
            'stock_ticker': stock_ticker,
            'date_formatted': date_formatted,
            'endpoint': url,
        }
        logger.info('polygonapi.call', extra={**log_extra})

        for attempt in range(self.MAX_RETRIES):
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()

            if response.status_code in [404]:
                logger.warning('polygonapi.404', extra={
                    **log_extra,
                    'internal': "This could be due to an unknown ticker a holiday, or a weekend"
                })
                return {}

            if response.status_code in [403, 429]:
                logger.warning('polygonapi.retry', extra={
                    **log_extra,
                    'response.status_code': response.status_code,
                    'response.message': response.json()
                })
                sleep(3)
                continue

            if response.status_code in [500, 502, 503, 504]:
                logger.warning('polygonapi.retry', extra={

                    'response.status_code': response.status_code,
                    'response.message': response.json()
                })
                sleep(1)
                continue

        logger.warning("polygonapi.fetch.error.max_retries", extra={
            **log_extra,
            'internal': f"max_retries of {self.MAX_RETRIES} and no data fetched."
        })

        return {}


if __name__ == '__main__':
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="Fetch stock data from Polygon API.")
    parser.add_argument('--stock_ticker', type=str, help='The stock ticker symbol.', required=False)
    parser.add_argument('--date', type=str, help='The date in YYYY-MM-DD format.', default=f"{date.today():%Y-%m-%d}")
    args = parser.parse_args()

    polygon_api = PolygonAPI()
    stock_checks = [
        ('AAPL', '2023-04-03'),  # market open
        ('AAPL', '2023-05-07'),  # Sunday
        ('AAPL', '2023-01-01'),  # holiday
        ('XYZA', '2223-04-03'),  # unknown ticker
    ] if not args.stock_ticker else [(args.stock_ticker, args.date)]

    for ticker, date_string in stock_checks:
        try:
            day = datetime.strptime(date_string, '%Y-%m-%d').date()
            stock_data = polygon_api.get_stock_data(ticker, day)
            print(f"Success: {stock_data}")
        except Exception as e:
            print(f"Fail: {e}")
