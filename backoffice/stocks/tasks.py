import logging

from celery import shared_task
logger = logging.getLogger(__name__)


@shared_task(name='stocks.process_stock_detail_from_crawler')
def process_stock_detail_from_crawler(stock_detail):
    logger.info(f'task.stocks.process.{stock_detail["stock_ticker"]}', extra=stock_detail)
    return stock_detail
