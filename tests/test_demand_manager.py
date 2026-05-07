# -*- coding: utf-8 -*-
from datetime import date
import pytest

from backend.app.models.demand_manager import DemandManager

@pytest.fixture
def valid_demand_manager():
    return DemandManager(
        demand_id=1,
        technician_id=10,
        status="Pendente"
    )

def make_dm(valid_demand_manager, **overrides):
    return DemandManager(**{**valid_demand_manager.__dict__, **overrides})

# --- criacao basica ---

def test_demand_manager_created_with_valid_fields(valid_demand_manager):
    assert valid_demand_manager.demand_id == 1
    assert valid_demand_manager.technician_id == 10
    assert valid_demand_manager.status == "Pendente"
    assert valid_demand_manager.is_deleted == False
    assert valid_demand_manager.next_demand_manager_id is None
    assert valid_demand_manager.demand_manager_id is None

# --- status ---

def test_invalid_status_should_fail(valid_demand_manager):
    with pytest.raises(ValueError, match="Status invalido"):
        make_dm(valid_demand_manager, status="Aguardando")

def test_all_valid_statuses_are_accepted(valid_demand_manager):
    for status in ["Pendente", "Em Execucao", "Concluido"]:
        dm = make_dm(valid_demand_manager, status=status)
        assert dm.status == status

def test_status_is_normalized(valid_demand_manager):
    dm = make_dm(valid_demand_manager, status="  pendente  ")
    assert dm.status == "Pendente"

# --- finish_date exige start_date ---

def test_finish_date_without_start_date_should_fail(valid_demand_manager):
    with pytest.raises(ValueError, match="Data de conclusao exige data de inicio"):
        make_dm(valid_demand_manager, start_date=None, finish_date=date(2026, 5, 10))

def test_finish_date_before_start_date_should_fail(valid_demand_manager):
    with pytest.raises(ValueError, match="Data de conclusao nao pode ser anterior a data de inicio"):
        make_dm(
            valid_demand_manager,
            start_date=date(2026, 5, 10),
            finish_date=date(2026, 5, 9)
        )

def test_valid_start_and_finish_date_is_accepted(valid_demand_manager):
    dm = make_dm(
        valid_demand_manager,
        start_date=date(2026, 5, 10),
        finish_date=date(2026, 5, 11)
    )
    assert dm.finish_date == date(2026, 5, 11)

# --- travel fields ---

def test_negative_travel_time_should_fail(valid_demand_manager):
    with pytest.raises(ValueError, match="Tempo de deslocamento nao pode ser negativo"):
        make_dm(valid_demand_manager, travel_time=-1.0)

def test_negative_travel_distance_should_fail(valid_demand_manager):
    with pytest.raises(ValueError, match="Distancia de deslocamento nao pode ser negativa"):
        make_dm(valid_demand_manager, travel_distance=-10.0)

def test_zero_travel_time_is_accepted(valid_demand_manager):
    dm = make_dm(valid_demand_manager, travel_time=0.0)
    assert dm.travel_time == 0.0

# --- soft delete ---

def test_is_deleted_defaults_to_false(valid_demand_manager):
    assert valid_demand_manager.is_deleted == False

def test_is_deleted_can_be_set_to_true(valid_demand_manager):
    dm = make_dm(valid_demand_manager, is_deleted=True)
    assert dm.is_deleted == True