import unittest
from datetime import datetime
from signal_parser.consensus import *
today = datetime.now()
import json

class TestConsensus(unittest.TestCase):

    def test_1(self):
        c = Outcome.from_dict({"hash":149490766844,"signer":"SimpleFX Ltd.","pair":"EURUSD","published_on":{"ts":1490554500,"mt4":"2017.03.26 18:55"},"opened_on":{"ts":1490553900,"mt4":"2017.03.26 18:45"},"invalidated_on":{"ts":1490595300,"mt4":"2017.03.27 06:15"},"last_checked":{"ts":1490595300,"mt4":"2017.03.27 06:15"},"last_available":{"ts":1515968100,"mt4":"2018.01.14 22:15"},"event":"tp_hit","state":"C"})
        self.assertEqual(c['pair'],"EURUSD")
        self.assertEqual(c['hash'],149490766844)
        self.assertEqual(c['signer'],"SimpleFX Ltd.")
        self.assertEqual(c['published_on']["ts"],1490554500)
        self.assertEqual(c['opened_on']["ts"],1490553900)
        self.assertEqual(c['invalidated_on']["ts"],1490595300)
        self.assertEqual(c['last_checked']["ts"],1490595300)
        self.assertEqual(c['last_available']["ts"],1515968100)
        self.assertEqual(c['event'],"tp_hit")
        self.assertEqual(c['state'],"C")

    def test_2(self):
        consen = OutcomeConsensus([])
        self.assertFalse(consen.has_consensus())

        c1 = {'state': "C", 'event': "tp_hit"}
        consen = OutcomeConsensus([c1])
        self.assertTrue(consen.has_consensus())
        self.assertEqual(consen.get_consensus(), ("C","tp_hit"))

        c2 = {'state': "C", 'event': "sl_hit"}
        consen = OutcomeConsensus([c1,c2])
        self.assertFalse(consen.has_consensus())

        c3 = {'state': "C", 'event': "tp_hit"}
        consen = OutcomeConsensus([c1,c2,c3])
        self.assertTrue(consen.has_consensus())

        c4 = {'state': "C", 'event': "sl_hit"}
        c5 = {'state': "C", 'event': "sl_hit"}
        consen = OutcomeConsensus([c1,c3,c4,c5])
        self.assertFalse(consen.has_consensus())

        consen = OutcomeConsensus([c1,c3,c3,c4,c5])
        self.assertTrue(consen.has_consensus())

    def test_3(self):
        c1 = {'state': "C", 'event': "tp_hit"}
        c2 = {'state': "R", 'event': "recheck"}
        ccs = OutcomeConsensus([c1,c1,c1,c2])
        self.assertEqual(ccs.get_consensus(), ("C","tp_hit"))

    def test_4(self):
        resultset = {'{"hash": 174843262703169,"granularity": "15","event": "open","calificador": "International Capital Markets Pty Ltd.","account_number": 624532,"pair": "EURCAD","state": "O","opened_on": {"ts": 1594267200,"mt4": "2020.07.09 04:00"},"invalidated_on": {"ts": -7200,"mt4": ""},"published_on": {"ts": 1594267260,"mt4": "2020.07.09 04:01"},"last_checked": {"ts": 1594416600,"mt4": "2020.07.10 21:30"},"last_available": {"ts": 1594417500,"mt4": "2020.07.10 21:45"},"spot_price": "1.53613000","signal": {"entry": 1.53400,"sl": 1.54000,"tp": 1.52700,"date": "2020.07.09 04:01","sign": "SELL","pair": "EURCAD","hash": 174843262703169,"tp_pips": 70.0,"sl_pips": 60.0}}'}
        outcome = [json.loads(c) for c in resultset]
        self.assertEqual(len(outcome),1)
        cs = OutcomeConsensus(outcome)
        self.assertEqual(cs.has_consensus(), True)
        self.assertEqual(cs.get_consensus(), ("O","open"))

    def test_5(self):
        test = OutcomeConsensus([
            {'state': "C", 'event': "tp_hit"},
            {'state': "P", 'event': "pending"},
            {'state': "C", 'event': "tp_hit"},
            {'state': "P", 'event': "pending"}
        ])

        self.assertFalse(test.has_consensus())
        self.assertTrue(test.has_weak_consensus())
        self.assertEqual(test.get_weak_consensus('C'), ('C','tp_hit'))
        self.assertEqual(test.get_weak_consensus(), ('C', 'tp_hit'))
