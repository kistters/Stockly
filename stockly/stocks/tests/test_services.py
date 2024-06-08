import unittest
from pathlib import Path

from stockly.stocks.services.marketwatch import marketwatch_stock_parser


class TestMarketwatchStockParser(unittest.TestCase):

    def setUp(self):
        # Load the HTML file
        test_dir = Path(__file__).parent / 'test'
        html_file_path = test_dir / 'example.html'
        with open(html_file_path, 'r', encoding='utf-8') as file:
            self.page_source = file.read()

    def test_marketwatch_stock_parser(self):
        # Call the method
        result = marketwatch_stock_parser(self.page_source)

        # Example of how you might structure your assertions
        # Update the expected list with the actual expected values from the example.html
        expected_keys = ['Example Key 1', 'Example Key 2']
        expected_values = ['Example Value 1', 'Example Value 2']
        expected_result = {'list': expected_keys + expected_values}

        # Perform the assertions
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
