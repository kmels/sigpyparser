import hashlib
import bson
import json

from datetime import datetime
from signal_parser.consensus import CalificacionConsensus

def myhash(t : str):
    """Returns a 12-digit integer hash using sha256"""
    h = hashlib.sha256()
    h.update(t.encode('utf-8'))
    return bson.Int64(h.hexdigest()[0:12],16)

def mt4_date_converter(o):
    if isinstance(o, datetime):
        return o.strftime("%Y.%m.%d %H:%M")
    if isinstance(o, float) and math.isnan(o):
        return -1
    if isinstance(o, dict):
        for k, v in dct.items():
            if isinstance(v, float) and math.isnan(v):
                o[k] = -1
        return o

def mt4_date_parser(dct):
    if 'date' in dct:
        try:
            dct['date'] = datetime.strptime(dct['date'], "%Y.%m.%d %H:%M")
        except:
            pass

    for k, v in dct.items():
        if isinstance(v, dict) and 'mt4' in v and 'ts' in v:
            try:
                dct[k]['mt4'] = datetime.strptime(v['mt4'], "%Y.%m.%d %H:%M")
            except:
                pass
        if isinstance(v, dict) and 'date' in v:
            try:
                dct[k]['date'] = datetime.strptime(v['date'], "%Y.%m.%d %H:%M")
            except:
                pass
    return dct

valid_buy = lambda t,entry,sl,tp: t is "BUY" and entry > sl and tp > entry
valid_sell = lambda t,entry,sl,tp: t is "SELL" and entry < sl and tp < entry

def parseSignal(t : str, d: datetime, p : str):
    #Check if it starts with a date
    if t is None:
        return None

    text = normalizeText(t)

    #print("Normalized text: " + text)

    isBuy = 'BUY' in text
    isSell = 'SELL' in text
    hasType = isBuy or isSell

    pair = getValidPair(text)
    if not (hasType and pair):
        if not pair:
            return Noise("Missing pair")
        if not hasType:
            return Noise("Missing type")

        return False
    _tokens = text.split(" ")
    if isBuy and isSell:
        _type = "BUY" if text.index("BUY") < text.index("SELL") else "SELL"
    else:
        _type = "BUY" if isBuy else "SELL"
    _prices = [float(t) for t in _tokens if isPrice(t)]

    if len(_prices)<3:
        return Noise("Less than 3 prices")

    def is_likely_price(price, _prices = _prices):
        sims = 0
        for ref_entry in _prices:
            points_away = pips_diff(price, ref_entry, pair)
            likely = points_away < 1500 and points_away >= 0
            #print(ref_entry,'..',price,'..',likely,"..", points_away)
            if likely:
                sims += 1
        #print("\t",sims)
        return sims >= 3

    #print("Prices: " + str(_prices))
    likely_prices = [p for p in _prices if is_likely_price(p)]
    #print("Likely prices: " + str(likely_prices))

    if len(likely_prices) != 3:
        if not 'TP' in text:
            return Noise("Missing TP")
        if not 'SL' in text:
            return Noise("Missing SL")

    div = 1
    if len(likely_prices) < 3:
        prices_ = [p/10 for p in _prices]
        likely_prices = [p for p in prices_ if is_likely_price(p, prices_)]
        div = 10

        if len(likely_prices) < 3:
            prices_ = [p/10 for p in prices_]
            likely_prices = [p for p in prices_ if is_likely_price(p, prices_)]
            div = 100

    setup = getValidSetup(_type, pair, _tokens, [], div)

    def mkSafeSetup(s):
        if not setup:
            return False
        setup['date'] = d
        setup['sign'] = _type
        setup['username'] = p
        setup['pair'] = 'XAUUSD' if pair == 'GOLD' else pair
        signal = Signal.from_dict(s)
        if signal.is_payout_safe():
            return signal
        else:
            return None

    if not mkSafeSetup(setup):
        setup = getValidSetup(_type, pair, _tokens, likely_prices, div)

    return mkSafeSetup(setup)

