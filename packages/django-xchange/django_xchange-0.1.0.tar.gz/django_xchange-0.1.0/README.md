Django XChange
==============

[![Pypi](https://badge.fury.io/py/django-xchange.svg)](https://badge.fury.io/py/django-xchange)
[![coverage](https://codecov.io/github/k-tech-italy/django-xchange/coverage.svg?branch=develop)](https://codecov.io/github/k-tech-italy/django-xchange?branch=develop)
[![Test](https://github.com/k-tech-italy/django-xchange/actions/workflows/tests.yaml/badge.svg)](https://github.com/k-tech-italy/django-xchange/actions/workflows/tests.yaml)
[![Docs](https://readthedocs.org/projects/django-xchange/badge/?version=stable)](http://django-xchange.readthedocs.io/en/stable/)
[![Django](https://img.shields.io/pypi/frameworkversions/django/django-xchange)](https://pypi.org/project/django-xchange/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/django-xchange.svg)](https://pypi.org/project/django-xchange/)

Django XChange is a library providing a Rate model containing currency exchange rates for a day.

It relies on third-party libraries to fetch historical exchange rates.

How to use
----------

Default configuration is defined at src/django_xchange/config.py::DEFAULT_SETTINGS

A Django settings DJANGO_XCHANGE dictionary must be configured to override the default settings.

It is mandatory to configure the DJANGO_XCHANGE['BROKERS'] item with a list of brokers you intend to use.

For example:

```python
DJANGO_XCHANGE = {
    'BROKERS': ['django_xchange.brokers.pyoxr.PyoxrBroker']
}
```

See specific notes for the third-party exchange providers configuration

Third-party libraries
---------------------

### Open Exchange Rates

Requirements:

- extra: pyoxr (eg. `pip install django-xchange[pyoxr]`)
- settings: OPEN_EXCHANGE_RATES_APP_ID the app id provided by Open Exchange Rates
