import hashlib
import math

from datetime import datetime

def myhash(t : str):
    """Returns an integer as hash using sha256"""
    h = hashlib.sha256()
    h.update(t.encode('utf-8'))
    return int(h.hexdigest()[0:12],16)

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

def pips_diff(p1: float, p2: float, pair: str) -> int:
    pips =  abs(p1 - p2)*100
    if not 'JPY' in pair and not 'XAU' in pair:
        pips *= 100
    if 'XAU' in pair:
        pips /= 10
    if 'BTC' in pair:
        pips /= 100000
    return pips

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
