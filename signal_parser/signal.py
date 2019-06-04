import json
from datetime import datetime

from . import *
from .consensus import *
from .noise import Noise

flags = {'AUD':'au','CAD':'ca','CHF':'ch',
                'EUR':'eu','GBP':'gb','USD':'us',
                'JPY':'jp', 'NZD':'nz'}
flags_sym = lambda c: ":flag-%s:" % flags.get(c) if c in flags else ""
flags_ = {'AUD': '🇦🇺','CAD':'🇨🇦','CHF':'🇨🇭',
                'EUR':'🇪🇺','GBP':'🇬🇧','USD':'🇺🇸',
                'JPY':'🇯🇵','NZD':'🇳🇿','XAU':'💎',
                'WTI': '⛽️', 'BRT': '⛽️'}
#/💰🛢
flags_sym_ = lambda c: flags_[c] if c in flags else ""

class Signal (dict):
    def __init__(self, entry : float, sl : float, tp : float, date : datetime, sign : str, username : str, pair : str,
                    inserted_at : datetime = None, outcomes : list = []):
        self['entry'] = entry
        self['sl'] = sl
        self['tp'] = tp
        self['date'] = date
        self['sign'] = sign
        self['pair'] = pair
        self['username'] = username
        if outcomes is None:
            outcomes = []
        self['outcomes'] = outcomes
        self.consensus = OutcomeConsensus(outcomes)
        mt4_date = date.strftime("%Y.%m.%d %H:%M")
        if not inserted_at:
            inserted_at = date.strftime("%Y.%m.%d %H:%M:%S")
        self['inserted_at'] = inserted_at

        self['mt4_rep'] = "%s %s %s %.5f SL %.5f TP %.5f" % (
            mt4_date, pair, sign, float(entry), float(sl), float(tp)
        )
        self['unique_rep'] = "%s %s %.5f SL %.5f TP %.5f" % (
            pair, sign, float(entry), float(sl), float(tp)
        )
        self['hash'] = myhash(self['mt4_rep'])
        self['odds'] = self.odds()
        #self['tp_pips'] = self.tp_pips()
        self['sl_pips'] = self.sl_pips()

    def odds(self) -> float:
        payout_odds = (float(self['tp'])-float(self['entry']))/(float(self['entry'])-float(self['sl']))
        return float("%.1f" % payout_odds)

    def set_date(self, date):
        self['date'] = date
        mt4_date = date.strftime("%Y.%m.%d %H:%M")
        self['mt4_rep'] = "%s %s %s %.5f SL %.5f TP %.5f" % (
            mt4_date, self['pair'], self['sign'], float(self['entry']), float(self['sl']), float(self['tp'])
        )

    def sl_pips(self) -> int:
        sl_pips = abs(float(self['entry'])-float(self['sl'])) * 100
        if ('XAU' in self['pair']):
            sl_pips /= 10
        if (not 'JPY' in self['pair'] and not 'XAU' in self['pair'] and not 'BTC' in self['pair']):
            sl_pips *= 100
        if ('BTC' in self['pair']):
            sl_pips /= 100
        return sl_pips

    def tp_pips(self) -> int:
        tp_pips = abs(float(self['entry'])-float(self['tp'])) * 100
        if ('XAU' in self['pair']):
            tp_pips /= 10
        if (not 'JPY' in self['pair'] and not 'XAU' in self['pair'] and not 'BTC' in self['pair']):
            tp_pips *= 100
        if ('BTC' in self['pair']):
            tp_pips /= 100
        return tp_pips

    def is_payout_safe(self) -> bool:
        if 'BTC' in self['pair']:
            return True
        else:
            if not 'sl_pips' in self:
                return Noise("Missing SL")
            if not self.odds() < 25.0 and self.odds() >= 0.1:
                return Noise("Unsafe payout: %.1f odds" % self.odds())
            if not (self['sl_pips'] <= 500 and self['sl_pips'] >= 10):
                return Noise("Unsafe SL: %.1f pips" % self['sl_pips'])
            return True

    @staticmethod
    def from_dict(unrounded: dict) -> dict:

        try:
            if '_id' in unrounded:
                del unrounded['_id']
            dumped = json.dumps(unrounded, default = mt4_date_converter)
            rounded = lambda x: float("%.5f" % float(x))
            it = json.loads(dumped,
                object_hook=mt4_date_parser, parse_float=rounded)
            s = Signal(it['entry'],it['sl'],it['tp'],it['date'],it['sign'],it['username'],
                            it['pair'], it.get('inserted_at'), it.get('outcomes'))
            for k in it.keys():
                s[k] = it[k]
            return s
        except Exception as e:
            print('-'*60)
            print("Exception...")
            import sys
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            print('-'*60)
            print(unrounded)
            raise e

    @staticmethod
    def dumps_from_dict(it: dict) -> str:
        return json.dumps(Signal.from_dict(it),
            default = mt4_date_converter)

    def eve(self):
        import datetime
        eve = self.copy()
        eve['date'] = datetime.datetime.strftime(self['date'],"%a, %d %b %Y %H:%M:%S GMT")
        return eve

    def csv(self):
        mt4_date = self['date'].strftime("%Y.%m.%d %H:%M")
        return ','.join(map(str, [mt4_date, self['pair'], self['sign'], self['entry'],
                        self['sl'], self['tp'], self['hash'], self['username']]))
    def __lt__(self, other):
         return self['date'] < other['date']

    def to_telegram_str(self):

        _str = self['mt4_rep'][0:16] + "\n"
        _str += flags_sym_(self['pair'][0:3]) + " "
        _str += self['pair'] + " "
        _str += flags_sym_(self['pair'][-3:]) + "\n"

        if self['sign'] == "BUY":
            _str +=  "☝ BUY "+"\t";
        else:
            _str += "👇 SELL "+"\t";

        _str += "🏁 " + str(self['entry']) +"\n";
        _str += " ✖" + str(self['sl'])+"\t";
        _str += " 🎯" + str(self['tp'])+"\n";
        _str += " 🎲 Payoff: " + ("%.1f" % self.odds())
        return _str

    def to_slack_str(self):
        _str = self['mt4_rep'][0:16] + "\n"
        _str += flags_sym(self['pair'][0:3]) + " "
        _str += self['pair'] + " "
        _str += flags_sym(self['pair'][-3:]) + "\n"

        point_sym = ":point_up_2:" if self['sign'] is 'BUY' else ':point_down:'
        _str += point_sym + " " + str(self['entry']) + " " + self['sign']

        _str += "\n:dart: " + str(self['tp'])
        _str += "\n:x: " + str(self['sl'])

        _str += "\n_RR:_ %.2f" % self.odds()
        _str += "\n_ID:_  " + str(self['hash'])
        return _str

    def has_consensus(self):
        return self.consensus.has_consensus()

    def get_consensus(self):
        return self.consensus.get_consensus()

class SignalList(list):
    def __init__(self, signals):        
        are_signals = [type(x) is Signal for x in signals]
        assert(all(are_signals))
        self.extend(signals)

        unique_hashes = list(set([s['hash'] for s in signals]))
        unique_reps = list(set([s['unique_rep'] for s in signals]))

        assert( len(unique_hashes) == len(signals), "Signals hashes in SignalList must be unique")
        assert( len(unique_hashes) == len(unique_reps), "Signals reps in SignalList must be unique")