def valid_setup(t,e,s,tp):
    """"Validate buy or sell prices."""
    if float(tp) <=0 or float(s) <= 0 or float(e) <= 0:
        return False
    return valid_buy(t,e,s,tp) or valid_sell(t,e,s,tp)

class Signal (dict):
    def __init__(self, entry, sl, tp, date, sign, username, pair,
                    inserted_at = None, calificaciones = []):
        self['entry'] = entry
        self['sl'] = sl
        self['tp'] = tp
        self['date'] = date
        self['sign'] = sign
        self['pair'] = pair
        self['username'] = username
        if not calificaciones:
            calificaciones = []
        self['calificaciones'] = calificaciones
        self.consensus = CalificacionConsensus(calificaciones)
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


    def odds(self):
        payout_odds = (float(self['tp'])-float(self['entry']))/(float(self['entry'])-float(self['sl']))
        return float("%.1f" % payout_odds)

    def set_date(self, date):
        self['date'] = date
        mt4_date = date.strftime("%Y.%m.%d %H:%M")
        self['mt4_rep'] = "%s %s %s %.5f SL %.5f TP %.5f" % (
            mt4_date, self['pair'], self['sign'], float(self['entry']), float(self['sl']), float(self['tp'])
        )

    def sl_pips(self):
        sl_pips = abs(float(self['entry'])-float(self['sl'])) * 100
        if ('XAU' in self['pair']):
            sl_pips /= 10
        if (not 'JPY' in self['pair'] and not 'XAU' in self['pair'] and not 'BTC' in self['pair']):
            sl_pips *= 100
        if ('BTC' in self['pair']):
            sl_pips /= 100
        return sl_pips

    def is_payout_safe(self):
        #tp_pips = abs(float(self['entry'])-float(self['tp']))
        #print("SL Pips: ", self.sl_pips())
        if 'BTC' in self['pair']:
            return True
        else:
            return self.odds() < 25.0 and self.odds() >= 0.1 and self['sl_pips'] <= 500 and self['sl_pips'] >= 10

    @staticmethod
    def from_dict(unrounded: dict):

        try:
            if '_id' in unrounded:
                del unrounded['_id']
            dumped = json.dumps(unrounded, default = mt4_date_converter)
            rounded = lambda x: float("%.5f" % float(x))
            it = json.loads(dumped,
                object_hook=mt4_date_parser, parse_float=rounded)
            s = Signal(it['entry'],it['sl'],it['tp'],it['date'],it['sign'],it['username'],
                            it['pair'], it.get('inserted_at'), it.get('calificaciones'))
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
    def dumps_from_dict(it: dict):
        return json.dumps(Signal.from_dict(it),
            default = mt4_date_converter)

    def from_trackrecord(it: dict):
        try:
            date_str = it['Day'] + ' ' + it['Time']
            import datetime
            date = datetime.datetime.strptime(date_str,'%d/%m/%Y %H:%M')
            return Signal(
                it['Entry'], it['SL'], it['TP'], date, it['Direction'].upper(), it['Source'], it['Base']+it['Counter']
            )
        except:
            print("Failed: %s " % str(it))
            return None
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

        if self['sign'] is "BUY":
            _str +=  "☝ BUY "+"\t";
        else:
            _str += "👇 SELL "+"\t";

        _str += "🏁 " + str(self['entry']) +"\n";
        _str += " ✖" + str(self['sl'])+"\t";
        _str += " 🎯" + str(self['tp'])+"\n";
        _str += " 🎲 Payoff: " + ("%.1f" % self.odds())
        return _str

    def to_telegram_str_prev(self):
        _str = "**" + self['username'] + "**\n"
        _str += self['mt4_rep'][0:16] + "\n"
        _str += flags_sym_(self['pair'][0:3]) + " "
        _str += self['pair'] + " "
        _str += flags_sym_(self['pair'][-3:]) + "\n"

        point_sym = "📈" if self['sign'] is "BUY" else '📉'
        _str += point_sym + " " + self['sign'] + " " + str(self['entry'])

        _str += "\n🔵 TP " + str(self['tp'])
        _str += " (%.0f)" % pips_diff(self['tp'],self['entry'],self['pair'])
        _str += "\n🔴 SL " + str(self['sl'])
        _str += " (%.0f)" % pips_diff(self['sl'],self['entry'],self['pair'])
        _str += "\nPayoff: %.1f" % self.odds()

        if 'track_record' in self:
            kelly = self['track_record']
            _str += "\n_Win Ratio:_ %.3f" % kelly['pair_winratio']

            kelly_ratio = (kelly['pair_winratio']*(self.odds()+1)-1)/self.odds()
            _str += "\n_Kelly:_ %.3f" % kelly_ratio
            if kelly_ratio > 0:
                _str += " ✔️"
            else:
                _str += " 🚫"

            pair_buys_winratio = (kelly['pair_buys_winratio']*(self.odds()+1)-1)/self.odds()
            pair_sells_winratio = (kelly['pair_sells_winratio']*(self.odds()+1)-1)/self.odds()
            if kelly['pair_closed_avgduration'] > 0:
                _str += "\n_Duración promedio:_ %.1f días" % kelly['pair_closed_avgduration']

            if kelly['pair_nclosed'] > 0:
                _str += "\n_Cerradas:_ %d trades" % kelly['pair_nclosed']

                if self['sign'] == 'BUY':
                    x = "\n_Cerradas BUY:_ %d (Win Ratio: %.3f, Kelly: %.2f)" % (kelly['pair_nclosed_buys'],kelly['pair_buys_winratio'],pair_buys_winratio)
                    _str += x
                    if pair_buys_winratio > 0:
                        _str += " ✔️" + "\n"
                    else:
                        _str += " 🚫 " + "\n"
                else:
                    x = "\n_Cerradas SELL:_ %d (_Win Ratio:_ %.3f, _Kelly:_ %.2f)" % (kelly['pair_nclosed_sells'],kelly['pair_sells_winratio'],pair_sells_winratio)
                    _str += x
                    if pair_sells_winratio > 0:
                        _str += " ✔️ " + "\n"
                    else:
                        _str += " 🚫 " + "\n"

            expectancy = kelly['provider_winratio']*kelly['provider_avgpayout'] - (1-kelly['provider_winratio'])
            _str += "_Overall (%d) Provider Expectancy_: %.3f (_Win Ratio:_ %.3f, _Avg Payoff:_ %.3f)" % (kelly['provider_nclosed'],expectancy,kelly['provider_winratio'],kelly['provider_avgpayout'])

            if expectancy > 0:
                _str += " ✔️ "
            else:
                _str += " 🚫 "

        #_str += "\n_ID:_  " + str(self['hash'])
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
        if 'track_record' in self:
            kelly = self['track_record']
            _str += "\n_Win Ratio:_ %.3f" % kelly['pair_winratio']

            kelly_ratio = (kelly['pair_winratio']*(self.odds()+1)-1)/self.odds()
            _str += "\n_Kelly:_ %.3f" % kelly_ratio
            if kelly_ratio > 0:
                _str += " :heavy_check_mark: "
            else:
                _str += " :no_entry_sign: "

            pair_buys_winratio = (kelly['pair_buys_winratio']*(self.odds()+1)-1)/self.odds()
            pair_sells_winratio = (kelly['pair_sells_winratio']*(self.odds()+1)-1)/self.odds()
            if kelly['pair_closed_avgduration'] > 0:
                _str += "\n_Duración promedio:_ %.1f días" % kelly['pair_closed_avgduration']

            if kelly['pair_nclosed'] > 0:
                _str += "\n_Cerradas:_ %d trades" % kelly['pair_nclosed']

                if self['sign'] == 'BUY':
                    x = "\n_Cerradas BUY:_ %d (Win Ratio: %.3f, Kelly: %.2f)" % (kelly['pair_nclosed_buys'],kelly['pair_buys_winratio'],pair_buys_winratio)
                    _str += x
                    if pair_buys_winratio > 0:
                        _str += " :heavy_check_mark: " + "\n"
                    else:
                        _str += " :no_entry_sign: " + "\n"
                else:
                    x = "\n_Cerradas SELL:_ %d (_Win Ratio:_ %.3f, _Kelly:_ %.2f)" % (kelly['pair_nclosed_sells'],kelly['pair_sells_winratio'],pair_sells_winratio)
                    _str += x
                    if pair_sells_winratio > 0:
                        _str += " :heavy_check_mark: " + "\n"
                    else:
                        _str += " :no_entry_sign: " + "\n"

            expectancy = kelly['provider_winratio']*kelly['provider_avgpayout'] - (1-kelly['provider_winratio'])
            _str += "_Overall (%d) Provider Expectancy_: %.3f (_Win Ratio:_ %.3f, _Avg Payoff:_ %.3f)" % (kelly['provider_nclosed'],expectancy,kelly['provider_winratio'],kelly['provider_avgpayout'])

            if expectancy > 0:
                _str += " :heavy_check_mark: "
            else:
                _str += " :no_entry_sign: "

        _str += "\n_ID:_  " + str(self['hash'])
        return _str

    def has_consensus(self):
        return self.consensus.has_consensus()

    def get_consensus(self):
        return self.consensus.get_consensus()

