# Changelog

## Dev

* Switch to Github Actions CI, remove travis-ci.
* Add support for Django 3.2 and Python 3.9

## v2.1.0 - August 22, 2020

* Remove support for older django and python versions
* Add support for Django 3.0 and Django 3.1
* Add support for [PostGIS](https://github.com/korfuri/django-prometheus/pull/221), Thanks [@EverWinter23](https://github.com/EverWinter23)

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