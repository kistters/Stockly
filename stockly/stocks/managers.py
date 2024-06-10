from django.db import models


class StockRecordManager(models.Manager):
    def latest_stock_record(self, stock_ticker):
        return self.filter(stock__code=stock_ticker).order_by('-created_at').first()

