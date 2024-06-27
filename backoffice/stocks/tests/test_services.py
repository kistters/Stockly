from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from backoffice.stocks.services import PolygonAPI, get_aggregate_stock_data
from backoffice.stocks.services.marketwatch import marketwatch_stock_parser
from backoffice.stocks.tests.utils import load_file, day, load_json


class TestMarketwatchStockParser(TestCase):

    def test_marketwatch_stock_parser_success(self):
        page_source = load_file('marketwatch.AMZN.html')
        parsed_data = marketwatch_stock_parser(page_source)
        expected = load_json('marketwatch.AMZN.parsed.json')
        self.assertEqual(parsed_data, expected)


class PolygonTestCase(TestCase):

    def setUp(self):
        self.polygon_api = PolygonAPI()

    @mock.patch.object(PolygonAPI, '_call')
    def test_get_stock_data_success(self, mock_call):
        mock_call.return_value = load_json('polygon.AMZN.json')
        result = self.polygon_api.get_stock_data(stock_ticker="AMZN", target_date=day('2024-06-08'))
        expected = {
            'close': 185.12,
            'high': 186.2,
            'low': 182.3,
            'open': 184.66
        }
        self.assertEqual(result, expected)


@mock.patch.object(PolygonAPI, '_call', new_callable=lambda: mock.Mock(return_value=load_json('polygon.AMZN.json')))
@mock.patch('backoffice.stocks.services.fetch_stock_data_from_marketwatch',
            new_callable=lambda: mock.Mock(return_value=load_file('marketwatch.AMZN.html')))
class ServicesStockTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def test_get_aggregate_stock_data_ok(self, marketwatch_mock_fetch, polygon_mock_call):
        result = get_aggregate_stock_data(stock_ticker="AMZN")
        expected = load_json('aggregate.AMZN.json')
        self.assertEqual(result, expected)

    def test_get_aggregate_stock_data_cache(self, marketwatch_mock_fetch, polygon_mock_call):
        get_aggregate_stock_data(stock_ticker="AMZN")
        expected = load_json('aggregate.AMZN.json')
        stock_cached_data = cache.get(f"AMZN:{timezone.now():%Y-%m-%d}")
        self.assertEqual(stock_cached_data, expected)
