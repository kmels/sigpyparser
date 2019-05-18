import pandas as pd
import datetime
from datetime import datetime

cardinality = lambda xs: len(set(xs))

def has_consensus(_vs):
    vs = cardinality(_vs)
    _freq = lambda ys, y: len([yi for yi in ys if yi == y])
    _freqs = [(_freq(_vs, v)) for v in _vs]
    return vs == 1 or (vs > 1 and vs < len(_vs) and cardinality(_freqs) != 1)

class CalificacionConsensus(list):
    def __init__(self, cs=[]):
        if type(cs) is not list:
            raise ValueError()
        self.cs = cs

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

    def get_consensus(self):
        if not self.has_consensus():
            raise EOFError
        state = [s['state'] for s in self.cs]
        event = [s['event'] for s in self.cs]
        if cardinality(state) == 1 and cardinality(event) == 1:
            return (state[0], event[0])
        else:
            #find the most frequent
            _freq = lambda ys, y: len([yi for yi in ys if yi == y])
            st = [(st, _freq(state, st)) for st in state]
            st = sorted(st, key=lambda k: k[1])
            ev = [(ev, _freq(event, ev)) for ev in event]
            ev = sorted(ev, key=lambda k: k[1])
            return (st[-1][0], ev[-1][0])

    def has_consensus(self):
        return has_consensus([s['state'] for s in self.cs]) and has_consensus([s['event'] for s in self.cs])
