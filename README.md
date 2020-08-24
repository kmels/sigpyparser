# Signals Python Parser

[![build status](http://img.shields.io/travis/kmels/sigpyparser/master.svg?style=flat)](https://travis-ci.org/kmels/sigpyparser)

[![codecov](https://codecov.io/gh/kmels/SigPyParser/branch/master/graph/badge.svg)](https://codecov.io/gh/kmels/SigPyParser)

This is a simple library to extract market signals from providers. A signal
consists of:
  * Pair
  * Entry price
  * Stop loss price
  * Take profit price
  * Date
  * Username

For each signal, the following is calculated:
  * Unique Hash identifier
  * Odds
  * Unique Rep
  * MT4 Rep

Features
----
 * Support for majoe FX pairs
 * Supports one or multiple TP
 * More than 100+ unit tests

Install
----

```
git clone git@github.com:kmels/SigPyParser.git
python3 setup.py install --user
```

Usage
----

```
python3

> from signal_parser import parser
> parser.parseSignal("SELL NZDUSD @ close 0.68042½ TP: 0.67541 (50.2 pips)SL: 0.69402 (136.0 pips)"")
```

Tests
----

```
python3 setup.py test # run all 
python3 -m unittest tests.fx_test.TestFXParser # run all fx parser tests
python3 -m unittest tests.crypto_tests.TestCryptoParser # run all crypto parser tests
python3 -m unittest tests.fx_test.TestFXParser.test_215
```

Test coverage
----

```
pip3 install pytest pytest-cov
pytest --cov=./
```

Roadmap
----
* Support multiple signals with multiple targets per text: pass test_115 in fx_test.py
+ Test SignalList constructor for SignalList of SignalList

Deployment via ZMQ REP
----

1. Build the container in .

`sudo docker build -t kmels/sigpyparser_zmqrep containers/zmq_rep`

2. Run the docker

`sudo docker run -P -p 10001:10001 kmels/sigpyparser_zmqrep`

