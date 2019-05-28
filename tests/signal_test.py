import unittest
from datetime import datetime
from signal_parser import parser

class TestSignal(unittest.TestCase):

    def test_1(self):
        sig = parser.parseSignal("""Usd/chf Buy now 1.00380
T-P (1) ✅ 1.00480
T-P (2) ✅ 1.00580
T-P (3) ✅ 1.00880
S-L❌ 1.00030""")

        sig = sig[0]
        self.assertEqual(sig['sign'], 'BUY')
        tg_text = sig.to_telegram_str()
        self.assertTrue("BUY" in tg_text)
        self.assertFalse("SELL" in tg_text)
