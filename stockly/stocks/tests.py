import json

from django.test import TestCase, Client
from django.urls import reverse


class StockTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_get_stock(self):
        response = self.client.get(reverse('stock-detail', kwargs={'stock_symbol': 'AAPL'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'symbol': 'AAPL',
        })

    def test_post_add_stock_amount(self):
        response = self.client.post(
            reverse('stock-detail', kwargs={'stock_symbol': 'AAPL'}),
            data=json.dumps({'amount': 5.33}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message': '5.33 units of stock AAPL were added to your stock record',
            'status': 201,
        })

    def test_post_invalid_data(self):
        response = self.client.post(
            reverse('stock-detail', kwargs={'stock_symbol': 'AAPL'}),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Amount is required'})
