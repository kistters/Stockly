import json
import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from stockly.stocks.forms import StockRecordForm
from stockly.stocks.models import StockRecord, Stock
from stockly.stocks.services import get_aggregate_stock_data

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def stock_detail(request, stock_ticker: str):
    stock_data = get_aggregate_stock_data(stock_ticker)  # I/O

    if request.method == 'GET':
        logger.info('stock.get', extra={
            'stock_ticker': stock_ticker,
        })

        latest_stock_record = StockRecord.objects.filter(stock__code=stock_ticker).order_by('-created_at').first()
        stock_data.update({
            'purchased_amount': latest_stock_record.amount if latest_stock_record else 0.0,
            'request_data': f"{latest_stock_record.created_at:%Y-%m-%d}" if latest_stock_record else None,
        })

        logger.info('stock.get.success', extra={
            'stock_ticker': stock_ticker,
            'stock_data': stock_data,
        })
        return JsonResponse(stock_data)

    elif request.method == 'POST':
        try:
            data_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        stock = get_object_or_404(Stock, code=stock_ticker)
        form = StockRecordForm({
            **data_json,
            'stock': stock
        })
        if form.is_valid():
            stock_record = form.save()

            logger.info('stock.update', extra={
                'stock_ticker': stock_ticker,
                'payload': form.data,
            })

            return JsonResponse({
                'message': f"{stock_record.amount} units of stock {stock_ticker} were added to your stock record."
            }, status=201)

        else:
            logger.exception('stock.update.failed', extra={
                'stock_ticker': stock_ticker,
                'payload': form.data,
                'errors': form.errors,
            })
            return JsonResponse({'errors': form.errors}, status=400)
