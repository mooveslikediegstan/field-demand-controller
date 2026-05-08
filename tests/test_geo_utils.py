# -*- coding: utf-8 -*-
import pytest
from backend.app.models.geo_utils import distance_between_coordinates

# SP → RJ: ~360km em linha reta, ~490km com fator
SP_LAT, SP_LON = -23.5505, -46.6333
RJ_LAT, RJ_LON = -22.9068, -43.1729

def test_distance_sp_to_rj_with_correction():
    dist = distance_between_coordinates(SP_LAT, SP_LON, RJ_LAT, RJ_LON)
    assert 480 < dist < 520

def test_distance_sp_to_rj_without_correction():
    dist = distance_between_coordinates(SP_LAT, SP_LON, RJ_LAT, RJ_LON, apply_correction=False)
    assert 350 < dist < 380

def test_same_city_returns_zero():
    dist = distance_between_coordinates(SP_LAT, SP_LON, SP_LAT, SP_LON)
    assert dist == 0.0

def test_distance_is_symmetric():
    dist_ab = distance_between_coordinates(SP_LAT, SP_LON, RJ_LAT, RJ_LON)
    dist_ba = distance_between_coordinates(RJ_LAT, RJ_LON, SP_LAT, SP_LON)
    assert abs(dist_ab - dist_ba) < 0.001