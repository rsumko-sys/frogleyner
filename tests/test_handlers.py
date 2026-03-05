import pytest
from handlers import target_water_ml, frog_percent

def test_target_water_ml():
    assert target_water_ml(70) == 2450
    assert target_water_ml(None) == 2500
    assert target_water_ml(0) == 2500

def test_frog_percent():
    assert frog_percent(1000, 2000) == 50
    assert frog_percent(0, 2000) == 0
    assert frog_percent(2000, 0) == 0
    assert frog_percent(3000, 2000) == 100
