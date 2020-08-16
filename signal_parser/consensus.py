import pandas as pd
import datetime
from datetime import datetime

cardinality = lambda xs: len(set(xs))

#  -- Consensus by majority (more than half)
def has_consensus(_vs):
    if len(_vs) == 0:
        return False
    size = cardinality(_vs)
    if size == 1:
        return True
    _freq = lambda ys, y: len([yi for yi in ys if yi == y])
    _freqs = dict([(_freq(_vs, v),v) for v in _vs])

    #   -- only 1 frequency means a tie
    if cardinality(_freqs) == 1:
        return False

    #  -- consensus when there is a majority 
    return len(_freqs) == size

#  -- Consensus by tie (same event cardinality)
def has_weak_consensus(_vs):
    vs = cardinality(_vs)
    _freq = lambda ys, y: len([yi for yi in ys if yi == y])
    _freqs = [(_freq(_vs, v)) for v in _vs]
    return cardinality(_freqs) == 1 and min(_freqs) > 1
    
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

    def __str__(self):
        return self.cs.__str__()

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

    def get_consensus(self, try_weak = True):
        if not self.has_consensus():
            if not try_weak:
                raise Exception("Does not have consensus or weak consensus")
            else:
                return self.get_weak_consensus()
                
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
        ret = weak_view.get_consensus()
        return ret

    def has_consensus(self):
        #sts = [s['state'] for s in self.cs]
        evs = [s['event'] for s in self.cs]
        return has_consensus(evs)

    def has_weak_consensus(self):
        sts = [s['state'] for s in self.cs]
        evs = [s['event'] for s in self.cs]
        return has_weak_consensus(sts) and has_weak_consensus(evs) and cardinality(sts) == cardinality(evs)
