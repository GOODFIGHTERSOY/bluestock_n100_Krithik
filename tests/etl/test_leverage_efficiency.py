import pytest
from src.analytics.leverage_efficiency import safe_divide

def test_safe_divide_normal():
    assert safe_divide(10, 2) == 5

def test_safe_divide_zero():
    assert safe_divide(10, 0) is None

def test_safe_divide_none():
    assert safe_divide(None, 5) is None

def test_safe_divide_nan():
    import math
    assert safe_divide(float("nan"), 5) is None