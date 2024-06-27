from django.contrib import admin

from backoffice.stocks.models import Stock


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'updated_at')
    search_fields = ('ticker',)
