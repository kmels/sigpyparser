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
 * Support for major FX pairs.
 * Supports one TP price
 * More than 100+ unit tests

Roadmap
----
* Support cryptocurrency signals
* Support multiple TP
* Support multiple signals per text
