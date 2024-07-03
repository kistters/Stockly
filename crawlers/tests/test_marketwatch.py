import pytest
import scrapy
from scrapy import Request
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

    assert [result.url for result in follow_results
            if isinstance(result, Request) and result.callback == spider.parse] == [expected_next_page]


def test_parse_extract_final_page(spider):
    url = 'https://www.marketwatch.com/tools/markets/stocks/country/united-states/777'

    response = HtmlResponse(
        url=url,
        body=load_mock_response('marketwatch_stocks_us_list_last_page.html'),
        encoding='utf-8',
        request=scrapy.Request(url=url)
    )

    follow_results = list(spider.parse(response))

    assert [result.url for result in follow_results
            if isinstance(result, Request) and result.callback == spider.parse] == []


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
        'meta': 'stock_data',
        'stock_ticker': 'AMZN',
        'company_name': 'Amazon.com Inc.',
        'performance_data': {
            'five_days': '4.45%',
            'one_month': '-1.70%',
            'three_months': '5.10%',
            'year_to_date': '21.30%',
            'one_year': '49.32%'
        },
        'competitors': [
            {'name': 'AAPL', 'stock_ticker': 'Apple Inc.', 'market_cap': {'value': '2.98T', 'currency': '$'}},
            {'name': 'MSFT', 'stock_ticker': 'Microsoft Corp.', 'market_cap': {'value': '3.16T', 'currency': '$'}},
            {'name': 'GOOG', 'stock_ticker': 'Alphabet Inc. Cl C', 'market_cap': {'value': '2.19T', 'currency': '$'}},
            {'name': 'GOOGL', 'stock_ticker': 'Alphabet Inc. Cl A', 'market_cap': {'value': '2.19T', 'currency': '$'}},
            {'name': 'META', 'stock_ticker': 'Meta Platforms Inc.', 'market_cap': {'value': '1.25T', 'currency': '$'}},
            {'name': 'WMT', 'stock_ticker': 'Walmart Inc.', 'market_cap': {'value': '541.22B', 'currency': '$'}},
            {'name': 'NFLX', 'stock_ticker': 'Netflix Inc.', 'market_cap': {'value': '279.49B', 'currency': '$'}},
            {'name': 'DIS', 'stock_ticker': 'Walt Disney Co.', 'market_cap': {'value': '184.51B', 'currency': '$'}},
            {'name': 'COST', 'stock_ticker': 'Costco Wholesale Corp.', 'market_cap': {'value': '373.71B', 'currency': '$'}},
            {'name': 'CVS', 'stock_ticker': 'CVS Health Corp.', 'market_cap': {'value': '76.5B', 'currency': '$'}}
        ]
    }
