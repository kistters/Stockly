from django.db import models

from backoffice.stocks.managers import StockRecordManager


class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    json_data = models.JSONField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticker


class StockRecord(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT, related_name='records')
    amount = models.DecimalField(max_digits=10, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)

    # will be necessary associate stock records with different users in the future.
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_records')
    objects = StockRecordManager()

    def __str__(self):
        return f"{self.stock} - {self.amount} shares"
