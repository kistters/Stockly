import logging
from typing import Any

import scrapy
from scrapy import Request
from scrapy.http import Response

logger = logging.getLogger(__name__)


class MarketwatchSpider(scrapy.Spider):
    name = "marketwatch"
    allowed_domains = ["marketwatch.com"]
    stock_detail_url = "https://www.marketwatch.com/investing/stock/{stock_ticker}"
    start_urls = ["https://www.marketwatch.com/tools/markets/stocks/country/united-states"]

    def __init__(self, stock_ticker=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_url = self.stock_detail_url.format(stock_ticker=stock_ticker) if stock_ticker else None
        logger.info(f'crawler.scrape.{stock_ticker}.start', extra=kwargs)

    def start_requests(self):
        if self.stock_url:
            yield Request(self.stock_url, callback=self.parse_stock_detail, meta={'selenium': True})
        else:
            for url in self.start_urls:
                yield Request(url, callback=self.parse, meta={'selenium': True})

    def parse(self, response: Response, **kwargs: Any) -> Any:
        links = response.xpath('//table[@class="table table-condensed"]//a/@href').getall()
        next_page = response.xpath('//ul[@class="pagination"]/li[last()]//a/@href').get()

        logger.info(f'crawler.scrape', extra={
            'links': links,
            'next_page': next_page
        })

        for link in links:
            stock_detail_url = link.split('?')[0]
            yield response.follow(stock_detail_url, callback=self.parse_stock_detail, meta={'selenium': True})

        if next_page:
            yield response.follow(next_page, self.parse, meta={'selenium': True})

    def parse_stock_detail(self, response: Response, **kwargs: Any) -> Any:
        stock_ticker = response.xpath('//span[@class="company__ticker"]/text()').get()
        company_name = response.xpath('//h1[@class="company__name"]/text()').get()
        if not stock_ticker:
            return

        xpath_performance = '//div[contains(@class,"performance")]/table'
        performance_keys = response.xpath(f'{xpath_performance}//tr//td[1]/text()').getall()
        performance_values = response.xpath(f'{xpath_performance}//tr//li[1]/text()').getall()
        performance_dict = dict(zip(performance_keys, performance_values))
        map_desired_fields = {
            '5 Day': 'five_days',
            '1 Month': 'one_month',
            '3 Month': 'three_months',
            'YTD': 'year_to_date',
            '1 Year': 'one_year',
        }

        performance = {
            map_desired_fields[key]: performance_dict[key]
            for key in map_desired_fields if key in performance_dict
        }

        xpath_competitors = '//div[contains(@class,"Competitors")]/table'
        competitors_numbers = response.xpath(f'{xpath_competitors}//td[contains(@class,"number")]/text()').getall()
        competitors_names = response.xpath(f'{xpath_competitors}//td//a/text()').getall()
        competitors_tickers = [
            link.split('?')[0].split('/')[-1].upper()
            for link in response.xpath(f'{xpath_competitors}//td//a/@href').getall()
        ]

        competitors = [{
            'name': company_name,
            'stock_ticker': ticker,
            "market_cap": {
                "value": market_cap_value[1:],
                "currency": market_cap_value[0]
            }}
            for company_name, ticker, market_cap_value in
            zip(competitors_tickers, competitors_names, competitors_numbers)
        ]

        yield {
            'meta': 'stock_data',
            'stock_ticker': stock_ticker,
            'company_name': company_name,
            'performance_data': performance,
            'competitors': competitors
        }
