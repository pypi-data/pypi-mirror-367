# LaughingFace

A library for managing and invoking AI modules with LaughingFace.

## Installation

Install via pip:

```
pip install laughingface
```

## Usage

```python
from laughingface import LaughingFace

# Initialize LaughingFace
laughing_face = LaughingFace(api_key="your-api-key")

# Sync modules
laughing_face.init()

# List modules
print(laughing_face.list_modules())

# Use a module
module = laughing_face.module("insulter")
result = module(name="John Doe")
print(result)
```
