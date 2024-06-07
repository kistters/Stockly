import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from stockly.stocks.services.googlefinance import GoogleScraper
from stockly.stocks.services.polygon import PolygonAPI

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def stock_detail(request, stock_ticker: str):
    if request.method == 'GET':
        logger.info('stock.get', extra={
            'stock_ticker': stock_ticker,
        })
        google_finance_client = GoogleScraper()
        google_search_stock_data = google_finance_client.get_stock_values(stock_ticker=stock_ticker)
        google_finance_stock_data = google_finance_client.get_stock_data(stock_ticker=stock_ticker)
        polygon_client = PolygonAPI()
        polygon_stock_data = polygon_client.get_stock_data(stock_ticker=stock_ticker)

        stock_data = {
            **google_finance_stock_data,
            'stock_values': {
                **google_search_stock_data,
                **polygon_stock_data
            }
        }
        return JsonResponse(stock_data)

    elif request.method == 'POST':
        try:
            payload = json.loads(request.body)
            logger.info('stock.update', extra={
                'stock_ticker': stock_ticker,
                'payload': payload,
            })

            amount = payload.get('amount')
            if amount is None:
                return JsonResponse({'error': 'Amount is required'}, status=400)

            return JsonResponse({
                'message': f"{amount} units of stock {stock_ticker} were added to your stock record",
                'status': 201
            }, status=201)
        except (ValueError, KeyError) as e:
            logger.exception('stock.update.failed', extra={
                'stock_ticker': stock_ticker,
                'payload': request.body,
            })
            return JsonResponse({'error': str(e)}, status=400)
