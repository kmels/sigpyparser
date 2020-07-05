import hashlib
import json

from datetime import datetime
from .signal import *
from .noise import *

from . import *

valid_buy = lambda t,entry,sl,tp: t is "BUY" and entry > sl and tp > entry
valid_sell = lambda t,entry,sl,tp: t is "SELL" and entry < sl and tp < entry

currencies = ['AUD','CAD','CHF','EUR','GBP','JPY','NZD','USD','XAU','WTI','BTC','ZAR']
pairs = [a+b for a in currencies[:-3] for b in currencies[:-3] if a is not b]
pairs.extend(['WTIUSD','XAUUSD'])

binance_cryptos = ['BNB','BTC','NEO','ETH','LTC','QTUM','EOS','SNT','BNT','GAS','BCH','BTM','USDT','HCC','HSR','OAX','DNT','MCO','ICN','ZRX','OMG','WTC','LRC','LLT','YOYO','TRX','STRAT','SNGLS','BQX','KNC','SNM','FUN','LINK','XVG','CTR','SALT','MDA','IOTA','SUB','IOT','ETC','MTL','MTH','ENG','AST','DASH','BTG','EVX','REQ','VIB','POWR','ARK','XRP','MOD','ENJ','STORJ','VEN','KMD','RCN','NULS','RDN','XMR','DLT','AMB','BAT','ZEC','BCPT','ARN','GVT','CDT','GXS','POE','QSP','BTS','XZC','LSK','TNT','FUEL','MANA','BCD','DGD','ADX','ADA','PPT','CMT','XLM','CND','LEND','WABI','SBTC','BCX','WAVES','TNB','GTO','ICX','OST','ELF','AION','ETF','BRD','NEBL','VIBE','LUN','CHAT','RLC','INS','IOST','STEEM','NANO','AE','VIA','BLZ','SYS','RPX','NCASH','POA','ONT','ZIL','STORM','XEM','WAN','WPR','QLC','GRS','EDO','WINGS','NAV','TRIG','APPC','PIVX','MFT','PHB','FET']

cryptocurrencies = []
cryptocurrencies.extend(binance_cryptos)
crypto_pairs = [base+"/"+counter for base in cryptocurrencies for counter in cryptocurrencies if base is not counter]
crypto_pairs.extend(['BTCUSD', 'XBTUSD'])

def is_likely_price(price, _prices, pair):
    """
    Returns true iff price change is less than 15% in FX
    """
    if pair in crypto_pairs:
        return True
    sims = 0
    for ref_entry in _prices:
        pct_change = ref_entry/price
        #  -- Definition of likelyprice: within 200% reach (2 times it's value%)
        likely = abs(1-pct_change) < 0.20 # 30 pct change 
        if likely:
            sims += 1
    return sims >= 3
    
