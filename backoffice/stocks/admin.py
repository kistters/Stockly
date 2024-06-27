from django.contrib import admin

from backoffice.stocks.models import Stock, StockRecord


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('code', 'company_name')
    search_fields = ('code', 'company_name')


@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = ('stock', 'amount', 'created_at')
    list_filter = ('created_at', 'stock')
    search_fields = ('stock__code',)
