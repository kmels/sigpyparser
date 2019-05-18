import unittest
from signal_parser import *
from datetime import datetime

today = datetime.now().replace(second=0).replace(microsecond=0)

def _parseSignal(t: str):
    signal = parseSignal(t,today,'p')
    if not signal:
        return None
    return signal

class TestParser(unittest.TestCase):

    def _testParser(self,text,expected):
        parsedSignal = _parseSignal(text)
        self.assertEqual(
            parsedSignal,
            expected,
            "\n\tEXPECTED: " + str(expected) + ".\n\tRESULT:   " +
            str(parsedSignal)
        )

    def test_1(self):
        self.assertEqual(
            parseSignal("GOLD BUY FROM CMP 1331 SL = 1327 TP = 1370", today, 'p'),
            Signal(1331.0,1327.0,1370.0,today,'BUY','p','XAUUSD')
        )

    def test_2(self):
        self.assertEqual(
            _parseSignal("""🇺🇸🇨🇭UsdChf↘️SELL➡️Now

☑️At ➡️0.9541
➖➖➖➖➖
❌Sl➡️0.9565
➖➖➖➖➖
✅Tp➡️0.9480"""),
            Signal(0.9541, 0.9565, 0.9480, today, 'SELL', 'p', 'USDCHF')
        )

    def test_3(self):
        self.assertEqual(
            _parseSignal("""🇳🇿🇺🇸NzdUsd↗️BUY➡️Now

☑️At ➡️0.7177
➖➖➖➖➖
❌Sl➡️0.7150
➖➖➖➖➖
✅Tp➡️0.7227"""),
            Signal(0.7177,0.7150,0.7227,today,'BUY','p','NZDUSD')
        )

    def test_4(self):
        self.assertEqual(
            _parseSignal("""Buy NZDUSD
0.7174
Sl 0.7124
Tp 0.7225"""),
            Signal(0.7174,0.7124,0.7225,today,'BUY','p','NZDUSD')
        )

    def test_5(self):
        self.assertEqual(
            _parseSignal("""Buy USDJPY
108.75
Sl 108.2
Tp 109.25"""),
            Signal(108.75,108.2,109.25, today,'BUY','p','USDJPY')
        )

    def test_6(self):
        self.assertEqual(
            _parseSignal("""Usdjpy buy now
@  109.400
Sl  108.800
Tp 110.800"""),
            Signal(109.4,108.8,110.80, today,'BUY','p','USDJPY')
        )

    def test_7(self):
        self.assertEqual(
            _parseSignal("""Gold Buy limit
@ 1336.00
Sl 1330.00
Tp 1350.00"""),
            Signal(1336.0,1330.0,1350.0,today,'BUY','p','XAUUSD')
        )

    def test_7b(self):
        slpips = Signal(1336.0,1330.0,1350.0,today,'BUY','p','XAUUSD').sl_pips()
        self.assertEqual(slpips, 60)

    def test_8(self):
        parsedSignal = _parseSignal("""EURJPY sell now
@ 130.900
sl @131.500
tp @ 130.000""")
        expected = Signal(130.9,131.5,130.0,today,'SELL','p','EURJPY')
        self.assertEqual(
            parsedSignal,
            expected,
            "\n\tEXPECTED: " + str(parsedSignal) + ".\n\tRESULT:   " +
            str(expected)
        )

    def test_9(self):
        self.assertEqual(
            _parseSignal("""eurnzd

sell now
@1.66200

sl @1.66900
tp @ 1.64500"""),
            Signal(1.662,1.669,1.645,today,'SELL','p','EURNZD')
        )

    def test_10(self):
        self.assertEqual(
            _parseSignal("""[ GBPJPY ] ❗️🎄BUY  💯💯❗️

        ‼️  [entry point] 🌻: [ 141.750 ]

        ♨️  [stop loss] 🥀: [ 141.150 ]

        ✅  [take profit] 🌹: [ 143.000 ]"""),
            Signal(141.75,141.15,143.0,today,'BUY','p','GBPJPY')
        )

    def test_11(self):
        self.assertEqual(
            _parseSignal("""🕴[ EURAUD ] ❗️🎄SELL  💯💯❗️
    (risky trade.... after 30 minit AUD news so carefull)

    ‼️  [entry point] 🌻: [ 1.48850 ]

    ♨️  [stop loss] 🥀: [ 1.49350 ]

    ✅  [take profit] 🌹: [ 1.47500 ] """),
            Signal(1.4885,1.4935,1.475,today,'SELL','p','EURAUD')
        )

    #FIXME
    def notest_12(self):
        text = b'\xe2\x97\xbe\xef\xb8\x8f'
        text += b'BUY EURUSD\xe2\x97\xbe\xef\xb8\x8fENTRY1.1905\n'
        text += b'1\xe2\x96\xaa\xef\xb8\x8fTP1.19171\n2'
        text += b'\xe2\x96\xaa\xef\xb8\x8fTP1.19271\n3\xe2'
        text += b'\x96\xaa\xef\xb8\x8fTP1.19371\n4\xe2\x96'
        text += b'\xaa\xef\xb8\x8fTP1.19471\n5\xe2\x96\xaa'
        text += b'\xef\xb8\x8fTP1.19571\n\xe2\x96\xaa\xef'
        text += b'\xb8\x8fSL1.1888'

        self._testParser(str(text),Signal(1.1905,1.1888,1.19171,today,'BUY','p','EURUSD'))

    def test_13(self):
        self._testParser("""#FREE SIGNAL 3⃣

    #GBPJPY  - BUY NOW
    En@143.50

    SL@142.00    - 150     -3%

    TP@146.50   +300     +6%

    Trade With Care 🤠
    🔔 RISK 《3%》
    🔔TP OR  SL""",
            Signal(143.5,142.0,146.5,today,'BUY','p','GBPJPY'))

    def test_14(self):
        self._testParser("""🚩SIGNAL FREE 5⃣  SELL EURUSD                                       EN      1.0740
#TP1    1.0670  +70
#TP2    1.0620  +120
#TP3    1.0570  +170
#SL       1.0810  -70
#🔘RISK (3%)""", Signal(1.0740,1.0810,1.0670,today,'SELL','p','EURUSD'))

    def test_15(self):
        self._testParser("""🚩SIGNAL FREE 6⃣ SELL AUDJPY                                        EN      85.30
TP1    83.50  +180
TP2    82.00  +330
TP3    80.50  +480
TP4    78.50  +680
SL       88.00  -270
🔘RISK (3%)""",
            Signal(85.3,88.0,83.50,today,'SELL','p','AUDJPY')
        )

    def test_16(self):
        self._testParser("AUDCHF SELL 0.766 SL 0.776 TP 0.75",
            Signal(0.766, 0.776, 0.75, today, 'SELL', 'p', 'AUDCHF'))

    def test_17(self):
        self._testParser("""GBPJPY
BUY LIMIT @ 150.70 - 150.66
TP 1 151.01
TP 2 151.35
TP 3 151.75
TP 4 154.33
SL 150.11""", Signal(150.70, 150.11, 151.01, today, 'BUY', 'p', 'GBPJPY'))

    def test_18(self):
        self._testParser("""AUDUSD
BUY @ 0.8011 - 0.8020
TP 1 0.8057
TP 2 0.8073
TP 3 0.8124
TP 4 0.8172
SL 0.7976""", Signal(0.8011, 0.7976, 0.8057, today, "BUY","p","AUDUSD"))

    def test_19(self):
        self._testParser("""NZDUSD
SELL (:point_down:)
@ 0.72300
TP1: 0.71300
TP2: 0.70300
SL: 0.73300""", Signal(0.723, 0.733,0.713, today, "SELL","p","NZDUSD"))

    def test_20(self):
        self._testParser("""🌹FOREX MINISTER 🌹

(500 DOLLER ACCOUNT MINIMUM)

1)  USDCAD (SETUP PLAN)

👉 1st buy limit set at
@ 1.24700 (lot size 0.01)

👉 2nd buy limit set at
@ 1.24000 (lot size 0.03)

-> set this setup and enjoy....
99.9% Sure Profit...

👉 TP SET 1.29000
👉NO SL

🌹FOREX MINISTER 🌹""", None)

    def test_21(self):
        self._testParser("""$$$ NEW TRADE $$$
Pair @ Australian Dollar / New Zealand Dollar (audnzd)
Direction @ Bearish
Entry @ 1.09150 (market price)
Stop loss @ 1.09950
1st target @ 1.08400
2nd target @ 1.07150""", Signal(1.0915, 1.0995, 1.0840, today, "SELL", "p", "AUDNZD"))

    def test_22(self):
        self._testParser("""$$$ NEW TRADE $$$
Pair @ New Zealand Dollar / Swiss Franc (nzdchf)
Direction @ Bullish
Entry @ 0.69780 (market price)
Stop loss @ 0.68985
1st target @ 0.70535
2nd target @ 0.71780""", Signal(0.6978, 0.68985, 0.70535, today, "BUY","p","NZDCHF"))

    def test_23(self):
        self._testParser("""USDCAD Sell
@1.23650
TP:1.23000
SL:1.24100""", Signal(1.2365, 1.241, 1.23, today, "SELL", "p", "USDCAD"))

    def test_24(self):
        self._testParser("""Trade Direction: BUY
Forex Pair: USDCAD
Timeframe: 1 Hour
Entry Price: 1.25623
Take Profit: 1.26423
Safety Stop Loss: 1.24823
Signal Expiry Time: 2017.10.06 20:31:32""", Signal(1.25623, 1.24823, 1.26423, today, "BUY", "p", "USDCAD"))

    def test_25(self):
        self._testParser("""Trade Direction: SELL
Forex Pair: USDJPY
Timeframe: 4 Hour
Entry Price: 109.563
Take Profit: 109.063
Safety Stop Loss: 110.063
Signal Expiry Time: 2017.09.08 06:55:45""", Signal(109.563, 110.063, 109.063, today, "SELL", "p", "USDJPY"))

    def test_26(self):
        self._testParser("""Gold trendline retest
Sell limit: 1314.68
Stop: 1337.74
Target: 1263.19 [Risk to reward ratio 2.23]""", Signal(1314.68,1337.74,1263.19, today, "SELL", "p", "XAUUSD"))

    def test_27(self):
        self._testParser("""EURUSD filling the gap
Sell limit: 1.19380
Stop: 1.19885
Target 1: 1.18437 [Risk to reward ratio 1.84]
Target 2: 1.16922 [Risk to reward ratio 4.94]""", Signal(1.1938, 1.19885, 1.18437, today, "SELL", "p", "EURUSD"))

    def test_28(self):
        self._testParser("""Buy EUR USD 1.1754
SL 1.1680
TP 1.1850""", Signal(1.1754, 1.1680, 1.1850, today, "BUY", "p", "EURUSD"))

    def test_29(self):
        self._testParser("""Sell NZD USD 0.7176
SL 0.7220
TP 0.7100""", Signal(0.7176, 0.7220, 0.71, today, "SELL", "p", "NZDUSD"))

    def test_30(self):
        self._testParser("""signal 37
 chfjpy sell : 114.830

sl : 50 pip
tp1 : 100 pip
tp 2 : 180 pip

@mql5signal""", None)

    def test_31(self):
        self._testParser("""Sell eur/jpy @ 132.950
Tp:132.650
Sl:133.500""", Signal(132.95, 133.5, 132.65, today, "SELL", "p", "EURJPY"))

    def test_32(self):
        self._testParser("""Currency Pair USD/CAD
Short from 1.2615
Target 1.2000
Stop/Loss 1.3000""", Signal(1.2615, 1.3, 1.2, today, "SELL", "p", "USDCAD"))

    def test_33(self):
        self._testParser("""NO 6 : DEUTSCHE BANK

Currency Pair EUR/CHF
Long from 1.1420
Target 1.2000
Stop/Loss 1.1200

Floating (pips) +58""", Signal(1.1420,1.12,1.2,today,"BUY","p","EURCHF"))

    def test_34(self):
        self._testParser("""5. Gbpjpy buy limit 146.50 Tp 150.00-153.00 sL (daily close under 145.20)""",
            Signal(146.5, 145.2, 150, today, "BUY", "p", "GBPJPY"))

    def test_35(self):
        self._testParser("""Buy limit Eurusd 1.1200 -1.1180 Tp 1.1300-1.1405 sL (if 4h candle close under 1.1150 then exit)/""",
            Signal(1.12, 1.1150, 1.13, today, "BUY", "p", "EURUSD")
        )

    def test_36(self):
        self._testParser("""$$$ UPDATE $$$
Pair @ Gold
Direction @ Bullish

1st target @ 1263.01 hit for partial profit.
We move the stop loss to 1248. This way we reduce our risk to 65 pips.""", Noise("Less than 3 prices"))

    def test_37(self):
        self._testParser("""buy limit on gold 1345_1347 sl 1340 tp 1358""", None)

    def test_38(self):
        self._testParser("""Eurusd Sell Now  1.07940
Sl 1.08550
Tp 0.0700""", None)

    def test_39(self):
        self._testParser("""Signal . no 15
SELL
GBPJPY @ 144.11
SL.        : 144.61
TP 1.    : 143.61
TP 2.    : 143.11""", Signal(144.11, 144.61, 143.61, today, "SELL", "p", "GBPJPY"))

    def test_40(self):
        self._testParser("""Signal . no 15
SELL
GBPJPY @ 144.11
SL.        : 144.61
TP 1:    : 143.52""", Signal(144.11, 144.61, 143.52, today, "SELL", "p", "GBPJPY"))

    def test_41(self):
        self._testParser("""USDCAD
Buy@1.25050
TP:1.2566
SL:1.2434""", Signal(1.2505,1.2434,1.2566,today,"BUY","p","USDCAD"))

    def test_42(self):
        self._testParser("""EURJPY Sell @132.650,133.000
TP:131.850,131.000
SL:133.500""", Signal(132.65, 133.5, 131.85, today, "SELL", "p", "EURJPY"))

    def test_43(self):
        self._testParser("""GBPAUD BUY NOW AT 1.68015
T.P 1
1.68321
T.P 2
1.68632
T.P 3
1.68899
S.L
1.67432""", Signal(1.68015,1.67432,1.68321, today,"BUY","p","GBPAUD"))

    def test_44(self):
        self._testParser("""SELL NOW EURUSD AT 1.1764
T.p 1
1.17170
T.p 2
1.16957
T.p 3
1.16779
S.l
1.1840""", Signal(1.1764, 1.1840, 1.1717, today, "SELL", "p", "EURUSD"))

    def test_45(self):
        self._testParser("""Free Signals 4 All:
Sell Gbpnzd at cmp 1.7610
Tp1 1.7517
Tp2 1.7419
Sl 1 7786💴💴💴💴💴💵💵💵""", None)

    def test_46(self):
        self._testParser("""Free Signals 4 All:
Sell Gbpnzd at cmp 1.7610
Tp1 1.7517
Tp2 1.7419
Sl 1.7786💴💴💴💴💴💵💵💵""", Signal(1.7610, 1.7786, 1.7517, today, "SELL", "p", "GBPNZD"))

    def test_47(self):
        self._testParser("""paid signals:
Sell EUR GBP 0.8870
SL 0.8950
TP 0.8700""", Signal(0.8870, 0.8950, 0.87, today,"SELL","p","EURGBP"))

    def test_48(self):
        self._testParser("""Signal (1)
Buy EUR/USD 1.17450
Tp1 1.17700
Tp2 1.17950
Sl 1.17000""", Signal(1.1745, 1.17, 1.177, today, "BUY", "p", "EURUSD"))

    def test_49(self):
        self._testParser("""# GBP NZD - Sell Again @ 1.8941 - SL : 1.8975 - TP : 1.8860 - 1.8820 - 1.8780""",
        Signal(1.8941,1.8975,1.886,today,"SELL","p","GBPNZD"))

    def test_50(self):
        self._testParser("""# EUR AUD - Sell @ 1.4934 - SL : 1.4995 - TP : Trailing STOP or 1.4910 - 1.4875""",
        Signal(1.4934,1.4995,1.4910,today,"SELL","p","EURAUD"))

    def test_51(self):
        self._testParser("""Gbpjpy sell now @ 149.25
S.l 149.75
T.p 147 """, Signal(149.25,149.75,147,today,"SELL","p","GBPJPY"))

    def test_52(self):
        self._testParser("""Gold sell now @ 1312
S.l 1317
T.p 1308
T.p2 1305""", Signal(1312, 1317, 1308, today, "SELL", "p", "XAUUSD"))

    def test_53(self):
        self._testParser("""Gold buy now @ 1300
More buy @ 1296
S .l for both Trade 1290
T.p1 1310
T.p2 1213""", Signal(1300,1290,1310, today,"BUY","p","XAUUSD"))

    def test_54(self):
        self._testParser("""SELL USD/CHF from ( 0.9775-0.9785)/$
S.L 0.9805 (25 Pip )
T.P : 0.9670 (110 Pip )""", Signal(0.9775,0.9805,0.9670,today,"SELL","p","USDCHF"))

    def test_55(self):
        self._testParser("""GBP/USD Sell From {1.2735_1.2740/$}
1st T.P:1.2670/$ (65 PiP)
S.L: @1.2770/$ (30 pip)""", Signal(1.2735, 1.277, 1.267, today,"SELL","p","GBPUSD"))

    def test_56(self):
        self._testParser("""Sell\nNzdusd\n0.7510\nStoploss\n0.7530\nTp..0.7450""",
        Signal(0.751,0.753,0.745,today,"SELL","p","NZDUSD"))

    def test_57(self):
        self._testParser("""Usdchff\nBuy\n0.9725\nSl..0.9620\nTp\n0.9950""",
        Signal(0.9725,0.962,0.995,today,"BUY","p","USDCHF"))

    def test_58(self):
        self._testParser("""🌹FOREX MINISTER 🌹

99% sure profit ✅

👉SHORT TERM OR MID TERM 👈

1)  USDJPY  (SETUP PLAN)

👉 1st sell now
@ 113.000(lot size 0.01)

👉 2nd sell limit set at
@ 114.000 (lot size 0.02)

👉 3rd sell limit set at
@ 115.200 (lot size 0.02)

👉 4th sell limit set at
@ 116.300(lot size 0.03)


-> set this setup and enjoy....
99.9% Sure Profit...

👉 TP SET 110 (300 PIP)
👉SL SET~~~~~~~~

🌹FOREX MINISTER 🌹""", None)

    def test_59(self):
        self._testParser("""
        USDJPY::\nbullish but is possible to retest 105.70-85 targeting 108.00-111.10 , you can buy it from this area with sL 50 pips or ( if a daily candle close under this zone)
        """, None)

    def test_60(self):
        self._testParser("""long term signal AUDCHF sell now 0.7525
SL :  0.7550
TP1:  0.7023
TP2 : 0.6725""", Signal(0.7525,0.7550,0.7023,today,"SELL","p","AUDCHF"))

    def test_61(self):
        self._testParser("""https://www.tradingview.com/chart/EURUSD/FTLH5hmC-EURUSD-Short-as-soon-as-the-market-opens/
EURUSD bearish fib idea - daily timeframe
Sell limit: [Enter when market opens]
Stop: 1.17787
Target 1: 1.14553 [Risk to reward ratio 2.18]
Target 2: 1.12987 [Risk to reward ratio 3.72]""", None)

    def test_62(self):
        self._testParser("""🌹FOREX MINISTER 🌹

100% sure profit ✅

👉MID TERM 👈

1)  EURAUD  (SETUP PLAN)

👉 1st sell limit set at
@ 1.55000 (lot size 0.01)

👉 2nd sell limit set at
@ 1.56500 (lot size 0.01)

👉 3rd sell limit set at
@ 1.58000 (lot size 0.02)


-> set this setup and enjoy....
99.9% Sure Profit...

👉 TP SET 1.50000(500 pip)
👉SL SET~~~~~~~~

🌹FOREX MINISTER 🌹""", None)

    #def test_63(self):
    #    self._testParser("""BUY BTCUSD 7000 TP 8000 SL 6800""", Signal(7000,8000,6800,today,"BUY","p","BTCUSD"))

    def test_64(self):
        self._testParser("""BUY EURUSD 1.1686 TP 1.1725 SL 1.1646""", Signal(1.1686,1.1646,1.1725,today, "BUY", "p", "EURUSD"))

    def test_65(self):
        self._testParser("""Riskly Trade :✳️✳️
Buy Gbp/Jpy @ 145.79
Tp - 146.85
Sl - 145.50 (29 pips)""", Signal(145.79, 145.5, 146.85, today, "BUY", "p", "GBPJPY"))

    def test_66(self):
        self._testParser("""forex center:
instant execution
🔴SELL AUDNZD @ 1.10780
🔸stop loss @ 1.11881
🔷 take profit@ 1.10445
lot size: 0.01 at 500 usd
SIGNAL NO:33""", Signal(1.1078, 1.11881, 1.10445, today, "SELL", "p", "AUDNZD"))

    def test_67(self):
        self._testParser("""Sell euraud market@1.5224
Risk 0.03/1000$
And sell limit@1.5250
Risk 0.05/1000$
Sl  1.5286
Tp  1.5166""", Signal(1.5224, 1.5286, 1.5166, today, "SELL", "p", "EURAUD"))

    def test_68(self):
        self._testParser("""SELL EURJPY NOW
AT 133.40
TP 132.00
SL 134.00""", Signal(133.4,134,132,today,"SELL","p","EURJPY"))

    def test_69(self):
        self._testParser("""GBPUSD Bearish BAT pattern Start to enter short position from 1.3193 to 1.3210 Sl above 1.3233 TP1: 1.3145 TP2: 1.3080
""", Signal(1.3193,1.3233,1.3145, today, "SELL", "p","GBPUSD"))

    def test_70(self):
        self._testParser("""Sell limit Euraud
at 1.5630 & 1.5530
SL 1.5730 Tp leave open""", None)

    def test_71(self):
        self._testParser("""❗️EurAud❕Buy ❕1.55500❗️

🅾️ SL 1.54700
✅ TP 1.56250""", Signal(1.555, 1.547, 1.5625, today, "BUY","p","EURAUD"))

    def test_72(self):
        self._testParser("""Gbp/nzd buy now 1.91200
sl 1.90300
tp 1.93700""", Signal(1.912, 1.9030, 1.9370, today, "BUY", "p", "GBPNZD"))

    def test_73(self):
        self._testParser("""BUY GBPUSD

At Price             : 1.33400
Take Profit      : 1.34600
Stop Loss        : 1.32200

BUY NZDUSD

At Price             : 0.69300
Take Profit      : 0.70500
Stop Loss         : 0.68100

 SELL USDCAD

At Price              :1.28400
Take Profit       : 1.27200
Stop Loss         : 1.29600

BUY AUDCAD

At Price             : 0.96700
Take Profit      : 0.97900
Stop Loss        : 0.95500


 BUY CHFJPY

At Price              : 114.300

Take Profit       : 115.500
Stop Loss         : 113.100

BUY CADJPY

At Price              : 88.300
Take Profit       : 89.500
Stop Loss          :87.100

BUY GBPJPY

At Price              : 151.300
Take Profit       :152.800
Stop Loss          : 150.00""", Signal(1.334, 1.322, 1.346, today, "BUY", "p", "GBPUSD"))

    def test_74(self):
        self._testParser("""signal 6
sell gbpaud 1.77666
sl :1.7839
tp 1.7696""", Signal(1.77666,1.7839,1.7696,today,"SELL","p","GBPAUD"))

    def test_75(self):
        self._testParser("""2:.  Usdchf 0.9921 sell now sl 0.9970 tp 0.9865 lot size 0.20 .""",
        Signal(0.9921,0.997,0.9865,today,"SELL","p","USDCHF"))

    def test_75(self):
        self._testParser("""BUY BTCUSD 18000 SL 15000 TP 22000""",
        Signal(18000,15000,22000,today,"BUY","p","BTCUSD"))

    def test_76(self):
        self._testParser("""Usdcad buy now 1.3241
Sl: 1.313
Tp: 1.345""", Signal(1.3241,1.313,1.345,today,"BUY","p","USDCAD"))

    def test_77(self):
        self._testParser("""Free signal 21.12.2017:

EURNZD SELL
Max 5% risk

ENTRY 1.69071
SL 1.7000
TP1 1.68450
TP2 1.68000""", Signal(1.69071, 1.7, 1.6845,today,"SELL","p","EURNZD"))

    def test_78(self):
        self._testParser("""Signal no.1✳️✳️
Buy Usd/Jpy @ 113.18
Tp - 114.02 & 114.85
Sl - ???

Support around 113.10""", None)

    def _untested_79(self):
        self._testParser("""*Tycoon Capital Trading And Investment Club*
*Trade Alert*
Pair: AUDUSD
Entry Type: SELL STOP @0.78265
Direction: SHORT @0.78265
Stop Loss: 0.78752
Take Profit: 0.77309
Risk small and keep your lots fixed or calculated.

#traderigorous #capitalgrowthexpects""", Signal(0.78265,0.78752, 0.77309,today,"SELL","p","AUDUSD"))

    def test_80(self):
        self._testParser("""EURJPY SELL NOW @ 134.30/35
SL 134.51
TP 131.50""", Signal(134.30,134.51,131.5,today,"SELL","p","EURJPY"))

    def test_81(self):
        self._testParser("""Usdjpy sell 112.600

Sl 113.200 80 pips
Tp 111.600 100 pips""", Signal(112.6,113.2,111.6,today,"SELL","p","USDJPY"))

    def test_82(self):
        self._testParser("""NZD/USD Sell H1
At :  0.7198
SL : 0.7231 - Risk 30 Pip
TP1 :0.7150 - Reward  60 pip
TP2 : 0.7086 - Reward  115 pip
TP3 : 0.70345 - Reward  165 pip""", Signal(0.7198, 0.7231, 0.7150,today,"SELL","p","NZDUSD"))

    def test_83(self):
        self._testParser("""EURJPY BUY LIMIT SET AT @
133.225

SL @ 133.000(22 PIP)
TP @ 133.825(60 PIP)""", Signal(133.225, 133.0, 133.825, today,"BUY","p","EURJPY"))

    def test_84(self):
        self._testParser("""ed_circle: sell USDJPY@111.76
:small_orange_diamond:stop loss @ 112.24
:large_blue_diamond: take profit@ 111.80
lot size: 0.01 at 500 usd
SIGNAL NO:27""", None) # take profit is above sell

    def test_85(self):
        self._testParser("""Signal no.5
Buy
Nzd cad @ 0.9084
Sl.                0.9004
Tp.               0.9154""", Signal(0.9084, 0.9004, 0.9154, today, "BUY", "p", "NZDCAD"))

    def test_86(self):
        self._testParser("""Sell
Cad chf @ 0.7437
Sl.               0.7537
Tp.              0.7283""", Signal(0.7437, 0.7537, 0.7283, today, "SELL","p","CADCHF"))

    def test_87(self):
        self._testParser("""Sell
Aud nzd @ 1.0780
Sl.                1.0895
Tp.                1.0700""", Signal(1.0780, 1.0895, 1.0700, today, "SELL","p","AUDNZD"))

    def test_88(self):
        self._testParser("""Buy
Gbp cad @ 1.7500
Sl.                1.7360
Tp.                1.7650""", Signal(1.7500, 1.7360, 1.7650, today, "BUY","p","GBPCAD"))

    def test_89(self):
        self._testParser("""BUY #EURJPY:: From {132.50-132.20}
T.P1 : 134.10 (160 Pip)
S.L : 131.50""", Signal(132.50,131.5,134.10, today, "BUY", "p", "EURJPY"))

    def test_90(self):
        self._testParser("""Buy cad jpy@85.37
Sl 84.37
Tp 87.00""", Signal(85.37,84.37,87, today, "BUY", "p", "CADJPY"))

    def test_91(self):
        self._testParser("""Buy :arrow_up_small: now @ 84.430
1st Tp @ 84.850
2nd Tp @ 85.420
Sl @ 84.100""", Noise("Missing pair")) # no pair

    def test_92(self):
        self._testParser("""AUDUSD SELL NOW 0.79356
T.p.1
0.78820
T.P 2
0.78335
T.P 3
0.77935
S.L
0.79920""", Signal(0.79356,0.7992,0.7882, today, "SELL", "p", "AUDUSD"))

    def test_93(self):
        self._testParser("""EURUSD SELL NOW 1.21910
T.p 1
1 21520
T.p 2
1.21012
T.p 3
1.19520
S.l
1.22720""", Signal(1.2191,1.2272,1.21012, today, "SELL", "p", "EURUSD"))

    def test_94(self):
        self._testParser("""33]
dartSignal: 20

Symbol chart : EUR/ NZD
Type  chart_with_upwards_trend : Modify buy
Price  checkered_flag : 1.6780
Tp 1  white_check_mark : 1.6850
SL  x : 1.6710
:spiral_calendar_pad:2018.1.14""", Signal(1.6780,1.6710,1.6850, today, "BUY", "p", "EURNZD")) #mal primer tp

    def test_95(self):
        self._testParser("""For gbpchf
Please sell at 1.3283
SL 1.3350 Tp1 1.3253
Tp2 1.3223""", Signal(1.3283,1.3350,1.3253, today, "SELL", "p", "GBPCHF"))

    def test_96(self):
        self._testParser("""GBPAUD buy stop 1.7754
Tp 1.785
Sl 1.77""", Signal(1.7754,1.77,1.785, today, "BUY", "p", "GBPAUD"))

    def test_97(self):
        self._testParser("""Gbpjpy Sell now 144.250
T-P :white_check_mark: 143.950
S-L :x: 144.600""", Signal(144.25,144.6,143.95, today, "SELL", "p", "GBPJPY"))

    def test_98(self):
        self._testParser("""Euraud sell now 1.56360
Stop loss 1.57000
Take profit 1.54000
Long term trade use moneymanagement""", Signal(1.56360,1.57000,1.54000, today, "SELL", "p", "EURAUD"))

    def test_99(self):
        self._testParser("""PAIR : EUR/JPY
ENTRY PRICE : 130.300

DIRECTION : SHORT :chart_with_downwards_trend:

SL : 130.700 (-40 pips)
TP : 122.500 (+780 pips)""", Signal(130.300,130.700,122.500, today, "SELL", "p", "EURJPY"))

    def test_100(self):
        self._testParser("""BUY XAU/USD  Now 1195.00
:small_red_triangle_down: SL :- 1185.00
:small_orange_diamond:TP1:- 1200.00
:small_orange_diamond:TP2:- 1220.00
:small_orange_diamond:Tp3:-  1250.00""", Signal(1195.00,1185.00,1200.00, today, "BUY", "p", "XAUUSD"))

    def test_101(self):
        self._testParser("""**buy usdjpy now at 110.28_110.20
stop 109.83
Target1#110.52
target2# 110.70""", Signal(110.28, 109.83, 110.52, today, "BUY", "p", "USDJPY"))

    def test_102(self):
        self._testParser("""Buy NZD USD 0.6470
STOP LOSS 0.6400
TAKE PROFIT 0.70000""", Signal(0.647, 0.64, 0.7, today, "BUY", "p", "NZDUSD"))

    def test_103(self):
        self._testParser("""📠 Signal Number :16

#CADCHF**BUY📣

🌷🎓Waves ScoUt Forex🎓🌷
At :73.94
SL :73.76**Risk**15Pip
TP :76.01**Reward**205pip🎯""", Signal(0.7394, 0.7376, 0.7601, today, "BUY", "p", "CADCHF"))

    def test_103b(self):
            self._testParser("""📠 Signal Number :16

    #CADCHF**BUY📣

    🌷🎓Waves ScoUt Forex🎓🌷
    At :73.94
    SL :73.66**Risk**25Pip
    TP :76.01**Reward**205pip🎯""", Signal(0.7394, 0.7366, 0.7601, today, "BUY", "p", "CADCHF"))

    def test_104(self):
        self._testParser(""":female-technologist:GBP USD Sell Now 1.2795
:cl: Sl 1.2890
:parking: Tp 1.2720""", Signal(1.2795, 1.289, 1.272, today, "SELL", "p", "GBPUSD"))

    def test_105(self):
        self._testParser("""Today Rock Call
Sell GOLD 1240
SL 1250
TARGET 1230:boom:®:pound:""", Signal(1240, 1250, 1230, today, "SELL", "p", "XAUUSD"))

    def test_106(self):
        self._testParser("""Buy Gbp cad 1.6660
Sl 1.6580
Tp1 1.6700
Tp2 1.6750
Tp3 1.6800
Tp4 1.6850
Tp5 1.6900""", Signal(1.666, 1.658, 1.67, today, "BUY", "p", "GBPCAD"))

    def test_107(self):
        self._testParser("""🔴XAU/USD SELL ENTRY AT
1247.92
Tp1 1240.92
Tp2 1235.92
Sl 1260.92""", Signal(1247.92, 1260.92, 1240.92, today, "SELL", "p","XAUUSD"))

    def test_108(self):
        self._testParser(""":small_blue_diamond:Gold buy now at 1224
   :small_red_triangle_down:Stop loss at 1215
:heavy_check_mark:Take Profit at 1243 & 1258""", Signal(1224, 1215, 1243, today, "BUY", "p", "XAUUSD"))

    def test_109(self):
        self._testParser("""#GBPUSD  Buy
ID : 4-03
At : 1.2724
SL : 1.2630 -  Risk 84 Pip
TP : 1.2921 - Reward 206 pip
Date : 2018/12/24""", Signal(1.2724, 1.2630, 1.2921, today, "BUY", "p", "GBPUSD"))

    def test_110(self):
        self._testParser("""🌐XAU USD Sell now 1280
⚜️TP 1270
⚜️ SL 1290
All Copyrights© Reserved""", Signal(1280, 1290, 1270, today, "SELL", "p", "XAUUSD"))

    def test_111(self):
        self._testParser("""# GBP AUD - Sell @ 1.8036 - SL : 1.8096 - TP : 1.8001 - 1.7970 - 1.7930""",
        Signal(1.8036, 1.8096, 1.8001, today, "SELL", "p", "GBPAUD"))


    def test_112(self):
        self._testParser("""Eur/aud @ Sell Now 1.63260
Take Profit: 20-50-100 Pips
Stop Loss:- 45Pips""", None);

    def test_113(self):
        self._testParser("""GBPCAD SELL: 1.7025
Tp1: 1.6990 (35pips)
Tp2: 1.6955 (70pips)
Tp3: 1.6885 (140pips)
SI: 1.7085 (60pips)

Hit tp1 +35pips 🕺💃""", Signal(1.7025, 1.7085, 1.6990, today, "SELL", "p", "GBPCAD"))

    def test_114(self):
        self._testParser("""AUDJPY Buy: 77.19
Tp1: 77.44 (25pips)
Tp2: 77.74 (55pips)
Tp3: 78.29 (110pips)
St 76.69 (50pips)

Hit tp1 +25pips :man_dancing::dancer:""", Signal(77.19, 76.69, 77.44, today, "BUY", "p", "AUDJPY"))

    def test_115(self):
        self._testParser("""#USDCHF Buy @ :point_down::point_down:
Buy1 @ 0.98020 Tp @ 0.98200
Buy 2 @0.97700  Tp @ 0.97950
Buy 3 @0.97200  Tp @ 0.97500
SL @ 0.97000""", Signal(0.9802, 0.97, 0.9820, today, "BUY", "p", "USDCHF"))
    #crypto

    def test_116(self):
        self._testParser("""📊 Instant Order 📊

GOLD sell now  at --------------------1291.33📊

🔹 SL POINT set at-------------------------1299.78❌

🔹TP POINT set at --------------------------1263.61✅

🔺GOLD long-term SELL trade so must put low lot


📊 SWING TRADE 📊""", Signal(1291.33, 1299.78, 1263.61, today, "SELL", "p", "XAUUSD"))

    def test_117(self):
        self._testParser("""Audnzd buy @ 1.0590
🔴1.05431
🔵1.06638""", Signal(1.059, 1.05431, 1.06638, today, "BUY", "p", "AUDNZD"))

    def test_118(self):
        self._testParser("""CADJPY W1 WHISKER SUPPORT : 2019.01.06 00:00 BUY @ 81.139½
TP:  81.851 (71.2 pips)SL: 76.754 (438.5 pips)Bid: 81.162Ask: 81.170Spread:
0.8Previous Low = 76.75401:36 International Capital Markets Pty Ltd.""", Signal(81.139, 76.754, 81.851, today, "BUY", "p", "CADJPY"))

    def test_119(self):
        self._testParser("""On More Extra Signal On Request of Followrs
No Signals More This Week

XUAUSD SELL NOW @ 1293.00
SL : 1296.00
TP : 1285.00 / 1275.00
All Copyrights Reserved®""", Noise("Missing pair")) #Signal(1293, 1296, 1285, today, "SELL", "p", "XAUUSD"))

    def test_120(self):
        self._testParser("""🇺🇸🇯🇵 USDJPY SELL NOW 108,70
👉🏼 SL♨️ 109,50
👉🏼 TP 💯108,90

2% Risk Per Trade 👨🏻‍💻
OMID AFGHAN FOREX
All CopyRight © Reserved""", None)

    def test_121(self):
        self._testParser("""SELL USDJPY 109.44
TP109.28
SL109.56""", Signal(109.44, 109.56, 109.28, today, "SELL", "p", "USDJPY"))

    def test_211(self):
        self._testParser("""Coin Name-> DNT

#binance

Buy Around-300

Sell Targets

Target 1- 330
Target 2- 345
Target 3- 420

 Stop Loss - 275""", Noise("Missing pair")) # Signal(300, 275, 330, "BUY", "p", "DNT"))

    def test_212(self):
        self._testParser("""Gbpjpy sell now 142.000
Sl 143.000
Tp 140.000

Gold sell now 1308
Sl 1318
Tp 1290""", Signal(142.0, 143.0, 140.0, today, "SELL", "p", "GBPJPY"))

#    def test_213(self):
#        self._testParser("""1). Short GBPJPY
#@144.250
#SL 144.500
#TP144.700""", Signal(144.25, 144.5, 144.7, today, "SELL", "p", "GBPJPY"))

#    def test_214(self):
#        self._testParser("""Eur/usd @ Buy now 1.12900
#Take Profit: 30-40-50 Pips
#Stop Loss:-40Pips""", Signal(1.1290, 1.1250, [1.132, 1.133, 1.134], "BUY", "p", "EURUSD"))
