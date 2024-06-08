from decimal import Decimal
from django.test import TestCase

from stockly.stocks.forms import StockRecordForm
from stockly.stocks.models import StockRecord


class StockRecordFormTest(TestCase):

    def setUp(self):
        self.stock = StockRecord.objects.create(stock='AAPL')

    def test_form_valid_data(self):
        form_data = {
            'stock': self.stock.id,
            'amount': '100.50'
        }
        form = StockRecordForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['amount'], Decimal('100.50'))

    def test_form_no_amount(self):
        form_data = {
            'stock': self.stock.id,
            # 'amount' is missing to test its requirement
        }
        form = StockRecordForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        self.assertEqual(form.errors['amount'], ['Amount is required'])

    def test_form_invalid_amount(self):
        form_data = {
            'stock': self.stock.id,
            'amount': 'invalid'
        }
        form = StockRecordForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        self.assertEqual(form.errors['amount'], ['Amount must be a numeric value'])
