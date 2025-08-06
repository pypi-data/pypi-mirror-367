# pyconverters_grobid

[![license](https://img.shields.io/github/license/oterrier/pyconverters_grobid)](https://github.com/oterrier/pyconverters_grobid/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyconverters_grobid/workflows/tests/badge.svg)](https://github.com/oterrier/pyconverters_grobid/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyconverters_grobid)](https://codecov.io/gh/oterrier/pyconverters_grobid)
[![docs](https://img.shields.io/readthedocs/pyconverters_grobid)](https://pyconverters_grobid.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyconverters_grobid)](https://pypi.org/project/pyconverters_grobid/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyconverters_grobid)](https://pypi.org/project/pyconverters_grobid/)

Convert PDF to structured text using [Grobid](https://github.com/kermitt2/grobid)

## Installation

You can simply `pip install pyconverters_grobid`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyconverters_grobid
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
