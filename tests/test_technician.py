# -*- coding: utf-8 -*-
from datetime import date
from typing import Optional
import pytest

from backend.app.models.technician import Technician

@pytest.fixture
def valid_technician():
    return Technician(
        technician_name="Carlos Silva",
        creation_date=date(2024, 1, 15),
        status="ativo",
        base_location_city_id=1,
        current_location_city_id=1,
        daily_capacity=8.8,
        position="Lider"
    )

def make_technician(valid_technician, **overrides):
    return Technician(**{**valid_technician.__dict__, **overrides})

# --- criacao basica ---

def test_technician_created_with_valid_fields(valid_technician):
    assert valid_technician.technician_name == "Carlos Silva"
    assert valid_technician.status == "ativo"
    assert valid_technician.daily_capacity == 8.8
    assert valid_technician.position == "Lider"

# --- status ---

def test_invalid_status_should_fail(valid_technician):
    with pytest.raises(ValueError, match="Status invalido"):
        make_technician(valid_technician, status="ferias")

def test_inactive_status_is_accepted(valid_technician):
    technician = make_technician(valid_technician, status="inativo")
    assert technician.status == "inativo"

def test_lowercase_status_is_normalized(valid_technician):
    technician = make_technician(valid_technician, status="ATIVO")
    assert technician.status == "ativo"

# --- position ---

def test_invalid_position_should_fail(valid_technician):
    with pytest.raises(ValueError, match="Cargo invalido"):
        make_technician(valid_technician, position="Estagiario")

def test_all_valid_positions_are_accepted(valid_technician):
    for position in ["Lider", "Supervisor", "Coordenador"]:
        technician = make_technician(valid_technician, position=position)
        assert technician.position == position

# --- dismiss_date ---

def test_inactive_technician_with_dismiss_date_is_accepted(valid_technician):
    technician = make_technician(
        valid_technician,
        status="inativo",
        dismiss_date=date(2025, 6, 1)
    )
    assert technician.dismiss_date == date(2025, 6, 1)

def test_active_technician_with_dismiss_date_should_fail(valid_technician):
    with pytest.raises(ValueError, match="Tecnico ativo nao pode ter data de demissao"):
        make_technician(valid_technician, status="ativo", dismiss_date=date(2025, 6, 1))

# --- daily_capacity ---

def test_zero_daily_capacity_should_fail(valid_technician):
    with pytest.raises(ValueError, match="Capacidade diaria deve ser maior que zero"):
        make_technician(valid_technician, daily_capacity=0.0)

def test_negative_daily_capacity_should_fail(valid_technician):
    with pytest.raises(ValueError, match="Capacidade diaria deve ser maior que zero"):
        make_technician(valid_technician, daily_capacity=-4.0)

# --- campos obrigatorios ---

def test_empty_name_should_fail(valid_technician):
    with pytest.raises(ValueError, match="Nome do tecnico nao pode ser vazio"):
        make_technician(valid_technician, technician_name="")