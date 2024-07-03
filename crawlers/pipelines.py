import logging

from celery import Celery
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)


def celery_config():
    settings = get_project_settings()
    return {
        'broker_url': settings.get('CELERY_BROKER_URL'),
        'result_backend': settings.get('CELERY_RESULT_BACKEND'),
        'task_serializer': settings.get('CELERY_TASK_SERIALIZER'),
        'accept_content': settings.get('CELERY_ACCEPT_CONTENT'),
        'result_serializer': settings.get('CELERY_RESULT_SERIALIZER'),
        'timezone': settings.get('CELERY_TIMEZONE'),
    }


class CeleryPipeline:

    def __init__(self):
        self.celery_app = Celery('pipeline')
        self.celery_app.config_from_object(celery_config(), namespace='CELERY')

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_item(self, item, spider):

        metadata = item.pop('meta')
        if metadata == 'stock_ticker_to_process':
            self.celery_app.send_task('stocks.crawler_stock_detail', [dict(item)])

        if metadata == 'stock_data':
            self.celery_app.send_task('stocks.process_stock_detail_from_crawler', [dict(item)])

        logger.info(f'crawler.sent.{metadata}.{item.get("stock_ticker")}.to_backoffice', extra={
            'spider_name': spider.name,
            'item': dict(item)
        })

        return item
