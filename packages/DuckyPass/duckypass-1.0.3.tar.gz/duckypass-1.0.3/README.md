# DuckyPassAPI

A Python module for generating passwords using the DuckyPass API.

## Installation

```bash
pip install DuckyPass
```

## Usage

```python
from DuckyPass import DuckyPassAPI

# Generate a single secure password
password = DuckyPass("secure", 1)
print(password)

# Generate 5 simple passwords
passwords = DuckyPass("simple", 5)
print(passwords)
```

## License

GPLv3