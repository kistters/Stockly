import logging
from django.test import TestCase, override_settings

from backoffice.stocks.models import Stock
from backoffice.stocks.tasks import process_stock_detail_from_crawler

logger = logging.getLogger(__name__)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class ProcessStockDetailFromCrawlerTest(TestCase):

    def setUp(self):
        self.stock_detail = {
            'stock_ticker': 'AMZN',
            'company_name': 'Amazon.com Inc.',
            'performance_data': {
                'five_days': '4.45%',
                'one_month': '-1.70%',
                'three_months': '5.10%',
                'year_to_date': '21.30%',
                'one_year': '49.32%'
            },
            'competitors': [
                {'name': 'AAPL', 'stock_ticker': 'Apple Inc.', 'market_cap': {'value': '2.98T', 'currency': '$'}},
                {'name': 'MSFT', 'stock_ticker': 'Microsoft Corp.', 'market_cap': {'value': '3.16T', 'currency': '$'}},
                {'name': 'GOOG', 'stock_ticker': 'Alphabet Inc. Cl C', 'market_cap': {'value': '2.19T', 'currency': '$'}},
                {'name': 'GOOGL', 'stock_ticker': 'Alphabet Inc. Cl A', 'market_cap': {'value': '2.19T', 'currency': '$'}},
                {'name': 'META', 'stock_ticker': 'Meta Platforms Inc.', 'market_cap': {'value': '1.25T', 'currency': '$'}},
                {'name': 'WMT', 'stock_ticker': 'Walmart Inc.', 'market_cap': {'value': '541.22B', 'currency': '$'}},
                {'name': 'NFLX', 'stock_ticker': 'Netflix Inc.', 'market_cap': {'value': '279.49B', 'currency': '$'}},
                {'name': 'DIS', 'stock_ticker': 'Walt Disney Co.', 'market_cap': {'value': '184.51B', 'currency': '$'}},
                {'name': 'COST', 'stock_ticker': 'Costco Wholesale Corp.', 'market_cap': {'value': '373.71B', 'currency': '$'}},
                {'name': 'CVS', 'stock_ticker': 'CVS Health Corp.', 'market_cap': {'value': '76.5B', 'currency': '$'}}
            ]
        }

    def test_process_stock_detail_create(self):
        self.assertEqual(Stock.objects.count(), 0)

        result = process_stock_detail_from_crawler(self.stock_detail)

        self.assertEqual(Stock.objects.count(), 1)
        stock = Stock.objects.get(ticker='AMZN')
        self.assertEqual(stock.json_data, self.stock_detail)
        self.assertEqual(result, self.stock_detail)

    def test_process_stock_detail_update(self):
        Stock.objects.create(ticker='AMZN', json_data={'stock_ticker': 'AMZN', 'expired': True})

        self.assertEqual(Stock.objects.count(), 1)

        result = process_stock_detail_from_crawler(self.stock_detail)

        self.assertEqual(Stock.objects.count(), 1)
        stock = Stock.objects.get(ticker='AMZN')
        self.assertEqual(stock.json_data, self.stock_detail)
        self.assertEqual(result, self.stock_detail)


    def test_process_stock_detail_update(self):
        Stock.objects.create(ticker='AMZN', json_data={'stock_ticker': 'AMZN', 'expired': True})

        self.assertEqual(Stock.objects.count(), 1)

        result = process_stock_detail_from_crawler(self.stock_detail)

        self.assertEqual(Stock.objects.count(), 1)
        stock = Stock.objects.get(ticker='AMZN')
        self.assertEqual(stock.json_data, self.stock_detail)
        self.assertEqual(result, self.stock_detail)