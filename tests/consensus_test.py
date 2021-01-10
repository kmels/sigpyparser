import unittest
from datetime import datetime
from signal_parser.consensus import *
today = datetime.now()
import json
import pytest

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
        self.assertEqual(test.get_consensus(), ("C","tp_hit"))

    def test_6(self):
        test = OutcomeConsensus([
            {'state': "O", 'event': "open"},
            {'state': "P", 'event': "pending"},
            {'state': "O", 'event': "open"},
            {'state': "P", 'event': "pending"}
        ])

        self.assertFalse(test.has_consensus())
        self.assertTrue(test.has_weak_consensus())
        pytest.raises(Exception, test.get_weak_consensus, 'C')
        self.assertEqual(test.get_weak_consensus(), ('O', 'open'))
        self.assertEqual(test.get_consensus(), ("O","open"))


        c1 = "{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"open\",\"calificador\": \"FX Choice Limited\",\"account_number\": 276110,\"pair\": \"EURUSD\",\"state\": \"O\",\"opened_on\": {\"ts\": 1597141801,\"mt4\": \"2020.08.11 10:30\"},\"invalidated_on\": {\"ts\": -10799,\"mt4\": \"\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597205701,\"mt4\": \"2020.08.12 04:15\"},\"last_available\": {\"ts\": 1597206601,\"mt4\": \"2020.08.12 04:30\"},\"spot_price\": 1.18148000,\"spot_price_pips\": 2.8,\"highest_price\": 1.18079000,\"lowest_price\": 1.17110000,\"highest_price_entry_pips\": 4.1,\"lowest_price_entry_pips\": 101.0,\"highest_price_date\": \"2020.08.11 13:30\",\"lowest_price_date\": \"2020.08.12 07:30\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": [1.16400,1.14400,1.12400],\"date\": \"2020.08.10 02:24\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 172.0,\"sl_pips\": 228.0}, \"secondary_scores\": [{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"open\",\"calificador\": \"FX Choice Limited\",\"account_number\": 276110,\"pair\": \"EURUSD\",\"state\": \"O\",\"opened_on\": {\"ts\": 1597141801,\"mt4\": \"2020.08.11 10:30\"},\"invalidated_on\": {\"ts\": -10799,\"mt4\": \"\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597205701,\"mt4\": \"2020.08.12 04:15\"},\"last_available\": {\"ts\": 1597206601,\"mt4\": \"2020.08.12 04:30\"},\"spot_price\": 1.18148000,\"spot_price_pips\": 2.8,\"highest_price\": 1.18079000,\"lowest_price\": 1.17110000,\"highest_price_entry_pips\": 4.1,\"lowest_price_entry_pips\": 101.0,\"highest_price_date\": \"2020.08.11 13:30\",\"lowest_price_date\": \"2020.08.12 07:30\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": 1.14400,\"date\": \"2020.08.10 05:23\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 372.0,\"sl_pips\": 228.0}},{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"open\",\"calificador\": \"FX Choice Limited\",\"account_number\": 276110,\"pair\": \"EURUSD\",\"state\": \"O\",\"opened_on\": {\"ts\": 1597141801,\"mt4\": \"2020.08.11 10:30\"},\"invalidated_on\": {\"ts\": -10799,\"mt4\": \"\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597205701,\"mt4\": \"2020.08.12 04:15\"},\"last_available\": {\"ts\": 1597206601,\"mt4\": \"2020.08.12 04:30\"},\"spot_price\": 1.18148000,\"spot_price_pips\": 2.8,\"highest_price\": 1.18079000,\"lowest_price\": 1.17110000,\"highest_price_entry_pips\": 4.1,\"lowest_price_entry_pips\": 101.0,\"highest_price_date\": \"2020.08.11 13:30\",\"lowest_price_date\": \"2020.08.12 07:30\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": 1.12400,\"date\": \"2020.08.10 05:23\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 572.0,\"sl_pips\": 228.0}}]}"
        c2 = "{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"pending\",\"calificador\": \"SimpleFX Ltd.\",\"account_number\": 294609,\"pair\": \"EURUSD\",\"state\": \"P\",\"opened_on\": {\"ts\": 0,\"mt4\": \"1970.01.01 00:00\"},\"invalidated_on\": {\"ts\": 0,\"mt4\": \"1970.01.01 00:00\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597041900,\"mt4\": \"2020.08.10 06:45\"},\"last_available\": {\"ts\": 1597042800,\"mt4\": \"2020.08.10 07:00\"},\"spot_price\": 1.18146000,\"spot_price_pips\": 2.6,\"highest_price\": 1.18003000,\"lowest_price\": 1.17646000,\"highest_price_entry_pips\": 11.7,\"lowest_price_entry_pips\": 47.4,\"highest_price_date\": \"2020.08.10 06:00\",\"lowest_price_date\": \"2020.08.10 06:45\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": [1.16400,1.14400,1.12400],\"date\": \"2020.08.10 02:24\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 172.0,\"sl_pips\": 228.0}, \"secondary_scores\": [{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"pending\",\"calificador\": \"SimpleFX Ltd.\",\"account_number\": 294609,\"pair\": \"EURUSD\",\"state\": \"P\",\"opened_on\": {\"ts\": 0,\"mt4\": \"1970.01.01 00:00\"},\"invalidated_on\": {\"ts\": 0,\"mt4\": \"1970.01.01 00:00\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597041900,\"mt4\": \"2020.08.10 06:45\"},\"last_available\": {\"ts\": 1597042800,\"mt4\": \"2020.08.10 07:00\"},\"spot_price\": 1.18146000,\"spot_price_pips\": 2.6,\"highest_price\": 1.18003000,\"lowest_price\": 1.17646000,\"highest_price_entry_pips\": 11.7,\"lowest_price_entry_pips\": 47.4,\"highest_price_date\": \"2020.08.10 06:00\",\"lowest_price_date\": \"2020.08.10 06:45\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": 1.14400,\"date\": \"2020.08.10 02:24\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 372.0,\"sl_pips\": 228.0}},{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"pending\",\"calificador\": \"SimpleFX Ltd.\",\"account_number\": 294609,\"pair\": \"EURUSD\",\"state\": \"P\",\"opened_on\": {\"ts\": 0,\"mt4\": \"1970.01.01 00:00\"},\"invalidated_on\": {\"ts\": 0,\"mt4\": \"1970.01.01 00:00\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597041900,\"mt4\": \"2020.08.10 06:45\"},\"last_available\": {\"ts\": 1597042800,\"mt4\": \"2020.08.10 07:00\"},\"spot_price\": 1.18146000,\"spot_price_pips\": 2.6,\"highest_price\": 1.18003000,\"lowest_price\": 1.17646000,\"highest_price_entry_pips\": 11.7,\"lowest_price_entry_pips\": 47.4,\"highest_price_date\": \"2020.08.10 06:00\",\"lowest_price_date\": \"2020.08.10 06:45\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": 1.12400,\"date\": \"2020.08.10 02:24\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 572.0,\"sl_pips\": 228.0}}]}"
        c3 = "{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"open\",\"calificador\": \"IFCMarkets. Corp.\",\"account_number\": 856507,\"pair\": \"EURUSD\",\"state\": \"O\",\"opened_on\": {\"ts\": 1597268428,\"mt4\": \"2020.08.12 21:40\"},\"invalidated_on\": {\"ts\": 1145428,\"mt4\": \"1970.01.14 06:10\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597376428,\"mt4\": \"2020.08.14 03:40\"},\"last_available\": {\"ts\": 1597377328,\"mt4\": \"2020.08.14 03:55\"},\"spot_price\": 1.17782000,\"spot_price_pips\": 33.8,\"highest_price\": 1.19060000,\"lowest_price\": 1.16980000,\"highest_price_entry_pips\": 94.0,\"lowest_price_entry_pips\": 114.0,\"highest_price_date\": \"2020.07.31 08:45\",\"lowest_price_date\": \"2020.07.28 10:00\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": [1.16400,1.14400,1.12400],\"date\": \"2020.08.10 02:24\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 172.0,\"sl_pips\": 228.0}, \"secondary_scores\": [{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"open\",\"calificador\": \"IFCMarkets. Corp.\",\"account_number\": 856507,\"pair\": \"EURUSD\",\"state\": \"O\",\"opened_on\": {\"ts\": 1597268428,\"mt4\": \"2020.08.12 21:40\"},\"invalidated_on\": {\"ts\": 1145428,\"mt4\": \"1970.01.14 06:10\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597376428,\"mt4\": \"2020.08.14 03:40\"},\"last_available\": {\"ts\": 1597377328,\"mt4\": \"2020.08.14 03:55\"},\"spot_price\": 1.17782000,\"spot_price_pips\": 33.8,\"highest_price\": 1.19060000,\"lowest_price\": 1.16980000,\"highest_price_entry_pips\": 94.0,\"lowest_price_entry_pips\": 114.0,\"highest_price_date\": \"2020.07.31 08:45\",\"lowest_price_date\": \"2020.07.28 10:00\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": 1.14400,\"date\": \"2020.07.27 20:13\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 372.0,\"sl_pips\": 228.0}},{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"open\",\"calificador\": \"IFCMarkets. Corp.\",\"account_number\": 856507,\"pair\": \"EURUSD\",\"state\": \"O\",\"opened_on\": {\"ts\": 1597268428,\"mt4\": \"2020.08.12 21:40\"},\"invalidated_on\": {\"ts\": 1145428,\"mt4\": \"1970.01.14 06:10\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597376428,\"mt4\": \"2020.08.14 03:40\"},\"last_available\": {\"ts\": 1597377328,\"mt4\": \"2020.08.14 03:55\"},\"spot_price\": 1.17782000,\"spot_price_pips\": 33.8,\"highest_price\": 1.19060000,\"lowest_price\": 1.16980000,\"highest_price_entry_pips\": 94.0,\"lowest_price_entry_pips\": 114.0,\"highest_price_date\": \"2020.07.31 08:45\",\"lowest_price_date\": \"2020.07.28 10:00\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": 1.12400,\"date\": \"2020.07.27 20:13\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 572.0,\"sl_pips\": 228.0}}]}"
        c4 = "{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"pending\",\"calificador\": \"FXTM\",\"account_number\": 2562684,\"pair\": \"EURUSD\",\"state\": \"P\",\"opened_on\": {\"ts\": -10800,\"mt4\": \"\"},\"invalidated_on\": {\"ts\": -10800,\"mt4\": \"\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597205700,\"mt4\": \"2020.08.12 04:15\"},\"last_available\": {\"ts\": 1597206600,\"mt4\": \"2020.08.12 04:30\"},\"spot_price\": 1.18138000,\"spot_price_pips\": 1.8,\"highest_price\": 1.18067000,\"lowest_price\": 1.17099000,\"highest_price_entry_pips\": 5.3,\"lowest_price_entry_pips\": 102.1,\"highest_price_date\": \"2020.08.11 13:30\",\"lowest_price_date\": \"2020.08.12 07:30\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": [1.16400,1.14400,1.12400],\"date\": \"2020.08.10 02:24\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 172.0,\"sl_pips\": 228.0}, \"secondary_scores\": [{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"pending\",\"calificador\": \"FXTM\",\"account_number\": 2562684,\"pair\": \"EURUSD\",\"state\": \"P\",\"opened_on\": {\"ts\": -10800,\"mt4\": \"\"},\"invalidated_on\": {\"ts\": -10800,\"mt4\": \"\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597205700,\"mt4\": \"2020.08.12 04:15\"},\"last_available\": {\"ts\": 1597206600,\"mt4\": \"2020.08.12 04:30\"},\"spot_price\": 1.18138000,\"spot_price_pips\": 1.8,\"highest_price\": 1.18067000,\"lowest_price\": 1.17099000,\"highest_price_entry_pips\": 5.3,\"lowest_price_entry_pips\": 102.1,\"highest_price_date\": \"2020.08.11 13:30\",\"lowest_price_date\": \"2020.08.12 07:30\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": 1.14400,\"date\": \"2020.08.10 05:24\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 372.0,\"sl_pips\": 228.0}},{\"hash\": 247876033469480,\"granularity\": \"15\",\"event\": \"pending\",\"calificador\": \"FXTM\",\"account_number\": 2562684,\"pair\": \"EURUSD\",\"state\": \"P\",\"opened_on\": {\"ts\": -10800,\"mt4\": \"\"},\"invalidated_on\": {\"ts\": -10800,\"mt4\": \"\"},\"published_on\": {\"ts\": 1597026240,\"mt4\": \"2020.08.10 02:24\"},\"last_checked\": {\"ts\": 1597205700,\"mt4\": \"2020.08.12 04:15\"},\"last_available\": {\"ts\": 1597206600,\"mt4\": \"2020.08.12 04:30\"},\"spot_price\": 1.18138000,\"spot_price_pips\": 1.8,\"highest_price\": 1.18067000,\"lowest_price\": 1.17099000,\"highest_price_entry_pips\": 5.3,\"lowest_price_entry_pips\": 102.1,\"highest_price_date\": \"2020.08.11 13:30\",\"lowest_price_date\": \"2020.08.12 07:30\",\"signal\": {\"entry\": 1.18120,\"sl\": 1.20400,\"tp\": 1.12400,\"date\": \"2020.08.10 05:24\",\"sign\": \"SELL\",\"pair\": \"EURUSD\",\"hash\": 247876033469480,\"tp_pips\": 572.0,\"sl_pips\": 228.0}}]}"

        test = OutcomeConsensus([json.loads(x) for x in [c1,c2,c3,c4]])
        self.assertEqual(test.get_consensus(), ("O","open"))

        test = OutcomeConsensus([
            {'state': "C", 'event': "tp_hit"},
            {'state': "C", 'event': "sl_hit"}
        ])
        self.assertFalse(test.has_weak_consensus())

        test = OutcomeConsensus([
            {'state': "O", 'event': "open"},
            {'state': "C", 'event': "sl_hit"}
        ])
        self.assertFalse(test.has_consensus())
        self.assertTrue(test.has_weak_consensus())
        self.assertEqual(test.get_consensus(), ("C","sl_hit"))

        test = OutcomeConsensus([
            {'state': "P", 'event': "pending"},
            {'state': "P", 'event': "pending"},
            {'state': "O", 'event': "open"},
            {'state': "O", 'event': "open"},
            {'state': "C", 'event': "sl_hit"}
        ])
        self.assertFalse(test.has_weak_consensus())

        test = OutcomeConsensus([
            {'state': "O", 'event': "open"},
            {'state': "P", 'event': "pending"}
        ])
        self.assertTrue(test.has_weak_consensus())
        self.assertEqual(test.get_consensus(), ("O","open"))

        test = OutcomeConsensus([
            {'state': "P", 'event': "pending"},
            {'state': "C", 'event': "tp_hit"},
            {'state': "C", 'event': "sl_hit"},
            {'state': "C", 'event': "sl_hit"},
            {'state': "P", 'event': "pending"}
        ])

        self.assertFalse(test.has_consensus())
        pytest.raises(Exception, test.get_consensus)

        test = OutcomeConsensus([
            {'state': "P", 'event': "pending"},
            {'state': "C", 'event': "tp_hit"},
            {'state': "C", 'event': "sl_hit"},
            {'state': "C", 'event': "sl_hit"},
            {'state': "P", 'event': "pending"},
            {'state': "P", 'event': "pending"}
        ])

        self.assertFalse(test.has_weak_consensus())
        self.assertTrue(test.has_consensus())
        self.assertEqual(test.get_consensus(), ("P","pending"))

    def test_7(self):
        test = OutcomeConsensus([
            {'state': "O", 'event': "open"},
            {'state': "O", 'event': "open"},
            {'state': "O", 'event': "open"},
            {'state': "C", 'event': "close"},
            {'state': "C", 'event': "sl_hit"},
            {'state': "C", 'event': "sl_hit"}
        ])

        self.assertTrue(test.has_consensus())
        self.assertFalse(test.has_weak_consensus())
        self.assertEqual(test.get_consensus(), ("O","open"))

    def test_8(self):
        test = OutcomeConsensus([
            {'state': "O", 'event': "open"},
            {'state': "O", 'event': "open"},
            {'state': "C", 'event': "sl_hit"},
        ])

        self.assertTrue(test.has_consensus())
        self.assertFalse(test.has_weak_consensus())
        self.assertEqual(test.get_consensus(), ("O","open"))

        test = OutcomeConsensus([
            {'state': "O", 'event': "open"},
            {'state': "O", 'event': "open"},
            {'state': "C", 'event': "sl_hit"},
            {'state': "C", 'event': "sl_hit"}
        ])

        self.assertFalse(test.has_consensus())
        self.assertTrue(test.has_weak_consensus())
        self.assertEqual(test.get_consensus(), ("C","sl_hit"))

        test = OutcomeConsensus([
            {'state': "O", 'event': "open"},
            {'state': "O", 'event': "open"},
            {'state': "C", 'event': "sl_hit"},
            {'state': "C", 'event': "sl_hit"},
            {'state': "C", 'event': "sl_hit"}
        ])

        self.assertTrue(test.has_consensus())
        self.assertFalse(test.has_weak_consensus())
        self.assertEqual(test.get_consensus(), ("C","sl_hit"))

    def test_9(self):
        test = OutcomeConsensus([
            {'state': "P", 'event': "pending"},
            {'state': "O", 'event': "open"},
            {'state': "O", 'event': "open"},
            {'state': "P", 'event': "pending"},
            {'state': "C", 'event': "tp_hit"}
        ])
        self.assertFalse(test.has_consensus())
        self.assertFalse(test.has_weak_consensus())
        pytest.raises(Exception, test.get_consensus)

        test = OutcomeConsensus([
            {'state': "P", 'event': "pending"},
            {'state': "O", 'event': "open"},
            {'state': "O", 'event': "open"},
            {'state': "P", 'event': "pending"},
            {'state': "C", 'event': "tp_hit"},
            {'state': "C", 'event': "tp_hit"}
        ])
        self.assertFalse(test.has_consensus())
        self.assertTrue(test.has_weak_consensus())
        self.assertEqual(test.get_consensus(), ("C","tp_hit"))


    def test_10(self):
        test = OutcomeConsensus([
            {'state': "P", 'event': "pending"},
            {'state': "O", 'event': "open"}
        ])
        self.assertFalse(test.has_consensus())
        self.assertTrue(test.has_weak_consensus())
        self.assertEqual(test.get_consensus(), ("O","open"))

    def test_11(self):
        ev = ['invalid_tp_hit', 'invalid_tp_hit', 'invalid_tp_hit', 'invalid_tp_hit', 'invalid_tp_hit', 'tp_hit', 'tp_hit', 'tp_hit', 'tp_hit', 'tp_hit']
        st = ['I', 'I', 'I', 'I', 'I', 'E', 'E', 'E', 'E', 'E']
        test = OutcomeConsensus([
            {'state': S, 'event': E} for S,E in
            zip(st, ev) 
        ])
        self.assertFalse(test.has_consensus())
        self.assertFalse(test.has_weak_consensus())
        pytest.raises(Exception, test.get_consensus)

        ev.append('invalid_tp_hit')
        st.append('I')
        test = OutcomeConsensus([
            {'state': S, 'event': E} for S,E in
            zip(st, ev) 
        ])
        self.assertTrue(test.has_consensus())
        self.assertFalse(test.has_weak_consensus())
        self.assertEqual(test.get_consensus(), ("I","invalid_tp_hit"))

        ev.append('tp_hit')
        st.append('E')
        ev.append('tp_hit')
        st.append('E')
        test = OutcomeConsensus([
            {'state': S, 'event': E} for S,E in
            zip(st, ev) 
        ])
        self.assertTrue(test.has_consensus())
        self.assertFalse(test.has_weak_consensus())
        self.assertEqual(test.get_consensus(), ("E","tp_hit"))

    def test_12(self):
        ev =  ['invalid_tp_hit', 'invalid_tp_hit', 'invalid_tp_hit', 'invalid_tp_hit', 'sl_hit', 'pending', 'pending', 'pending', 'sl_hit', 'sl_hit', 'sl_hit', 'sl_hit']        
        st =  ['I', 'I', 'I', 'I', 'E', 'P', 'P', 'P', 'E', 'E', 'E', 'E']

        self.assertTrue(st.count('I') == 4)
        self.assertTrue(st.count('E') == 5)
        self.assertTrue(st.count('P') == 3)

        test = OutcomeConsensus([
            {'state': S, 'event': E} for S,E in
            zip(st, ev) 
        ])
        self.assertTrue(test.has_consensus())
        self.assertFalse(test.has_weak_consensus())

        ev = ['invalid_tp_hit', 'invalid_tp_hit', 'invalid_tp_hit', 'invalid_tp_hit', 'sl_hit', 'pending', 'pending', 'pending', 'sl_hit', 'sl_hit', 'sl_hit', 'pending']
        st = ['I', 'I', 'I', 'I', 'E', 'P', 'P', 'P', 'E','E', 'E', 'P']
        self.assertTrue(st.count('I') == 4)
        self.assertTrue(st.count('E') == 4)
        self.assertTrue(st.count('P') == 4)

        test = OutcomeConsensus([
            {'state': S, 'event': E} for S,E in
            zip(st, ev) 
        ])
        self.assertFalse(test.has_consensus())
        self.assertTrue(test.has_weak_consensus())
        self.assertEqual(test.get_weak_consensus(), ("I","invalid_tp_hit"))

    def test_13(self):
        ev = ['sl_hit', 'sl_hit', 'sl_hit', 'sl_hit', 'recheck', 'sl_hit', 'sl_hit', 'tp_hit', 'sl_hit', 'sl_hit', 'sl_hit', 'sl_hit', 'sl_hit', 'sl_hit', 'sl_hit']
        st = ['C', 'C', 'C', 'C', 'R', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C']
        test = OutcomeConsensus([
            {'state': S, 'event': E} for S,E in
            zip(st, ev)
        ])
        self.assertTrue(test.has_consensus())
        self.assertFalse(test.has_weak_consensus())