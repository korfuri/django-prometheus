# Changelog

## DEV

* Remove support for older django and python versions

## v2.0.0 - Jan 20, 2020

* Added support for newer Django and Python versions
* Added an extensibility that applications to add their own labels to middleware (request/response) metrics
* Allow overriding and setting custom bucket values for request/response latency histogram metric
* Internal improvements:
  * use tox
  * Use pytest
  * use Black
  * Automate pre-releases on every commit ot master
  * Fix flaky tests.

## v1.1.0 -  Sep 28, 2019

* maintenance release that updates this library to support recent and supported version of python & Django