class Noise():
    def __init__(self, msg):
        self.msg = msg
    def __eq__(self, obj):
        return type(obj) is Noise and obj.msg == self.msg
    def __str__(self):
        return self.msg

currencies = ['AUD','CAD','CHF','EUR','GBP','JPY','NZD','USD','XAU','WTI','BTC']
pairs = [a+b for a in currencies[:-3] for b in currencies[:-3] if a is not b]
pairs.extend(['BTCUSD','WTIUSD','XAUUSD'])

def getValidPair(text):
    # test exact 6 letters
    sixletters = [t for t in text.split(" ") if len(t) is 6]
    found_pairs = [p for p in sixletters if p[:3]
             in currencies and p[-3:] in currencies]
    if len(found_pairs) > 0 and pairs[0] in pairs:
        return found_pairs[0]
    return False

def isPrice(t):
    try:
        return float(t) > 0
    except ValueError:
        return False

def getPriceFollowing(tokens, prevtoken, likely_prices, fallback_index = 0):
    if prevtoken in tokens:
        i = next(i for i,t in enumerate(tokens) if prevtoken in t) #fails if prevtoken is not in t
    else:
        i = fallback_index
    if i < len(tokens):
        if len(likely_prices) == 0:
            nextPrices = [float(t) for t in tokens[i:] if isPrice(t)]
        else:
            nextPrices = [float(t) for t in tokens[i:] if isPrice(t) and float(t) in likely_prices]
        return nextPrices[0] if len(nextPrices) > 0 else 0.0
    return 0.0