def find_valid_setups(_prices, _tokens, text, pair, _type, d: datetime, p: ""):
    likely_prices = [p for p in _prices if is_likely_price(p, _prices, pair)]
    
    #  -- Si no tiene 3 precios, verificar si tiene SL y TP
    if len(likely_prices) < 3:
        if not 'TP' in _tokens:
            return Noise("Missing TP")
        if not 'SL' in _tokens:
            return Noise("Missing SL")

    #  -- Si tiene menos de 3 precios, tratar de rescatar typos en puntos decimales
    div = 1
    if len(likely_prices) < 3:
        prices_ = [p/10 for p in _prices]
        likely_prices = [p for p in prices_ if is_likely_price(p, prices_, pair)]
        div = 10

        if len(likely_prices) < 3:
            prices_ = [p/10 for p in prices_]
            likely_prices = [p for p in prices_ if is_likely_price(p, prices_, pair)]
            div = 100

    setup = getValidSetup(_type, pair, _tokens, [], div, d)
    
    def mkSafeSetup(s: dict):
        if not type(s) is dict:
            return Noise("Invalid setup")
        s['date'] = d
        s['sign'] = _type
        s['username'] = p
        s['pair'] = 'XAUUSD' if pair == 'GOLD' else pair
        return purifySetup(s)

    if setup:
        setup['date'] = d
        setup['sign'] = _type
        setup['username'] = p
        setup['pair'] = 'XAUUSD' if pair == 'GOLD' else pair

    setup = mkSafeSetup(setup)
    
    if not setup:
        setup = getValidSetup(_type, pair, _tokens, likely_prices, div, d)
        if type(setup) is list:
            setup = [mkSafeSetup(s) for s in setup]
        elif setup:
            setup = mkSafeSetup(setup)
        else:
            # no valid setups, then try:
            # remove first 'tp'  (if HTTPS is before TP)
            new_begin = _tokens.index("TP")
            setup = getValidSetup(_type, pair, _tokens[new_begin+1:], likely_prices, div, d)
            if setup:
                setup = mkSafeSetup(setup)

    valid_setups = []
    if setup:
        valid_setups.append(setup)

        def remove_price(p: float, ts: list):
            replacements = [(t,float(t)) for t in ts if isPrice(t) and str(float(t)) != t]
            pstr = str(float(p))
            if len(replacements) > 0:
                tstrs = "\t".join(ts)
                for rep in replacements:
                    tstrs = tstrs.replace("\t"+rep[0]+"\t", "\t"+str(rep[1]) + "\t")
                ts = tstrs.split("\t")

            if pstr in ts:
                ts.remove(pstr)
            return ts

        prices = [float(pr) for pr in _tokens if isPrice(pr)]
        unlikely_prices = [pr for pr in prices if not float(pr) in likely_prices]
        for invp in unlikely_prices:
            _tokens = remove_price(invp, _tokens)

        # check for more setups
        if type(setup) is list:
            valid_setups = setup
        else:
            next_tp_candidate = getPriceFollowing(_tokens, setup['tp'], [])
            _tokens = remove_price(setup['tp'], _tokens)
            prev_tp = setup['tp']
            next_setup_candidate = getValidSetup(_type, pair, _tokens, [], div, d)
            # there's another tp
            while next_tp_candidate and type(next_setup_candidate) is dict and prev_tp != next_setup_candidate['tp']:
                next_setup_candidate['date'] = setup['date']
                next_setup_candidate['sign'] = _type
                next_setup_candidate['username'] = setup['username']
                next_setup_candidate['pair'] = setup['pair']

                next_setup = mkSafeSetup(next_setup_candidate)
                if next_setup:
                    valid_setups.append(next_setup)
                    prev_tp = next_setup['tp']

                # check for more setups
                next_tp_candidate = getPriceFollowing(_tokens, next_setup_candidate['tp'], [])
                _tokens = remove_price(next_setup_candidate['tp'], _tokens)
                prev_tp = next_setup_candidate['tp']
                next_setup_candidate = getValidSetup(_type, pair, _tokens, [], div, d)
                if not next_setup_candidate and len(likely_prices) > 0:
                    next_setup_candidate = getValidSetup(_type, pair, _tokens, likely_prices, div, d)
    return valid_setups  
        
def parseSignal(t: str, d: datetime = None, p: str = ""):
    """
    Given a text with some signal, returns either Signal, SignalList or Noise. 
    """
    if t is None:
        return Noise("Empty text")

    # Extract date from signal in MT4 format
    res = re.search("\d{4}\\.\d{2}\\.\\d{2} \d\d?:\d\d?", t)
    if res != None:
        start_pos = res.start()
        # Check: expiry date
        expiry = 'EXPIR' in t.upper()
        if expiry:
            expiry_pos = t.upper().index('EXPIR')
            if expiry_pos > start_pos:
                d = datetime.strptime(t[start_pos:start_pos+16], "%Y.%m.%d %H:%M")    
        else:
            d = datetime.strptime(t[start_pos:start_pos+16], "%Y.%m.%d %H:%M")

    if not d:
        d = datetime.utcnow()
    text = normalizeText(t)
    isBuy = 'BUY' in text
    isSell = 'SELL' in text
    hasType = isBuy or isSell

    if not hasType:
        return Noise("Missing type")

    pair = getValidPair(text)
    if not pair:
        return Noise("Missing pair")
    _tokens = text.split(" ")
    if isBuy and isSell:
        _type = "BUY" if text.index("BUY") < text.index("SELL") else "SELL"

        n = text.index("SELL" if _type=="BUY" else "BUY")
        text2 = pair + " " +text[n:]
        text1 = pair + " " +text[0:n]

        ret1 = parseSignal(text1, d, p)
        ret2 = parseSignal(text2, d, p)

        if type(ret1) and type(ret2) is SignalList:
            return SignalList(ret1 + ret2)
        elif type(ret1) is Signal and not type(ret2) is Signal:
            return ret1
        elif type(ret2) is Signal and not type(ret1) is Signal:
            return ret2
    else:
        _type = "BUY" if isBuy else "SELL"    
    _prices = [float(t) for t in _tokens if isPrice(t)]

    if len(_prices)<3:
        return Noise("Less than 3 prices")

    valid_setups = find_valid_setups(_prices, _tokens, text, pair, _type, d, p)
    if type(valid_setups) is Noise:
        return valid_setups
    elif len(valid_setups) == 0:
        return None
    else:
        if len(valid_setups) == 1:
            assert(type(valid_setups[0]) is Signal)
            return valid_setups[0]
        else:
            return SignalList(valid_setups)

