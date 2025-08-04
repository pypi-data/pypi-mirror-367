# Kosmos

Koordinations-, Optimierungs- und Simulations-Software für Modulare Quanten-Systeme in 6G Netzwerken

Make sure that you have Python version >=3.13

## Installation

### Install from PyPI (when published)

```sh
pip install kosmos
```

### Development Setup

```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -e ".[dev]"
```

## Usage

```sh
python -m kosmos.main
```

### Run tests

```sh
pytest -v
```

### Get test coverage

```sh
coverage run -m pytest tests/ && coverage report -m
```

### Run lint

```sh
ruff check .
```

### Run format

```sh
ruff format .
```

## Building and Publishing

### Build the package

```sh
python -m build
```

### Publish to PyPI

```sh
pip install twine
twine upload dist/*
```
