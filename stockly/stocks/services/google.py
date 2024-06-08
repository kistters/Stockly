import logging

from bs4 import BeautifulSoup

from stockly.extra_logging import log_duration
from stockly.selenium import WebDriverManager
from stockly.stocks.utils import clean_signs

logger = logging.getLogger(__name__)

G_FINANCE_BASE_URL = "https://www.google.com/finance/quote/{}:NASDAQ"
G_SEARCH_BASE_URL = "https://www.google.com/search?q={}&hl=en"


def google_search_stock_parser(page_source: str):
    soup = BeautifulSoup(page_source, 'html.parser')

    stock_keys_elems = [elm.text for elm in soup.select('td.JgXcPd')]
    stock_values_elems = [elm.text for elm in soup.select('td.iyjjgb')]
    stock_data_dict = dict(zip(stock_keys_elems, stock_values_elems))

    map_desired_fields = {
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        '52-wk high': '52_week_high',
        '52-wk low': '52_week_low',
    }

    filtered_and_renamed_dict = {
        map_desired_fields[key]: stock_data_dict[key]
        for key in map_desired_fields if key in stock_data_dict
    }

    return filtered_and_renamed_dict


def google_finance_stock_parser(page_source: str):
    soup = BeautifulSoup(page_source, 'html.parser')

    company_name_elem = soup.select_one('div.zzDege')
    company_name = company_name_elem.text if company_name_elem else ""

    stock_keys_elems = [elm.text for elm in soup.select('div.mfs7Fc')]
    stock_values_elems = [elm.text for elm in soup.select('div.P6K39c')]
    summary_box_dict = dict(zip(stock_keys_elems, stock_values_elems))

    map_desired_fields = {
        'Previous close': 'previous_close',
        'Market cap': 'market_cap',
        'Avg Volume': 'avg_volume',
        'CEO': 'ceo',
        'Headquarters': 'headquarters',
        'Founded': 'founded',
        'Employees': 'employees'
    }

    filtered_and_renamed_dict = {
        map_desired_fields[key]: summary_box_dict[key]
        for key in map_desired_fields if key in summary_box_dict
    }

    clean_signs('$', filtered_and_renamed_dict, ['previous_close'])

    google_finance_stock_data_parsed = {
        'company_name': company_name,
        **filtered_and_renamed_dict,
    }
    return google_finance_stock_data_parsed


@log_duration(logger)
def get_stock_data_from_google_finance(stock_ticker) -> dict:
    url = G_FINANCE_BASE_URL.format(stock_ticker)
    result = {}
    log_extra = {
        'stock_ticker': stock_ticker,
        'google_finance_url': url,
    }
    logger.info('googlefinance.scraper', extra={**log_extra})
    try:
        with WebDriverManager() as driver:
            driver.get(url)
            page_source = driver.page_source

        result = google_finance_stock_parser(page_source)
    except Exception as ex:
        logger.exception('googlefinance.scraper.fail', extra={
            **log_extra,
            'exception': str(ex)
        })
        return result

    logger.info('googlefinance.scraper.success', extra={
        **log_extra,
        'google_finance_parsed': result,
    })

    return result


@log_duration(logger)
def get_stock_data_from_google_search(stock_ticker) -> dict:
    url = G_SEARCH_BASE_URL.format(stock_ticker)
    result = {}
    log_extra = {
        'stock_ticker': stock_ticker,
        'google_search_url': url,
    }
    logger.info('googlesearch.scraper', extra={**log_extra})
    try:
        with WebDriverManager() as driver:
            driver.get(url)
            page_source = driver.page_source

        result = google_search_stock_parser(page_source)

    except Exception as ex:
        logger.exception('googlesearch.scraper.fail', extra={
            **log_extra,
            'exception': str(ex)
        })
        return result

    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Fetch stock data from Polygon API.")
    parser.add_argument('--stock_ticker', type=str, help='The stock ticker symbol.', required=False)
    args = parser.parse_args()

    stock_checks = ["AAPL", "AMZN", "GOOGL", "DASD"] if not args.stock_ticker else [args.stock_ticker]
    for ticker in stock_checks:
        try:
            stock_data = get_stock_data_from_google_finance(ticker)
            print(f"Success: {stock_data}")
        except Exception as e:
            print(f"Fail: {e}")