def valid_setup(t : str, e : float, s : float, tp : float) -> bool:
    """"Validate buy or sell prices."""
    if float(tp) <=0 or float(s) <= 0 or float(e) <= 0:
        return False
    ret = valid_buy(t,e,s,tp) or valid_sell(t,e,s,tp)
    return ret

def getValidCryptoPair(text : str) -> str:
    # Look for hashtags and $ first

    tokens = text.split(" ")
    found_pairs = [t for t in tokens if t in crypto_pairs]

    if len(found_pairs) == 0:
        # Default to counter in satoshis
        found_cryptos = [c for c in tokens if c in cryptocurrencies]
        btc_pairs = [c+"/BTC" for c in found_cryptos if (c+"/BTC") in crypto_pairs]
        found_pairs.extend(btc_pairs)

    if len(found_pairs) > 0 and pairs[0] in pairs:
        return found_pairs[0]
    
    return Noise("Missing pair")

def getValidFXPair(text : str) -> str:
    sixletters = [t for t in text.split(" ") if len(t) is 6]
    found_pairs = [p for p in sixletters if p[:3]
             in currencies and p[-3:] in currencies]
    if len(found_pairs) > 0 and pairs[0] in pairs:
        return found_pairs[0]
    return Noise("Missing pair")

def getValidPair(text: str) -> str:
    
    fx = getValidFXPair(text)
    if fx and type(fx) is str:
        return fx
    
    crypto = getValidCryptoPair(text)
    if crypto:
        return crypto
    
    return Noise("Missing pair") 

def isPrice(t: str) -> bool:
    try:
        return float(t) > 0
    except ValueError:
        return False

def getPriceFollowing(tokens : list, prevtoken : str, likely_prices : list, fallback_index : int = 0) -> float:

    if isPrice(prevtoken):
        replacements = [(t,float(t)) for t in tokens if isPrice(t) and str(float(t)) != t]
        prevtoken = str(float(prevtoken))
        if len(replacements) > 0:
            ts = "\t".join(tokens)
            for rep in replacements:
                ts = ts.replace(rep[0], str(rep[1]) + "\t")
            tokens = ts.split("\t")

    if prevtoken in tokens:
        i = next(i for i,t in enumerate(tokens) if prevtoken in t) #fails if prevtoken is not in t
    else:
        i = fallback_index
    if i < len(tokens):
        if len(likely_prices) == 0:
            nextPrices = [float(t) for t in tokens[i+1:] if isPrice(t)]
        else:
            nextPrices = [float(t) for t in tokens[i+1:] if isPrice(t) and float(t) in likely_prices]
        ret = nextPrices[0] if len(nextPrices) > 0 else 0.0
        return ret
    return 0.0

def purifySetup(s : dict) -> dict:
    if not type(s) is dict:
        return Noise("Invalid setup.")
    signal = Signal.from_dict(s)
    sanity_signal = signal.is_payout_safe()
    if sanity_signal:
        return signal
    else:
        return sanity_signal

