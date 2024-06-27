import requests
from django.conf import settings


def schedule_spider(spider_name, **kwargs):
    """
    Schedules a spider to run via ScrapyD.

    :param spider_name: Name of the spider to run inside folder crawlers/spiders/
    :param kwargs: Additional arguments to pass to the spider
    :return: The job ID of the scheduled job
    """
    url = f'{settings.SCRAPYD_ENDPOINT}/schedule.json'
    data = {
        'project': 'default',
        'spider': spider_name,
    }
    data.update(kwargs)

    response = requests.post(url, data=data)

    if response.status_code == 200:
        job_id = response.json().get('jobid')
        return job_id
    else:
        response.raise_for_status()


"""
job_id = schedule_spider(spider_name='marketwatch', stock_ticker="AMZN")
job_id = schedule_spider(spider_name='marketwatch') #ALL
"""