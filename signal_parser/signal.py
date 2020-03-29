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

        precise = "%.5f"
        if "BTC" in pair:
            precise = "%.9f"

        self['mt4_rep'] = ("%s %s %s "+precise+" SL "+precise+" TP "+precise) % (
            mt4_date, pair, sign, float(entry), float(sl), float(tp)
        )
        self['unique_rep'] = ("%s %s "+precise+" SL "+precise+" TP "+precise) % (
            pair, sign, float(entry), float(sl), float(tp)
        )
        self['hash'] = myhash(self['mt4_rep'])
        self['odds'] = self.odds()
        self['tp_pips'] = self.tp_pips()
        self['sl_pips'] = self.sl_pips()

    def canonical(self):
        return self

    def odds(self) -> float:

        def payoff(tp,entry):
            payout_odds = (float(self['tp'])-float(self['entry']))/(float(self['entry'])-float(self['sl']))
            return float("%.1f" % payout_odds)

        if type(self['tp']) is list:
            return [payoff(tp, self['entry']) for tp in self['tp']]
        else:
            return payoff(self['tp'], self['entry'])

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
        if all([not p in self['pair'] for p in ['JPY','XAU','BTC']]):
            sl_pips *= 100
        if any([p in self['pair'] for p in ['BTC','ZAR']]):
            sl_pips /= 100
        return round(sl_pips,1)

    def tp_pips(self) -> int:
        tp_pips = abs(float(self['entry'])-float(self['tp'])) * 100
        if ('XAU' in self['pair']):
            tp_pips /= 1000
        if all([not p in self['pair'] for p in ['JPY','XAU','BTC']]):
            tp_pips *= 100
        if any([p in self['pair'] for p in ['BTC','ZAR']]):
            tp_pips /= 100

        return round(tp_pips,1)

    def is_payout_safe(self, max_payout = 25.0, min_payout = 0.1, max_sl_pips = 500, min_sl_pips = 10.0) -> bool:
        if 'BTC' in self['pair']:
            return True
        else:
            if not 'sl_pips' in self:
                return Noise("Missing SL")
            if not self.odds() < max_payout and self.odds() >= min_payout:
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
            if "BTC" in unrounded['pair']:
                rounded = lambda x: float("%.9f" % float(x))
            else:
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
        # Sorry - does not receive yet: list of SignalList, SignalList of SignalList
        are_signals = [type(x) is Signal for x in signals]
        if not all(are_signals):
            print("Types are signals: ", [type(x) for x in signals])
            print(signals)
            assert(all(are_signals))
        self.extend(signals)

        unique_hashes = list(set([s['hash'] for s in signals]))
        unique_reps = list(set([s['unique_rep'] for s in signals]))

        assert( len(unique_hashes) == len(signals), "Signals hashes in SignalList must be unique")
        assert( len(unique_hashes) == len(unique_reps), "Signals reps in SignalList must be unique")

    def canonical(self):
        # Returns multiple take profits as one signal
        # with a list for the field `tp`.

        import copy
        # Case 1: one stop loss, multilple take profits - RPT = RPT/Number of TPs
        # Case 2: multiple signals (buy and sell) - RPT = RPT
        # Case 3: multiple pairs - RPT = RPT
        unique = lambda q: len(set([r[q] for r in self])) == 1
        multiple_tp = unique('sign') and unique('pair') and unique('sl')
        buy_and_sell = unique('pair') and not unique('sign')
        if (multiple_tp):

            # case 1:
            # return a signal with multiple tp's ('tp' is list)
            take_profits = [s['tp'] for s in self]
            ret_sig = copy.deepcopy(self[0])
            ret_sig['tp'] = take_profits

            payoffs = [s['odds'] for s in self]
            ret_sig['odds'] = payoffs
            return ret_sig
        elif (buy_and_sell):

            # case 2:
            # group by stop loss
            grouped_by_sl = {}

            for r in self:
                if not r['sl'] in grouped_by_sl:
                    grouped_by_sl[r['sl']] = []
                grouped_by_sl[r['sl']].append(r)
            return [SignalList(g).canonical() for g in grouped_by_sl.values()]

        else:

            # case 3:
            # multiple pairs

            grouped_by_pair = {}

            for r in self:
                if not r['pair'] in grouped_by_pair:
                    grouped_by_pair[r['pair']] = []
                grouped_by_pair[r['pair']].append(r)


            canonicals = []
            for c in [SignalList(g).canonical() for g in grouped_by_pair.values()]:
                if type(c) is Signal:
                    canonicals.append(c)
                else:
                    canonicals.extend(c.canonical())
            return canonicals
