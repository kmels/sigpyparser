import unittest
from datetime import datetime

from signal_parser import *
from signal_parser.signal import *
from signal_parser.parser import *

today = datetime.now().replace(second=0).replace(microsecond=0)

def _parseSignal(t: str):
    return parseSignal(t,today,'p')

class TestCryptoParser(unittest.TestCase):

    def _testParser(self,text,expected):
        parsedSignal = _parseSignal(text)

        if type(expected) in [Signal,Noise,type(None)]:
            self.assertEqual(
                parsedSignal,
                expected,
                "\n\tEXPECTED: " + str(expected) + ".\n\tRESULT:   " +
                str(parsedSignal)
            )
        else:
            assert(type(expected) == SignalList)

            self.assertTrue(type(parsedSignal) == SignalList,
                "\n\tEXPECTED: SignalList, got %s" % str(type(parsedSignal)))
            self.assertEqual(len(parsedSignal), len(expected),
                "\n\tEXPECTED: %d, got %d" % (len(expected),len(parsedSignal)))

            self.assertEqual(
                parsedSignal[0],
                expected[0],
                "\n\tEXPECTED: " + str(expected) + ".\n\tRESULT:   " +
                str(parsedSignal)
            )

            self.assertEqual(
                parsedSignal[1]['unique_rep'],
                expected[1]['unique_rep'],
                "\n\tEXPECTED: " + str(expected[1]['unique_rep']) + ".\n\tRESULT:   " +
                str(parsedSignal[1]['unique_rep'])
            )
            
            expected = sorted(expected, key=lambda s: s['tp'])
            parsedSignal = sorted(parsedSignal, key=lambda s: s['tp'])

            expected_strs = ','.join([i['unique_rep'] for i in expected])
            parsedSignal_strs = ','.join([i['unique_rep'] for i in parsedSignal])

            self.assertEqual(parsedSignal_strs, expected_strs,
                "\n\tEXPECTED: " + expected_strs + ".\n\tRESULT:   " + parsedSignal_strs)

            for i, exp in enumerate(expected):
                self.assertEqual(parsedSignal[i]['unique_rep'], expected[i]['unique_rep'],
                "\n\t#"+str(i)+". EXPECTED: " + str(expected[i]['unique_rep']) + ".\n\tRESULT:   " +
                str(parsedSignal[i]['unique_rep']))

            self.assertEqual(
                parsedSignal,
                expected,
                "\n\tEXPECTED: " + str(expected) + ".\n\tRESULT:   " +
                str(parsedSignal)
            )

    def test_crypto1(self):
        sig1 = Signal(11100,10920,11800,today,'BUY','p','MDA/BTC')
        sig2 = Signal(11100,10920,12100,today,'BUY','p','MDA/BTC')
        sig3 = Signal(11100,10920,13000,today,'BUY','p','MDA/BTC')
        
        assert(type(sig1) is Signal)
        self._testParser("""🌴FREE SIGNAL🌴
💎#MDA
💎Buy zone 11100-11270
💎Tg1 11800
💎Tg2 12100
💎Tg3 13000
💎Stop 10920""", SignalList([sig1,sig2,sig3]))

    def test_crypto2(self):
        sig1 = Signal(300,275,330,today,'BUY','p','DNT/BTC')
        sig2 = Signal(300,275,345,today,'BUY','p','DNT/BTC')
        sig3 = Signal(300,275,420,today,'BUY','p','DNT/BTC')
        self._testParser("""Coin Name-> DNT       
#binance

Buy Around-300

Sell Targets

Target 1- 330
Target 2- 345
Target 3- 420

 Stop Loss - 275""", SignalList([sig1,sig2,sig3]))

    def test_crypto3(self):
        self._testParser("""#MFT
#Binance 

Buy zone: 40 - 43 sats

Targets :

T1 : 47 
T2 : 50 
T3 : 54 
T4 : 58 
T5 : 65""", Noise("Missing SL"))

    def test_crypto4(self):        
        self._testParser("""To Moon CRYPTO SIGNALS 🏴‍☠️, [31.05.19 08:07]
[Forwarded from Luxury crypto signal / VIP SIGNAL]
Coin - #PHB/Btc

Buy zone - .310

Sell Target

Target 1 - 350
Target 2- 400
Target 3- 500

STOP - 0290""", None)

    def test_crypto5(self):
        sig1 = Signal(190,160,250,today,'BUY','p','ZIL/BTC')
        sig2 = Signal(190,160,320,today,'BUY','p','ZIL/BTC')
        sig3 = Signal(190,160,400,today,'BUY','p','ZIL/BTC')
        
        self._testParser("""To Moon CRYPTO SIGNALS 🏴‍☠️, [03.06.19 10:44]
[Forwarded from Luxury crypto signal / VIP SIGNAL]
Coin - #ZIL/BTC 

#BINANCE

BUY ZONE -  190

SELL TARGET 

TARGET 1 - 250
TARGET 2 - 320
TARGET 3 - 400
 
STOP LOSS : 160""", SignalList([sig1,sig2,sig3]))



    def test_crypto6(self):        
        self._testParser("""Buy FET at 2350-2380  sat
target = 3400 sat
stop bellow 2190


COIN: #PIVX/BTC (BINANCE)

📌BUY PRICE:   0.0000860 - 890

🔥 TARGET :  0.0000950 - 1030 - 1200

❌ Stop-loss: 0.0000770""", None)

    def test_crypto7(self):        
        self._testParser("""https://www.tradingview.com/x/9dRqwTjX/

###

COIN: #ENJ/BTC (BINANCE)

📌BUY PRICE:   0.00002150 - 2180

🔥 TARGET :  0.00002290 - 2470 - 2650

❌ Stop-loss: 0.00001990

https://www.tradingview.com/x/ZFmVEuQX/""", None)


    def test_crypto8(self):        
        self._testParser("""MID TERM 📍 #BTS📍

#BITTREX ▶️ https://international.bittrex.com/Market/Index?MarketName=BTC-BTS

Buy Zone: 850 or below
T 1: 1130
T 2: 1380
 T 3: 1670
T 4: 1920""", Noise("Missing SL"))

