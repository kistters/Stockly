import logging
from datetime import date
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class PolygonAPI:
    API_ENDPOINT = "https://api.polygon.io/v1"
    MAX_RETRIES = 3
    headers = {}

    def __init__(self):
        self.headers.update({
            'Authorization': f'Bearer {settings.POLYGON_API_KEY}'
        })

    def _call(self, method, url, attempt=0):
        try:
            response = getattr(requests, method)(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as ex:

            if ex.response.status_code in [403]:
                logger.critical(f'polygonapi.{method}.fail', extra={
                    'url': url,
                    'error': ex.response.json()
                })
                return {}

            if attempt > self.MAX_RETRIES:
                return {}

            return self._call(method, url, attempt=attempt + 1)

    def get_stock_data(self, stock_ticker, target_date: date = None) -> dict:
        url = f'{self.API_ENDPOINT}/open-close/{stock_ticker}/{target_date:%Y-%m-%d}'
        logger.info('polygonapi.call.start', extra={
            'stock_ticker': stock_ticker,
            'url': url,
        })

        response_json = self._call('get', url)

        logger.info('polygonapi.get.success', extra={
            'stock_ticker': stock_ticker,
            'url': url,
            'response': response_json,
        })

        filtered_dict = {
            key: value for key, value in response_json.items()
            if key in ['open', 'high', 'low', 'close']
        }

        return filtered_dict
