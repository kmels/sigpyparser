import pandas as pd
import datetime
from datetime import datetime
import json

def serialize_date(o):
    if isinstance(o, datetime):
        return o.strftime("%Y.%m.%d %H:%M")

cardinality = lambda xs: len(set(xs))

#  -- Consensus by majority (more than half)
def has_consensus(_vs):
    if len(_vs) == 0:
        return False
    size = cardinality(_vs)
    if size == 1:
        return True
    _freqs = {v: _vs.count(v) for v in _vs}
    _counts = list(_freqs.values())
    #   -- only 1 frequency means a tie
    if cardinality(_counts) == 1:
        return False
    #  -- consensus when there is a majority 
    max_count = max(_counts)
    return _counts.count(max_count) == 1
    #return cardinality(_freqs.values()) == size

#  -- Consensus by tie (same event cardinality)
def has_weak_consensus(_vs):
    vs = cardinality(_vs)
    _freq = lambda ys, y: len([yi for yi in ys if yi == y])
    _freqs = [(_freq(_vs, v)) for v in _vs]
    
    is_tie = cardinality(_freqs) == 1 and min(_freqs) >= 1
    max_freq = max(_freqs)
    is_weak_able = any([_freq(_vs, wa) == max_freq for wa in _vs if wa in ['tp_hit','sl_hit','closed','open', 'O','P','C']])
    return is_tie and is_weak_able

class Outcome(dict):
    def __init__(self, hash, signer, pair, published_on, opened_on, invalidated_on,
                    last_checked, last_available, event, state):
        self['hash'] = hash
        self['signer'] = signer
        self['pair'] = pair
        self['published_on'] = published_on
        self['opened_on'] = opened_on
        self['invalidated_on'] = invalidated_on
        self['last_checked'] = last_checked
        self['last_available'] = last_available
        self['event'] = event
        self['state'] = state

    @staticmethod
    def from_dict(it: dict):
        return Outcome(it['hash'],it['signer'],it['pair'], it['published_on'],
                            it['opened_on'],it['invalidated_on'],it['last_checked'], it['last_available'],
                            it['event'],it['state'])

class OutcomeConsensus(list):
    def __init__(self, cs=[]):
        if type(cs) is not list:
            raise ValueError("Expecting parameter to be of type: list")
        self.cs = cs

    def __repr__(self):
        return json.dumps(self.json(), default = serialize_date)

    def __str__(self):
        return json.dumps(self.json(), default = serialize_date)

    def json(self):
        it = self.get_consensus()
        st = it[0]

        if st == 'C':
            avg_open = pd.Series([c['opened_on']['ts'] for c in self.cs if c['state'] == st]).mean()
            avg_close = pd.Series([c['invalidated_on']['ts'] for c in self.cs if c['state'] == st]).mean()
            return {
                "duration": (avg_close - avg_open) / 3600.0,
                "opened_on":  datetime.fromtimestamp(avg_open),
                "invalidated_on":  datetime.fromtimestamp(avg_close),
                "event": it[1],
                "state": it[0]
            }
        else:
            return {
                "event": it[1],
                "state": it[0],
            }

    #  -- Checks for majority or for weak consensus without pending
    def get_consensus(self, try_weak = True):
        if not self.has_consensus():
            if not try_weak:
                raise Exception("Does not have consensus or weak consensus")
            else:
                #  -- Try without Pending
                try:
                    return self.get_weak_consensus()
                except:
                    #  -- Try close over open (greedy)
                    try:
                        return self.get_weak_consensus(st = 'C')
                    except:
                        return self.get_weak_consensus(ev = 'open')
                        

        state = [s['state'] for s in self.cs]
        event = [s['event'] for s in self.cs]
        if cardinality(state) == 1 and cardinality(event) == 1:
            return (state[0], event[0])
        else:
            #find the most frequent
            _freq = lambda ys, y: len([yi for yi in ys if yi == y])

            ev = [(ev, _freq(event, ev)) for ev in event]
            ev = sorted(ev, key=lambda k: k[1])

            consensus_ev = ev[-1][0]

            state = [s['state'] for s in self.cs if s['event'] == consensus_ev]
            st = [(st, _freq(state, st)) for st in state]
            st = sorted(st, key=lambda k: k[1])

            return (st[-1][0], consensus_ev)

    def get_weak_consensus(self, st = None, ev = None):
        if not self.has_weak_consensus():
            raise Exception("Does not have weak consensus")
        
        if ev != None and st != None:
            is_intended = lambda s: s['state'] == st and s['event'] == ev
        elif ev != None and st == None:
            is_intended = lambda s: s['event'] == ev
        elif st != None and ev == None:
            is_intended = lambda s: s['state'] == st
        elif st == None and ev == None:
            is_intended = lambda s: s['state'] != 'P'

        stev_elems = [{'state': s['state'], 'event': s['event']} for s in self.cs if is_intended(s)]

        weak_view = OutcomeConsensus(stev_elems)
        try:
            return weak_view.get_consensus(try_weak = False)
        except Exception as e:
             try:
                 return self.get_weak_consensus(st = 'I')
             except:
                 raise e
    #  -- Returns true iff there is a majority event
    def has_consensus(self):
        evs = [s['event'] for s in self.cs]
        return has_consensus(evs)

    #  -- Returns true iff there is a tie and "pending" is part of the tie ("pending" is not really a good result so can be ignored)
    def has_weak_consensus(self):
        sts = [s['state'] for s in self.cs]
        evs = [s['event'] for s in self.cs]
        return has_weak_consensus(sts) and has_weak_consensus(evs) and cardinality(sts) == cardinality(evs)
