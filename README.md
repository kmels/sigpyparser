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

Install
----

´´´
python3 setup.py install --user
´´´

Usage
----

´´´
python3

> from signal_parser import *
> parser.parseSignal("")

´´´

Features
----
 * Support for major FX pairs.
 * Supports one and multiple TP price(s)
 * More than 100+ unit tests


Roadmap
----
* Support multiple signals with multiple targets per text
