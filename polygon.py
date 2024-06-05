from time import sleep

import requests

from utils import get_env


class PolygonAPI:
    API_ENDPOINT = "https://api.polygon.io/v1"
    MAX_RETRIES = 3
    headers = {}

    def __init__(self):
        self.api_key = get_env('POLYGON_API_KEY')
        self._append_authorization_header()

    def _append_authorization_header(self):
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})

    def get_stock_data(self, stock_ticker, date):
        url = f'{self.API_ENDPOINT}/open-close/{stock_ticker}/{date}'

        for attempt in range(self.MAX_RETRIES):
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()

            if response.status_code in [500, 502, 503, 504]:
                sleep(1)
                continue


if __name__ == '__main__':
    polygon_api = PolygonAPI()
    stock_data = polygon_api.get_stock_data('AAPL', '2023-04-20') # market open
    print(stock_data)
    stock_data = polygon_api.get_stock_data('AAPL', '2023-01-01')  # holiday
    print(stock_data)