def getValidSetup(_type, pair, tokens, likely_prices, div = 1):
    _prices = [t for t in tokens if isPrice(t)]

    #print("Getting valid setup ")
    entry = getPriceFollowing(tokens, pair, likely_prices)
    #if "TP" in tokens
    tp = getPriceFollowing(tokens, "TP", likely_prices)
    sl = getPriceFollowing(tokens, "SL", likely_prices)

    if div > 1:
        tp = round(tp/div, 5)
        sl = round(sl/div, 5)
        entry = round(entry/div, 5)

    if valid_setup(_type, entry, sl, tp):
        return { 'entry': entry, 'sl': sl, 'tp': tp }
    if "ENTRY" in tokens:
        entry = getPriceFollowing(tokens, "ENTRY", likely_prices)
        tp = getPriceFollowing(tokens, "TP", likely_prices)
        sl = getPriceFollowing(tokens, "SL", likely_prices)

        if div > 1:
            tp = round(tp/div, 5)
            sl = round(sl/div, 5)
            entry = round(entry/div, 5)

    if valid_setup(_type, entry, sl, tp):
        return { 'entry': entry, 'sl': sl, 'tp': tp }

    #print("Likely prices: " + str(len(likely_prices)) + " ... " + str(('SL' in tokens and 'TP' in tokens)))
    if len(likely_prices) == 3 and not ('SL' in tokens and 'TP' in tokens):
        entry = likely_prices[0]
        sl = likely_prices[1]
        tp = likely_prices[2]
        #print("Trying")
        if valid_setup(_type, entry, sl, tp):
            return { 'entry': entry, 'sl': sl, 'tp': tp }
        if valid_setup(_type, entry, tp, sl):
            return { 'entry': entry, 'sl': tp, 'tp': sl }

    if len(likely_prices) > 3:
        return getValidSetup(_type, pair, tokens, likely_prices[1:], div)
    return False

