# Signals Python Parser

[![build status](http://img.shields.io/travis/kmels/sigpyparser/master.svg?style=flat)](https://travis-ci.org/kmels/sigpyparser)

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
python3 setup.py test
```

Roadmap
----
* Support multiple signals with multiple targets per text
