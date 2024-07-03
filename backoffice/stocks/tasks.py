import logging

from celery import shared_task

from .models import Stock
from ..utils.scrapyd_integration import schedule_spider

logger = logging.getLogger(__name__)


@shared_task(name='stocks.process_stock_detail_from_crawler')
def process_stock_detail_from_crawler(stock_detail: dict):
    stock_ticker = stock_detail.get('stock_ticker')
    stock_obj, created = Stock.objects.update_or_create(ticker=stock_ticker, defaults={'json_data': stock_detail})
    if created:
        logger.info(f'task.stocks.process.{stock_ticker}.created', extra=stock_obj.json_data)
    else:
        logger.info(f'task.stocks.process.{stock_ticker}.updated', extra=stock_obj.json_data)

    return stock_detail


@shared_task(name='stocks.crawler_stock_detail')
def crawler_stock_detail(stock_metadata: dict):
    stock_ticker = stock_metadata.get('stock_ticker')
    job_id = schedule_spider(**stock_metadata)
    logger.info(f'task.stocks.{stock_ticker}.crawler_schedule', extra={
        "job_id": job_id,
        **stock_ticker
    })
