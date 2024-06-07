import logging
import time
from datetime import datetime

from stockly.stocks.services.google import GoogleScraper
from stockly.stocks.services.polygon import PolygonAPI

logger = logging.getLogger(__name__)


def get_aggregate_stock_data(stock_ticker: str) -> dict:
    start_at = time.time()
    google_finance_client = GoogleScraper()
    polygon_client = PolygonAPI()

    google_search_stock_data = google_finance_client.get_stock_values(stock_ticker=stock_ticker)
    google_finance_stock_data = google_finance_client.get_stock_data(stock_ticker=stock_ticker)
    polygon_stock_data = polygon_client.get_stock_data(stock_ticker=stock_ticker)

    stock_data = {
        **google_finance_stock_data,
        'stock_values': {
            **google_search_stock_data,
            **polygon_stock_data
        }
    }

    end_at = time.time()

    logger.info("stock_data.duration", extra={
        "stock_ticker": stock_ticker,
        "duration_ms": f"{(end_at - start_at) * 1000:.3f}",
        "start_time": datetime.fromtimestamp(start_at).isoformat(),
        "end_time": datetime.fromtimestamp(end_at).isoformat(),
    })

    return stock_data
