from typing import Any

import scrapy
from scrapy import Request
from scrapy.http import Response


class MarketwatchSpider(scrapy.Spider):
    name = "marketwatch"
    allowed_domains = ["marketwatch.com"]
    stock_detail_url = "https://www.marketwatch.com/investing/stock/{stock_ticker}"
    start_urls = ["https://www.marketwatch.com/tools/markets/stocks/country/united-states"]

    def __init__(self, stock_ticker=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_url = self.stock_detail_url.format(stock_ticker=stock_ticker) if stock_ticker else None

    def start_requests(self):
        if self.stock_url:
            yield Request(self.stock_url, callback=self.parse_stock_detail, meta={'selenium': True})
        else:
            for url in self.start_urls:
                yield Request(url, callback=self.parse, meta={'selenium': True})

    def parse(self, response: Response, **kwargs: Any) -> Any:
        links = response.xpath('//table[@class="table table-condensed"]//a/@href').getall()
        next_page = response.xpath('//ul[@class="pagination"]/li[last()]//a/@href').get()

        for link in links[:10]:
            stock_detail_url = link.split('?')[0]
            yield response.follow(stock_detail_url, callback=self.parse_stock_detail, meta={'selenium': True})

        if next_page and False:
            yield response.follow(next_page, self.parse, meta={'selenium': True})

    def parse_stock_detail(self, response: Response, **kwargs: Any) -> Any:
        item = {
            'stock_ticker': response.xpath('//span[@class="company__ticker"]/text()').get(),
            'company_name': response.xpath('//h1[@class="company__name"]/text()').get(),
        }

        if not any(value is None for value in item.values()):
            yield item
