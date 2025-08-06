# pyconverters_newsml

[![license](https://img.shields.io/github/license/oterrier/pyconverters_newsml)](https://github.com/oterrier/pyconverters_newsml/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyconverters_newsml/workflows/tests/badge.svg)](https://github.com/oterrier/pyconverters_newsml/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyconverters_newsml)](https://codecov.io/gh/oterrier/pyconverters_newsml)
[![docs](https://img.shields.io/readthedocs/pyconverters_newsml)](https://pyconverters_newsml.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyconverters_newsml)](https://pypi.org/project/pyconverters_newsml/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyconverters_newsml)](https://pypi.org/project/pyconverters_newsml/)

Fetch articles from Pubmed

## Installation

You can simply `pip install pyconverters_newsml`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyconverters_newsml
```

### Running the test suite

You can run the full test suite against all supported versions of Python (3.8) with:

```
tox
```

### Building the documentation

You can build the HTML documentation with:

```
tox -e docs
```

The built documentation is available at `docs/_build/index.html.
