# A2A Client

A simple A2A client library.

## Installation

```bash
pip install a2aclient
```

## Usage

```python
from a2aclient import hello_world

# Basic usage
print(hello_world())  # Output: Hello, World! Welcome to a2aclient!

# With custom name
print(hello_world("Alice"))  # Output: Hello, Alice! Welcome to a2aclient!
```

## Command Line Usage

After installation, you can also use the command line interface:

```bash
a2aclient
```

## Development

To install in development mode:

```bash
pip install -e .[dev]
```

## Building and Publishing

To build the package:

```bash
python -m build
```

To upload to PyPI:

```bash
twine upload dist/*
```

## License

MIT License