import re
def normalizeText(t):
    t = t.upper()
    t = t.encode('unicode-escape').decode('utf-8', 'strict')
    t = re.sub("\\\\U........", "", t)
    t = re.sub("\\\\u....", "", t)
    t = re.sub("\\\\U....", "", t)
    t = re.sub("\\\\n", " ", t)
    try:
        #Inside text pair
        pair = next(iter([p for p in pairs if p in t]))
        t = re.sub("%s"%pair," %s " % pair, t)
    except StopIteration as e:
        pass

    import sys
    t = re.sub("BEAR","SELL",t)
    t = re.sub("BULL","BUY",t)
    t = re.sub("SHORT","SELL",t)
    t = re.sub("SELL STOP","SELL",t)
    t = re.sub("SELL LIMIT","SELL",t)
    t = re.sub("BUY STOP","BUY",t)
    t = re.sub("BUY LIMIT","BUY",t)
    t = re.sub("LONG","BUY",t)
    t = re.sub("(SELL|BUY) TERM","",t)
    t = t.replace('💯'," ")
    t = t.replace('#'," ")
    t = t.replace('S-L'," SL ")
    t = t.replace('T-P'," TP ")
    t = t.replace('-'," ")
    t = t.replace('@',' ')

    for p in pairs:
        base = p[0:3]
        counter = p[3:6]
        regex = "(%s).(%s)" % (base,counter)
        matches = re.findall(regex, t)
        if len(matches) > 0:
            t = re.sub(regex,"\g<1>\g<2>",t)
            break
        regex = "(%s)..?(%s)" % (base,counter)
        matches = re.findall(regex, t)
        if len(matches) > 0:
            t = re.sub(regex,"\g<1>\g<2>",t)
            break

    t = re.sub("(\d),(\d)","\g<1>.\g<2>",t) # fix numbers

    t = re.sub("SL"," SL ",t)
    t = re.sub("TP"," TP ",t)
    t = re.sub("\s+\\.","",t)
    t = re.sub("(\\.\\.)+"," ",t)
    t = re.sub("T\\.P"," TP ",t)
    t = re.sub("S\\.L"," SL ",t)
    t = re.sub("STOP LOSS"," SL ",t)
    t = re.sub("STOP"," SL ",t)
    if not 'SL' in t:
        t = re.sub('SI','SL',t)
        t = re.sub('ST','SL',t)
    t = re.sub("TARGET"," TP ",t)
    t = re.sub("TAKE PROFIT"," TP ",t)
    t = re.sub("((\d+)\\.(\d+))"," \g<1> ", t)
    t = re.sub("((\d+)\\.(\s+))"," ", t)
    t = re.sub("SELL"," SELL ", t)
    t = re.sub("BUY"," BUY ", t)
    t = re.sub('TP(.+)\s(\d+)\s((\d+)\.(\d+))(SL?)',' TP \g<3> ', t)
    t = t.replace(',',' ').replace(":"," ")
    t = t.replace('[',' ').replace(']',' ')
    t = t.replace('(',' ').replace(')',' ')
    t = re.sub(':',' ', t)
    t = re.sub("TP\s+1\s+"," TP ",t)
    t = re.sub("TP\s+2\s+"," TP ",t)
    t = re.sub("TP\s+3\s+"," TP ",t)
    t = re.sub('GOLD','XAUUSD',t)

    return t

def pips_diff(p1,p2,pair):
    pips =  abs(p1 - p2)*100
    if not 'JPY' in pair and not 'XAU' in pair:
        pips *= 100
    if 'XAU' in pair:
        pips /= 10
    if 'BTC' in pair:
        pips /= 100000
    return pips

def main():
    """Entry point for the application script"""
    print("Call your main application code here")
