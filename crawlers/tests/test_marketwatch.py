import pytest
import scrapy
from scrapy.http import HtmlResponse
from crawlers.spiders.marketwatch import MarketwatchSpider
from crawlers.tests.utils import load_mock_response


@pytest.fixture
def spider():
    return MarketwatchSpider()


def test_parse_extract_next_page(spider):
    url = 'https://www.marketwatch.com/tools/markets/stocks/country/united-states'

    expected_next_page = "https://www.marketwatch.com/tools/markets/stocks/country/united-states/2"

    response = HtmlResponse(
        url=url,
        body=load_mock_response('marketwatch_stocks_us_list.html'),
        encoding='utf-8',
        request=scrapy.Request(url=url)
    )

    follow_results = list(spider.parse(response))

    assert [result.url for result in follow_results if result.callback == spider.parse] == [expected_next_page]


def test_parse_extract_final_page(spider):
    url = 'https://www.marketwatch.com/tools/markets/stocks/country/united-states/777'

    response = HtmlResponse(
        url=url,
        body=load_mock_response('marketwatch_stocks_us_list_last_page.html'),
        encoding='utf-8',
        request=scrapy.Request(url=url)
    )

    follow_results = list(spider.parse(response))
    assert [result.url for result in follow_results if result.callback == spider.parse] == []


def test_parse_extract_stock_detail_url_list(spider):
    url = 'https://www.marketwatch.com/tools/markets/stocks/country/united-states'

    response = HtmlResponse(
        url=url,
        body=load_mock_response('marketwatch_stocks_us_list.html'),
        encoding='utf-8',
        request=scrapy.Request(url=url)
    )

    follow_results = [
        result.url for result in list(spider.parse(response))
        if result.callback == spider.parse_stock_detail]

    assert len(follow_results) == 150
    assert follow_results[:10] == [
        'https://www.marketwatch.com/investing/Stock/OONEF',
        'https://www.marketwatch.com/investing/Stock/VCXA',
        'https://www.marketwatch.com/investing/Stock/VCXAU',
        'https://www.marketwatch.com/investing/Stock/VCXAW',
        'https://www.marketwatch.com/investing/Stock/VCXB.UT',
        'https://www.marketwatch.com/investing/Stock/VCXB',
        'https://www.marketwatch.com/investing/Stock/VCXB.WT',
        'https://www.marketwatch.com/investing/Stock/TXG',
        'https://www.marketwatch.com/investing/Stock/YI',
        'https://www.marketwatch.com/investing/Stock/RETC'
    ]


def test_parse_extract_stock_detail_data(spider):
    url = 'https://www.marketwatch.com/investing/Stock/AMZN'

    response = HtmlResponse(
        url=url,
        body=load_mock_response('marketwatch_stock_detail_AMZN.html'),
        encoding='utf-8',
        request=scrapy.Request(url=url)
    )

    stock_data = next(spider.parse_stock_detail(response))

    assert stock_data == {
        'company_name': "Amazon.com Inc.",
        'ticker': "AMZN",
    }
