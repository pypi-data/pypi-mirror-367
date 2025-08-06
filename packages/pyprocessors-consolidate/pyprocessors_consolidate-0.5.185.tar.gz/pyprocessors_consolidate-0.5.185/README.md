# pyprocessors_consolidate

[![license](https://img.shields.io/github/license/oterrier/pyprocessors_consolidate)](https://github.com/oterrier/pyprocessors_consolidate/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyprocessors_consolidate/workflows/tests/badge.svg)](https://github.com/oterrier/pyprocessors_consolidate/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyprocessors_consolidate)](https://codecov.io/gh/oterrier/pyprocessors_consolidate)
[![docs](https://img.shields.io/readthedocs/pyprocessors_consolidate)](https://pyprocessors_consolidate.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyprocessors_consolidate)](https://pypi.org/project/pyprocessors_consolidate/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyprocessors_consolidate)](https://pypi.org/project/pyprocessors_consolidate/)

Consolidate annotations coming from different annotators

## Installation

You can simply `pip install pyprocessors_consolidate`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyprocessors_consolidate
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
