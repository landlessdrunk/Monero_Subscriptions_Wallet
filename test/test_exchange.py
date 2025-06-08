import unittest
from unittest.mock import patch
from src.exchange import Exchange
import vcr
from decimal import Decimal

class TestExchange(unittest.TestCase):
    def test_convert(self):
        with patch('src.exchange.xe_scrape', return_value=2):
            Exchange.US_EXCHANGE = 1
            self.assertEqual(Exchange.convert('BTC', 12345), '24,690.00000000')

        with patch('src.exchange.goldback_scrape', return_value=2):
            Exchange.US_EXCHANGE = 1
            self.assertEqual(Exchange.convert('XGB', 10000), '20,000.00')

        self.assertEqual(Exchange.convert('XMR', 2), '2.00')

    def test_display(self):
        with patch('src.exchange.Exchange.convert', return_value='10,000.00'):
            self.assertEqual(Exchange.display('USD'), '$10,000.00 (10,000.00) USD')

    def test_to_atomic_units(self):
        Exchange.US_EXCHANGE = Decimal(324)
        self.assertEqual(Exchange.to_atomic_units('XMR', 1), 1000000000000)
        with vcr.use_cassette('test/fixtures/cassettes/usd_to_atomic_units.yaml'):
            self.assertEqual(Exchange.to_atomic_units('USD', 1), 3086419753)
        with vcr.use_cassette('test/fixtures/cassettes/gb_to_atomic_units.yaml'):
            self.assertEqual(Exchange.to_atomic_units('XGB', 1), 20432098765)
        with vcr.use_cassette('test/fixtures/cassettes/btc_to_atomic_units.yaml'):
            self.assertEqual(Exchange.to_atomic_units('BTC', 1), 334520493827160)

if __name__ == '__main__':
    unittest.main()
