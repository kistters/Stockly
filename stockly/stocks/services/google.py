import logging

from selenium.webdriver.common.by import By

from stockly.selenium import WebDriverManager

logger = logging.getLogger(__name__)

G_FINANCE_BASE_URL = "https://www.google.com/finance/quote/{}:NASDAQ"
G_SEARCH_BASE_URL = "https://www.google.com/search?q={}"


def get_google_stock_data(stock_ticker) -> dict:
    url = G_FINANCE_BASE_URL.format(stock_ticker)
    log_extra = {
        'stock_ticker': stock_ticker,
        'google_finance_url': url,
    }
    logger.info('googlefinance.scraper', extra={**log_extra})
    try:
        with WebDriverManager() as driver:
            driver.get(url)
            company_name = driver.find_element(By.CSS_SELECTOR, 'div.zzDege').text
            stock_keys = [elm.text for elm in driver.find_elements(By.CSS_SELECTOR, 'div.mfs7Fc')]
            stock_values = [elm.text for elm in driver.find_elements(By.CSS_SELECTOR, 'div.P6K39c')]
            summary_box_dict = dict(zip(stock_keys, stock_values))

    except Exception as ex:
        logger.exception('googlefinance.scraper.fail', extra={
            **log_extra,
            'exception': str(ex)
        })
        return {}

    map_desired_fields = {
        'PREVIOUS CLOSE': 'previous_close',
        'MARKET CAP': 'market_cap',
        'AVG VOLUME': 'avg_volume',
        'CEO': 'ceo',
        'HEADQUARTERS': 'headquarters'
    }

    filtered_and_renamed_dict = {
        map_desired_fields[key]: summary_box_dict[key]
        for key in map_desired_fields if key in summary_box_dict
    }

    stock_data_parsed = {
        'company_code': stock_ticker,
        'company_name': company_name,
        **filtered_and_renamed_dict,
    }

    logger.info('googlefinance.scraper.success', extra={
        **log_extra,
        'data_parsed': stock_data_parsed,
    })

    return stock_data_parsed


def get_google_stock_values(stock_ticker) -> dict:
    url = G_SEARCH_BASE_URL.format(stock_ticker)
    log_extra = {
        'stock_ticker': stock_ticker,
        'google_search_url': url,
    }
    logger.info('googlesearch.scraper', extra={**log_extra})

    try:
        with WebDriverManager() as driver:
            driver.get(url)
            stock_keys = [elm.text for elm in driver.find_elements(By.CSS_SELECTOR, 'td.JgXcPd')]
            stock_values = [elm.text for elm in driver.find_elements(By.CSS_SELECTOR, 'td.iyjjgb')]
            stock_data_dict = dict(zip(stock_keys, stock_values))

    except Exception as ex:
        logger.exception('googlesearch.scraper.fail', extra={
            **log_extra,
            'exception': str(ex)
        })
        return {}

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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Fetch stock data from Polygon API.")
    parser.add_argument('--stock_ticker', type=str, help='The stock ticker symbol.', required=False)
    args = parser.parse_args()

    stock_checks = ["AAPL", "AMZN", "GOOGL", "DASD"] if not args.stock_ticker else [args.stock_ticker]
    for ticker in stock_checks:
        try:
            stock_data = get_google_stock_data(ticker)
            print(f"Success: {stock_data}")
        except Exception as e:
            print(f"Fail: {e}")
