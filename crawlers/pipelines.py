from celery import Celery
from scrapy.utils.project import get_project_settings


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
        if 'stock_ticker' in dict(item).keys():
            self.celery_app.send_task('stocks.process_stock_detail_from_crawler', [dict(item)])
        return item
