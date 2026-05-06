# -*- coding: utf-8 -*-
from backend.app.models.city import City
import pytest

@pytest.fixture
def valid_city():
    return City(
        city_name="Sao Paulo",
        state="SP",
        country="Brasil",
        geolocation_lat=-23.5505,
        geolocation_lon=-46.6333
    )

def make_city(valid_city, **overrides):
    return City(**{**valid_city.__dict__, **overrides})

# --- criacao basica ---

def test_city_created_with_valid_fields(valid_city):
    assert valid_city.city_name == "Sao Paulo"
    assert valid_city.state == "SP"
    assert valid_city.country == "Brasil"
    assert valid_city.geolocation_lat == -23.5505
    assert valid_city.geolocation_lon == -46.6333

# --- state ---

def test_lowercase_state_is_normalized(valid_city):
    city = make_city(valid_city, state="sp")
    assert city.state == "SP"

def test_invalid_state_should_fail(valid_city):
    with pytest.raises(ValueError, match="Estado invalido"):
        make_city(valid_city, state="XX")

def test_exterior_state_is_accepted(valid_city):
    city = make_city(valid_city, state="EX")
    assert city.state == "EX"

# --- campos obrigatorios ---

def test_empty_city_name_should_fail(valid_city):
    with pytest.raises(ValueError, match="Nome da cidade nao pode ser vazio"):
        make_city(valid_city, city_name="")

def test_empty_country_should_fail(valid_city):
    with pytest.raises(ValueError, match="Pais nao pode ser vazio"):
        make_city(valid_city, country="")

# --- geolocation ---

def test_latitude_above_limit_should_fail(valid_city):
    with pytest.raises(ValueError, match="Latitude invalida"):
        make_city(valid_city, geolocation_lat=91.0)

def test_latitude_below_limit_should_fail(valid_city):
    with pytest.raises(ValueError, match="Latitude invalida"):
        make_city(valid_city, geolocation_lat=-91.0)

def test_longitude_above_limit_should_fail(valid_city):
    with pytest.raises(ValueError, match="Longitude invalida"):
        make_city(valid_city, geolocation_lon=181.0)

def test_longitude_below_limit_should_fail(valid_city):
    with pytest.raises(ValueError, match="Longitude invalida"):
        make_city(valid_city, geolocation_lon=-181.0)

def test_boundary_latitude_is_accepted(valid_city):
    city = make_city(valid_city, geolocation_lat=90.0)
    assert city.geolocation_lat == 90.0

def test_boundary_longitude_is_accepted(valid_city):
    city = make_city(valid_city, geolocation_lon=180.0)
    assert city.geolocation_lon == 180.0