from django import forms
from django.utils.translation import gettext_lazy as _

from .models import StockRecord


class StockRecordForm(forms.ModelForm):
    class Meta:
        model = StockRecord
        fields = ['stock', 'amount']
        error_messages = {
            'amount': {
                'invalid': _("Amount must be a numeric value."),
            },
        }
