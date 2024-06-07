import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def stock_detail(request, stock_symbol: str):
    if request.method == 'GET':
        stock_data = {
            'symbol': stock_symbol,
        }
        return JsonResponse(stock_data)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            if amount is None:
                return JsonResponse({'error': 'Amount is required'}, status=400)

            return JsonResponse({
                'message': f"{amount} units of stock {stock_symbol} were added to your stock record",
                'status': 201
            }, status=201)
        except (ValueError, KeyError) as e:
            return JsonResponse({'error': str(e)}, status=400)
