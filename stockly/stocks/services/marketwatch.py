import logging

from bs4 import BeautifulSoup

from stockly.selenium import WebDriverManager

logger = logging.getLogger(__name__)

TICKER = "MSFT"
MARKETWATCH_BASE_URL = "www.marketwatch.com"
MARKETWATCH_STOCK_URL = 'https://www.marketwatch.com/investing/stock/{}'


def marketwatch_stock_parser(page_source: str) -> dict:
    soup = BeautifulSoup(page_source, 'html.parser')

    company_name_elem = soup.select_one('h1.company__name')

    # Performance
    performance_table_rows = soup.select('div.performance tr.table__row')
    performance_keys = [row.select_one('td.table__cell').text for row in performance_table_rows]
    performance_values = [row.select_one('li.content__item.value').text for row in performance_table_rows]
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

    # Competitors
    competitors_names = [elm.text for elm in soup.select('div.Competitors td.table__cell a.link')]
    competitors_stock_tickers = [elm.get('href').split('?')[0].split('/')[-1] for elm in soup.select('div.Competitors td.table__cell a.link')]
    competitors_market_cap_currency = [elm.text[0] for elm in soup.select('div.Competitors td.table__cell.number')]
    competitors_market_cap_value = [elm.text[1:] for elm in soup.select('div.Competitors td.table__cell.number')]

    competitors_zip_data = zip(
        competitors_names,
        competitors_stock_tickers,
        competitors_market_cap_value,
        competitors_market_cap_currency
    )
    competitors = [{
        "ticker": str(ticker).upper(),
        "company_name": company_name,
        "market_cap": {
            "value": market_cap_value,
            "currency": currency
        }
    } for company_name, ticker, market_cap_value, currency in competitors_zip_data]

    return {
        "company_name": company_name_elem.text,
        'performance': performance,
        'competitors': competitors
    }


def fetch_stock_data_from_marketwatch(stock_ticker: str) -> str:
    url = MARKETWATCH_STOCK_URL.format(stock_ticker)
    with WebDriverManager(MARKETWATCH_BASE_URL) as driver:
        driver.get(url)
        return driver.page_source
