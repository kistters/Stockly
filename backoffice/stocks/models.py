from django.db import models


class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    json_data = models.JSONField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticker
