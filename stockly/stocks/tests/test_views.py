import json
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from stockly.stocks.services import PolygonAPI
from stockly.stocks.tests.utils import load_file, load_json


@mock.patch.object(PolygonAPI, '_call', new_callable=lambda: mock.Mock(return_value=load_json('polygon.AMZN.json')))
@mock.patch('stockly.stocks.services.fetch_stock_data_from_marketwatch',
            new_callable=lambda: mock.Mock(return_value=load_file('marketwatch.AMZN.html')))
class StockTests(TestCase):

    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_get_stock(self, marketwatch_mock_fetch, polygon_mock_call):
        response = self.client.get(reverse('stock-detail', kwargs={'stock_ticker': 'AAPL'}))
        self.assertEqual(response.status_code, 200)
        expected = load_json('get.AMZN.not.purchased.json')
        self.assertEqual(response.json(), expected)

    def test_post_add_stock_amount(self, marketwatch_mock_fetch, polygon_mock_call):
        response = self.client.post(
            reverse('stock-detail', kwargs={'stock_ticker': 'AMZN'}),
            data=json.dumps({'amount': 5.33}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message': '5.33 units of stock AMZN were added to your stock record.'
        })

    def test_get_stock_after_post_add_stock_amount(self, marketwatch_mock_fetch, polygon_mock_call):
        response = self.client.post(
            reverse('stock-detail', kwargs={'stock_ticker': 'AMZN'}),
            data=json.dumps({'amount': 5.33}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.get(reverse('stock-detail', kwargs={'stock_ticker': 'AMZN'}))
        self.assertEqual(response.status_code, 200)
        expected = load_json('get.AMZN.with.purchase.json')
        self.assertEqual(response.json(), expected)

    def test_post_invalid_data(self, marketwatch_mock_fetch, polygon_mock_call):
        response = self.client.post(
            reverse('stock-detail', kwargs={'stock_ticker': 'AMZN'}),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'errors': {'amount': ['This field is required.']}})
