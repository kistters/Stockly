from decimal import Decimal, InvalidOperation

from django import forms
from .models import StockRecord


class StockRecordForm(forms.ModelForm):
    class Meta:
        model = StockRecord
        fields = ['stock', 'amount']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise forms.ValidationError('Amount is required')

        try:
            amount = Decimal(amount)
        except InvalidOperation:
            raise forms.ValidationError('Amount must be a numeric value')

        return amount
