"""conftest.py — shared fixtures for the shipping test suite."""

import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from data_generator import generate_rows


@pytest.fixture(scope="session")
def sample_rows():
    """20 reproducible synthetic rows."""
    return generate_rows(count=20, seed=42)


@pytest.fixture(scope="session")
def sample_row(sample_rows):
    return sample_rows[0]


@pytest.fixture(scope="session")
def mapped_fields(sample_row):
    from column_mapper import map_row
    return map_row(sample_row)


@pytest.fixture(scope="session")
def cda_tree(mapped_fields):
    from transformer import transform
    return transform(mapped_fields)
