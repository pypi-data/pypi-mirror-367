# configtony

A (tiny) configuration library.

## Installing

```bash
# The easy way
pip install configtony

# Installing from source
git clone https://github.com/IAmMoltony/configtony.git
cd configtony
pip install .
```

## Example

```python
from configtony import Config

config = Config("config.jsonc")
# Adds an option called 'username' that is of string type, default 'John'
config.add_option("username", str, "John")
config.add_option("some_flag", bool, False)
config.parse()

print(config.get("username"))
```
