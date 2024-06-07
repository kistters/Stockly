import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from stockly.logging import log_duration
from stockly.stocks.services.google import get_google_stock_data, get_google_stock_values
from stockly.stocks.services.polygon import PolygonAPI

logger = logging.getLogger(__name__)


@log_duration(logger)
def get_google_stock_values_async(stock_ticker: str):
    return get_google_stock_values(stock_ticker)


@log_duration(logger)
def get_google_stock_data_async(stock_ticker: str):
    return get_google_stock_data(stock_ticker)


@log_duration(logger)
def get_polygon_stock_data_async(stock_ticker: str):
    return PolygonAPI().get_stock_data(stock_ticker, None)


@log_duration(logger)
def get_aggregate_stock_data(stock_ticker: str) -> dict:
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(get_google_stock_values_async, stock_ticker): 'google_stock_values',
            executor.submit(get_google_stock_data_async, stock_ticker): 'google_search_stock_data',
            executor.submit(get_polygon_stock_data_async, stock_ticker): 'polygon_stock_data'
        }

        results = {}
        for future in as_completed(futures):
            task_name = futures[future]
            try:
                results[task_name] = future.result()
            except Exception as e:
                logger.error(f"Task {task_name} generated an exception: {e}")

    google_stock_values = results.get('google_stock_values', {})
    google_search_stock_data = results.get('google_search_stock_data', {})
    polygon_stock_data = results.get('polygon_stock_data', {})

    stock_data = {
        **google_search_stock_data,
        'stock_values': {
            **google_stock_values,
            **polygon_stock_data
        }
    }

    return stock_data