def getValidSetup(_type : str, pair: str, tokens: list, likely_prices: list, div : int = 1, d: datetime = None) -> dict:
    _prices = [t for t in tokens if isPrice(t)]
    entry = getPriceFollowing(tokens, pair, likely_prices)
    # Only one stop loss enabled
    sl = getPriceFollowing(tokens, "SL", likely_prices)
    # At least one TP
    tp = getPriceFollowing(tokens, "TP", likely_prices)

    if not "BTC" in pair:
        precision = 5
    else:
        precision = 9

    if div > 1:
        tp = round(tp/div, precision)
        sl = round(sl/div, precision)
        entry = round(entry/div, precision)
    
    valid_setups = []
    if valid_setup(_type, entry, sl, tp):
        s = { 'entry': entry, 'sl': sl, 'tp': tp, 'pair': pair, 'date': d, 'sign': _type, 'username': '' }
        if purifySetup(s):
            return s
    if "ENTRY" in tokens:
        entry = getPriceFollowing(tokens, "ENTRY", likely_prices)
        tp = getPriceFollowing(tokens, "TP", likely_prices)
        sl = getPriceFollowing(tokens, "SL", likely_prices)

        if div > 1:
            tp = round(tp/div, precision)
            sl = round(sl/div, precision)
            entry = round(entry/div, precision)

    if valid_setup(_type, entry, sl, tp):
        s = { 'entry': entry, 'sl': sl, 'tp': tp, 'pair': pair, 'date': d, 'sign': _type, 'username': '' }
        if purifySetup(s):
            return s

    if len(likely_prices) == 3 and not ('SL' in tokens and 'TP' in tokens):
        entry = likely_prices[0]
        sl = likely_prices[1]
        tp = likely_prices[2]
        if valid_setup(_type, entry, sl, tp):
            return { 'entry': entry, 'sl': sl, 'tp': tp }

        if valid_setup(_type, entry, tp, sl):
            return { 'entry': entry, 'sl': tp, 'tp': sl }
    if len(likely_prices) > 3:
        # ALL COMBINATIONS
        xs = likely_prices

        #  -- Crear combinaciones o listas de precios candidatas
        combinations = [[x,y,z]
            for xi,x in enumerate(xs)
            for yi,y in enumerate(xs) for zi,z in enumerate(xs) if x != y and y != z and xi > yi and yi > zi]

        if pair in tokens:
            tokens.remove(pair)
            tokens = [pair] + tokens

        #  -- Las combinaciones se mapean a una lista de setups
        mapped_combos = [
            getValidSetup(_type, pair, tokens, c, div, d)
            for c in combinations]

        valid_combos = [v for v in mapped_combos if v]
        if len(valid_combos) < 1:
            pass
        elif len(valid_combos) == 1:
            #  -- Tiene un setup valido, tratar de obtener los precios
            return valid_combos[0]
            #valid_combos[0]
            #ps = list(valid_combos[0].values())
            #return getValidSetup(_type, pair, tokens, ps, div, d)
        elif len(valid_combos) >= 1:
            return valid_combos
    return False

import re
def normalizeText(t: str) -> str:
    t = t.upper()
    t = t.encode('unicode-escape')
    t = t.decode('utf-8', 'strict')
    t = re.sub("\\\\U........", " ", t)
    t = re.sub("\\\\u....", " ", t)
    t = re.sub("\\\\U....", " ", t)
    t = re.sub("\\\\n", " ", t)
    try:
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
    t = re.sub("BOUGHT","BUY",t)
    t = re.sub("SOLD","SELL",t)
    t = re.sub("BUY LIMIT","BUY",t)
    t = re.sub("LONG","BUY",t)
    t = re.sub("(SELL|BUY) TERM","",t)
    t = t.replace('💯'," ")
    t = t.replace('#'," ")
    #t = t.replace('$'," ")
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
            t = re.sub(regex,"\\g<1>\\g<2>",t)
            break
        regex = "(%s)..?(%s)" % (base,counter)
        matches = re.findall(regex, t)
        if len(matches) > 0:
            t = re.sub(regex,"\\g<1>\\g<2>",t)
            break
    t = re.sub("(\\d),(\\d)","\\g<1>.\\g<2>",t) # fix numbers
    t = re.sub("_"," _ ",t)
    t = re.sub("TG","TP",t)
    t = re.sub("SL"," SL ",t)
    t = re.sub("TP"," TP ",t)
    
    t = re.sub(" \\.(\\d+)"," \\g<1> ", t)
    t = re.sub("\\s+\\.","",t)
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
    t = re.sub("(\\d+) PIPS"," ", t) #TODO: Support relative pips parsing
    t = re.sub("((\\d+)\\.(\\d+))"," \\g<1> ", t)
    t = re.sub("((\\d+)\\.(\\s+))"," ", t)
    t = re.sub("SELL"," SELL ", t)
    t = re.sub("BUY"," BUY ", t)
    t = re.sub('TP(.+)\\s+(\\d+)\\s+((\\d+)\\.(\\d+))(SL?)',' TP \\g<3> ', t)
    t = t.replace(',',' ').replace(":"," ")
    t = t.replace('[',' ').replace(']',' ')
    t = t.replace('(',' ').replace(')',' ')
    t = re.sub(':',' ', t)
    t = re.sub("TP\\s+1\\s+"," TP ",t)
    t = re.sub("TP\\s+2\\s+"," TP ",t)
    t = re.sub("TP\\s+3\\s+"," TP ",t)
    t = re.sub('GOLD','XAUUSD',t)

    return t
