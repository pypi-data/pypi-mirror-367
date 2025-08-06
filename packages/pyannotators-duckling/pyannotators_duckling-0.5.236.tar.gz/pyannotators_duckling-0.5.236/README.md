# pyannotators_duckling

[![license](https://img.shields.io/github/license/oterrier/pyannotators_duckling)](https://github.com/oterrier/pyannotators_duckling/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyannotators_duckling/workflows/tests/badge.svg)](https://github.com/oterrier/pyannotators_duckling/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyannotators_duckling)](https://codecov.io/gh/oterrier/pyannotators_duckling)
[![docs](https://img.shields.io/readthedocs/pyannotators_duckling)](https://pyannotators_duckling.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyannotators_duckling)](https://pypi.org/project/pyannotators_duckling/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyannotators_duckling)](https://pypi.org/project/pyannotators_duckling/)

Annotator based on Facebook's Duckling

## Installation

You can simply `pip install pyannotators_duckling`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyannotators_duckling
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
