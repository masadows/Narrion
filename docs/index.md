# Narrion

Welcome to the documentation for **Narrion**.

## Getting Started

This project uses **Python 3.12** and [uv](https://github.com/astral-sh/uv) for dependency management and package handling.

### Prerequisites

Ensure you have `make` installed. If you do not have `uv` installed, please install it first.

## Installation

### Create the Virtual Environment
```bash
    make create_environment
```

### Install Dependencies:

* For development (includes testing and docs tools):
```bash
    make requirements-dev
```

* For production only:
```bash
    make requirements
```

## Usage

To run the main application:
```bash
    make run
```

To open the icon browser (Qt Awesome):

```bash
    make browser
```

## Development Workflow

We use `ruff` for formatting/linting and `pytest` for testing.

### Quality & Testing

* **Linting** (Check code quality using ruff):
```bash
        make lint
```

* **Formatting** (Auto-fix code style using ruff):
```bash
    make format
```

* **Testing**:
```bash
    make test
```

* **Clean Up** (Remove compiled Python files and cache):
```bash
    make clean
```

## Documentation

To build and serve this documentation locally (live-reload):
```bash
    make docs-serve
```

To build the static site (HTML output):
```bash
    make docs
```