from datetime import datetime
import numpy as np
signal_payout = lambda os: np.array([o for o in os]).mean() if type(os) is list else os

def mkpips(d,p):
    m = d * 100
    if not 'JPY' in p and not 'XAU' in p:
        m *= 100
    if 'XAU' in p:
        m /= 10
    return abs(m)

def track_record_of_selection(signals):
    init = datetime.now()
    signals = sorted(signals, key = lambda x: x.get('signal', {}).get('date',''))

    last_closed_trade = None
    roi = 0
    pips = 0

    nsignals = len(signals)
    nclosed = 0
    nwins = 0
    nlosses = 0
    nbreakevens = 0
    ninvalids = 0
    nopened = 0
    unscored = 0
    npending = 0
    missing_consensus = 0
    unanimous_signals = 0

    risk = 0.005
    geometric_winratio = 1
    geometric_odds = 1

    high_watermark = 0
    low_underwater = 0

    positive_streak = 0
    negative_streak = 0

    max_consecutive_losses = 0
    max_consecutive_wins = 0

    roi_since_high_watermark = 0
    volatility = 0 # abs(high watermark) + abs(low underwater)
    worst_drawdown = 0 #high-low, but low after high

    pain = 0
    gain = 0

    for closed_score in signals:
        signal = closed_score['signal']
        if not 'odds' in signal:
            if type(signal['tp']) is list:
                signal['odds'] = [abs(tp-signal['entry']) / abs(signal['sl']-signal['entry']) for tp in signal['tp']]
            else:
                signal['odds'] = abs(signal['tp']-signal['entry']) / abs(signal['sl']-signal['entry'])
        payoff = signal_payout(signal['odds'])

        st_consensus = closed_score['state']
        ev_consensus = closed_score['event']
        # sum if closed
        if st_consensus == 'C':
            close_timestamp = closed_score['invalidated_on']['ts']
            open_timestamp = closed_score['opened_on']['ts']

            if not last_closed_trade or close_timestamp > last_closed_trade:
                last_closed_trade = close_timestamp

            nclosed += 1

            signal['duration'] = close_timestamp - open_timestamp

            # sum if  wins
            loss = ev_consensus == "sl_hit"
            win = ev_consensus == "tp_hit"
            fact = 1
            if loss:
                if type(signal['tp']) is list:
                    fact = len(signal['tp'])
                    #nclosed += (fact - 1)
                nlosses += 1
                roi -= risk
                print(signal)

                pips -= mkpips(signal['entry'] - signal['sl'], signal['pair'])
                positive_streak = 0
                negative_streak += 1
                roi_since_high_watermark -= risk
                pain += risk
                if negative_streak > max_consecutive_losses:
                    max_consecutive_losses = negative_streak
            if win:
                payoff_ = signal['tp_pips'] / signal['sl_pips']
                if type(signal['tp']) is list:
                    fact = len(signal['tp'])

                roi += risk/fact*payoff_
                nwins += 1 / fact
                geometric_winratio = geometric_winratio * (1 + risk/fact)

                if type(signal['tp']) is list:

                    pips += mkpips(signal['entry'] - signal['tp'][0], signal['pair']) / fact

                    if len(closed_score.get('secondary_scores',[])) != len(signal['tp']):
                        print("MISSING SECONDARY SCORES ")

                    for i, ssc in enumerate(closed_score.get('secondary_scores',[])):

                        if ssc['state'] != 'C':
                            continue
                        #nclosed += 1
                        if ssc['event'] == 'sl_hit':
                            nbreakevens += 1
                        if ssc['event'] == 'tp_hit':
                            if not 'tp_pips' in ssc['signal']:
                                print("MISSING TP PIPS: ", ssc)

                            #pips += ssc['signal'].get('tp_pips',0)
                            pips += mkpips(signal['entry'] - signal['tp'][i+1], signal['pair']) / fact
                            nwins += 1 / fact
                            positive_streak += 1
                            payoff_ = ssc['signal']['tp_pips'] / ssc['signal']['sl_pips']
                            roi += risk/fact*payoff_
                            gain += risk/fact*payoff_
                            roi_since_high_watermark += risk/fact*payoff_
                            roi_since_high_watermark += risk/fact*payoff_
                            geometric_winratio = geometric_winratio * (1 + risk/fact)

                else:
                    pips += mkpips(signal['entry'] - signal['tp'], signal['pair'])

                payoff_ = signal['tp_pips'] / signal['sl_pips']

                positive_streak += 1
                negative_streak = 0
                roi_since_high_watermark += risk/fact*payoff_
                gain += risk/fact*payoff_

                if positive_streak > max_consecutive_wins:
                    max_consecutive_wins = positive_streak

            if roi > high_watermark:
                high_watermark = roi
                roi_since_high_watermark = 0
            elif roi < low_underwater:
                low_underwater = roi

            if roi_since_high_watermark < worst_drawdown:
                worst_drawdown = roi_since_high_watermark

            geometric_odds = geometric_odds * (1+risk*payoff)
        # sum if invalidated
        if st_consensus == 'I':
            ninvalids += 1
        if st_consensus == 'R':
            unscored += 1
        if st_consensus == 'P':
            npending += 1
        # sum if open
        if st_consensus == 'O':
            nopened += 1

    if nclosed == 0:
        winratio = -1
        avgpayout = -1
    else:
        winratio = nwins*1.0/nclosed
        if len(signals)>0:
            avgpayout = np.array([signal_payout(s['signal']['odds']) for s in signals]).mean()
        else:
            avgpayout = -1

    ms = (datetime.now()-init).total_seconds()*1000
    #logging.debug("Processed in %.1f ms" % (ms))

    if nclosed == 0:
        root = -1
    else:
        root = 1/(1.0*nclosed)
    geo_mean_payout = pow(geometric_odds, root)
    geo_mean_payout = round((geo_mean_payout-1)/risk,2)
    geo_expected_win = pow(geometric_winratio, root)
    geo_expected_win = round((geo_expected_win-1)/risk,2)

    if worst_drawdown == 0:
        sharpe_ratio = roi/risk
    else:
        sharpe_ratio = roi/abs(worst_drawdown)

    if pain == 0:
        gain_to_pain_ratio = 0
    else:
        gain_to_pain_ratio = round(gain/pain,2)
    #assert nclosed == (nwins+nlosses)
    geometric_kelly = 0
    if geo_mean_payout:
        geometric_kelly = round((geo_expected_win*(geo_mean_payout+1)-1)/geo_mean_payout,2)

    if not last_closed_trade:
        last_closed_trade = 0

    last_closed_datetime = datetime.fromtimestamp(last_closed_trade)
    last_closed_delta = datetime.utcnow() - last_closed_datetime

    return {
        "process_time_in_ms": ms,
        'roi': round(roi*100,2),
        'pips': round(pips,1),
        'winratio': float("%.2f" % winratio),
        "geometric_winratio": geo_expected_win,

        'avgpayout': float("%.2f" % avgpayout),
        "geometric_avg_payout": geo_mean_payout,

        'nwins': int(round(nwins,0)),
        'nlosses': nlosses,
        'nclosed': nclosed,

        'nopened': nopened,
        'npending': npending,
        'ninvalids': ninvalids,
        "unscored": unscored,

        'missing_consensus': missing_consensus,
        'unanimous_signals': unanimous_signals,
        'nsignals': nsignals,

        "expected_kelly_risk": round((winratio*(avgpayout+1)-1)/avgpayout,2),
        "geometric_kelly_risk": geometric_kelly,

        "sharpe_ratio": round(sharpe_ratio,2),
        "gain_to_pain_ratio": round(gain_to_pain_ratio,2),

        'max_consecutive_wins': max_consecutive_wins,
        'max_consecutive_losses': max_consecutive_losses,
        'worst_drawdown': worst_drawdown,
        'high_watermark': high_watermark,

        'last_closed_datetime': last_closed_datetime.strftime("%Y.%m.%d %H:%M"),
        'last_closed_delta': str(last_closed_delta),
        'last_closed_delta_seconds': int(last_closed_delta.total_seconds())
    }