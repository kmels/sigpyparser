
import unittest
from datetime import datetime
from signal_parser import parser

class TestParser(unittest.TestCase):

    def test_1(self):
        tokens = ['XAUUSD', '', 'SWING', 'TRADE', '', '', 'BUY', '', '', '', '1288', '/', 'IDEAL', '1280', '', '', 'TP', '1291', '', '', 'TP', '1300', '', '', 'TP', '1311', '', 'TP', '', '4', '1324', '', 'SL', '', '1265', '']
        likely_prices = []
        next_price = parser.getPriceFollowing(tokens, "1291", likely_prices)
        self.assertEqual(1300, next_price)

        likely_prices = [1291.0, 1300.0, 1311.0, 4.0, 1324.0, 1265.0]
        next_price = parser.getPriceFollowing(tokens, "1291", likely_prices)
        self.assertEqual(1300, next_price)

        next_price = parser.getPriceFollowing(tokens, "1291.0", [])
        self.assertEqual(1300, next_price)

    def test_2(self):
        tokens =  ['XAUUSD', '', 'SWING', 'TRADE', '', '', 'BUY', '', '', '', '1288.0', '/', 'IDEAL', '1280.0', '', '', 'TP', '', '', 'TP', '', '', 'TP', '', 'TP', '', '1324.0.0', '', 'SL', '', '1265.0', '']
        next_price = parser.getPriceFollowing(tokens, "XAUUSD", [])
        self.assertEqual(1288.0, next_price)

        tokens =  ['TP', '1324.0', '', 'SL', '', '1265.0', '']

        next_price = parser.getPriceFollowing(tokens, "TP", [])
        self.assertEqual(1324.0, next_price)

        next_price = parser.getPriceFollowing(tokens, "SL", [])
        self.assertEqual(1265.0, next_price)
