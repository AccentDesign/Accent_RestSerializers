# Accent_RestSerializers

[![Testing workflow](https://github.com/AccentDesign/Accent_RestSerializers/actions/workflows/test.yml/badge.svg)](https://github.com/AccentDesign/Accent_RestSerializers/actions/workflows/test.yml)

## Description

Library of useful Rest Framework serializers for django

## Includes

Many-to-many serializer that will loop through an infinite depth and create, update and delete related entities.


## Getting Started

Installation

```bash
pip install git+https://github.com/AccentDesign/Accent_RestSerializers.git@master#egg=rest_serializers
```

settings.py

```bash
INSTALLED_APPS = [
   ...
   'rest_serializers',
   ...
]
```

## Usage

### ManyToManySerializer

This class is required in the parent serializer.

Example

```python
from rest_serializers.serializers import ManyToManySerializer

class ChildSerializer(serializers.ModelSerializer):
     class Meta:
        model = Child
        fields = ('id', 'name')


class ParentSerializer(ManyToManySerializer):
     children = ChildSerializer(many=True)

     class Meta:
        model = Parent
        fields = ('id', 'name', 'children')
```

Here the ChildSerializer can also inherit from ManyToManySerializer to include a further depth and so on.

### Install dependencies

```bash
uv sync --all-extras
```

### Run tests

```bash
uv run tests/manage.py test
```

### Run linters

black:
```bash
uv run black rest_serializers tests
```

ruff:
```bash
uv run ruff check --fix rest_serializers tests
```

### Build package

install dependencies:
```bash
uv tool install hatch
```

build package:
```bash
rm -rf dist && uv build
```

### Publish package

```bash
uv publish --token <token>
```