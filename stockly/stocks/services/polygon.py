from time import sleep
from datetime import date
import requests
from django.conf import settings


class PolygonAPI:
    API_ENDPOINT = "https://api.polygon.io/v1"
    MAX_RETRIES = 3
    headers = {}

    def __init__(self):
        self.api_key = settings.POLYGON_API_KEY
        self._append_authorization_header()

    def _append_authorization_header(self):
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})

    def get_stock_data(self, stock_ticker, date):
        url = f'{self.API_ENDPOINT}/open-close/{stock_ticker}/{date}'
        for attempt in range(self.MAX_RETRIES):
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()

            if response.status_code in [404]:
                raise Exception(f"Not found data for {stock_ticker}. This could be due to an unknown ticker, "
                                f"a holiday, or a weekend.")

            if response.status_code in [403, 429]:
                sleep(5)
                continue

            if response.status_code in [500, 502, 503, 504]:
                sleep(1)
                continue

            raise Exception(f"Failed to fetch data for {stock_ticker} - status code: {response.status_code} "
                            f"- message: {response.json()}")


if __name__ == '__main__':
    import argparse

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
        ('AAPL', '2223-04-55'),  # day doesn't exist
    ] if not args.stock_ticker else [(args.stock_ticker, args.date)]

    for ticker, date in stock_checks:
        try:
            stock_data = polygon_api.get_stock_data(ticker, date)
            print(f"Success: {stock_data}")
        except Exception as e:
            print(f"Fail: {e}")