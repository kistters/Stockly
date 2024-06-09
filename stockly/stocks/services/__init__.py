import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.cache import cache
from django.utils import timezone

from stockly.extra_logging import log_duration
from stockly.stocks.constants import CACHE_TTL_STOCK
from stockly.stocks.models import Stock
from stockly.stocks.services.marketwatch import fetch_stock_data_from_marketwatch, marketwatch_stock_parser
from stockly.stocks.services.polygon import PolygonAPI

logger = logging.getLogger(__name__)


@log_duration(logger)
def get_polygon_stock_data_async(stock_ticker: str):
    return PolygonAPI().get_stock_data(stock_ticker, timezone.now().date())


@log_duration(logger)
def get_marketwatch_stock_data_async(stock_ticker: str):
    return marketwatch_stock_parser(fetch_stock_data_from_marketwatch(stock_ticker))


@log_duration(logger)
def get_aggregate_stock_data(stock_ticker: str) -> dict:
    stock_cache_key = f"{stock_ticker}:{timezone.now():%Y-%m-%d}"
    stock_cached_data = cache.get(stock_cache_key)
    if stock_cached_data:
        return stock_cached_data

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(get_marketwatch_stock_data_async, stock_ticker): 'stock_data_marketwatch',
            executor.submit(get_polygon_stock_data_async, stock_ticker): 'stock_data_polygon'
        }

        results = {}
        for future in as_completed(futures):
            task_name = futures[future]
            try:
                results[task_name] = future.result()
            except Exception as e:
                logger.error(f"Task {task_name} generated an exception: {e}")

    stock_data_marketwatch = results.get('stock_data_marketwatch', {})
    polygon_stock_data = results.get('stock_data_polygon', {})

    stock_data = {
        **stock_data_marketwatch,
    }
    if polygon_stock_data:
        stock_data.update({
            'stock_values': polygon_stock_data
        })

    stock, _ = Stock.objects.get_or_create(
        code=stock_ticker,
        defaults={'company_name': stock_data.get('company_name', '')}
    )

    cache.set(stock_cache_key, stock_data, timeout=CACHE_TTL_STOCK)

    return stock_data
