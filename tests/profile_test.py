import unittest
from datetime import datetime
from signal_parser.track_record import *
today = datetime.now()
import json
import pytest

class TestProfileTrackRecord(unittest.TestCase):

    def test_1(self):
        sig1 = {"hash": 165666897609357, "granularity": "15", "event": "tp_hit", "calificador": "ThinkMarkets", "account_number": 11546726, "pair": "EURJPY", "state": "C", "opened_on": {"ts": 1604926800, "mt4": "2020.11.09 13:00"}, "invalidated_on": {"ts": 1604929500, "mt4": "2020.11.09 13:45"}, "published_on": {"ts": 1604568660, "mt4": "2020.11.05 09:31"}, "last_checked": {"ts": 1604929500, "mt4": "2020.11.09 13:45"}, "last_available": {"ts": 1606517100, "mt4": "2020.11.27 22:45"}, "highest_price": 125.127, "lowest_price": 122.217, "highest_price_entry_pips": 97.6, "lowest_price_entry_pips": 193.4, "highest_price_date": "2020.11.09 16:45", "lowest_price_date": "2020.11.06 05:45", "signal": {"entry": 124.151, "sl": 122.321, "tp": 124.508, "date": "2020.11.05 09:31", "sign": "BUY", "pair": "EURJPY", "hash": 165666897609357, "tp_pips": 35.7, "sl_pips": 183.0}}
        sig2 = {"hash": 155596072261839, "granularity": "15", "event": "tp_hit", "calificador": "FBS Inc", "account_number": 230775352, "pair": "AUDNZD", "state": "C", "opened_on": {"ts": 1604273400, "mt4": "2020.11.01 23:30"}, "invalidated_on": {"ts": 1604397600, "mt4": "2020.11.03 10:00"}, "published_on": {"ts": 1604273580, "mt4": "2020.11.01 23:33"}, "last_checked": {"ts": 1604397600, "mt4": "2020.11.03 10:00"}, "last_available": {"ts": 1606517100, "mt4": "2020.11.27 22:45"}, "highest_price": 1.07577, "lowest_price": 1.0471, "highest_price_entry_pips": 139.7, "lowest_price_entry_pips": 147.0, "highest_price_date": "2020.11.05 23:45", "lowest_price_date": "2020.11.24 03:00", "signal": {"entry": 1.0618, "sl": 1.0582, "tp": [1.06614, 1.07234, 1.0807], "date": "2020.11.01 23:33", "sign": "BUY", "pair": "AUDNZD", "hash": 155596072261839, "tp_pips": 43.4, "sl_pips": 36.0}, "secondary_scores": [{"hash": 155596072261839, "granularity": "15", "event": "tp_hit", "calificador": "FBS Inc", "account_number": 230775352, "pair": "AUDNZD", "state": "C", "opened_on": {"ts": 1604273400, "mt4": "2020.11.01 23:30"}, "invalidated_on": {"ts": 1604496600, "mt4": "2020.11.04 13:30"}, "published_on": {"ts": 1604273580, "mt4": "2020.11.01 23:33"}, "last_checked": {"ts": 1604496600, "mt4": "2020.11.04 13:30"}, "last_available": {"ts": 1606517100, "mt4": "2020.11.27 22:45"}, "highest_price": 1.07577, "lowest_price": 1.0471, "highest_price_entry_pips": 139.7, "lowest_price_entry_pips": 147.0, "highest_price_date": "2020.11.05 23:45", "lowest_price_date": "2020.11.24 03:00", "signal": {"entry": 1.0618, "sl": 1.0582, "tp": 1.07234, "date": "2020.11.02 00:33", "sign": "BUY", "pair": "AUDNZD", "hash": 155596072261839, "tp_pips": 105.4, "sl_pips": 36.0}}, {"hash": 155596072261839, "granularity": "15", "event": "sl_hit", "calificador": "FBS Inc", "account_number": 230775352, "pair": "AUDNZD", "state": "C", "opened_on": {"ts": 1604273400, "mt4": "2020.11.01 23:30"}, "invalidated_on": {"ts": 1605098700, "mt4": "2020.11.11 12:45"}, "published_on": {"ts": 1604273580, "mt4": "2020.11.01 23:33"}, "last_checked": {"ts": 1605098700, "mt4": "2020.11.11 12:45"}, "last_available": {"ts": 1606517100, "mt4": "2020.11.27 22:45"}, "highest_price": 1.07577, "lowest_price": 1.0471, "highest_price_entry_pips": 139.7, "lowest_price_entry_pips": 147.0, "highest_price_date": "2020.11.05 23:45", "lowest_price_date": "2020.11.24 03:00", "signal": {"entry": 1.0618, "sl": 1.0582, "tp": 1.0807, "date": "2020.11.02 00:33", "sign": "BUY", "pair": "AUDNZD", "hash": 155596072261839, "tp_pips": 189.0, "sl_pips": 36.0}}]}

        signals = [sig1, sig2]
        track_record = track_record_of_selection(signals)

        assert (track_record['nwins'] == 2)
        assert (track_record['nlosses'] == 0)

        assert track_record['roi'] == 0.79, "Unexpected roi: %s " % track_record['roi']
        assert track_record['pips'] == 85.30, "Unexpected pips: %s " % track_record['pips']
        assert track_record['winratio'] == 0.83, "Unexpected winratio: %s " % track_record['winratio']
        assert track_record['geometric_winratio'] == 0.83, "Unexpected geometric_winratio: %s " % track_record['geometric_winratio']
        assert track_record['roi'] == 0.79, "Unexpected roi: %s " % track_record['roi']