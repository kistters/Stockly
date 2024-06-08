import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.cache import cache
from django.utils import timezone

from stockly.logging import log_duration
from stockly.stocks.constants import CACHE_TTL_STOCK
from stockly.stocks.models import Stock
from stockly.stocks.services.google import get_stock_data_from_google_search, get_stock_data_from_google_finance
from stockly.stocks.services.polygon import PolygonAPI

logger = logging.getLogger(__name__)


@log_duration(logger)
def get_polygon_stock_data_async(stock_ticker: str):
    return PolygonAPI().get_stock_data(stock_ticker, None)


@log_duration(logger)
def get_aggregate_stock_data(stock_ticker: str) -> dict:
    stock_cache_key = f"{stock_ticker}:{timezone.now():%Y-%m-%d}"
    stock_data = cache.get(stock_cache_key)
    if stock_data and False:
        return stock_data

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(get_stock_data_from_google_search, stock_ticker): 'stock_data_google_search',
            executor.submit(get_stock_data_from_google_finance, stock_ticker): 'stock_data_google_finance',
            executor.submit(get_polygon_stock_data_async, stock_ticker): 'polygon_stock_data'
        }

        results = {}
        for future in as_completed(futures):
            task_name = futures[future]
            try:
                results[task_name] = future.result()
            except Exception as e:
                logger.error(f"Task {task_name} generated an exception: {e}")

    stock_data_google_search = results.get('stock_data_google_search', {})
    stock_data_google_finance = results.get('stock_data_google_finance', {})
    polygon_stock_data = results.get('polygon_stock_data', {})

    stock_data = {
        'company_code': stock_ticker,
        **stock_data_google_finance,
        **stock_data_google_search,
        **polygon_stock_data
    }

    stock, _ = Stock.objects.get_or_create(
        code=stock_ticker,
        defaults={'company_name': stock_data.get('company_name', '')}
    )

    cache.set(stock_cache_key, stock_data, timeout=CACHE_TTL_STOCK)

    return stock_data
