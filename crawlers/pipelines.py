import json
import os


class CrawlersPipeline:
    stocks_directory = '.stocks'

    def process_item(self, item, spider):
        if 'stock_ticker' in dict(item).keys():

            if not os.path.exists(self.stocks_directory):
                os.makedirs(self.stocks_directory)

            with open(f"{self.stocks_directory}/{item.get('stock_ticker')}.json", 'w') as f:
                json.dump(dict(item), f, ensure_ascii=False, indent=4)

        return item
