# Averager

**Averager** is a simple Python library to calculate averages of values.

```python
>>> import averager
>>> averager.average(1, 2, 3)
2
>>> averager.weighted_average((1, 2), (2, 3))
1.6
>>> averager.median(5, 1, 2)
2
>>> averager.mode(1, 2, 4, 3, 3)
3
```

> [!WARNING]
> Averager is deprecated, and no new features will be added. Please use the built-in [
`statistics` module][statistics] for similar functionality and more.

[![Total Downloads](https://img.shields.io/pepy/dt/averager)][pypi]
[![Supported Versions](https://img.shields.io/pypi/pyversions/averager.svg)][pypi]
[![Testing Status](https://img.shields.io/github/actions/workflow/status/bsoyka/averager/test.yml?branch=main&label=tests)][testing]
[![Coverage](https://img.shields.io/codecov/c/github/bsoyka/averager)][codecov]
[![GitHub last commit](https://img.shields.io/github/last-commit/bsoyka/averager)][github]

## Installation and usage

Averager is [available on PyPI][pypi].
Install it with your preferred package manager:

```sh
$ uv add averager
$ pip install averager
```

Averager officially supports Python 3.9+.

**[Read the documentation][docs]** to learn how to use Averager.

[codecov]: https://codecov.io/github/bsoyka/averager

[docs]: https://averager.readthedocs.io

[github]: https://github.com/bsoyka/averager

[license]: https://github.com/bsoyka/averager/blob/master/LICENSE

[pypi]: https://pypi.org/project/averager/

[statistics]: https://docs.python.org/3/library/statistics.html

[testing]: https://github.com/bsoyka/averager/actions/workflows/test.yml
